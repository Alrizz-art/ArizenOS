"""
Arizen Memory — Knowledge Ingestion, Retrieval, and Session Context Agent.

Memory is the persistence layer of the ArizenOS agent ecosystem. It
maintains three memory scopes:
  - Working  : in-process dict (cleared on restart)
  - Session  : SQLite rows for the current user session
  - Persistent: ChromaDB vectors + SQLite FTS for long-term knowledge

Every other agent delegates to Memory for context enrichment and
result persistence. Memory never calls other agents.

All invocations come from Commander.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncIterator, Optional
from uuid import uuid4

from agents._base.base_agent import AgentContext, AgentManifest, BaseAgent
from agents._base.tool_registry import tool

logger = logging.getLogger("arizen.memory")


class MemoryScope(str, Enum):
    WORKING    = "working"     # RAM only
    SESSION    = "session"     # SQLite, current session
    PERSISTENT = "persistent"  # ChromaDB + SQLite FTS, cross-session


@dataclass
class MemoryEntry:
    id:         str             = field(default_factory=lambda: str(uuid4()))
    scope:      MemoryScope     = MemoryScope.SESSION
    content:    str             = ""
    metadata:   dict            = field(default_factory=dict)
    embedding:  Optional[list]  = None
    created_at: float           = field(default_factory=time.time)
    source:     str             = ""    # agent name that stored this
    tags:       list[str]       = field(default_factory=list)


@dataclass
class QueryResult:
    entry:    MemoryEntry = field(default_factory=MemoryEntry)
    score:    float       = 0.0
    scope:    str         = ""


class MemoryAgent(BaseAgent):
    """
    Arizen Memory — manages all knowledge scopes for the agent ecosystem.

    Execution model:
        1. Route action (store | query | context_for_query | store_interaction | compress | forget)
        2. For store: embed content → ChromaDB + SQLite FTS
        3. For query: hybrid search (vector + keyword) → rerank → return top-k
        4. For context_for_query: fast pre-flight to enrich Commander's planning
        5. Periodic compression: merge session entries into long-term memory
    """

    MANIFEST = AgentManifest(
        name="memory",
        display="Arizen Memory",
        version="1.0.0",
        tier=1,
        tools=[
            "memory.store",
            "memory.query",
            "memory.semantic_search",
            "memory.context_for_query",
            "memory.store_interaction",
            "memory.compress_session",
            "memory.forget",
            "filesystem.read",
            "filesystem.walk",
        ],
        memory_scopes=["working", "session", "persistent"],
        fs_access=True,
        net_access=False,
        llm_tier="nano",
        autostart=True,
        max_restart=10,
    )

    FS_ALLOWLIST: list[str] = [
        "memory/",
        "knowledge/",
        "docs/",
        "agents/",
        "core/",
        "playbooks/",
    ]

    # Paths
    SQLITE_PATH: str = "memory/persistent/arizen_memory.db"
    CHROMA_PATH: str = "memory/persistent/chroma"
    SESSION_PATH: str = "memory/session/session_store.py"

    CHUNK_SIZE:    int = 512    # tokens per chunk
    CHUNK_OVERLAP: int = 64
    TOP_K:         int = 5

    def __init__(self, ctx: AgentContext, bus, llm, embedder, db, chroma) -> None:
        super().__init__(ctx)
        self._bus     = bus
        self._llm     = llm
        self._embed   = embedder
        self._db      = db
        self._chroma  = chroma
        self._working: dict[str, MemoryEntry] = {}

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action = task.get("tool", "memory.query").split(".")[-1]
        dispatch = {
            "store":              self._store,
            "query":              self._query,
            "semantic_search":    self._semantic_search,
            "context_for_query":  self._context_for_query,
            "store_interaction":  self._store_interaction,
            "compress_session":   self._compress_session,
            "forget":             self._forget,
        }
        handler = dispatch.get(action, self._query)
        result  = await handler(task)
        yield str(result)

    # ------------------------------------------------------------------
    # Store
    # ------------------------------------------------------------------

    @tool(name="memory.store", side_effects="write")
    async def _store(self, task: dict) -> dict:
        content  = task.get("content", "")
        scope    = MemoryScope(task.get("scope", "session"))
        metadata = task.get("metadata", {})
        source   = task.get("source", "unknown")
        tags     = task.get("tags", [])

        entry = MemoryEntry(
            scope=scope, content=content,
            metadata=metadata, source=source, tags=tags
        )

        if scope == MemoryScope.WORKING:
            self._working[entry.id] = entry

        elif scope == MemoryScope.SESSION:
            await self._db.execute(
                "INSERT INTO session_memory (id, content, metadata, source, tags, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (entry.id, content, str(metadata), source, str(tags), entry.created_at)
            )

        else:  # persistent
            chunks = self._chunk(content)
            for i, chunk in enumerate(chunks):
                embedding = await self._embed.embed(chunk)
                await self._chroma.add(
                    ids=[f"{entry.id}-{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": source, "tags": str(tags), **metadata}]
                )
                await self._db.execute(
                    "INSERT INTO persistent_memory (id, content, source, created_at) VALUES (?, ?, ?, ?)",
                    (f"{entry.id}-{i}", chunk, source, entry.created_at)
                )

        logger.debug("Memory stored [%s] %s chars from %s", scope.value, len(content), source)
        return {"id": entry.id, "scope": scope.value}

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @tool(name="memory.query", side_effects="read_only")
    async def _query(self, task: dict) -> list[dict]:
        query = task.get("query", "")
        limit = int(task.get("limit", self.TOP_K))
        scope = task.get("scope", "all")

        results: list[QueryResult] = []

        if scope in ("working", "all"):
            for entry in self._working.values():
                if query.lower() in entry.content.lower():
                    results.append(QueryResult(entry=entry, score=0.9, scope="working"))

        if scope in ("session", "all"):
            rows = await self._db.fetchall(
                "SELECT id, content, source, created_at FROM session_memory "
                "WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            for row in rows:
                e = MemoryEntry(id=row[0], content=row[1], source=row[2], created_at=row[3])
                results.append(QueryResult(entry=e, score=0.7, scope="session"))

        if scope in ("persistent", "all"):
            sem = await self._semantic_search({"query": query, "limit": limit})
            results.extend(sem)

        results.sort(key=lambda r: r.score, reverse=True)
        return [{"content": r.entry.content, "score": r.score, "scope": r.scope, "source": r.entry.source}
                for r in results[:limit]]

    @tool(name="memory.semantic_search", side_effects="read_only")
    async def _semantic_search(self, task: dict) -> list[QueryResult]:
        query = task.get("query", "")
        limit = int(task.get("limit", self.TOP_K))
        try:
            embedding = await self._embed.embed(query)
            raw = await self._chroma.query(
                query_embeddings=[embedding],
                n_results=limit,
                include=["documents", "distances", "metadatas"]
            )
            results = []
            for doc, dist, meta in zip(
                raw["documents"][0], raw["distances"][0], raw["metadatas"][0]
            ):
                score = max(0.0, 1.0 - dist)
                e = MemoryEntry(content=doc, source=meta.get("source",""), metadata=meta)
                results.append(QueryResult(entry=e, score=score, scope="persistent"))
            return results
        except Exception as exc:
            logger.warning("Semantic search failed: %s", exc)
            return []

    @tool(name="memory.context_for_query", side_effects="read_only")
    async def _context_for_query(self, task: dict) -> dict:
        """Fast context enrichment for Commander's planning phase."""
        query = task.get("query", "")
        limit = int(task.get("limit", 3))
        hits  = await self._query({"query": query, "limit": limit, "scope": "all"})
        return {
            "relevant_memory": hits,
            "session_summary": await self._session_summary(),
        }

    # ------------------------------------------------------------------
    # Interaction persistence
    # ------------------------------------------------------------------

    @tool(name="memory.store_interaction", side_effects="write")
    async def _store_interaction(self, task: dict) -> dict:
        query   = task.get("query", "")
        intent  = task.get("intent", "")
        results = task.get("results", {})
        content = f"Query: {query}\nIntent: {intent}\nResults: {str(results)[:500]}"
        return await self._store({
            "content": content,
            "scope": "persistent",
            "source": "commander",
            "tags": ["interaction", intent],
        })

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    @tool(name="memory.compress_session", side_effects="write")
    async def _compress_session(self, task: dict) -> dict:
        """Summarize old session entries → persistent memory. Called nightly."""
        rows = await self._db.fetchall(
            "SELECT content FROM session_memory ORDER BY created_at ASC LIMIT 100", ()
        )
        if not rows:
            return {"compressed": 0}
        combined = "\n".join(r[0] for r in rows)
        summary  = await self._llm.complete(
            f"Summarize these memory entries into key facts (max 200 words):\n{combined}",
            tier="nano"
        )
        await self._store({"content": summary, "scope": "persistent", "source": "memory.compress", "tags": ["summary"]})
        await self._db.execute("DELETE FROM session_memory WHERE created_at < ?", (time.time() - 86400,))
        return {"compressed": len(rows)}

    @tool(name="memory.forget", side_effects="destructive", requires_approval=True)
    async def _forget(self, task: dict) -> dict:
        """Remove entries matching tags or source. Requires user approval."""
        tags   = task.get("tags", [])
        source = task.get("source", "")
        count  = 0
        if source:
            r = await self._db.execute("DELETE FROM persistent_memory WHERE source = ?", (source,))
            count += r.rowcount
        logger.info("Memory forgot %d entries (source=%s, tags=%s)", count, source, tags)
        return {"forgotten": count}

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    @tool(name="filesystem.walk", side_effects="read_only")
    async def ingest_directory(self, path: str) -> dict:
        """Ingest all text files in a directory into persistent memory."""
        self._assert_allowed(path)
        count = 0
        for f in Path(path).rglob("*"):
            if f.suffix in {".md", ".py", ".rs", ".ts", ".toml", ".txt"} and f.is_file():
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    await self._store({
                        "content": content,
                        "scope": "persistent",
                        "source": str(f),
                        "tags": ["filesystem", f.suffix[1:]],
                    })
                    count += 1
                except Exception:
                    pass
        return {"ingested": count, "path": path}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _chunk(self, text: str, size: int = 512, overlap: int = 64) -> list[str]:
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i:i+size]))
            i += size - overlap
        return chunks or [text]

    async def _session_summary(self) -> str:
        rows = await self._db.fetchall(
            "SELECT content FROM session_memory ORDER BY created_at DESC LIMIT 10", ()
        )
        return " | ".join(r[0][:80] for r in rows) if rows else ""

    def _assert_allowed(self, path: str) -> None:
        if not any(str(path).startswith(p) for p in self.FS_ALLOWLIST):
            raise PermissionError(f"Memory: '{path}' outside allowed sandbox")
