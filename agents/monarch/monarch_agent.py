"""
Monarch — Master Orchestrator Agent.
Decomposes NL tasks into a DAG of sub-tasks, delegates to specialist
agents, and synthesizes the final response.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    WAITING   = "waiting"
    COMPLETE  = "complete"
    FAILED    = "failed"


@dataclass
class SubTask:
    id:         str = field(default_factory=lambda: str(uuid4()))
    agent:      str = ""
    tool:       str = ""
    inputs:     dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    status:     TaskStatus = TaskStatus.PENDING
    output:     Optional[dict] = None


@dataclass
class ExecutionPlan:
    id:     str = field(default_factory=lambda: str(uuid4()))
    query:  str = ""
    tasks:  list[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING


class MonarchAgent:
    """Master orchestrator. Plans and delegates to specialist agents."""

    def __init__(self, bus, llm, tools) -> None:
        self._bus   = bus
        self._llm   = llm
        self._tools = tools
        logger.info("Monarch initialized")

    async def handle(self, query: str) -> AsyncIterator[str]:
        """Main entry point — yields streaming response tokens."""
        plan    = await self._plan(query)
        results = await self._execute(plan)
        async for token in self._synthesize(query, results):
            yield token

    async def _plan(self, query: str) -> ExecutionPlan:
        """Decompose query into task DAG (LLM-driven in v0.4)."""
        plan = ExecutionPlan(query=query)
        plan.tasks = [SubTask(agent="executor", tool="shell", inputs={"query": query})]
        return plan

    async def _execute(self, plan: ExecutionPlan) -> dict:
        results: dict = {}
        for task in plan.tasks:
            if task.depends_on:
                await asyncio.gather(*(self._wait(results, d) for d in task.depends_on))
            results[task.id] = await self._bus.delegate(task.agent, task.tool, task.inputs)
        return results

    async def _synthesize(self, query: str, results: dict) -> AsyncIterator[str]:
        context = "\n".join(str(v) for v in results.values())
        prompt  = f"Query: {query}\n\nResults:\n{context}\n\nSynthesize:"
        async for token in self._llm.stream(prompt):
            yield token

    async def _wait(self, results: dict, task_id: str) -> None:
        while task_id not in results:
            await asyncio.sleep(0.05)
