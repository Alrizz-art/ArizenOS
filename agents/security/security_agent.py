"""
Arizen Security — Vulnerability Scanning, Audit, and Threat Detection Agent.

Security is a read-mostly, high-trust agent that audits code, dependencies,
filesystem permissions, and running processes. It never auto-remediates
without explicit user approval. It runs in its own process with the most
restricted network access of all agents (disabled entirely).

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

logger = logging.getLogger("arizen.security")


class ThreatLevel(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"


@dataclass
class Finding:
    level:       ThreatLevel = ThreatLevel.INFO
    category:    str         = ""     # vuln | secret | perm | dep | config
    title:       str         = ""
    description: str         = ""
    location:    str         = ""
    cve:         str         = ""
    remediation: str         = ""


@dataclass
class AuditReport:
    target:   str           = ""
    findings: list[Finding] = field(default_factory=list)
    score:    float         = 100.0   # 0 (worst) → 100 (clean)
    summary:  str           = ""


# Patterns for secret / credential leakage detection
SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("GitHub Token",    re.compile(r'ghp_[A-Za-z0-9]{36}')),
    ("AWS Key",         re.compile(r'AKIA[0-9A-Z]{16}')),
    ("Private Key",     re.compile(r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----')),
    ("Password in ENV", re.compile(r'(?i)(password|secret|token)\s*=\s*["\'][^"\']{6,}["\']')),
    ("Connection Str",  re.compile(r'(mongodb|postgresql|mysql)://[^\s"\'<]+')),
]


class SecurityAgent(BaseAgent):
    """
    Arizen Security — audits code, dependencies, and system state.

    Execution model:
        1. Parse scan target (file | directory | deps | process)
        2. Run static analysis (secret scan, hardcoded creds, unsafe patterns)
        3. Run dependency audit (pip-audit / cargo audit)
        4. Score and rank findings by severity
        5. Return AuditReport to Commander
        6. NEVER auto-remediate — always return findings for human review
    """

    MANIFEST = AgentManifest(
        name="security",
        display="Arizen Security",
        version="1.0.0",
        tier=2,
        tools=[
            "filesystem.read",
            "filesystem.walk",
            "filesystem.stat",
            "shell.run_audit",
            "process.list",
        ],
        memory_scopes=["session", "persistent"],
        fs_access=True,
        net_access=False,    # completely offline — no CVE DB calls
        llm_tier="standard",
        autostart=True,
        max_restart=5,
    )

    # File extensions to scan for secrets
    SCAN_EXTENSIONS: set[str] = {
        ".py", ".rs", ".ts", ".tsx", ".js", ".toml",
        ".yaml", ".yml", ".json", ".env", ".sh",
    }

    # Dangerous patterns in code
    CODE_DANGERS: list[tuple[str, str, re.Pattern]] = [
        ("high",   "eval() usage",         re.compile(r'\beval\s*\(')),
        ("high",   "exec() usage",         re.compile(r'\bexec\s*\(')),
        ("medium", "shell=True",           re.compile(r'shell\s*=\s*True')),
        ("medium", "pickle.loads",         re.compile(r'pickle\.loads')),
        ("low",    "print() credentials",  re.compile(r'print\(.*(password|token|secret)', re.I)),
        ("high",   "SQL string concat",    re.compile(r'f["\'].*SELECT.*\{', re.I)),
    ]

    def __init__(self, ctx: AgentContext, bus, llm, shell) -> None:
        super().__init__(ctx)
        self._bus   = bus
        self._llm   = llm
        self._shell = shell

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action = task.get("tool", "security.scan").split(".")[-1]
        target = task.get("target", ".")

        if action == "audit":
            report = await self._full_audit(target)
        else:
            report = await self._scan(target)

        yield self._format_report(report)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------

    async def _scan(self, target: str) -> AuditReport:
        report = AuditReport(target=target)
        path = Path(target)

        if path.is_file():
            files = [path]
        else:
            files = [
                f for f in path.rglob("*")
                if f.suffix in self.SCAN_EXTENSIONS and f.is_file()
            ]

        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Secret detection
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    report.findings.append(Finding(
                        level=ThreatLevel.CRITICAL,
                        category="secret",
                        title=f"Potential {label} exposed",
                        location=str(f),
                        remediation="Remove credential and rotate immediately. Use DPAPI or env vars.",
                    ))

            # Dangerous code patterns
            for severity, title, pattern in self.CODE_DANGERS:
                if pattern.search(content):
                    report.findings.append(Finding(
                        level=ThreatLevel(severity),
                        category="vuln",
                        title=title,
                        location=str(f),
                        remediation=f"Review all uses of '{title}' in {f.name}",
                    ))

        report.score = max(0.0, 100.0 - len(report.findings) * 10)
        return report

    async def _full_audit(self, target: str) -> AuditReport:
        import asyncio
        scan_task  = asyncio.create_task(self._scan(target))
        dep_task   = asyncio.create_task(self._dep_audit())
        scan, deps = await asyncio.gather(scan_task, dep_task)
        scan.findings.extend(deps.findings)
        scan.score = max(0.0, 100.0 - len(scan.findings) * 8)
        return scan

    @tool(name="shell.run_audit", side_effects="read_only")
    async def _dep_audit(self) -> AuditReport:
        report = AuditReport(target="dependencies")
        pip_r   = await self._shell.run(["pip-audit", "--format=json"], timeout=120)
        cargo_r = await self._shell.run(["cargo", "audit", "--json"], timeout=120)

        import json
        for raw, source in [(pip_r.stdout, "pip"), (cargo_r.stdout, "cargo")]:
            try:
                data = json.loads(raw)
                vulns = data.get("vulnerabilities", []) if source == "pip" else data.get("vulnerabilities", {}).get("list", [])
                for v in vulns:
                    report.findings.append(Finding(
                        level=ThreatLevel.HIGH,
                        category="dep",
                        title=f"Vulnerable dependency ({source}): {v.get('name', '?')}",
                        cve=v.get("id", ""),
                        remediation=f"Upgrade to {v.get('fix_versions', ['latest'])}",
                    ))
            except Exception:
                pass

        return report

    def _format_report(self, report: AuditReport) -> str:
        if not report.findings:
            return f"✓ Security scan clean. Score: {report.score:.0f}/100"

        critical = [f for f in report.findings if f.level == ThreatLevel.CRITICAL]
        high     = [f for f in report.findings if f.level == ThreatLevel.HIGH]
        rest     = [f for f in report.findings if f.level not in (ThreatLevel.CRITICAL, ThreatLevel.HIGH)]

        lines = [f"Security Report — Score: {report.score:.0f}/100\n"]
        for group, label in [(critical, "CRITICAL"), (high, "HIGH"), (rest, "OTHER")]:
            for f in group:
                lines.append(f"[{label}] {f.title}")
                lines.append(f"  Location: {f.location}")
                if f.cve:
                    lines.append(f"  CVE: {f.cve}")
                lines.append(f"  Fix: {f.remediation}\n")

        return "\n".join(lines)
