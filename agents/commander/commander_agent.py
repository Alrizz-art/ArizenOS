"""
Arizen Commander — Master Orchestrator for the ArizenOS Agent Ecosystem.

Commander is the single point of authority over all specialist agents.
It receives raw user intent, decomposes it into a typed execution plan (DAG),
dispatches sub-tasks to the appropriate agents, tracks progress, and
synthesizes the final response stream.

No specialist agent is ever called directly by the user — all traffic
flows through Commander.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Optional
from uuid import uuid4

from agents._base.base_agent import AgentContext, AgentManifest, BaseAgent
from agents._base.tool_registry import tool

logger = logging.getLogger("arizen.commander")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AgentName(str, Enum):
    COMMANDER  = "commander"
    CODER      = "coder"
    RESEARCHER = "researcher"
    FIXER      = "fixer"
    DEVOPS     = "devops"
    SECURITY   = "security"
    DESIGNER   = "designer"
    MEMORY     = "memory"


class TaskType(str, Enum):
    """Canonical intent classes Commander can classify a user request into."""
    CODE_GENERATE     = "code.generate"
    CODE_REVIEW       = "code.review"
    CODE_REFACTOR     = "code.refactor"
    DEBUG_ERROR       = "debug.error"
    DEBUG_EXPLAIN     = "debug.explain"
    RESEARCH_WEB      = "research.web"
    RESEARCH_DOCS     = "research.docs"
    DEVOPS_BUILD      = "devops.build"
    DEVOPS_DEPLOY     = "devops.deploy"
    DEVOPS_MONITOR    = "devops.monitor"
    SECURITY_SCAN     = "security.scan"
    SECURITY_AUDIT    = "security.audit"
    DESIGN_COMPONENT  = "design.component"
    DESIGN_THEME      = "design.theme"
    MEMORY_STORE      = "memory.store"
    MEMORY_QUERY      = "memory.query"
    COMPOSITE         = "composite"      # requires multiple agents


class SubTaskStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    WAITING  = "waiting"
    COMPLETE = "complete"
    FAILED   = "failed"
    SKIPPED  = "skipped"


class ApprovalLevel(str, Enum):
    NONE         = "none"         # auto-execute
    LOG_ONLY     = "log_only"     # execute + audit log
    NOTIFY       = "notify"       # execute + HUD notification
    CONFIRM      = "confirm"      # requires user confirmation
    BLOCK        = "block"        # never execute


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SubTask:
    """A single node in the execution DAG."""
    id:             str             = field(default_factory=lambda: str(uuid4()))
    task_type:      TaskType        = TaskType.MEMORY_QUERY
    agent:          AgentName       = AgentName.MEMORY
    tool:           str             = ""
    inputs:         dict            = field(default_factory=dict)
    depends_on:     list[str]       = field(default_factory=list)     # task IDs
    approval:       ApprovalLevel   = ApprovalLevel.NONE
    timeout_sec:    int             = 30
    status:         SubTaskStatus   = SubTaskStatus.PENDING
    output:         Optional[dict]  = None
    error:          Optional[str]   = None


@dataclass
class ExecutionPlan:
    """Full DAG for a single user request."""
    id:          str             = field(default_factory=lambda: str(uuid4()))
    query:       str             = ""
    intent:      TaskType        = TaskType.COMPOSITE
    tasks:       list[SubTask]   = field(default_factory=list)
    status:      SubTaskStatus   = SubTaskStatus.PENDING
    context:     dict            = field(default_factory=dict)  # injected from Memory


@dataclass
class CommanderMessage:
    """
    Typed envelope for all Commander ↔ agent communication.
    Serialised as MessagePack over the named pipe bus.
    """
    message_id:  str   = field(default_factory=lambda: str(uuid4()))
    source:      str   = AgentName.COMMANDER
    target:      str   = ""
    msg_type:    str   = ""    # TASK_REQUEST | TASK_RESULT | STATUS | EMERGENCY_STOP
    payload:     dict  = field(default_factory=dict)
    correlation: str   = ""    # links result back to SubTask.id


# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------

INTENT_ROUTING: dict[TaskType, AgentName] = {
    TaskType.CODE_GENERATE:   AgentName.CODER,
    TaskType.CODE_REVIEW:     AgentName.CODER,
    TaskType.CODE_REFACTOR:   AgentName.CODER,
    TaskType.DEBUG_ERROR:     AgentName.FIXER,
    TaskType.DEBUG_EXPLAIN:   AgentName.FIXER,
    TaskType.RESEARCH_WEB:    AgentName.RESEARCHER,
    TaskType.RESEARCH_DOCS:   AgentName.RESEARCHER,
    TaskType.DEVOPS_BUILD:    AgentName.DEVOPS,
    TaskType.DEVOPS_DEPLOY:   AgentName.DEVOPS,
    TaskType.DEVOPS_MONITOR:  AgentName.DEVOPS,
    TaskType.SECURITY_SCAN:   AgentName.SECURITY,
    TaskType.SECURITY_AUDIT:  AgentName.SECURITY,
    TaskType.DESIGN_COMPONENT:AgentName.DESIGNER,
    TaskType.DESIGN_THEME:    AgentName.DESIGNER,
    TaskType.MEMORY_STORE:    AgentName.MEMORY,
    TaskType.MEMORY_QUERY:    AgentName.MEMORY,
}

# Actions that always require explicit approval before execution
APPROVAL_REQUIRED: set[str] = {
    "filesystem.delete",
    "filesystem.move",
    "devops.deploy",
    "devops.service.restart",
    "security.quarantine",
    "shell.execute_arbitrary",
}


# ---------------------------------------------------------------------------
# Commander Agent
# ---------------------------------------------------------------------------

class CommanderAgent(BaseAgent):
    """
    Arizen Commander — orchestrates all specialist agents.

    Execution model:
        1. Classify user intent → TaskType
        2. Enrich context from Memory (always)
        3. Build ExecutionPlan (DAG of SubTasks)
        4. Check approval gates; prompt user if required
        5. Execute DAG respecting dependency order + parallelism
        6. Synthesize results → streaming response
        7. Commit outcome to Memory
    """

    MANIFEST = AgentManifest(
        name="commander",
        display="Arizen Commander",
        version="1.0.0",
        tier=3,
        tools=[
            "bus.delegate",
            "bus.broadcast",
            "bus.emergency_stop",
            "plan.classify",
            "plan.build_dag",
            "plan.approve",
            "agent.list",
            "agent.health_check",
        ],
        memory_scopes=["session", "persistent"],
        fs_access=False,
        net_access=False,
        llm_tier="power",
        autostart=True,
        max_restart=10,
    )

    def __init__(self, ctx: AgentContext, bus, llm) -> None:
        super().__init__(ctx)
        self._bus = bus
        self._llm = llm

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def handle(self, task: dict) -> AsyncIterator[str]:
        """
        Main entry point — receives raw task dict from the daemon.
        Yields streaming response tokens back to the Nexus UI.
        """
        query = task.get("query", "")
        logger.info("Commander received: %r", query[:120])

        # 1. Retrieve session context from Memory
        context = await self._fetch_context(query)

        # 2. Classify intent
        intent = await self._classify(query, context)
        logger.info("Classified as: %s", intent)

        # 3. Build execution plan
        plan = await self._build_plan(query, intent, context)

        # 4. Approval gate
        plan = await self._approval_gate(plan)

        # 5. Execute DAG
        results = await self._execute_dag(plan)

        # 6. Synthesize
        async for token in self._synthesize(query, intent, results, context):
            yield token

        # 7. Commit to memory
        asyncio.create_task(self._commit_memory(query, intent, results))

    # ------------------------------------------------------------------
    # Step implementations
    # ------------------------------------------------------------------

    async def _fetch_context(self, query: str) -> dict:
        """Pull relevant memory context before planning."""
        try:
            return await self._bus.delegate(
                AgentName.MEMORY, "memory.context_for_query",
                {"query": query, "limit": 5}
            )
        except Exception as exc:
            logger.warning("Memory context fetch failed: %s", exc)
            return {}

    async def _classify(self, query: str, context: dict) -> TaskType:
        """Use LLM to classify query into a TaskType."""
        type_names = [t.value for t in TaskType]
        prompt = (
            f"Classify this user request into exactly one category.\n"
            f"Categories: {', '.join(type_names)}\n"
            f"Request: {query}\n"
            f"Context keys: {list(context.keys())}\n"
            f"Reply with just the category name."
        )
        raw = await self._llm.complete(prompt, tier="nano")
        raw = raw.strip().lower()
        for t in TaskType:
            if t.value in raw:
                return t
        return TaskType.COMPOSITE

    async def _build_plan(
        self, query: str, intent: TaskType, context: dict
    ) -> ExecutionPlan:
        """Decompose request into DAG of SubTasks."""
        plan = ExecutionPlan(query=query, intent=intent, context=context)

        if intent == TaskType.COMPOSITE:
            plan.tasks = await self._plan_composite(query, context)
        else:
            agent = INTENT_ROUTING.get(intent, AgentName.MEMORY)
            plan.tasks = [
                SubTask(
                    task_type=intent,
                    agent=agent,
                    tool=intent.value,
                    inputs={"query": query, "context": context},
                    approval=self._approval_for(intent.value),
                )
            ]

        logger.info("Plan built: %d task(s)", len(plan.tasks))
        return plan

    async def _plan_composite(self, query: str, context: dict) -> list[SubTask]:
        """LLM-driven multi-agent plan for complex requests."""
        prompt = (
            "You are a planning engine. Decompose this request into a list of "
            "agent sub-tasks. Return JSON: [{agent, tool, inputs, depends_on}].\n"
            f"Available agents: {[a.value for a in AgentName if a != AgentName.COMMANDER]}\n"
            f"Request: {query}"
        )
        raw = await self._llm.complete(prompt, tier="standard")
        import json
        try:
            steps = json.loads(raw)
            tasks = []
            id_map: dict[int, str] = {}
            for i, step in enumerate(steps):
                t = SubTask(
                    agent=AgentName(step.get("agent", "memory")),
                    tool=step.get("tool", ""),
                    inputs={**step.get("inputs", {}), "context": context},
                    depends_on=[id_map[d] for d in step.get("depends_on", []) if d in id_map],
                    approval=self._approval_for(step.get("tool", "")),
                )
                id_map[i] = t.id
                tasks.append(t)
            return tasks
        except Exception as exc:
            logger.error("Composite plan parse failed: %s", exc)
            return []

    def _approval_for(self, tool_name: str) -> ApprovalLevel:
        if tool_name in APPROVAL_REQUIRED:
            return ApprovalLevel.CONFIRM
        return ApprovalLevel.NONE

    async def _approval_gate(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Pause plan execution if any task requires user confirmation."""
        for task in plan.tasks:
            if task.approval == ApprovalLevel.CONFIRM:
                approved = await self._bus.request_approval(task)
                if not approved:
                    task.status = SubTaskStatus.SKIPPED
                    logger.info("Task %s skipped by user", task.id)
        return plan

    async def _execute_dag(self, plan: ExecutionPlan) -> dict[str, dict]:
        """Execute SubTasks in dependency order, running independents in parallel."""
        plan.status = SubTaskStatus.RUNNING
        results: dict[str, dict] = {}
        pending = list(plan.tasks)

        while pending:
            ready = [
                t for t in pending
                if t.status == SubTaskStatus.PENDING
                and all(results.get(dep) is not None for dep in t.depends_on)
                and t.status != SubTaskStatus.SKIPPED
            ]

            if not ready:
                await asyncio.sleep(0.05)
                if all(t.status in (SubTaskStatus.COMPLETE, SubTaskStatus.FAILED,
                                    SubTaskStatus.SKIPPED) for t in pending):
                    break
                continue

            # Launch ready tasks in parallel
            async def run(subtask: SubTask) -> None:
                subtask.status = SubTaskStatus.RUNNING
                try:
                    result = await asyncio.wait_for(
                        self._bus.delegate(subtask.agent, subtask.tool, subtask.inputs),
                        timeout=subtask.timeout_sec,
                    )
                    subtask.output = result
                    subtask.status = SubTaskStatus.COMPLETE
                    results[subtask.id] = result
                except Exception as exc:
                    subtask.error = str(exc)
                    subtask.status = SubTaskStatus.FAILED
                    results[subtask.id] = {"error": str(exc)}
                    logger.error("SubTask %s failed: %s", subtask.id, exc)

            await asyncio.gather(*(run(t) for t in ready))
            for t in ready:
                pending.remove(t)

        plan.status = SubTaskStatus.COMPLETE
        return results

    async def _synthesize(
        self, query: str, intent: TaskType, results: dict, context: dict
    ) -> AsyncIterator[str]:
        """Stream a final response synthesized from all agent outputs."""
        summary = "\n\n".join(
            f"[{k}]: {v}" for k, v in results.items() if not isinstance(v, dict) or "error" not in v
        )
        prompt = (
            f"User request: {query}\n"
            f"Intent: {intent.value}\n"
            f"Agent results:\n{summary}\n\n"
            "Provide a clear, direct response. Cite sources if relevant."
        )
        async for token in self._llm.stream(prompt, tier="standard"):
            yield token

    async def _commit_memory(self, query: str, intent: TaskType, results: dict) -> None:
        """Persist this interaction to Memory for future context."""
        try:
            await self._bus.delegate(
                AgentName.MEMORY, "memory.store_interaction",
                {"query": query, "intent": intent.value, "results": results}
            )
        except Exception as exc:
            logger.warning("Memory commit failed: %s", exc)

    # ------------------------------------------------------------------
    # Emergency controls
    # ------------------------------------------------------------------

    @tool(name="bus.emergency_stop", side_effects="system", requires_approval=False)
    async def emergency_stop(self) -> None:
        """Immediately halt all running agent tasks. Bound to hotkey."""
        logger.warning("EMERGENCY STOP triggered by Commander")
        await self._bus.broadcast({"msg_type": "EMERGENCY_STOP"})
        self._running = False
