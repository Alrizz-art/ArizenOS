"""
Arizen Coder — Code Generation, Review, and Refactoring Agent.

Coder specializes in software engineering tasks across Python, Rust,
TypeScript, and shell scripting. It integrates with the local filesystem
(read/write within declared paths), understands the ArizenOS codebase
structure, and can generate diffs, create new files, and review pull
request diffs.

Coder is always invoked by Commander — never directly.
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

logger = logging.getLogger("arizen.coder")


class Language(str, Enum):
    PYTHON     = "python"
    RUST       = "rust"
    TYPESCRIPT = "typescript"
    SHELL      = "shell"
    TOML       = "toml"
    MARKDOWN   = "markdown"
    AUTO       = "auto"


@dataclass
class CodeTask:
    action:    str          = ""   # generate | review | refactor | explain | test
    language:  Language     = Language.AUTO
    prompt:    str          = ""
    file_path: str          = ""   # target file (optional)
    context:   str          = ""   # existing code or surrounding context
    diff_mode: bool         = False


@dataclass
class CodeResult:
    action:    str   = ""
    language:  str   = ""
    code:      str   = ""
    diff:      str   = ""
    file_path: str   = ""
    summary:   str   = ""
    warnings:  list  = field(default_factory=list)


LANGUAGE_MAP: dict[str, Language] = {
    ".py":   Language.PYTHON,
    ".rs":   Language.RUST,
    ".ts":   Language.TYPESCRIPT,
    ".tsx":  Language.TYPESCRIPT,
    ".sh":   Language.SHELL,
    ".toml": Language.TOML,
    ".md":   Language.MARKDOWN,
}


class CoderAgent(BaseAgent):
    """
    Arizen Coder — handles all code-related tasks.

    Execution model:
        1. Parse CodeTask from Commander's inputs
        2. Detect language (from file extension or LLM)
        3. Load file context if file_path provided
        4. Route to specialized handler (generate/review/refactor/test)
        5. Validate output (syntax check where possible)
        6. Return CodeResult to Commander
    """

    MANIFEST = AgentManifest(
        name="coder",
        display="Arizen Coder",
        version="1.0.0",
        tier=2,
        tools=[
            "filesystem.read",
            "filesystem.write",
            "filesystem.diff",
            "filesystem.list_dir",
            "shell.syntax_check",
            "shell.run_tests",
        ],
        memory_scopes=["session"],
        fs_access=True,
        net_access=False,
        llm_tier="power",
        autostart=True,
        max_restart=5,
    )

    # Declared filesystem sandbox — Coder may not access paths outside this list.
    FS_ALLOWLIST: list[str] = [
        "agents/",
        "core/",
        "integrations/",
        "skills/",
        "ui/",
        "apps/",
        "docs/",
        "scripts/",
        "playbooks/",
    ]

    def __init__(self, ctx: AgentContext, bus, llm) -> None:
        super().__init__(ctx)
        self._bus = bus
        self._llm = llm

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action  = task.get("tool", "code.generate").split(".")[-1]
        query   = task.get("query", "")
        context = task.get("context", {})
        fp      = task.get("file_path", "")

        lang = self._detect_language(fp, query)
        file_ctx = await self._load_file(fp) if fp else ""

        handler = {
            "generate":  self._generate,
            "review":    self._review,
            "refactor":  self._refactor,
            "explain":   self._explain,
            "test":      self._test,
        }.get(action, self._generate)

        result = await handler(query, lang, file_ctx, fp, context)
        yield str(result)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _generate(
        self, query: str, lang: Language, file_ctx: str, fp: str, ctx: dict
    ) -> CodeResult:
        """Generate new code from a natural language description."""
        system = (
            f"You are an expert {lang.value} developer. "
            "Write clean, well-commented code. No markdown fences unless asked. "
            "Follow ArizenOS conventions: async-first, type-annotated, Pydantic models."
        )
        prompt = f"{query}\n\nExisting context:\n{file_ctx}" if file_ctx else query
        code = await self._llm.complete(prompt, system=system, tier="power")
        code = self._strip_fences(code)

        if fp:
            await self._write_file(fp, code)

        return CodeResult(
            action="generate", language=lang.value,
            code=code, file_path=fp,
            summary=f"Generated {lang.value} code ({len(code.splitlines())} lines)"
        )

    async def _review(
        self, query: str, lang: Language, file_ctx: str, fp: str, ctx: dict
    ) -> CodeResult:
        """Review code and return structured feedback."""
        system = (
            "You are a senior code reviewer. Identify bugs, style issues, "
            "security concerns, and improvement opportunities. "
            "Format: severity (critical/major/minor), location, explanation, suggestion."
        )
        prompt = f"Review this {lang.value} code:\n\n{file_ctx or query}"
        feedback = await self._llm.complete(prompt, system=system, tier="standard")
        return CodeResult(
            action="review", language=lang.value,
            summary=feedback, file_path=fp
        )

    async def _refactor(
        self, query: str, lang: Language, file_ctx: str, fp: str, ctx: dict
    ) -> CodeResult:
        """Refactor existing code; return unified diff."""
        system = (
            "You are a refactoring expert. Apply the requested changes while "
            "preserving behavior. Return only the complete refactored file."
        )
        prompt = f"Refactor instruction: {query}\n\nOriginal code:\n{file_ctx}"
        refactored = await self._llm.complete(prompt, system=system, tier="power")
        refactored = self._strip_fences(refactored)
        diff = self._make_diff(file_ctx, refactored, fp)

        if fp:
            await self._write_file(fp, refactored)

        return CodeResult(
            action="refactor", language=lang.value,
            code=refactored, diff=diff, file_path=fp,
            summary=f"Refactored {fp or 'code'}"
        )

    async def _explain(
        self, query: str, lang: Language, file_ctx: str, fp: str, ctx: dict
    ) -> CodeResult:
        """Explain what a piece of code does in plain language."""
        prompt = (
            f"Explain this {lang.value} code concisely. "
            f"Cover: purpose, key logic, inputs/outputs, side effects.\n\n"
            f"{file_ctx or query}"
        )
        explanation = await self._llm.complete(prompt, tier="standard")
        return CodeResult(action="explain", language=lang.value, summary=explanation)

    async def _test(
        self, query: str, lang: Language, file_ctx: str, fp: str, ctx: dict
    ) -> CodeResult:
        """Generate unit tests for the given code."""
        system = (
            f"Generate comprehensive unit tests for this {lang.value} code. "
            "Cover: happy path, edge cases, error handling. "
            "Use pytest for Python, cargo test for Rust, vitest for TypeScript."
        )
        prompt = f"{file_ctx or query}"
        tests = await self._llm.complete(prompt, system=system, tier="power")
        tests = self._strip_fences(tests)
        return CodeResult(action="test", language=lang.value, code=tests, summary="Tests generated")

    # ------------------------------------------------------------------
    # Filesystem tools
    # ------------------------------------------------------------------

    @tool(name="filesystem.read", side_effects="read_only")
    async def _load_file(self, path: str) -> str:
        self._assert_allowed(path)
        try:
            return Path(path).read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    @tool(name="filesystem.write", side_effects="write", requires_approval=True)
    async def _write_file(self, path: str, content: str) -> None:
        self._assert_allowed(path)
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        logger.info("Coder wrote: %s", path)

    def _assert_allowed(self, path: str) -> None:
        if not any(str(path).startswith(prefix) for prefix in self.FS_ALLOWLIST):
            raise PermissionError(f"Coder: path '{path}' outside allowed sandbox")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_language(self, path: str, query: str) -> Language:
        if path:
            ext = Path(path).suffix.lower()
            if ext in LANGUAGE_MAP:
                return LANGUAGE_MAP[ext]
        for lang in Language:
            if lang.value in query.lower():
                return lang
        return Language.PYTHON

    def _strip_fences(self, text: str) -> str:
        return re.sub(r"^```[a-z]*\n|```$", "", text, flags=re.MULTILINE).strip()

    def _make_diff(self, original: str, modified: str, path: str) -> str:
        import difflib
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile=f"a/{path}", tofile=f"b/{path}"
        )
        return "".join(diff)
