"""
Task Queue — priority-aware, concurrency-limited async queue for playbook steps.

Features:
  - Priority ordering (higher runs first within a wave)
  - Concurrency cap per agent (prevents agent saturation)
  - Graceful drain with timeout
  - Backpressure signalling
"""
from __future__ import annotations

import asyncio
import heapq
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger("arizen.playbook.queue")


@dataclass(order=True)
class QueueItem:
    priority:    int                           # lower = runs first in heapq (negate actual priority)
    enqueued_at: float = field(compare=False)
    step_id:     str   = field(compare=False, default="")
    agent:       str   = field(compare=False, default="")
    fn:          Any   = field(compare=False, default=None)  # async callable
    args:        tuple = field(compare=False, default_factory=tuple)
    kwargs:      dict  = field(compare=False, default_factory=dict)


@dataclass
class QueueStats:
    enqueued:  int   = 0
    dequeued:  int   = 0
    completed: int   = 0
    failed:    int   = 0
    wait_ms:   float = 0.0   # average wait time


class PlaybookTaskQueue:
    """
    Priority-based async task queue for playbook step execution.

    Concurrency limits are enforced per agent name to prevent any single
    agent from being overwhelmed while others idle.

    Usage:
        queue = PlaybookTaskQueue(max_concurrency=8, per_agent_limit=2)
        await queue.enqueue(step, fn=executor.run_step, args=(step, ctx))
        results = await queue.drain(timeout=300)
    """

    def __init__(
        self,
        max_concurrency: int = 8,
        per_agent_limit: int = 2,
    ) -> None:
        self._heap: list[QueueItem]           = []
        self._lock                            = asyncio.Lock()
        self._semaphore                       = asyncio.Semaphore(max_concurrency)
        self._agent_semaphores: dict[str, asyncio.Semaphore] = {}
        self._per_agent_limit                 = per_agent_limit
        self._running: dict[str, asyncio.Task]= {}
        self._results: dict[str, Any]         = {}
        self._stats                           = QueueStats()

    # ------------------------------------------------------------------
    # Enqueue
    # ------------------------------------------------------------------

    async def enqueue(
        self,
        step_id:  str,
        agent:    str,
        fn:       Callable[..., Coroutine],
        args:     tuple = (),
        kwargs:   dict  = None,
        priority: int   = 5,
    ) -> None:
        item = QueueItem(
            priority    = -priority,   # heapq is min-heap; negate for max-priority-first
            enqueued_at = time.monotonic(),
            step_id     = step_id,
            agent       = agent,
            fn          = fn,
            args        = args,
            kwargs      = kwargs or {},
        )
        async with self._lock:
            heapq.heappush(self._heap, item)
            self._stats.enqueued += 1
        logger.debug("Enqueued step '%s' (priority=%d, agent=%s)", step_id, priority, agent)

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------

    async def execute_wave(self, timeout: float = 300.0) -> dict[str, Any]:
        """
        Execute all currently queued items concurrently, respecting limits.
        Returns {step_id: result} for this wave.
        """
        tasks: list[asyncio.Task] = []
        async with self._lock:
            items, self._heap = list(self._heap), []

        for item in sorted(items):   # already sorted by heapq priority
            task = asyncio.create_task(self._run_item(item), name=item.step_id)
            tasks.append(task)
            self._running[item.step_id] = task

        if tasks:
            await asyncio.wait(tasks, timeout=timeout)

        wave_results: dict[str, Any] = {}
        for item in items:
            wave_results[item.step_id] = self._results.pop(item.step_id, None)
            self._running.pop(item.step_id, None)

        return wave_results

    async def _run_item(self, item: QueueItem) -> None:
        agent_sem = self._get_agent_sem(item.agent)
        async with self._semaphore:
            async with agent_sem:
                wait_ms = (time.monotonic() - item.enqueued_at) * 1000
                self._stats.wait_ms = (self._stats.wait_ms + wait_ms) / 2
                self._stats.dequeued += 1
                try:
                    result = await item.fn(*item.args, **item.kwargs)
                    self._results[item.step_id] = result
                    self._stats.completed += 1
                except Exception as exc:
                    self._results[item.step_id] = {"error": str(exc)}
                    self._stats.failed += 1
                    logger.error("Queue item '%s' failed: %s", item.step_id, exc)

    def _get_agent_sem(self, agent: str) -> asyncio.Semaphore:
        if agent not in self._agent_semaphores:
            self._agent_semaphores[agent] = asyncio.Semaphore(self._per_agent_limit)
        return self._agent_semaphores[agent]

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    async def cancel_all(self) -> None:
        for task in self._running.values():
            task.cancel()
        if self._running:
            await asyncio.gather(*self._running.values(), return_exceptions=True)
        self._running.clear()

    @property
    def stats(self) -> QueueStats:
        return self._stats

    @property
    def depth(self) -> int:
        return len(self._heap)
