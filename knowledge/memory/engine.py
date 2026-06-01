"""
Memory Engine — unified interface for all ArizenOS agent memory.

Combines:
  LongTermMemory  — persistent facts, preferences, learned knowledge
  ProjectMemory   — project-scoped context and decisions
  Episodic buffer — recent interaction history (last N turns)

This is the class that agents (primarily Memory agent) call directly.
Commander also calls it before every response to prime context.

Usage:
    engine = MemoryEngine(chroma, sqlite, embedder)

    # Store
    await engine.store("User prefers dark mode", scope="persistent", tags=["preference","ui"])
    await engine.store_project("ArizenOS", "Chose SQLite WAL + ChromaDB dual-write")

    # Query
    records  = await engine.query("user preferences", limit=5)
    ctx_str  = await engine.project_context("ArizenOS", "memory storage design")
    rag_ctx  = await engine.rag_context("how does retry work?")
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from knowledge.memory.long_term import LongTermMemory, MemoryRecord, MemoryScope
from knowledge.memory.project_memory import ProjectMemory, ProjectSummary
from knowledge.storage.chroma_store import ChromaStore
from knowledge.storage.sqlite_store import SQLiteStore
from knowledge.processing.embedder import Embedder
from knowledge.query.rag import MemoryRAGPipeline, RAGContext
from knowledge.query.semantic_search import SemanticSearch

logger = logging.getLogger("arizen.memory.engine")


@dataclass
class InteractionRecord:
    """A single turn in the episodic buffer."""
    id:         str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    role:       str = "user"         # "user" | "agent" | "tool"
    agent:      str = ""
    content:    str = ""
    timestamp:  float = field(default_factory=time.time)
    playbook:   str = ""


class EpisodicBuffer:
    """Ring buffer of recent interaction turns — never persisted to disk."""
    def __init__(self, max_turns: int = 30) -> None:
        self._turns:    list[InteractionRecord] = []
        self._max       = max_turns

    def push(self, record: InteractionRecord) -> None:
        self._turns.append(record)
        if len(self._turns) > self._max:
            self._turns = self._turns[-self._max:]

    def recent(self, n: int = 10) -> list[InteractionRecord]:
        return self._turns[-n:]

    def as_context(self, n: int = 6) -> str:
        turns = self.recent(n)
        if not turns:
            return ""
        lines = ["## Recent Interactions"]
        for t in turns:
            ts = time.strftime("%H:%M", time.localtime(t.timestamp))
            lines.append(f"[{ts}] {t.role.upper()} ({t.agent}): {t.content[:200]}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._turns.clear()


class MemoryEngine:
    """
    PRIMARY MEMORY INTERFACE for ArizenOS agents.

    All agent memory operations flow through here. The Memory agent is
    the exclusive owner; other agents call it via the message bus.
    """

    def __init__(
        self,
        chroma:   ChromaStore,
        sqlite:   SQLiteStore,
        embedder: Embedder,
        episodic_turns: int = 30,
    ) -> None:
        self._ltm      = LongTermMemory(chroma, sqlite, embedder)
        self._projects = ProjectMemory(self._ltm)
        self._episodic = EpisodicBuffer(max_turns=episodic_turns)
        self._search   = SemanticSearch(chroma, sqlite, embedder)
        self._rag      = MemoryRAGPipeline(self._search)

    # ── Store ─────────────────────────────────────────────────────

    async def store(
        self,
        content:    str,
        scope:      str         = "persistent",
        tags:       list[str]   = None,
        source:     str         = "",
        project:    str         = "",
        importance: float       = 0.5,
        ttl_sec:    int         = -1,
    ) -> str:
        """Store a memory record. Returns record ID."""
        try:
            mem_scope = MemoryScope(scope)
        except ValueError:
            mem_scope = MemoryScope.PERSISTENT
        return await self._ltm.store(
            content=content, scope=mem_scope, tags=tags,
            source=source, project=project,
            importance=importance, ttl_sec=ttl_sec,
        )

    async def store_project(
        self,
        project:    str,
        content:    str,
        tags:       list[str]   = None,
        source:     str         = "",
        record_type: str        = "knowledge",
        importance: float       = 0.5,
    ) -> str:
        """Store a knowledge record scoped to a project."""
        return await self._projects.store(
            project=project, content=content, tags=tags,
            source=source, record_type=record_type, importance=importance,
        )

    def push_interaction(
        self,
        role:    str,
        content: str,
        agent:   str   = "",
        playbook: str  = "",
    ) -> None:
        """Record an interaction turn in the episodic buffer (in-memory only)."""
        self._episodic.push(InteractionRecord(
            role=role, agent=agent, content=content, playbook=playbook
        ))

    # ── Query ─────────────────────────────────────────────────────

    async def query(
        self,
        query:   str,
        scope:   Optional[str]  = None,
        project: Optional[str]  = None,
        limit:   int            = 10,
    ) -> list[MemoryRecord]:
        """Query long-term memory by semantic + keyword search."""
        scope_enum = MemoryScope(scope) if scope else None
        return await self._ltm.query(
            query=query, scope=scope_enum, project=project, limit=limit
        )

    async def project_context(self, project: str, query: str, limit: int = 6) -> str:
        """Return project memory as a formatted context string for LLM."""
        return await self._projects.get_context(project, query, limit=limit)

    async def rag_context(self, query: str, source: Optional[str] = None) -> RAGContext:
        """Build a RAG context block from memory for the given query."""
        return await self._rag.build_context(query=query, source=source)

    def episodic_context(self, n: int = 6) -> str:
        """Return recent interaction history as a context string."""
        return self._episodic.as_context(n)

    async def project_summary(self, project: str) -> ProjectSummary:
        return await self._projects.summarize(project)

    # ── Maintenance ───────────────────────────────────────────────

    async def forget(
        self,
        scope:          Optional[str] = None,
        project:        Optional[str] = None,
        older_than_sec: int           = 0,
    ) -> int:
        scope_enum = MemoryScope(scope) if scope else None
        return await self._ltm.forget(
            scope=scope_enum, project=project, older_than_sec=older_than_sec
        )

    async def stats(self) -> dict[str, Any]:
        sqlite_stats = self._ltm._sqlite.stats()
        return {
            "long_term":    sqlite_stats.get("memory_by_scope", {}),
            "episodic":     len(self._episodic._turns),
            "projects":     {},
        }
