"""
Arizen Agent Communication Contracts.

Defines the canonical message envelope, all typed message kinds, and
the permission matrix governing which agents may send to which targets.

All inter-agent communication is mediated by Commander and serialised
as MessagePack over the \\.\pipe\arizen-agents named pipe. Direct
agent-to-agent calls are prohibited.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


# ───────────────────────────────────────────────
# Message kinds
# ───────────────────────────────────────────────

class MsgKind(str, Enum):
    # Commander → Agent
    TASK_REQUEST    = "TASK_REQUEST"
    EMERGENCY_STOP  = "EMERGENCY_STOP"
    CONFIG_UPDATE   = "CONFIG_UPDATE"
    HEALTH_CHECK    = "HEALTH_CHECK"

    # Agent → Commander
    TASK_RESULT     = "TASK_RESULT"
    TASK_STREAM     = "TASK_STREAM"     # streaming token chunk
    TASK_ERROR      = "TASK_ERROR"
    STATUS_REPORT   = "STATUS_REPORT"
    APPROVAL_NEEDED = "APPROVAL_NEEDED"

    # Commander → Commander (internal planning)
    PLAN_CREATED    = "PLAN_CREATED"
    PLAN_UPDATED    = "PLAN_UPDATED"

    # Broadcast (Commander → all)
    SHUTDOWN        = "SHUTDOWN"
    PAUSE           = "PAUSE"
    RESUME          = "RESUME"


# ───────────────────────────────────────────────
# Envelope
# ───────────────────────────────────────────────

@dataclass
class ArizenMessage:
    """
    Canonical message envelope for all ArizenOS agent IPC.
    Serialised as MessagePack v5 over named pipes.

    Fields
    ------
    message_id   : UUIDv4 — globally unique per message
    correlation  : links a TASK_RESULT back to its TASK_REQUEST
    source       : agent name sending this message
    target       : agent name or "broadcast"
    kind         : MsgKind enum value
    payload      : arbitrary dict (schema depends on kind)
    timestamp_ms : Unix milliseconds
    priority     : 0 (lowest) → 10 (emergency)
    ttl_sec      : message expires if not processed within this window
    """
    message_id:   str      = field(default_factory=lambda: str(uuid4()))
    correlation:  str      = ""
    source:       str      = ""
    target:       str      = ""
    kind:         MsgKind  = MsgKind.TASK_REQUEST
    payload:      dict     = field(default_factory=dict)
    timestamp_ms: int      = field(default_factory=lambda: int(__import__("time").time() * 1000))
    priority:     int      = 5
    ttl_sec:      int      = 30


# ───────────────────────────────────────────────
# Typed payloads
# ───────────────────────────────────────────────

@dataclass
class TaskRequestPayload:
    """Payload for MsgKind.TASK_REQUEST (Commander → Agent)."""
    task_id:     str          = field(default_factory=lambda: str(uuid4()))
    tool:        str          = ""
    inputs:      dict         = field(default_factory=dict)
    timeout_sec: int          = 30
    approval:    str          = "none"    # none | log_only | confirm
    context:     dict         = field(default_factory=dict)


@dataclass
class TaskResultPayload:
    """Payload for MsgKind.TASK_RESULT (Agent → Commander)."""
    task_id:  str         = ""
    success:  bool        = True
    output:   Any         = None
    error:    str         = ""
    duration_ms: int      = 0
    metadata: dict        = field(default_factory=dict)


@dataclass
class TaskStreamPayload:
    """Payload for MsgKind.TASK_STREAM — streaming LLM token chunk."""
    task_id: str  = ""
    token:   str  = ""
    done:    bool = False


@dataclass
class ApprovalNeededPayload:
    """Payload for MsgKind.APPROVAL_NEEDED (Agent → Commander → UI)."""
    task_id:     str   = ""
    tool:        str   = ""
    description: str   = ""
    side_effects: str  = ""
    inputs:      dict  = field(default_factory=dict)


@dataclass
class StatusReportPayload:
    """Payload for MsgKind.STATUS_REPORT (Agent → Commander)."""
    agent:      str   = ""
    status:     str   = "healthy"     # healthy | degraded | failed
    cpu_pct:    float = 0.0
    mem_mb:     float = 0.0
    tasks_done: int   = 0
    uptime_sec: float = 0.0


# ───────────────────────────────────────────────
# Permission Matrix
# ───────────────────────────────────────────────
#
# Columns = target; Rows = source.
# ✓ = may send  |  ✗ = prohibited  |  A = requires approval
#
#                   commander  coder  researcher  fixer  devops  security  designer  memory
# commander              —       ✓        ✓        ✓      ✓        ✓        ✓        ✓
# coder               ✓ (result) —        ✗        ✗      ✗        ✗        ✗       ✓ (read)
# researcher          ✓ (result) ✗        —        ✗      ✗        ✗        ✗       ✓ (read)
# fixer               ✓ (result) ✗        ✗        —      ✗        ✗        ✗       ✓ (read)
# devops              ✓ (result) ✗        ✗        ✗      —        ✗        ✗       ✓ (read)
# security            ✓ (result) ✗        ✗        ✗      ✗        —        ✗       ✓ (read)
# designer            ✓ (result) ✗        ✗        ✗      ✗        ✗        —       ✓ (read)
# memory              ✓ (result) ✗        ✗        ✗      ✗        ✗        ✗       —

PERMISSION_MATRIX: dict[str, dict[str, bool]] = {
    "commander":  {"commander": False, "coder": True,  "researcher": True,  "fixer": True,  "devops": True,  "security": True,  "designer": True,  "memory": True },
    "coder":      {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "researcher": {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "fixer":      {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "devops":     {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "security":   {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "designer":   {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": True },
    "memory":     {"commander": True,  "coder": False, "researcher": False, "fixer": False, "devops": False, "security": False, "designer": False, "memory": False},
}


def assert_permitted(source: str, target: str) -> None:
    row = PERMISSION_MATRIX.get(source, {})
    if not row.get(target, False):
        raise PermissionError(
            f"Communication contract violation: {source!r} → {target!r} is prohibited. "
            "All messages must be routed through Commander."
        )
