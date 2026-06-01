"""
Arizen Designer — UI Component Generation, Theme Management, and
Design System Adherence Agent.

Designer generates React/TypeScript UI components, manages Tauri
theme tokens (branding/tokens/), checks accessibility (WCAG AA),
and produces SVG assets. It understands the ArizenOS design language
and the Command Nexus codebase structure.

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

logger = logging.getLogger("arizen.designer")


class DesignAction(str, Enum):
    COMPONENT   = "component"    # Generate a new React/TSX component
    THEME       = "theme"        # Update design tokens (CSS vars, TOML)
    ICON        = "icon"         # Generate or modify SVG icon
    AUDIT       = "audit"        # Accessibility + consistency audit
    STORYBOOK   = "storybook"    # Generate Storybook story


@dataclass
class ComponentSpec:
    name:        str        = ""
    description: str        = ""
    props:       list[dict] = field(default_factory=list)
    variant:     str        = "default"
    accessible:  bool       = True


@dataclass
class DesignResult:
    action:    str  = ""
    code:      str  = ""
    file_path: str  = ""
    tokens:    dict = field(default_factory=dict)
    warnings:  list = field(default_factory=list)
    summary:   str  = ""


class DesignerAgent(BaseAgent):
    """
    Arizen Designer — generates UI code and manages the design system.

    Execution model:
        1. Parse design intent → DesignAction + ComponentSpec
        2. Load existing design tokens from branding/tokens/
        3. Generate component / update tokens / audit existing UI
        4. Run accessibility check on generated HTML/JSX
        5. Write output to ui/command-nexus/src/ (requires approval)
        6. Return DesignResult to Commander
    """

    MANIFEST = AgentManifest(
        name="designer",
        display="Arizen Designer",
        version="1.0.0",
        tier=2,
        tools=[
            "filesystem.read",
            "filesystem.write",
            "filesystem.list_dir",
            "design.read_tokens",
            "design.write_tokens",
            "design.accessibility_check",
        ],
        memory_scopes=["session"],
        fs_access=True,
        net_access=False,
        llm_tier="power",
        autostart=False,    # on-demand; not always needed
        max_restart=3,
    )

    FS_ALLOWLIST: list[str] = [
        "ui/",
        "apps/",
        "branding/",
    ]

    TOKEN_FILE: str = "branding/tokens/tokens.toml"

    # ArizenOS design constraints given to LLM
    DESIGN_SYSTEM_PROMPT: str = """
You are the ArizenOS UI engineer. Follow these rules exactly:
- Stack: React 18 + TypeScript, Tauri 2.0, CSS Modules
- Design tokens: use CSS variables from branding/tokens/tokens.toml (--color-*, --radius-*, --font-*)
- Motion: Framer Motion for animations; prefer subtle, fast transitions (150–250ms)
- Accessibility: every interactive element needs aria-label, role, and keyboard support
- Theme: dark-first; support light via data-theme="light" on :root
- No Tailwind — CSS Modules only
- Export default; named props interface; JSDoc on public interface
- Arizen visual language: monospace accents, sharp geometry, terminal-inspired palette
"""

    def __init__(self, ctx: AgentContext, bus, llm) -> None:
        super().__init__(ctx)
        self._bus = bus
        self._llm = llm

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action  = task.get("tool", "design.component").split(".")[-1]
        query   = task.get("query", "")
        fp      = task.get("file_path", "")

        tokens  = await self._load_tokens()

        dispatch = {
            "component": self._gen_component,
            "theme":     self._update_theme,
            "icon":      self._gen_icon,
            "audit":     self._audit,
            "storybook": self._gen_story,
        }

        handler = dispatch.get(action, self._gen_component)
        result  = await handler(query, fp, tokens, task)
        yield self._format(result)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _gen_component(
        self, query: str, fp: str, tokens: dict, task: dict
    ) -> DesignResult:
        system = self.DESIGN_SYSTEM_PROMPT + f"\n\nDesign tokens available:\n{tokens}"
        prompt = (
            f"Generate a complete React/TypeScript component.\n"
            f"Requirement: {query}\n"
            f"Output: TypeScript component + CSS Module. "
            f"Separate them with // --- CSS MODULE ---"
        )
        raw = await self._llm.complete(prompt, system=system, tier="power")

        tsx, css = self._split_tsx_css(raw)
        comp_name = self._extract_component_name(tsx) or "ArComponent"

        out_path  = fp or f"ui/command-nexus/src/components/{comp_name}/{comp_name}.tsx"
        css_path  = out_path.replace(".tsx", ".module.css")

        warnings = self._check_accessibility(tsx)

        if tsx:
            await self._write_file(out_path, tsx)
        if css:
            await self._write_file(css_path, css)

        return DesignResult(
            action="component", code=tsx, file_path=out_path,
            warnings=warnings,
            summary=f"Generated {comp_name} component ({len(tsx.splitlines())} lines TSX)"
        )

    async def _update_theme(
        self, query: str, fp: str, tokens: dict, task: dict
    ) -> DesignResult:
        system = (
            "You are a design token manager for ArizenOS. "
            "Update the TOML token file based on the request. "
            "Return ONLY valid TOML. Preserve all existing tokens unless explicitly changed. "
            "Token categories: [colors], [typography], [spacing], [radius], [motion]"
        )
        prompt = f"Current tokens:\n{tokens}\n\nChange request: {query}\n\nReturn updated TOML:"
        new_toml = await self._llm.complete(prompt, system=system, tier="standard")
        await self._write_file(self.TOKEN_FILE, new_toml.strip())
        return DesignResult(
            action="theme", file_path=self.TOKEN_FILE,
            summary="Design tokens updated"
        )

    async def _gen_icon(
        self, query: str, fp: str, tokens: dict, task: dict
    ) -> DesignResult:
        system = (
            "Generate a clean, minimal SVG icon. "
            "Requirements: 24x24 viewBox, single currentColor stroke, "
            "stroke-width=1.5, no fill unless specified, rounded linecap."
        )
        svg = await self._llm.complete(query, system=system, tier="standard")
        svg = svg.strip()
        out = fp or f"branding/assets/icons/{query[:20].replace(' ','_').lower()}.svg"
        await self._write_file(out, svg)
        return DesignResult(action="icon", code=svg, file_path=out, summary=f"SVG icon generated: {out}")

    async def _audit(
        self, query: str, fp: str, tokens: dict, task: dict
    ) -> DesignResult:
        path = Path(fp or "ui/command-nexus/src")
        issues: list[str] = []
        for f in path.rglob("*.tsx"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                issues.extend(self._check_accessibility(content, str(f)))
            except Exception:
                pass
        summary = f"Audit complete: {len(issues)} issues found\n" + "\n".join(issues[:20])
        return DesignResult(action="audit", warnings=issues, summary=summary)

    async def _gen_story(
        self, query: str, fp: str, tokens: dict, task: dict
    ) -> DesignResult:
        system = "Generate a Storybook 7 story (CSF3 format) for a React/TypeScript component."
        comp_content = await self._load_file(fp) if fp else query
        story = await self._llm.complete(f"Component:\n{comp_content}", system=system, tier="standard")
        out = fp.replace(".tsx", ".stories.tsx") if fp else "ui/command-nexus/src/components/Story.stories.tsx"
        await self._write_file(out, story)
        return DesignResult(action="storybook", code=story, file_path=out, summary="Storybook story generated")

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    @tool(name="design.read_tokens", side_effects="read_only")
    async def _load_tokens(self) -> dict:
        try:
            import tomllib
            return tomllib.loads(Path(self.TOKEN_FILE).read_text(encoding="utf-8"))
        except Exception:
            return {}

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
        logger.info("Designer wrote: %s", path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check_accessibility(self, tsx: str, location: str = "") -> list[str]:
        issues = []
        if "<img" in tsx and "alt=" not in tsx:
            issues.append(f"{location}: <img> missing alt attribute")
        if re.search(r'<button[^>]*>', tsx) and "aria-label" not in tsx:
            issues.append(f"{location}: <button> may be missing aria-label")
        if "onClick" in tsx and "onKeyDown" not in tsx and "onKeyPress" not in tsx:
            issues.append(f"{location}: onClick handler without keyboard equivalent")
        return issues

    def _split_tsx_css(self, raw: str) -> tuple[str, str]:
        parts = re.split(r"//\s*---\s*CSS MODULE\s*---", raw, maxsplit=1)
        tsx = parts[0].strip() if parts else raw.strip()
        css = parts[1].strip() if len(parts) > 1 else ""
        return tsx, css

    def _extract_component_name(self, tsx: str) -> str:
        m = re.search(r'(?:function|const)\s+([A-Z][A-Za-z0-9]+)', tsx)
        return m.group(1) if m else ""

    def _assert_allowed(self, path: str) -> None:
        if not any(str(path).startswith(p) for p in self.FS_ALLOWLIST):
            raise PermissionError(f"Designer: '{path}' outside allowed sandbox")

    def _format(self, result: DesignResult) -> str:
        parts = [result.summary]
        if result.warnings:
            parts += ["", "Accessibility warnings:"] + [f"  • {w}" for w in result.warnings]
        if result.file_path:
            parts.append(f"\nOutput: {result.file_path}")
        return "\n".join(parts)
