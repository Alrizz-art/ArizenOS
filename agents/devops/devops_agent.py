"""
Arizen DevOps — Build, Deployment, Service Management, and CI Agent.

DevOps automates the engineering pipeline: building the ArizenOS daemon
and UI, running CI checks, managing Windows services, and orchestrating
release packaging. It operates within declared shell permissions and
always logs its actions to the audit trail.

All invocations come from Commander. Destructive operations (service
restart, deploy) require explicit user approval before execution.
"""
from __future__ import annotations

import logging
import shlex
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator

from agents._base.base_agent import AgentContext, AgentManifest, BaseAgent
from agents._base.tool_registry import tool

logger = logging.getLogger("arizen.devops")


class BuildTarget(str, Enum):
    DAEMON  = "daemon"      # Rust — arizen-daemon
    UI      = "ui"          # TypeScript/Tauri — command-nexus
    AGENTS  = "agents"      # Python — intelligence layer
    ALL     = "all"


class ServiceAction(str, Enum):
    START   = "start"
    STOP    = "stop"
    RESTART = "restart"
    STATUS  = "status"


@dataclass
class BuildResult:
    target:  str  = ""
    success: bool = False
    output:  str  = ""
    elapsed: float = 0.0
    artifact_path: str = ""


@dataclass
class CIReport:
    passed:   bool       = False
    steps:    list[dict] = field(default_factory=list)
    warnings: list[str]  = field(default_factory=list)
    errors:   list[str]  = field(default_factory=list)


class DevOpsAgent(BaseAgent):
    """
    Arizen DevOps — automates build, CI, and deployment pipelines.

    Execution model:
        1. Parse action (build | deploy | ci | monitor | service)
        2. Validate target + permissions
        3. Approval gate for destructive ops (restart, deploy)
        4. Execute shell pipeline with timeout
        5. Parse output → structured result
        6. Return status to Commander + emit HUD event
    """

    MANIFEST = AgentManifest(
        name="devops",
        display="Arizen DevOps",
        version="1.0.0",
        tier=2,
        tools=[
            "shell.run",
            "shell.run_streaming",
            "service.control",
            "service.status",
            "filesystem.read_log",
            "process.list",
            "process.kill",
        ],
        memory_scopes=["session", "persistent"],
        fs_access=True,
        net_access=False,
        llm_tier="nano",
        autostart=True,
        max_restart=5,
    )

    # Shell command allowlist — DevOps may only run these top-level commands.
    COMMAND_ALLOWLIST: set[str] = {
        "cargo", "rustup", "npm", "pnpm", "npx",
        "python", "pip", "pytest",
        "sc", "net",                            # Windows service control
        "powershell", "pwsh",
        "git", "gh",
        "docker", "docker-compose",
    }

    BUILD_COMMANDS: dict[BuildTarget, list[str]] = {
        BuildTarget.DAEMON: ["cargo", "build", "--release", "--manifest-path", "core/arizen-daemon/Cargo.toml"],
        BuildTarget.UI:     ["pnpm", "--filter", "command-nexus", "build"],
        BuildTarget.AGENTS: ["pip", "install", "-r", "requirements.txt"],
        BuildTarget.ALL:    ["pwsh", "-File", "scripts/build/build_all.ps1"],
    }

    def __init__(self, ctx: AgentContext, bus, llm, shell) -> None:
        super().__init__(ctx)
        self._bus   = bus
        self._llm   = llm
        self._shell = shell

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action = task.get("tool", "devops.build").split(".")[-1]
        target = task.get("target", "all")
        query  = task.get("query", "")

        dispatch = {
            "build":   self._build,
            "ci":      self._run_ci,
            "deploy":  self._deploy,
            "monitor": self._monitor,
            "service": self._service,
        }

        handler = dispatch.get(action, self._build)
        result  = await handler(target, query, task)
        yield str(result)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    async def _build(self, target: str, query: str, task: dict) -> BuildResult:
        bt = BuildTarget(target) if target in BuildTarget._value2member_map_ else BuildTarget.ALL
        cmd = self.BUILD_COMMANDS[bt]
        self._assert_allowed(cmd[0])

        import time
        start = time.monotonic()
        result = await self._shell.run(cmd, timeout=300, cwd=".")
        elapsed = time.monotonic() - start

        return BuildResult(
            target=bt.value,
            success=result.returncode == 0,
            output=result.stdout[-3000:] + result.stderr[-1000:],
            elapsed=elapsed,
        )

    # ------------------------------------------------------------------
    # CI
    # ------------------------------------------------------------------

    async def _run_ci(self, target: str, query: str, task: dict) -> CIReport:
        report = CIReport()
        ci_steps = [
            ("typecheck", ["cargo", "clippy", "--all-targets"]),
            ("tests",     ["cargo", "test", "--all"]),
            ("py-lint",   ["python", "-m", "flake8", "agents/", "core/"]),
            ("py-test",   ["python", "-m", "pytest", "tests/", "-x"]),
        ]
        for name, cmd in ci_steps:
            self._assert_allowed(cmd[0])
            r = await self._shell.run(cmd, timeout=120)
            step = {"name": name, "passed": r.returncode == 0, "output": r.stdout[-1000:]}
            report.steps.append(step)
            if r.returncode != 0:
                report.errors.append(f"{name}: {r.stderr[-200:]}")

        report.passed = not report.errors
        return report

    # ------------------------------------------------------------------
    # Deploy (approval-gated)
    # ------------------------------------------------------------------

    @tool(name="devops.deploy", side_effects="destructive", requires_approval=True)
    async def _deploy(self, target: str, query: str, task: dict) -> dict:
        cmd = ["pwsh", "-File", "scripts/release/deploy.ps1", f"-Target={target}"]
        result = await self._shell.run(cmd, timeout=600)
        return {"success": result.returncode == 0, "output": result.stdout[-2000:]}

    # ------------------------------------------------------------------
    # Service control (approval-gated for restart/stop)
    # ------------------------------------------------------------------

    @tool(name="service.control", side_effects="system", requires_approval=True)
    async def _service(self, target: str, query: str, task: dict) -> dict:
        action_str = task.get("action", "status")
        action = ServiceAction(action_str) if action_str in ServiceAction._value2member_map_ else ServiceAction.STATUS
        svc_name = task.get("service_name", "ArizenDaemon")

        if action == ServiceAction.STATUS:
            r = await self._shell.run(["sc", "query", svc_name], timeout=10)
        elif action == ServiceAction.START:
            r = await self._shell.run(["sc", "start", svc_name], timeout=30)
        elif action == ServiceAction.STOP:
            r = await self._shell.run(["sc", "stop", svc_name], timeout=30)
        else:  # restart
            await self._shell.run(["sc", "stop", svc_name], timeout=30)
            import asyncio; await asyncio.sleep(2)
            r = await self._shell.run(["sc", "start", svc_name], timeout=30)

        return {"service": svc_name, "action": action.value, "output": r.stdout, "success": r.returncode == 0}

    # ------------------------------------------------------------------
    # Monitor
    # ------------------------------------------------------------------

    async def _monitor(self, target: str, query: str, task: dict) -> dict:
        r = await self._shell.run(["sc", "query", "ArizenDaemon"], timeout=10)
        py_r = await self._shell.run(["pwsh", "-Command", "Get-Process python | Select-Object Name,CPU,WorkingSet"], timeout=10)
        return {
            "daemon_status": r.stdout,
            "python_processes": py_r.stdout,
        }

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------

    def _assert_allowed(self, cmd: str) -> None:
        if cmd not in self.COMMAND_ALLOWLIST:
            raise PermissionError(f"DevOps: command '{cmd}' not in allowlist")
