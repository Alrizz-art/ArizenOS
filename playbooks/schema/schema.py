"""
Playbook Schema — Pydantic v2 validation model for YAML playbooks.

A playbook is the primary unit of workflow automation in ArizenOS.
It defines triggers, steps, variables, and error handling in YAML.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, model_validator


class TriggerType(str, Enum):
    HOTKEY    = "hotkey"
    CRON      = "cron"
    FILE      = "file"
    EVENT     = "event"
    AGENT     = "agent"
    MANUAL    = "manual"


class SideEffectProfile(str, Enum):
    READ_ONLY   = "read_only"
    IDEMPOTENT  = "idempotent"
    WRITE       = "write"
    DESTRUCTIVE = "destructive"
    SYSTEM      = "system"


class Trigger(BaseModel):
    type:    TriggerType
    binding: Optional[str] = None    # hotkey binding, cron expression, file glob, event name
    filter:  Optional[str] = None    # additional filter expression


class Step(BaseModel):
    id:       str
    skill:    Optional[str] = None   # skill reference e.g. "filesystem.read"
    agent:    Optional[str] = None   # agent name e.g. "archivist"
    prompt:   Optional[str] = None   # natural language instruction for agent
    input:    Optional[Any] = None
    output:   Optional[str] = None   # variable name to store output
    approval: bool = False           # require human approval before this step
    retry:    int  = 0               # max retries on failure
    timeout:  int  = 30              # seconds

    @model_validator(mode='after')
    def skill_or_agent(self) -> 'Step':
        if not self.skill and not self.agent:
            raise ValueError("Step must specify either 'skill' or 'agent'")
        return self


class ErrorHandler(BaseModel):
    action:  str               # notify | retry | skip | abort
    message: Optional[str] = None


class Playbook(BaseModel):
    name:        str
    version:     str                    = "1.0"
    description: Optional[str]         = None
    trigger:     Trigger
    variables:   dict[str, Any]        = Field(default_factory=dict)
    steps:       list[Step]            = Field(default_factory=list)
    on_error:    Optional[ErrorHandler] = None
    tags:        list[str]             = Field(default_factory=list)


def load_playbook(yaml_path: str) -> Playbook:
    """Load and validate a playbook YAML file."""
    import yaml
    from pathlib import Path
    raw = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    return Playbook.model_validate(raw)
