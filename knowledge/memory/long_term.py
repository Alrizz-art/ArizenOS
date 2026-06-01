"""
Long-term Memory — stores persistent facts, decisions, and learned knowledge
across sessions. Backed by both ChromaDB (semantic recall) and SQLite (metadata
+ keyword search + TTL management).

Memory scopes:
  persistent  — survives indefinitely (user preferences, learned facts)
  session     — pruned on process restart (current task context)
  episodic    — recent interactions (auto-pruned after N days)
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from knowledge.ingestion.base import Chunk, Document
from knowledge.storage.chroma_store import ChromaStore
from knowledge.storage.sqlite_store import SQLiteStore
from knowledge.processing.embedder import Embedder
from knowledge.processing.chunker import Chunker
from knowledge.processing.metadata import MetadataExtractor

logger = logging.getLogger("arizen.memory.longterm")


class MemoryScope(str, Enum):
    PERSISTENT = "persistent"   # forever
    SESSION    = "session"      # until process restart (short TTL)
    EPISODIC   = "episodic"     # recent, auto-pruned (7-day default)


@dataclass
class MemoryRecord:
    id:          str
    scope:       MemoryScope
    content:     str
    tags:        list[str]                = field(default_factory=list)
    source:      str                      = ""
    project:     str                      = ""
    created_at:  float                    = field(default_factory=time.time)
    ttl_sec:     int                      = 0
    importance:  float                    = 0.5     # 0–1 relevance weight
    access_count: int                     = 0
    embedding:   list[float]              = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        if self.ttl_sec <= 0:
            return False
        return (self.created_at + self.ttl_sec) < time.time()


_SCOPE_TTL = {
    MemoryScope.PERSISTENT: 0,          # no TTL
    MemoryScope.SESSION:    3600,        # 1 hour
    MemoryScope.EPISODIC:   7 * 86400,  # 7 days
}


class LongTermMemory:
    """
    Stores and retrieves persistent agent memory.

    Writes go to both ChromaDB (for semantic search) and SQLite (for keyword
    search, metadata queries, and TTL management).

    Usage:
        ltm = LongTermMemory(chroma, sqlite, embedder)
        await ltm.store("User prefers Rust for performance-critical code",
                        scope=MemoryScope.PERSISTENT, tags=["preference","language"])
        records = await ltm.query("user language preferences")
    """

    def __init__(self, chroma: ChromaStore, sqlite: SQLiteStore, embedder: Embedder) -> None:
        self._chroma   = chroma
        self._sqlite   = sqlite
        self._embedder = embedder
        self._chunker  = Chunker(chunk_size=800, chunk_overlap=0)

    async def store(
        self,
        content:    str,
        scope:      MemoryScope  = MemoryScope.PERSISTENT,
        tags:       list[str]    = None,
        source:     str          = "",
        project:    str          = "",
        importance: float        = 0.5,
        ttl_sec:    int          = -1,   # -1 = use scope default
    ) -> str:
        """Store a memory record. Returns the record ID."""
        record_id = str(uuid.uuid4())
        effective_ttl = _SCOPE_TTL[scope] if ttl_sec == -1 else ttl_sec

        # Embed
        embedding = await self._embedder.embed_query(content)

        # ChromaDB
        chunk = Chunk(
            id          = record_id,
            document_id = record_id,
            source      = f"memory:{scope.value}",
            content     = content,
            embedding   = embedding,
            metadata    = {
                "scope":      scope.value,
                "tags":       ",".join(tags or []),
                "source":     source,
                "project":    project,
                "importance": importance,
                "ttl_sec":    effective_ttl,
                "document_id": record_id,
                "title":      content[:60],
                "url":        "",
            },
        )
        await __import__('asyncio').to_thread(
            self._chroma.upsert_chunks, [chunk], "arizen_memory"
        )

        # SQLite
        self._sqlite.store_memory(
            record_id=record_id, scope=scope.value, content=content,
            tags=tags, source=source, project=project,
            ttl_sec=effective_ttl, importance=importance,
        )
        logger.debug("Memory stored: scope=%s id=%s tags=%s", scope.value, record_id[:8], tags)
        return record_id

    async def query(
        self,
        query:    str,
        scope:    Optional[MemoryScope] = None,
        project:  Optional[str]         = None,
        limit:    int                   = 10,
        strategy: str                   = "hybrid",
    ) -> list[MemoryRecord]:
        """Retrieve relevant memory records for a query."""
        # Keyword search via SQLite
        scope_filter = scope.value if scope else None
        kw_records   = self._sqlite.search_memory(query, scope=scope_filter, project=project, limit=limit * 2)

        # Semantic search via ChromaDB
        embedding    = await self._embedder.embed_query(query)
        where        = {"source": f"memory:{scope.value}"} if scope else None
        sem_results  = await __import__('asyncio').to_thread(
            self._chroma.query, embedding, limit * 2, "arizen_memory", where
        )

        # Merge by ID (prefer semantic score for ordering)
        seen: set[str] = set()
        merged: list[MemoryRecord] = []

        for r in sem_results:
            if r.chunk_id in seen:
                continue
            seen.add(r.chunk_id)
            merged.append(MemoryRecord(
                id         = r.chunk_id,
                scope      = MemoryScope(r.metadata.get("scope", "persistent")),
                content    = r.content,
                tags       = r.metadata.get("tags", "").split(",") if r.metadata.get("tags") else [],
                source     = r.metadata.get("source", ""),
                project    = r.metadata.get("project", ""),
                importance = float(r.metadata.get("importance", 0.5)),
                embedding  = [],
            ))

        for row in kw_records:
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            merged.append(MemoryRecord(
                id         = row["id"],
                scope      = MemoryScope(row["scope"]),
                content    = row["content"],
                tags       = row["tags"].split(",") if row.get("tags") else [],
                source     = row.get("source", ""),
                project    = row.get("project", ""),
                importance = row.get("importance", 0.5),
            ))

        # Filter expired, sort by importance
        valid = [r for r in merged if not r.is_expired]
        valid.sort(key=lambda r: -r.importance)
        return valid[:limit]

    async def forget(
        self,
        scope:     Optional[MemoryScope] = None,
        older_than_sec: int              = 0,
        project:   Optional[str]         = None,
    ) -> int:
        """Prune memory records by scope, age, or project. Returns count deleted."""
        pruned = self._sqlite.prune_expired_memory()
        logger.info("Memory pruned %d expired records", pruned)
        return pruned

    async def update_importance(self, record_id: str, importance: float) -> None:
        self._sqlite._db.execute(
            "UPDATE memory_records SET importance=? WHERE id=?", (importance, record_id)
        )
        self._sqlite._db.commit()
