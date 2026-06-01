"""
Playbook Schema — Extended Pydantic v2 models for ArizenOS Playbooks.

A Playbook is the primary unit of execution in ArizenOS.
Every user intent eventually maps to a Playbook instance.
Playbooks are YAML-defined, validated, DAG-executed, and fully observable.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


# ─── Enumerations ─────────────────────────────────────────────────────────────

class AgentName(str, Enum):
    COMMANDER  = "commander"
    CODER      = "coder"
    RESEARCHER = "researcher"
    FIXER      = "fixer"
    DEVOPS     = "devops"
    SECURITY   = "security"
    DESIGNER   = "designer"
    MEMORY     = "memory"


class TriggerType(str, Enum):
    MANUAL  = "manual"
    HOTKEY  = "hotkey"
    CRON    = "cron"
    FILE    = "file"
    EVENT   = "event"
    AGENT   = "agent"
    HTTP    = "http"


class OnFailure(str, Enum):
    ABORT    = "abort"     # stop playbook, surface error
    SKIP     = "skip"      # skip this step, continue
    RETRY    = "retry"     # use step-level retry policy
    CONTINUE = "continue"  # ignore failure, continue
    ROLLBACK = "rollback"  # trigger rollback steps


class BackoffStrategy(str, Enum):
    FIXED       = "fixed"
    LINEAR      = "linear"
    EXPONENTIAL = "exponential"
    JITTER      = "jitter"   # exponential + random jitter


class CheckpointScope(str, Enum):
    OUTPUTS = "outputs"   # persist step outputs
    MEMORY  = "memory"    # persist agent memory context
    ALL     = "all"


class LogLevel(str, Enum):
    DEBUG   = "debug"
    INFO    = "info"
    WARNING = "warning"
    ERROR   = "error"


class InputType(str, Enum):
    STRING  = "string"
    INTEGER = "integer"
    FLOAT   = "float"
    BOOLEAN = "boolean"
    LIST    = "list"
    DICT    = "dict"
    FILE    = "file"     # path to a file
    SECRET  = "secret"   # loaded from secrets store, never logged


# ─── Trigger ──────────────────────────────────────────────────────────────────

class Trigger(BaseModel):
    type:       TriggerType
    binding:    Optional[str] = None   # hotkey string / cron expr / file glob / event name
    filter:     Optional[str] = None   # jinja2 condition on event payload
    debounce_ms: int          = 0      # ignore rapid re-fires within this window


# ─── Input Schema ─────────────────────────────────────────────────────────────

class InputSpec(BaseModel):
    """Declares a single playbook input parameter."""
    type:        InputType         = InputType.STRING
    description: str               = ""
    required:    bool              = True
    default:     Optional[Any]     = None
    enum:        Optional[list]    = None     # allowed values
    min:         Optional[float]   = None     # numeric bounds
    max:         Optional[float]   = None
    pattern:     Optional[str]     = None     # regex for string validation

    @field_validator("pattern")
    @classmethod
    def valid_regex(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                re.compile(v)
            except re.error as exc:
                raise ValueError(f"Invalid regex pattern: {exc}") from exc
        return v


# ─── Retry Policy ─────────────────────────────────────────────────────────────

class RetryPolicy(BaseModel):
    max_attempts:  int             = 3
    backoff:       BackoffStrategy = BackoffStrategy.EXPONENTIAL
    delay_sec:     float           = 2.0
    max_delay_sec: float           = 60.0
    on:            list[str]       = Field(default_factory=lambda: ["error", "timeout"])
    not_on:        list[str]       = Field(default_factory=lambda: ["approval_denied", "permission_error"])

    @field_validator("max_attempts")
    @classmethod
    def positive_attempts(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_attempts must be >= 1")
        return v


# ─── Approval Gate ────────────────────────────────────────────────────────────

class ApprovalGate(BaseModel):
    required:    bool   = True
    message:     str    = ""           # shown to user in Command Nexus
    auto_after:  int    = 0            # auto-approve after N seconds (0 = never)
    timeout_sec: int    = 300          # abort if no response within this window


# ─── Checkpoint ───────────────────────────────────────────────────────────────

class Checkpoint(BaseModel):
    after:  str                       # step ID to checkpoint after
    scope:  CheckpointScope = CheckpointScope.ALL
    ttl_sec: int            = 86400   # checkpoint expiry (1 day default)


# ─── Rollback Step ────────────────────────────────────────────────────────────

class RollbackStep(BaseModel):
    id:     str
    agent:  AgentName
    tool:   str
    inputs: dict[str, Any] = Field(default_factory=dict)


# ─── Step ─────────────────────────────────────────────────────────────────────

class Step(BaseModel):
    """A single unit of work in a Playbook."""
    id:           str
    name:         str                       = ""
    description:  str                       = ""

    # Routing
    agent:        AgentName
    tool:         str                       # e.g. "code.generate", "memory.query"

    # I/O
    inputs:       dict[str, Any]            = Field(default_factory=dict)
    output_var:   Optional[str]             = None  # store result as {{ vars.NAME }}

    # DAG
    depends_on:   list[str]                 = Field(default_factory=list)
    parallel_with: list[str]               = Field(default_factory=list)

    # Control flow
    condition:    Optional[str]             = None  # jinja2 bool expression; skip if False
    on_failure:   OnFailure                 = OnFailure.ABORT
    retry:        Optional[RetryPolicy]     = None
    timeout_sec:  int                       = 60
    approval:     Optional[ApprovalGate]    = None

    # Execution hints
    llm_tier:     Optional[str]             = None  # override agent default
    priority:     int                       = 5     # 1–10; higher runs first in queue

    @field_validator("id")
    @classmethod
    def valid_id(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9_-]*$', v):
            raise ValueError(f"Step id must be lowercase_snake or kebab-case, got: {v!r}")
        return v

    @model_validator(mode='after')
    def check_deps_not_self(self) -> 'Step':
        if self.id in self.depends_on:
            raise ValueError(f"Step '{self.id}' cannot depend on itself")
        return self


# ─── Error Handler ────────────────────────────────────────────────────────────

class ErrorHandler(BaseModel):
    action:  OnFailure          = OnFailure.ABORT
    notify:  bool               = True
    message: str                = ""
    rollback: bool              = False  # execute rollback_steps if defined


# ─── Observability ────────────────────────────────────────────────────────────

class ObservabilityConfig(BaseModel):
    log_level:    LogLevel      = LogLevel.INFO
    emit_events:  bool          = True   # publish to arizen-events pipe
    metrics:      list[str]     = Field(
        default_factory=lambda: ["duration", "token_usage", "step_count", "failure_rate"]
    )
    trace_inputs: bool          = False  # include step inputs in logs (security-sensitive)
    hud_overlay:  bool          = True   # show progress in HUD


# ─── Playbook ─────────────────────────────────────────────────────────────────

class Playbook(BaseModel):
    """
    A Playbook is the primary runtime unit of ArizenOS.
    Every user action eventually executes as a Playbook instance.
    """
    # Identity
    name:           str
    version:        str                         = "1.0.0"
    description:    str                         = ""
    author:         str                         = "user"
    tags:           list[str]                   = Field(default_factory=list)

    # Invocation
    trigger:        Trigger                     = Field(default_factory=lambda: Trigger(type=TriggerType.MANUAL))
    inputs:         dict[str, InputSpec]        = Field(default_factory=dict)

    # Runtime variables (set during execution, not by user)
    variables:      dict[str, Any]              = Field(default_factory=dict)

    # Execution graph
    steps:          list[Step]                  = Field(min_length=1)

    # Error + rollback
    on_error:       ErrorHandler                = Field(default_factory=ErrorHandler)
    rollback_steps: list[RollbackStep]          = Field(default_factory=list)

    # Checkpoints
    checkpoints:    list[Checkpoint]            = Field(default_factory=list)

    # Observability
    observability:  ObservabilityConfig         = Field(default_factory=ObservabilityConfig)

    # Timeout for the entire playbook
    timeout_sec:    int                         = 3600

    @model_validator(mode='after')
    def validate_step_graph(self) -> 'Playbook':
        ids = {s.id for s in self.steps}
        # Check all depends_on reference valid step IDs
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in ids:
                    raise ValueError(f"Step '{step.id}' depends_on unknown step '{dep}'")
        # Check all checkpoints reference valid step IDs
        for cp in self.checkpoints:
            if cp.after not in ids:
                raise ValueError(f"Checkpoint references unknown step '{cp.after}'")
        return self

    @model_validator(mode='after')
    def no_duplicate_step_ids(self) -> 'Playbook':
        ids = [s.id for s in self.steps]
        seen: set[str] = set()
        for sid in ids:
            if sid in seen:
                raise ValueError(f"Duplicate step id: '{sid}'")
            seen.add(sid)
        return self

    def step_by_id(self, sid: str) -> Optional[Step]:
        return next((s for s in self.steps if s.id == sid), None)
