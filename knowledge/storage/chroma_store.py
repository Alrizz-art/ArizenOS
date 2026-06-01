"""
ChromaDB vector store for the Arizen Knowledge Engine.

Collections:
  arizen_knowledge   — all ingested chunks from all sources
  arizen_memory      — short/long-term agent memory
  arizen_projects    — project-scoped knowledge

Each collection uses nomic-embed-text embeddings (768-dim, HNSW index).
ChromaDB runs embedded (no server) with a persistent on-disk database.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import chromadb
from chromadb.config import Settings

from knowledge.ingestion.base import Chunk, SearchResult

logger = logging.getLogger("arizen.knowledge.chroma")

CHROMA_PATH   = "memory/chroma"
KNOWLEDGE_COL = "arizen_knowledge"
MEMORY_COL    = "arizen_memory"
PROJECTS_COL  = "arizen_projects"

# Chroma metadata values must be str | int | float | bool — no nested dicts/lists
def _flatten_metadata(meta: dict) -> dict[str, str | int | float | bool]:
    flat: dict[str, str | int | float | bool] = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)):
            flat[k] = v
        elif isinstance(v, list):
            flat[k] = ",".join(str(i) for i in v)[:500]
        elif v is None:
            flat[k] = ""
        else:
            flat[k] = str(v)[:500]
    return flat


class ChromaStore:
    """
    Wraps ChromaDB for the Knowledge Engine.

    All operations are synchronous (chromadb client is sync).
    Call from async code via asyncio.to_thread() for non-blocking behaviour.
    """

    def __init__(self, persist_path: str = CHROMA_PATH) -> None:
        Path(persist_path).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False),
        )
        self._knowledge = self._get_or_create(KNOWLEDGE_COL)
        self._memory    = self._get_or_create(MEMORY_COL)
        self._projects  = self._get_or_create(PROJECTS_COL)
        logger.info("ChromaStore ready at %s", persist_path)

    def _get_or_create(self, name: str) -> chromadb.Collection:
        return self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Upsert ─────────────────────────────────────────────────────

    def upsert_chunks(self, chunks: list[Chunk], collection: str = KNOWLEDGE_COL) -> None:
        col = self._resolve(collection)
        ids, embeddings, documents, metadatas = [], [], [], []
        for c in chunks:
            if not c.embedding or all(v == 0.0 for v in c.embedding):
                continue   # skip un-embedded chunks (keyword search will cover them)
            ids.append(c.id)
            embeddings.append(c.embedding)
            documents.append(c.content)
            metadatas.append(_flatten_metadata(c.metadata))

        if ids:
            col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
            logger.debug("ChromaDB upserted %d chunks → %s", len(ids), collection)

    # ── Query ──────────────────────────────────────────────────────

    def query(
        self,
        embedding:  list[float],
        top_k:      int = 8,
        collection: str = KNOWLEDGE_COL,
        where:      Optional[dict] = None,
    ) -> list[SearchResult]:
        col = self._resolve(collection)
        try:
            result = col.query(
                query_embeddings=[embedding],
                n_results=min(top_k, col.count() or 1),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            return []

        results: list[SearchResult] = []
        for i, doc_id in enumerate(result["ids"][0]):
            meta     = result["metadatas"][0][i]
            distance = result["distances"][0][i]
            score    = max(0.0, 1.0 - distance)   # cosine → similarity
            results.append(SearchResult(
                chunk_id    = doc_id,
                document_id = meta.get("document_id", ""),
                source      = meta.get("source", ""),
                title       = meta.get("title", ""),
                content     = result["documents"][0][i],
                score       = round(score, 4),
                metadata    = dict(meta),
                url         = meta.get("url", ""),
                rank        = i,
            ))
        return results

    # ── Delete ─────────────────────────────────────────────────────

    def delete_by_document(self, document_id: str, collection: str = KNOWLEDGE_COL) -> int:
        col = self._resolve(collection)
        existing = col.get(where={"document_id": document_id}, include=[])
        if existing["ids"]:
            col.delete(ids=existing["ids"])
            return len(existing["ids"])
        return 0

    def delete_by_source(self, source: str, collection: str = KNOWLEDGE_COL) -> int:
        col = self._resolve(collection)
        existing = col.get(where={"source": source}, include=[])
        if existing["ids"]:
            col.delete(ids=existing["ids"])
            return len(existing["ids"])
        return 0

    # ── Stats ──────────────────────────────────────────────────────

    def count(self, collection: str = KNOWLEDGE_COL) -> int:
        return self._resolve(collection).count()

    def stats(self) -> dict[str, int]:
        return {
            "knowledge": self._knowledge.count(),
            "memory":    self._memory.count(),
            "projects":  self._projects.count(),
        }

    def _resolve(self, name: str) -> chromadb.Collection:
        match name:
            case c if c == MEMORY_COL:    return self._memory
            case c if c == PROJECTS_COL:  return self._projects
            case _:                       return self._knowledge
