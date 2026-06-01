"""
Step Executor — runs a single Playbook Step against the agent bus.

Handles:
  - Template rendering before dispatch
  - Condition evaluation (skip if false)
  - Approval gate (block + wait for user response)
  - Timeout enforcement
  - Retry orchestration
  - Output extraction and storage in TemplateContext
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Optional

from playbooks.schema.playbook_schema import OnFailure, Step
from core.playbook_engine.template import TemplateContext, TemplateEngine
from core.playbook_engine.retry import RetryEngine, RetryOutcome
from core.playbook_engine.observer import PlaybookObserver

logger = logging.getLogger("arizen.playbook.executor")


class StepSkipped(Exception):
    """Raised when a step's condition evaluates to False."""


class StepApprovalDenied(Exception):
    """Raised when the user declines the approval gate."""


class StepResult:
    def __init__(self, step_id: str, output: Any, duration_ms: int, tokens: int = 0) -> None:
        self.step_id     = step_id
        self.output      = output
        self.duration_ms = duration_ms
        self.tokens      = tokens
        self.success     = True

    @classmethod
    def failure(cls, step_id: str, error: str, duration_ms: int) -> "StepResult":
        r = cls(step_id, {"error": error}, duration_ms)
        r.success = False
        return r


class StepExecutor:
    """
    Executes a single Playbook Step.

    Dependencies injected:
      - bus       : agent message bus (delegates to specialist agents)
      - approval  : callable(step) → bool (prompts user via Command Nexus)
      - template  : TemplateEngine for input rendering
      - retry_eng : RetryEngine
      - observer  : PlaybookObserver for event emission
    """

    def __init__(self, bus, approval_fn, observer: PlaybookObserver) -> None:
        self._bus      = bus
        self._approve  = approval_fn
        self._template = TemplateEngine()
        self._retry    = RetryEngine()
        self._obs      = observer

    async def run(
        self,
        step:    Step,
        ctx:     TemplateContext,
        wave:    int = 0,
    ) -> StepResult:
        """
        Execute one step. Returns StepResult (success or failure).
        Raises StepSkipped or StepApprovalDenied for control flow.
        """
        start_ms = int(time.monotonic() * 1000)

        # ── 1. Condition check ────────────────────────────────────────
        if step.condition:
            should_run = self._template.render_condition(step.condition, ctx)
            if not should_run:
                logger.info("Step '%s' skipped — condition false: %s", step.id, step.condition)
                self._obs.step_skipped(step.id, f"condition: {step.condition}")
                raise StepSkipped(f"condition evaluated to false: {step.condition}")

        # ── 2. Render inputs ─────────────────────────────────────────
        try:
            rendered_inputs = self._template.render(step.inputs, ctx)
        except ValueError as exc:
            error = f"Template render failed: {exc}"
            logger.error("Step '%s': %s", step.id, error)
            return StepResult.failure(step.id, error, int(time.monotonic() * 1000) - start_ms)

        # ── 3. Approval gate ─────────────────────────────────────────
        if step.approval and step.approval.required:
            self._obs.approval_requested(step.id, step.tool, step.approval.message)
            try:
                granted = await asyncio.wait_for(
                    self._request_approval(step, rendered_inputs),
                    timeout=step.approval.timeout_sec,
                )
            except asyncio.TimeoutError:
                granted = False

            if granted:
                self._obs.approval_granted(step.id)
            else:
                self._obs.approval_denied(step.id)
                raise StepApprovalDenied(f"User denied approval for step '{step.id}'")

        # ── 4. Emit started ──────────────────────────────────────────
        self._obs.step_started(step.id, step.agent.value, step.tool, wave)
        logger.info("Executing step '%s' → %s:%s", step.id, step.agent.value, step.tool)

        # ── 5. Execute with retry ────────────────────────────────────
        circuit_key = f"{step.agent.value}:{step.tool}"

        async def call_agent() -> Any:
            return await asyncio.wait_for(
                self._bus.delegate(step.agent.value, step.tool, rendered_inputs),
                timeout=step.timeout_sec,
            )

        retry_result = await self._retry.run(
            fn=call_agent,
            policy=step.retry,
            circuit_key=circuit_key,
        )

        duration_ms = int(time.monotonic() * 1000) - start_ms

        # ── 6. Handle retry outcome ───────────────────────────────────
        if retry_result.outcome == RetryOutcome.SUCCESS:
            output = retry_result.result
            tokens = output.get("token_usage", 0) if isinstance(output, dict) else 0
            # Store in context if output_var declared
            if step.output_var and output is not None:
                ctx.step_outputs[step.id]       = output
                ctx.variables[step.output_var]  = output
            else:
                ctx.step_outputs[step.id] = output

            self._obs.step_completed(step.id, duration_ms, wave, tokens)
            return StepResult(step.id, output, duration_ms, tokens)

        else:
            error = retry_result.last_error or str(retry_result.outcome)
            self._obs.step_failed(step.id, error, retry_result.attempts, wave)
            logger.error("Step '%s' failed after %d attempt(s): %s",
                         step.id, retry_result.attempts, error)
            return StepResult.failure(step.id, error, duration_ms)

    # ------------------------------------------------------------------
    # Approval
    # ------------------------------------------------------------------

    async def _request_approval(self, step: Step, inputs: dict) -> bool:
        """Delegate approval request to the configured approval function."""
        try:
            return await self._approve({
                "step_id":    step.id,
                "tool":       step.tool,
                "agent":      step.agent.value,
                "message":    step.approval.message if step.approval else "",
                "inputs":     inputs,
                "side_effects": "write",
            })
        except Exception as exc:
            logger.warning("Approval request failed: %s — defaulting to denied", exc)
            return False
