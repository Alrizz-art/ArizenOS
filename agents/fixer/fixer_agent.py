"""
Arizen Fixer — Error Diagnosis, Debugging, and Automated Patch Agent.

Fixer receives error logs, stack traces, or bug descriptions and produces
structured diagnoses with actionable patches. It integrates with the local
codebase (read-only by default; write requires approval) and can run tests
to verify a fix before proposing it.

All invocations come from Commander.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncIterator

from agents._base.base_agent import AgentContext, AgentManifest, BaseAgent
from agents._base.tool_registry import tool

logger = logging.getLogger("arizen.fixer")


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"


@dataclass
class BugReport:
    error_text:  str   = ""
    file_path:   str   = ""
    line_number: int   = 0
    context:     str   = ""
    stack_trace: str   = ""


@dataclass
class Diagnosis:
    severity:    Severity    = Severity.MEDIUM
    root_cause:  str         = ""
    explanation: str         = ""
    affected:    list[str]   = field(default_factory=list)
    patch:       str         = ""
    diff:        str         = ""
    verified:    bool        = False
    confidence:  float       = 0.0


class FixerAgent(BaseAgent):
    """
    Arizen Fixer — diagnoses bugs and generates verified patches.

    Execution model:
        1. Parse error text → BugReport (regex + LLM)
        2. Locate affected file(s) from stack trace
        3. Load file context (±50 lines around error)
        4. LLM diagnosis → root cause + patch
        5. Optional: run test suite to verify patch
        6. Return Diagnosis to Commander (patch requires approval before write)
    """

    MANIFEST = AgentManifest(
        name="fixer",
        display="Arizen Fixer",
        version="1.0.0",
        tier=2,
        tools=[
            "filesystem.read",
            "filesystem.write",
            "filesystem.grep",
            "shell.run_tests",
            "shell.lint",
        ],
        memory_scopes=["session"],
        fs_access=True,
        net_access=False,
        llm_tier="power",
        autostart=True,
        max_restart=5,
    )

    STACK_PATTERNS: list[re.Pattern] = [
        re.compile(r'File "(.+?)", line (\d+)'),           # Python
        re.compile(r'at (.+?):(\d+):\d+'),                 # TypeScript/Node
        re.compile(r'--> (.+?):(\d+):\d+'),                # Rust
        re.compile(r'(\S+\.py):(\d+): (error|warning):'),  # flake8/mypy
    ]

    def __init__(self, ctx: AgentContext, bus, llm, shell) -> None:
        super().__init__(ctx)
        self._bus   = bus
        self._llm   = llm
        self._shell = shell

    async def handle(self, task: dict) -> AsyncIterator[str]:
        query   = task.get("query", "")
        context = task.get("context", {})

        report    = await self._parse_report(query)
        diagnosis = await self._diagnose(report)
        yield self._format_diagnosis(diagnosis)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    async def _parse_report(self, error_text: str) -> BugReport:
        report = BugReport(error_text=error_text)

        for pattern in self.STACK_PATTERNS:
            m = pattern.search(error_text)
            if m:
                report.file_path   = m.group(1)
                report.line_number = int(m.group(2))
                break

        if report.file_path:
            report.context = await self._load_context(report.file_path, report.line_number)

        lines = error_text.splitlines()
        trace_start = next((i for i, l in enumerate(lines) if "Traceback" in l or "stack backtrace" in l), None)
        if trace_start is not None:
            report.stack_trace = "\n".join(lines[trace_start:])

        return report

    async def _diagnose(self, report: BugReport) -> Diagnosis:
        system = (
            "You are an expert debugger. Given an error and code context, provide:\n"
            "1. SEVERITY: (critical/high/medium/low)\n"
            "2. ROOT_CAUSE: one-line summary\n"
            "3. EXPLANATION: detailed analysis\n"
            "4. PATCH: the fixed code (complete function or block)\n"
            "5. CONFIDENCE: 0.0–1.0\n"
            "Format strictly as JSON."
        )
        prompt = (
            f"Error:\n{report.error_text}\n\n"
            f"Stack trace:\n{report.stack_trace}\n\n"
            f"File context ({report.file_path}:{report.line_number}):\n{report.context}"
        )
        raw = await self._llm.complete(prompt, system=system, tier="power")

        import json
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

        diag = Diagnosis(
            severity    = Severity(data.get("SEVERITY", "medium").lower()),
            root_cause  = data.get("ROOT_CAUSE", "Unknown"),
            explanation = data.get("EXPLANATION", raw),
            patch       = data.get("PATCH", ""),
            confidence  = float(data.get("CONFIDENCE", 0.5)),
            affected    = [report.file_path] if report.file_path else [],
        )

        if diag.patch and report.context:
            import difflib
            diff = difflib.unified_diff(
                report.context.splitlines(keepends=True),
                diag.patch.splitlines(keepends=True),
                fromfile=f"a/{report.file_path}",
                tofile=f"b/{report.file_path}",
            )
            diag.diff = "".join(diff)

        return diag

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    @tool(name="filesystem.read", side_effects="read_only")
    async def _load_context(self, path: str, line: int, window: int = 50) -> str:
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
            start = max(0, line - window)
            end   = min(len(lines), line + window)
            numbered = [f"{i+start+1:4d} | {l}" for i, l in enumerate(lines[start:end])]
            return "\n".join(numbered)
        except FileNotFoundError:
            return f"# File not found: {path}"

    @tool(name="filesystem.write", side_effects="write", requires_approval=True)
    async def _apply_patch(self, path: str, patched_content: str) -> bool:
        try:
            Path(path).write_text(patched_content, encoding="utf-8")
            logger.info("Fixer applied patch to %s", path)
            return True
        except Exception as exc:
            logger.error("Patch application failed: %s", exc)
            return False

    @tool(name="shell.run_tests", side_effects="idempotent")
    async def _run_tests(self, test_path: str) -> dict:
        result = await self._shell.run(["pytest", test_path, "-x", "--tb=short"], timeout=60)
        return {"passed": result.returncode == 0, "output": result.stdout}

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_diagnosis(self, d: Diagnosis) -> str:
        parts = [
            f"**Severity:** {d.severity.value.upper()}",
            f"**Root Cause:** {d.root_cause}",
            f"**Confidence:** {d.confidence:.0%}",
            "",
            d.explanation,
        ]
        if d.diff:
            parts += ["", "```diff", d.diff, "```"]
        return "\n".join(parts)
