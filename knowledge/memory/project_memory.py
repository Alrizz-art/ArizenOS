"""
Project Memory — scopes knowledge and memory to a specific project context.

Each project gets its own ChromaDB collection prefix and SQLite scope,
so querying "ArizenOS" project memory doesn't pollute results with
unrelated projects.

Features:
  - Per-project knowledge storage (code, decisions, docs, context)
  - Project context summary (auto-generated from stored records)
  - Cross-project knowledge transfer (explicit)
  - Project timeline (ordered record of decisions)
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from knowledge.memory.long_term import LongTermMemory, MemoryRecord, MemoryScope
from knowledge.storage.chroma_store import ChromaStore
from knowledge.storage.sqlite_store import SQLiteStore
from knowledge.processing.embedder import Embedder

logger = logging.getLogger("arizen.memory.project")


@dataclass
class ProjectSummary:
    project:      str
    record_count: int
    topics:       list[str]
    last_updated: float
    decisions:    list[str]   = field(default_factory=list)   # key decision records
    open_tasks:   list[str]   = field(default_factory=list)

    def as_context(self) -> str:
        lines = [
            f"# Project: {self.project}",
            f"Records: {self.record_count} | Updated: {_fmt_ts(self.last_updated)}",
            f"Topics: {', '.join(self.topics[:8])}",
        ]
        if self.decisions:
            lines.append("\n## Key Decisions")
            lines.extend(f"- {d}" for d in self.decisions[:5])
        return "\n".join(lines)


class ProjectMemory:
    """
    Project-scoped memory layer built on top of LongTermMemory.

    Usage:
        pm = ProjectMemory(ltm)
        await pm.store("ArizenOS", "We chose SQLite WAL + ChromaDB dual-write for memory persistence")
        context = await pm.get_context("ArizenOS", "how is memory stored?")
    """

    def __init__(self, ltm: LongTermMemory) -> None:
        self._ltm = ltm

    async def store(
        self,
        project:    str,
        content:    str,
        tags:       list[str] = None,
        source:     str       = "",
        record_type: str      = "knowledge",   # "knowledge" | "decision" | "task" | "error"
        importance: float     = 0.5,
    ) -> str:
        """Store a knowledge record scoped to a project."""
        all_tags = list(set((tags or []) + [project, record_type]))
        return await self._ltm.store(
            content    = content,
            scope      = MemoryScope.PERSISTENT,
            tags       = all_tags,
            source     = source,
            project    = project,
            importance = importance,
        )

    async def query(
        self,
        project: str,
        query:   str,
        limit:   int = 10,
    ) -> list[MemoryRecord]:
        """Retrieve project-scoped memory relevant to a query."""
        return await self._ltm.query(
            query   = query,
            project = project,
            limit   = limit,
        )

    async def get_context(self, project: str, query: str, limit: int = 6) -> str:
        """
        Build a project context string ready for LLM injection.
        Combines a project summary header with the most relevant records.
        """
        records = await self.query(project, query, limit=limit)
        if not records:
            return f"No project memory found for '{project}'."
        lines = [f"## Project Memory: {project}\n"]
        for i, r in enumerate(records, 1):
            tag_str = ", ".join(r.tags[:4]) if r.tags else ""
            lines.append(f"[{i}] {r.content.strip()[:400]}")
            if tag_str:
                lines.append(f"     tags: {tag_str}")
            lines.append("")
        return "\n".join(lines)

    async def summarize(self, project: str) -> ProjectSummary:
        """Build a summary of all stored project memory."""
        records  = await self._ltm.query(project, project, limit=100)
        proj_recs = [r for r in records if project in (r.project or "")]
        topics: list[str] = []
        for r in proj_recs:
            topics.extend(t for t in r.tags if t != project)
        from collections import Counter
        top_topics = [t for t, _ in Counter(topics).most_common(10)]

        decisions = [
            r.content[:100] for r in proj_recs
            if "decision" in r.tags or r.importance >= 0.8
        ][:5]

        last_updated = max((r.created_at for r in proj_recs), default=time.time())
        return ProjectSummary(
            project      = project,
            record_count = len(proj_recs),
            topics       = top_topics,
            last_updated = last_updated,
            decisions    = decisions,
        )

    async def forget_project(self, project: str) -> int:
        """Remove all memory records for a project."""
        return await self._ltm.forget(project=project)


def _fmt_ts(ts: float) -> str:
    from datetime import datetime
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M UTC")
