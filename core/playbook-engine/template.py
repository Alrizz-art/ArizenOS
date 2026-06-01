"""
Playbook Template Engine — Jinja2-based variable interpolation for playbook inputs.

Templates can reference:
  {{ inputs.project_name }}         — playbook inputs
  {{ steps.step_id.output }}        — output of a previous step
  {{ vars.MY_VAR }}                 — playbook-level variables
  {{ env.HOME }}                    — environment variables (sandboxed whitelist)
  {{ now() }}                       — current datetime
  {{ uuid() }}                      — fresh UUID

All template rendering is sandboxed — no file I/O, no subprocess, no __import__.
"""
from __future__ import annotations

import os
import re
import uuid as _uuid
from datetime import datetime
from typing import Any

from jinja2 import Environment, StrictUndefined, TemplateSyntaxError, UndefinedError

# Whitelisted env vars accessible in templates
ENV_WHITELIST: set[str] = {"HOME", "USERNAME", "USERPROFILE", "COMPUTERNAME", "ARIZEN_DATA"}


def _make_env() -> Environment:
    env = Environment(
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
    env.globals["now"]  = lambda: datetime.now().isoformat()
    env.globals["uuid"] = lambda: str(_uuid.uuid4())
    return env


_JINJA = _make_env()


class TemplateContext:
    """Holds all variable scopes available during playbook execution."""

    def __init__(
        self,
        inputs:    dict[str, Any]       = None,
        step_outputs: dict[str, Any]    = None,
        variables: dict[str, Any]       = None,
    ) -> None:
        self.inputs       = inputs       or {}
        self.step_outputs = step_outputs or {}   # keyed by step.id
        self.variables    = variables    or {}

    def as_dict(self) -> dict[str, Any]:
        safe_env = {k: v for k, v in os.environ.items() if k in ENV_WHITELIST}
        return {
            "inputs":  self.inputs,
            "steps":   {sid: {"output": out} for sid, out in self.step_outputs.items()},
            "vars":    self.variables,
            "env":     safe_env,
        }


class TemplateEngine:
    """Renders Jinja2 templates against a TemplateContext."""

    def render(self, value: Any, ctx: TemplateContext) -> Any:
        """Recursively render templates in dicts, lists, and strings."""
        if isinstance(value, str):
            return self._render_str(value, ctx.as_dict())
        elif isinstance(value, dict):
            return {k: self.render(v, ctx) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.render(item, ctx) for item in value]
        return value

    def render_condition(self, condition: str, ctx: TemplateContext) -> bool:
        """Evaluate a Jinja2 boolean condition. Returns True if step should run."""
        if not condition:
            return True
        try:
            result = _JINJA.from_string(f"{{% if {condition} %}}true{{% else %}}false{{% endif %}}").render(ctx.as_dict())
            return result.strip() == "true"
        except (TemplateSyntaxError, UndefinedError):
            return True   # fail-open: run step if condition can't be evaluated

    def _render_str(self, template: str, ctx: dict) -> str:
        if "{{" not in template and "{%" not in template:
            return template   # fast path — no template syntax
        try:
            return _JINJA.from_string(template).render(ctx)
        except UndefinedError as exc:
            raise ValueError(f"Template variable not found: {exc}") from exc
        except TemplateSyntaxError as exc:
            raise ValueError(f"Template syntax error: {exc}") from exc

    @staticmethod
    def extract_vars(template: str) -> list[str]:
        """Extract referenced variable names from a template string."""
        return re.findall(r'\{\{\s*([\w.]+)\s*\}\}', template)
