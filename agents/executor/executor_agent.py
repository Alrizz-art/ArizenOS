"""
Executor — Task Execution Agent.
Runs OS-level tasks: shell commands, file ops, app launches.
All destructive actions require explicit approval.
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DESTRUCTIVE_TOOLS = {"delete_file", "move_file", "run_shell", "write_file"}


@dataclass
class ToolResult:
    success: bool
    output:  str
    error:   Optional[str] = None


class ExecutorAgent:
    """Executes OS-level tasks with approval gates on destructive ops."""

    def __init__(self, approval_bus) -> None:
        self._approval = approval_bus
        logger.info("Executor initialized")

    async def run(self, tool: str, inputs: dict) -> ToolResult:
        if tool in DESTRUCTIVE_TOOLS:
            approved = await self._approval.request(tool, inputs)
            if not approved:
                return ToolResult(False, "", "Action cancelled by user")

        match tool:
            case "run_shell":
                return await self._shell(inputs.get("command", ""))
            case "read_file":
                return self._read_file(Path(inputs.get("path", "")))
            case "open_app":
                return await self._open(inputs.get("target", ""))
            case _:
                return ToolResult(False, "", f"Unknown tool: {tool}")

    async def _shell(self, command: str) -> ToolResult:
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            return ToolResult(
                success=proc.returncode == 0,
                output=stdout.decode("utf-8", errors="replace"),
                error=stderr.decode("utf-8", errors="replace") or None,
            )
        except asyncio.TimeoutError:
            return ToolResult(False, "", "Command timed out after 30s")

    def _read_file(self, path: Path) -> ToolResult:
        try:
            return ToolResult(True, path.read_text(encoding="utf-8"))
        except Exception as e:
            return ToolResult(False, "", str(e))

    async def _open(self, target: str) -> ToolResult:
        try:
            subprocess.Popen(["start", target], shell=True)
            return ToolResult(True, f"Opened: {target}")
        except Exception as e:
            return ToolResult(False, "", str(e))
