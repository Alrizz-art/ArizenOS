"""
Playbook Engine — the PRIMARY RUNTIME of ArizenOS.

Every user action executes as a Playbook. The engine is the single
authority over how playbooks are loaded, validated, scheduled, executed,
checkpointed, and observed.

Entry points:
  engine.run(playbook, inputs)          — execute a named or inline playbook
  engine.run_file(path, inputs)         — load YAML + execute
  engine.resume(run_id)                 — resume from last checkpoint
  engine.list_runs()                    — active + recent runs
  engine.cancel(run_id)                 — emergency cancel

Execution flow:
  load → validate → context → graph → (resume?) → waves → checkpoint → synthesize
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from playbooks.schema.playbook_schema import (
    AgentName, OnFailure, Playbook, Step,
)
from playbooks.schema.validator import PlaybookValidator
from core.playbook_engine.graph import ExecutionGraph, GraphBuilder, Wave
from core.playbook_engine.template import TemplateContext, TemplateEngine
from core.playbook_engine.executor import (
    StepApprovalDenied, StepExecutor, StepResult, StepSkipped,
)
from core.playbook_engine.checkpoint import CheckpointManager, CheckpointState
from core.playbook_engine.observer import PlaybookObserver
from core.playbook_engine.queue import PlaybookTaskQueue
from core.playbook_engine.retry import RetryEngine

logger = logging.getLogger("arizen.playbook.engine")


# ─── Run State ────────────────────────────────────────────────────────────────

class RunStatus(str, Enum):
    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETED  = "completed"
    FAILED     = "failed"
    CANCELLED  = "cancelled"
    ROLLED_BACK = "rolled_back"


@dataclass
class RunHandle:
    """Live reference to a running or completed playbook execution."""
    run_id:       str
    playbook_name: str
    status:       RunStatus            = RunStatus.PENDING
    started_at:   float               = field(default_factory=time.monotonic)
    completed_at: float               = 0.0
    outputs:      dict[str, Any]      = field(default_factory=dict)
    error:        str                 = ""
    observer:     Optional[PlaybookObserver] = field(default=None, repr=False)

    @property
    def duration_sec(self) -> float:
        end = self.completed_at or time.monotonic()
        return end - self.started_at


# ─── Engine Configuration ─────────────────────────────────────────────────────

@dataclass
class EngineConfig:
    checkpoint_db:    str  = "memory/persistent/checkpoints.db"
    playbook_library: str  = "playbooks/library"
    max_concurrency:  int  = 8       # parallel steps across all waves
    per_agent_limit:  int  = 2       # parallel tasks per agent
    default_timeout:  int  = 3600    # whole-playbook timeout (sec)
    hud_pipe:         str  = r"\\.\pipe\arizen-events"
    trace_inputs:     bool = False   # log step inputs (disable in prod)


# ─── Playbook Engine ──────────────────────────────────────────────────────────

class PlaybookEngine:
    """
    PRIMARY RUNTIME of ArizenOS.

    All user actions that require agent coordination execute through here.
    Commander delegates to the engine; the engine delegates to agents.

    The engine is stateful: it tracks active runs, checkpoints, and metrics.
    It is safe to run multiple playbooks concurrently.
    """

    def __init__(self, bus, approval_fn, config: EngineConfig = None) -> None:
        self._bus        = bus
        self._approve    = approval_fn
        self._cfg        = config or EngineConfig()
        self._validator  = PlaybookValidator()
        self._graph_bld  = GraphBuilder()
        self._checkpoint = CheckpointManager(self._cfg.checkpoint_db)
        self._active:    dict[str, RunHandle] = {}
        self._history:   list[RunHandle]      = []
        logger.info("PlaybookEngine initialized — library: %s", self._cfg.playbook_library)

    # ──────────────────────────────────────────────────────────────────
    # Public entry points
    # ──────────────────────────────────────────────────────────────────

    async def run_file(
        self,
        path:   str,
        inputs: dict[str, Any] = None,
        run_id: str            = None,
    ) -> AsyncIterator[str]:
        """Load a YAML playbook file and execute it."""
        result = self._validator.validate_file(path)
        if not result.valid:
            errors = "; ".join(f"[{i.location}] {i.message}" for i in result.errors)
            raise ValueError(f"Playbook validation failed: {errors}")
        async for token in self.run(result.playbook, inputs=inputs, run_id=run_id):
            yield token

    async def run_named(
        self,
        name:   str,
        inputs: dict[str, Any] = None,
        run_id: str            = None,
    ) -> AsyncIterator[str]:
        """Look up a playbook by name in the library and execute it."""
        path = Path(self._cfg.playbook_library) / f"{name}.yaml"
        if not path.exists():
            # Also try .yml
            path = Path(self._cfg.playbook_library) / f"{name}.yml"
        if not path.exists():
            raise FileNotFoundError(
                f"Playbook '{name}' not found in library '{self._cfg.playbook_library}'"
            )
        async for token in self.run_file(str(path), inputs=inputs, run_id=run_id):
            yield token

    async def run(
        self,
        playbook: Playbook,
        inputs:   dict[str, Any] = None,
        run_id:   str            = None,
        resume:   bool           = False,
    ) -> AsyncIterator[str]:
        """
        Execute a Playbook instance. Yields streaming status/result tokens.

        If resume=True and a checkpoint exists for run_id, continues from
        the last saved checkpoint rather than starting fresh.
        """
        run_id = run_id or str(uuid.uuid4())
        inputs = inputs or {}

        # Validate inputs against schema
        self._validate_inputs(playbook, inputs)

        # Build execution graph
        graph = self._graph_bld.build(playbook)

        # Build initial context
        ctx = TemplateContext(
            inputs=inputs,
            variables=dict(playbook.variables),
        )

        # Resume from checkpoint?
        checkpoint_state: Optional[CheckpointState] = None
        if resume and self._checkpoint.has_checkpoint(run_id):
            checkpoint_state = self._checkpoint.load(run_id)
            if checkpoint_state:
                ctx.step_outputs = dict(checkpoint_state.step_outputs)
                ctx.variables.update(checkpoint_state.variables)
                logger.info("Resuming run %s from checkpoint (done: %d steps)",
                            run_id[:8], len(checkpoint_state.completed_step_ids))

        # Create observer + handle
        observer = PlaybookObserver(
            run_id=run_id,
            playbook_name=playbook.name,
            hud_pipe=self._cfg.hud_pipe,
            trace_inputs=self._cfg.trace_inputs,
        )
        handle = RunHandle(run_id=run_id, playbook_name=playbook.name,
                           status=RunStatus.RUNNING, observer=observer)
        self._active[run_id] = handle

        observer.playbook_started(
            total_steps=len(playbook.steps),
            waves=len(graph.waves),
        )
        logger.info(
            "Playbook '%s' started | run=%s | %d steps | %d waves | est=%.0fs",
            playbook.name, run_id[:8], len(playbook.steps),
            len(graph.waves), graph.estimated_sec,
        )

        yield f"▶ Running playbook: {playbook.name} ({len(playbook.steps)} steps)\n"

        try:
            async for token in asyncio.wait_for(
                self._execute_graph(
                    graph, ctx, handle, observer, checkpoint_state, playbook
                ),
                timeout=playbook.timeout_sec,
            ):
                yield token

            handle.status      = RunStatus.COMPLETED
            handle.outputs     = ctx.step_outputs
            handle.completed_at = time.monotonic()
            observer.playbook_completed()
            logger.info("Playbook '%s' completed in %.1fs", playbook.name, handle.duration_sec)
            yield f"\n✓ Playbook complete ({handle.duration_sec:.1f}s)\n"

        except asyncio.TimeoutError:
            handle.error  = f"Playbook timed out after {playbook.timeout_sec}s"
            handle.status = RunStatus.FAILED
            observer.playbook_failed(handle.error)
            yield f"\n✗ {handle.error}\n"
            if playbook.on_error.rollback:
                async for t in self._rollback(playbook, ctx, observer):
                    yield t

        except asyncio.CancelledError:
            handle.status = RunStatus.CANCELLED
            yield "\n⊘ Playbook cancelled\n"
            raise

        except Exception as exc:
            handle.error  = str(exc)
            handle.status = RunStatus.FAILED
            observer.playbook_failed(handle.error)
            logger.exception("Playbook '%s' failed: %s", playbook.name, exc)
            yield f"\n✗ Playbook failed: {exc}\n"
            if playbook.on_error.rollback and playbook.rollback_steps:
                async for t in self._rollback(playbook, ctx, observer):
                    yield t

        finally:
            self._history.append(handle)
            self._active.pop(run_id, None)

    async def resume(self, run_id: str) -> AsyncIterator[str]:
        """Resume a checkpointed run by ID."""
        state = self._checkpoint.load(run_id)
        if not state:
            raise LookupError(f"No checkpoint found for run_id: {run_id}")
        result = self._validator.validate_file(
            str(Path(self._cfg.playbook_library) / f"{state.playbook_name}.yaml")
        )
        if not result.valid:
            raise ValueError(f"Playbook '{state.playbook_name}' is no longer valid")
        async for token in self.run(result.playbook, run_id=run_id, resume=True):
            yield token

    async def cancel(self, run_id: str) -> bool:
        """Cancel an active run. Returns True if found and cancelled."""
        if run_id in self._active:
            self._active[run_id].status = RunStatus.CANCELLED
            logger.warning("Run %s cancelled", run_id[:8])
            return True
        return False

    def list_runs(self) -> list[dict]:
        """Return active and recent run summaries."""
        active  = [self._run_summary(h) for h in self._active.values()]
        recent  = [self._run_summary(h) for h in self._history[-20:]]
        return active + recent

    def list_playbooks(self) -> list[str]:
        """List available playbooks in the library."""
        lib = Path(self._cfg.playbook_library)
        return [p.stem for p in lib.glob("*.yaml")] + [p.stem for p in lib.glob("*.yml")]

    # ──────────────────────────────────────────────────────────────────
    # Core execution
    # ──────────────────────────────────────────────────────────────────

    async def _execute_graph(
        self,
        graph:      ExecutionGraph,
        ctx:        TemplateContext,
        handle:     RunHandle,
        observer:   PlaybookObserver,
        checkpoint: Optional[CheckpointState],
        playbook:   Playbook,
    ) -> AsyncIterator[str]:
        executor = StepExecutor(self._bus, self._approve, observer)
        done_ids: set[str] = set(checkpoint.completed_step_ids if checkpoint else [])

        for wave in graph.waves:
            # Skip waves already completed by checkpoint
            if all(s.id in done_ids for s in wave.steps):
                logger.debug("Wave %d fully checkpointed — skipping", wave.index)
                continue

            wave_start = time.monotonic()
            observer.wave_started(wave.index, wave.step_ids)
            yield f"  ⟡ Wave {wave.index + 1}/{len(graph.waves)}: {', '.join(wave.step_ids)}\n"

            # Build a task queue for this wave
            queue = PlaybookTaskQueue(
                max_concurrency=self._cfg.max_concurrency,
                per_agent_limit=self._cfg.per_agent_limit,
            )

            for step in wave.steps:
                if step.id in done_ids:
                    continue
                await queue.enqueue(
                    step_id  = step.id,
                    agent    = step.agent.value,
                    fn       = self._run_step,
                    args     = (step, ctx, wave.index, executor, playbook),
                    priority = step.priority,
                )

            wave_results = await queue.execute_wave(timeout=sum(s.timeout_sec for s in wave.steps) + 30)

            # Process results
            for step in wave.steps:
                if step.id in done_ids:
                    continue
                result = wave_results.get(step.id)
                if isinstance(result, StepSkipped):
                    done_ids.add(step.id)
                    continue
                if isinstance(result, StepApprovalDenied):
                    if step.on_failure == OnFailure.ABORT:
                        raise StepApprovalDenied(str(result))
                    done_ids.add(step.id)
                    continue
                if result is None or (isinstance(result, dict) and "error" in result):
                    error = str(result.get("error", "unknown")) if isinstance(result, dict) else "no result"
                    if not await self._handle_failure(step, error, playbook):
                        raise RuntimeError(f"Step '{step.id}' failed: {error}")
                    done_ids.add(step.id)
                    continue

                # Success
                if isinstance(result, StepResult):
                    ctx.step_outputs[step.id] = result.output
                    if step.output_var:
                        ctx.variables[step.output_var] = result.output
                    yield f"    ✓ {step.id} ({result.duration_ms}ms)\n"

                done_ids.add(step.id)

                # Checkpoint?
                cp_config = next((c for c in playbook.checkpoints if c.after == step.id), None)
                if cp_config:
                    self._checkpoint.save_step(
                        handle.run_id, playbook.name, step.id,
                        ctx.step_outputs.get(step.id), wave.index, cp_config.ttl_sec
                    )
                    self._checkpoint.save_variables(handle.run_id, ctx.variables)
                    observer.checkpoint_saved(step.id)
                    yield f"    ⊛ Checkpoint saved: {step.id}\n"

            wave_dur = time.monotonic() - wave_start
            observer.wave_completed(wave.index, wave_dur)

    async def _run_step(
        self,
        step:     Step,
        ctx:      TemplateContext,
        wave:     int,
        executor: StepExecutor,
        playbook: Playbook,
    ) -> Any:
        try:
            return await executor.run(step, ctx, wave)
        except StepSkipped as exc:
            return exc
        except StepApprovalDenied as exc:
            return exc
        except Exception as exc:
            logger.error("Step '%s' raised unexpected: %s", step.id, exc)
            return {"error": str(exc)}

    # ──────────────────────────────────────────────────────────────────
    # Failure handling
    # ──────────────────────────────────────────────────────────────────

    async def _handle_failure(self, step: Step, error: str, playbook: Playbook) -> bool:
        """Returns True if execution should continue, False if it should abort."""
        match step.on_failure:
            case OnFailure.ABORT:
                return False
            case OnFailure.SKIP:
                logger.warning("Step '%s' failed — skipping per policy: %s", step.id, error)
                return True
            case OnFailure.CONTINUE:
                logger.warning("Step '%s' failed — continuing per policy: %s", step.id, error)
                return True
            case OnFailure.ROLLBACK:
                return False   # caller triggers rollback
            case _:
                return False

    async def _rollback(
        self, playbook: Playbook, ctx: TemplateContext, observer: PlaybookObserver
    ) -> AsyncIterator[str]:
        if not playbook.rollback_steps:
            return
        yield "\n⟲ Running rollback steps...\n"
        observer.playbook_failed("rollback triggered")
        tmpl = TemplateEngine()
        for rs in playbook.rollback_steps:
            try:
                inputs = tmpl.render(rs.inputs, ctx)
                await self._bus.delegate(rs.agent.value, rs.tool, inputs)
                yield f"  ↩ {rs.id} rolled back\n"
            except Exception as exc:
                logger.error("Rollback step '%s' failed: %s", rs.id, exc)
                yield f"  ✗ Rollback '{rs.id}' failed: {exc}\n"
        observer._emit(observer._obs._emit if hasattr(observer, '_obs') else
                       lambda k, **kw: None, "PLAYBOOK_ROLLED_BACK")

    # ──────────────────────────────────────────────────────────────────
    # Input validation
    # ──────────────────────────────────────────────────────────────────

    def _validate_inputs(self, playbook: Playbook, inputs: dict[str, Any]) -> None:
        for name, spec in playbook.inputs.items():
            if spec.required and name not in inputs and spec.default is None:
                raise ValueError(f"Required input '{name}' not provided for playbook '{playbook.name}'")
            if name not in inputs and spec.default is not None:
                inputs[name] = spec.default
            val = inputs.get(name)
            if val is not None and spec.enum and val not in spec.enum:
                raise ValueError(f"Input '{name}' value '{val}' not in allowed values: {spec.enum}")
            if spec.pattern and isinstance(val, str):
                import re
                if not re.match(spec.pattern, val):
                    raise ValueError(f"Input '{name}' does not match pattern '{spec.pattern}'")

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _run_summary(self, handle: RunHandle) -> dict:
        m = handle.observer.metrics if handle.observer else None
        return {
            "run_id":      handle.run_id,
            "playbook":    handle.playbook_name,
            "status":      handle.status.value,
            "duration_sec": round(handle.duration_sec, 1),
            "error":       handle.error,
            "metrics":     m.to_dict() if m else {},
        }
