"""
Playbook Observer — structured event emission, metrics collection, and HUD integration.

Every significant state transition in the execution engine emits a typed event.
Events flow to:
  1. The structured logger (JSON, file-backed)
  2. The arizen-events named pipe (→ HUD overlay)
  3. An in-memory metrics store (queryable via Commander)

Event hierarchy:
  PLAYBOOK_STARTED → WAVE_STARTED → STEP_STARTED → STEP_COMPLETED
                                                  → STEP_FAILED
                                                  → STEP_SKIPPED
                   → WAVE_COMPLETED
                → CHECKPOINT_SAVED
                → APPROVAL_REQUESTED → APPROVAL_GRANTED / APPROVAL_DENIED
                → PLAYBOOK_COMPLETED
                → PLAYBOOK_FAILED
                → PLAYBOOK_ROLLED_BACK
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

logger = logging.getLogger("arizen.playbook.observer")


class EventKind(str, Enum):
    PLAYBOOK_STARTED     = "PLAYBOOK_STARTED"
    PLAYBOOK_COMPLETED   = "PLAYBOOK_COMPLETED"
    PLAYBOOK_FAILED      = "PLAYBOOK_FAILED"
    PLAYBOOK_ROLLED_BACK = "PLAYBOOK_ROLLED_BACK"
    WAVE_STARTED         = "WAVE_STARTED"
    WAVE_COMPLETED       = "WAVE_COMPLETED"
    STEP_STARTED         = "STEP_STARTED"
    STEP_COMPLETED       = "STEP_COMPLETED"
    STEP_FAILED          = "STEP_FAILED"
    STEP_SKIPPED         = "STEP_SKIPPED"
    STEP_RETRYING        = "STEP_RETRYING"
    CHECKPOINT_SAVED     = "CHECKPOINT_SAVED"
    APPROVAL_REQUESTED   = "APPROVAL_REQUESTED"
    APPROVAL_GRANTED     = "APPROVAL_GRANTED"
    APPROVAL_DENIED      = "APPROVAL_DENIED"


@dataclass
class PlaybookEvent:
    kind:         EventKind
    run_id:       str
    playbook_name: str
    timestamp_ms: int            = field(default_factory=lambda: int(time.time() * 1000))
    step_id:      str            = ""
    wave_index:   int            = -1
    data:         dict[str, Any] = field(default_factory=dict)
    event_id:     str            = field(default_factory=lambda: str(uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "event_id":     self.event_id,
            "kind":         self.kind.value,
            "run_id":       self.run_id,
            "playbook":     self.playbook_name,
            "step_id":      self.step_id,
            "wave":         self.wave_index,
            "timestamp_ms": self.timestamp_ms,
            **self.data,
        }


@dataclass
class RunMetrics:
    run_id:           str
    playbook_name:    str
    started_at:       float = field(default_factory=time.monotonic)
    completed_at:     float = 0.0
    total_steps:      int   = 0
    completed_steps:  int   = 0
    failed_steps:     int   = 0
    skipped_steps:    int   = 0
    retried_steps:    int   = 0
    approvals_shown:  int   = 0
    approvals_granted: int  = 0
    checkpoints_saved: int  = 0
    token_usage:      int   = 0   # accumulated from agent results
    wave_count:       int   = 0

    @property
    def duration_sec(self) -> float:
        end = self.completed_at or time.monotonic()
        return end - self.started_at

    @property
    def success_rate(self) -> float:
        total = self.completed_steps + self.failed_steps
        return self.completed_steps / total if total else 1.0

    def to_dict(self) -> dict:
        return {
            "run_id":           self.run_id,
            "playbook":         self.playbook_name,
            "duration_sec":     round(self.duration_sec, 2),
            "total_steps":      self.total_steps,
            "completed_steps":  self.completed_steps,
            "failed_steps":     self.failed_steps,
            "skipped_steps":    self.skipped_steps,
            "retried_steps":    self.retried_steps,
            "success_rate":     round(self.success_rate, 3),
            "wave_count":       self.wave_count,
            "token_usage":      self.token_usage,
            "approvals_granted":self.approvals_granted,
            "checkpoints_saved":self.checkpoints_saved,
        }


class PlaybookObserver:
    """
    Collects and dispatches structured events from the execution engine.

    Subscribers receive all events via callback.
    HUD integration writes events to the arizen-events named pipe.
    """

    def __init__(
        self,
        run_id:        str,
        playbook_name: str,
        hud_pipe:      Optional[str] = r"\\.\pipe\arizen-events",
        trace_inputs:  bool          = False,
    ) -> None:
        self._run_id       = run_id
        self._pb_name      = playbook_name
        self._hud_pipe     = hud_pipe
        self._trace_inputs = trace_inputs
        self._metrics      = RunMetrics(run_id=run_id, playbook_name=playbook_name)
        self._subscribers: list[Callable[[PlaybookEvent], None]] = []
        self._events: list[PlaybookEvent] = []

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, fn: Callable[[PlaybookEvent], None]) -> None:
        self._subscribers.append(fn)

    # ------------------------------------------------------------------
    # Emit helpers (called by engine / executor)
    # ------------------------------------------------------------------

    def playbook_started(self, total_steps: int, waves: int) -> None:
        self._metrics.total_steps = total_steps
        self._metrics.wave_count  = waves
        self._emit(EventKind.PLAYBOOK_STARTED, data={"total_steps": total_steps, "waves": waves})

    def playbook_completed(self) -> None:
        self._metrics.completed_at = time.monotonic()
        self._emit(EventKind.PLAYBOOK_COMPLETED, data=self._metrics.to_dict())

    def playbook_failed(self, error: str) -> None:
        self._metrics.completed_at = time.monotonic()
        self._emit(EventKind.PLAYBOOK_FAILED, data={"error": error, **self._metrics.to_dict()})

    def wave_started(self, wave_index: int, step_ids: list[str]) -> None:
        self._emit(EventKind.WAVE_STARTED, wave_index=wave_index, data={"step_ids": step_ids})

    def wave_completed(self, wave_index: int, duration_sec: float) -> None:
        self._emit(EventKind.WAVE_COMPLETED, wave_index=wave_index, data={"duration_sec": round(duration_sec, 2)})

    def step_started(self, step_id: str, agent: str, tool: str, wave: int) -> None:
        self._emit(EventKind.STEP_STARTED, step_id=step_id, wave_index=wave,
                   data={"agent": agent, "tool": tool})

    def step_completed(self, step_id: str, duration_ms: int, wave: int, tokens: int = 0) -> None:
        self._metrics.completed_steps += 1
        self._metrics.token_usage     += tokens
        self._emit(EventKind.STEP_COMPLETED, step_id=step_id, wave_index=wave,
                   data={"duration_ms": duration_ms, "tokens": tokens})

    def step_failed(self, step_id: str, error: str, attempt: int, wave: int) -> None:
        self._metrics.failed_steps += 1
        self._emit(EventKind.STEP_FAILED, step_id=step_id, wave_index=wave,
                   data={"error": error, "attempt": attempt})

    def step_skipped(self, step_id: str, reason: str) -> None:
        self._metrics.skipped_steps += 1
        self._emit(EventKind.STEP_SKIPPED, step_id=step_id, data={"reason": reason})

    def step_retrying(self, step_id: str, attempt: int, delay_sec: float) -> None:
        self._metrics.retried_steps += 1
        self._emit(EventKind.STEP_RETRYING, step_id=step_id,
                   data={"attempt": attempt, "delay_sec": delay_sec})

    def checkpoint_saved(self, step_id: str) -> None:
        self._metrics.checkpoints_saved += 1
        self._emit(EventKind.CHECKPOINT_SAVED, step_id=step_id)

    def approval_requested(self, step_id: str, tool: str, message: str) -> None:
        self._metrics.approvals_shown += 1
        self._emit(EventKind.APPROVAL_REQUESTED, step_id=step_id,
                   data={"tool": tool, "message": message})

    def approval_granted(self, step_id: str) -> None:
        self._metrics.approvals_granted += 1
        self._emit(EventKind.APPROVAL_GRANTED, step_id=step_id)

    def approval_denied(self, step_id: str) -> None:
        self._emit(EventKind.APPROVAL_DENIED, step_id=step_id)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def metrics(self) -> RunMetrics:
        return self._metrics

    def events_for_step(self, step_id: str) -> list[PlaybookEvent]:
        return [e for e in self._events if e.step_id == step_id]

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _emit(self, kind: EventKind, step_id: str = "", wave_index: int = -1,
              data: dict = None) -> None:
        event = PlaybookEvent(
            kind=kind, run_id=self._run_id, playbook_name=self._pb_name,
            step_id=step_id, wave_index=wave_index, data=data or {}
        )
        self._events.append(event)
        logger.info("[%s] %s %s", kind.value,
                    f"step={step_id}" if step_id else "",
                    json.dumps(data or {})[:120])
        for fn in self._subscribers:
            try:
                fn(event)
            except Exception as exc:
                logger.warning("Observer subscriber failed: %s", exc)
        # Non-blocking HUD write (best-effort)
        asyncio.get_event_loop().call_soon(self._write_hud, event)

    def _write_hud(self, event: PlaybookEvent) -> None:
        """Write event JSON to the arizen-events named pipe (non-blocking, best-effort)."""
        if not self._hud_pipe:
            return
        try:
            import win32pipe, win32file  # type: ignore
            pipe = win32file.CreateFile(
                self._hud_pipe,
                win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING, 0, None
            )
            payload = (json.dumps(event.to_dict()) + "\n").encode("utf-8")
            win32file.WriteFile(pipe, payload)
            win32file.CloseHandle(pipe)
        except Exception:
            pass   # HUD unavailable — silently skip
