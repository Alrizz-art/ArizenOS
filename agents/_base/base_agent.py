"""
BaseAgent — Abstract base class for all ArizenOS agents.

Every agent (Monarch, Archivist, Executor, Sentinel, Weaver, Oracle)
inherits from this class and implements handle().

Agents are started as isolated Python processes by the Rust daemon.
They communicate via the named pipe IPC bus — never by direct import.
"""
from __future__ import annotations

import abc
import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncIterator

from pydantic import BaseModel

logger = logging.getLogger("arizen.agent")


@dataclass
class AgentContext:
    """Runtime context passed to each agent on startup."""
    agent_id:    str
    agent_name:  str
    pipe_path:   str                 = r"\.pipearizen-agents"
    config_path: Path                = field(default_factory=lambda: Path(os.environ.get(
                                         "ARIZEN_CONFIG",
                                         Path.home() / "AppData/Local/ArizenOS/config.toml"
                                     )))
    sandbox_dir: Path                = field(default_factory=lambda: Path(os.environ.get(
                                         "ARIZEN_SANDBOX",
                                         Path.home() / "AppData/Local/ArizenOS/sandbox"
                                     )))


class AgentManifest(BaseModel):
    """Declared capabilities and constraints of an agent."""
    name:             str
    display:          str
    version:          str               = "0.1.0"
    tier:             int               = 2
    tools:            list[str]         = []
    memory_scopes:    list[str]         = ["session"]
    fs_access:        bool              = False
    net_access:       bool              = False
    llm_tier:         str               = "standard"
    autostart:        bool              = True
    max_restart:      int               = 5


class BaseAgent(abc.ABC):
    """
    Abstract base for all ArizenOS agents.
    Subclasses implement handle() to process incoming tasks.
    """

    MANIFEST: AgentManifest  # must be defined in subclass

    def __init__(self, ctx: AgentContext) -> None:
        self._ctx  = ctx
        self._name = ctx.agent_name
        self._log  = logging.getLogger(f"arizen.{self._name}")
        self._running = False

    @abc.abstractmethod
    async def handle(self, task: dict) -> AsyncIterator[str]:
        """Process a task and yield streaming response tokens."""
        ...

    async def start(self) -> None:
        """Connect to IPC bus and begin processing messages."""
        self._running = True
        self._log.info("%s agent started (pid=%d)", self._name, os.getpid())
        try:
            await self._run_loop()
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            self._log.info("%s agent stopped", self._name)

    async def stop(self) -> None:
        self._running = False

    async def _run_loop(self) -> None:
        """Main IPC message loop — override to customize transport."""
        while self._running:
            await asyncio.sleep(0.1)   # placeholder: real impl uses named pipe reader

    def health(self) -> dict:
        return {"agent": self._name, "status": "healthy", "running": self._running}
