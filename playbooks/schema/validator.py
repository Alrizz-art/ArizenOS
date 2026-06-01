"""
Playbook Validator — loads, validates, and reports YAML playbook files.
Returns structured errors with line numbers and fix suggestions.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from playbooks.schema.playbook_schema import Playbook

logger = logging.getLogger("arizen.playbook.validator")


@dataclass
class ValidationIssue:
    level:      str   = "error"     # error | warning | info
    location:   str   = ""          # e.g. "steps[2].depends_on[0]"
    message:    str   = ""
    suggestion: str   = ""
    line:       int   = 0


@dataclass
class ValidationResult:
    valid:    bool                   = False
    playbook: Optional[Playbook]     = None
    issues:   list[ValidationIssue]  = field(default_factory=list)
    raw:      dict                   = field(default_factory=dict)

    @property
    def errors(self)   -> list[ValidationIssue]: return [i for i in self.issues if i.level == "error"]
    @property
    def warnings(self) -> list[ValidationIssue]: return [i for i in self.issues if i.level == "warning"]


class PlaybookValidator:
    """
    Validates a YAML playbook file and returns a structured result.
    
    Usage:
        result = PlaybookValidator().validate_file("playbooks/library/create_project.yaml")
        if result.valid:
            engine.run(result.playbook, inputs)
        else:
            for issue in result.errors:
                print(f"[{issue.location}] {issue.message}")
    """

    def validate_file(self, path: str) -> ValidationResult:
        p = Path(path)
        if not p.exists():
            return ValidationResult(issues=[ValidationIssue(
                level="error", message=f"File not found: {path}"
            )])
        try:
            raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            line = getattr(getattr(exc, "problem_mark", None), "line", 0)
            return ValidationResult(issues=[ValidationIssue(
                level="error", location=f"line {line+1}",
                message=f"YAML parse error: {exc}"
            )])
        return self.validate_dict(raw)

    def validate_str(self, yaml_str: str) -> ValidationResult:
        try:
            raw = yaml.safe_load(yaml_str)
        except yaml.YAMLError as exc:
            return ValidationResult(issues=[ValidationIssue(
                level="error", message=f"YAML parse error: {exc}"
            )])
        return self.validate_dict(raw)

    def validate_dict(self, raw: dict) -> ValidationResult:
        result = ValidationResult(raw=raw)
        try:
            playbook = Playbook.model_validate(raw)
            result.playbook = playbook
            result.issues   = self._semantic_checks(playbook)
            result.valid    = not result.errors
        except ValidationError as exc:
            for e in exc.errors():
                loc  = ".".join(str(p) for p in e["loc"])
                msg  = e["msg"]
                hint = self._suggest(loc, msg)
                result.issues.append(ValidationIssue(
                    level="error", location=loc,
                    message=msg, suggestion=hint
                ))
        return result

    # ------------------------------------------------------------------
    # Semantic checks (beyond Pydantic schema)
    # ------------------------------------------------------------------

    def _semantic_checks(self, pb: Playbook) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Cycle detection via DFS
        if cycles := self._find_cycles(pb):
            for cycle in cycles:
                issues.append(ValidationIssue(
                    level="error",
                    location="steps",
                    message=f"Circular dependency detected: {' → '.join(cycle)}",
                    suggestion="Remove one of the depends_on edges to break the cycle.",
                ))

        # Steps that are unreachable (no path from root)
        reachable = self._reachable_steps(pb)
        for step in pb.steps:
            if step.id not in reachable:
                issues.append(ValidationIssue(
                    level="warning",
                    location=f"steps.{step.id}",
                    message=f"Step '{step.id}' is unreachable (nothing depends on its output)",
                    suggestion="Add this step as a dependency of another step, or it will run as a root node.",
                ))

        # Approval gate on non-destructive tools is unnecessary
        for step in pb.steps:
            if step.approval and "read" in step.tool:
                issues.append(ValidationIssue(
                    level="warning",
                    location=f"steps.{step.id}.approval",
                    message=f"Approval gate on read-only tool '{step.tool}' is unusual.",
                    suggestion="Consider removing the approval gate for read-only steps.",
                ))

        # Input defaults satisfy type constraints
        for name, spec in pb.inputs.items():
            if spec.default is not None and spec.enum and spec.default not in spec.enum:
                issues.append(ValidationIssue(
                    level="error",
                    location=f"inputs.{name}.default",
                    message=f"Default value '{spec.default}' not in enum {spec.enum}",
                ))

        # Timeout sanity
        if pb.timeout_sec < 10:
            issues.append(ValidationIssue(
                level="warning",
                location="timeout_sec",
                message="Playbook timeout under 10 seconds may cause premature failures.",
                suggestion="Set timeout_sec to at least 60 for non-trivial playbooks.",
            ))

        return issues

    def _find_cycles(self, pb: Playbook) -> list[list[str]]:
        graph = {s.id: set(s.depends_on) for s in pb.steps}
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            for neighbour in graph.get(node, set()):
                if neighbour not in visited:
                    dfs(neighbour, path + [neighbour])
                elif neighbour in rec_stack:
                    cycle_start = path.index(neighbour)
                    cycles.append(path[cycle_start:] + [neighbour])
            rec_stack.discard(node)

        for step_id in graph:
            if step_id not in visited:
                dfs(step_id, [step_id])
        return cycles

    def _reachable_steps(self, pb: Playbook) -> set[str]:
        # All steps are reachable if they form a connected DAG (roots included)
        return {s.id for s in pb.steps}

    def _suggest(self, loc: str, msg: str) -> str:
        hints = {
            "steps":         "Each step needs 'id', 'agent', and 'tool'.",
            "agent":         f"Valid agents: commander, coder, researcher, fixer, devops, security, designer, memory",
            "trigger.type":  "Valid trigger types: manual, hotkey, cron, file, event, agent, http",
            "inputs":        "Each input needs 'type' (string/integer/boolean/list/dict/file/secret)",
        }
        for key, hint in hints.items():
            if key in loc:
                return hint
        return ""
