"""
Semantic Search — hybrid retrieval combining vector similarity (ChromaDB)
and keyword full-text search (SQLite FTS5).

The hybrid ranker uses Reciprocal Rank Fusion (RRF) to merge both result
lists into a single ranked output that outperforms either method alone.

Usage:
    searcher = SemanticSearch(chroma_store, sqlite_store, embedder)
    results  = await searcher.search("how does the retry engine work?", top_k=8)
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from knowledge.ingestion.base import SearchResult
from knowledge.storage.chroma_store import ChromaStore
from knowledge.storage.sqlite_store import SQLiteStore
from knowledge.processing.embedder import Embedder

logger = logging.getLogger("arizen.knowledge.search")

RRF_K = 60   # Reciprocal Rank Fusion constant (recommended: 60)


class SemanticSearch:
    """
    Hybrid semantic + keyword search over the Arizen knowledge base.

    Strategies:
      semantic  — ChromaDB vector similarity only
      keyword   — SQLite FTS5 BM25 only
      hybrid    — RRF fusion of both (default, best quality)
    """

    def __init__(
        self,
        chroma:   ChromaStore,
        sqlite:   SQLiteStore,
        embedder: Embedder,
    ) -> None:
        self._chroma   = chroma
        self._sqlite   = sqlite
        self._embedder = embedder

    async def search(
        self,
        query:    str,
        top_k:    int = 8,
        strategy: str = "hybrid",   # "semantic" | "keyword" | "hybrid"
        source:   Optional[str] = None,
        collection: str = "arizen_knowledge",
    ) -> list[SearchResult]:
        """Return ranked SearchResult list for the given query."""
        if not query.strip():
            return []

        match strategy:
            case "semantic":
                return await self._semantic(query, top_k, collection, source)
            case "keyword":
                return self._keyword(query, top_k, source)
            case _:
                return await self._hybrid(query, top_k, collection, source)

    # ── Semantic (ChromaDB vector) ──────────────────────────────────

    async def _semantic(
        self, query: str, top_k: int, collection: str, source: Optional[str]
    ) -> list[SearchResult]:
        embedding = await self._embedder.embed_query(query)
        where = {"source": source} if source else None
        return await asyncio.to_thread(
            self._chroma.query, embedding, top_k, collection, where
        )

    # ── Keyword (SQLite FTS5) ───────────────────────────────────────

    def _keyword(self, query: str, top_k: int, source: Optional[str]) -> list[SearchResult]:
        return self._sqlite.fts_search(query, top_k=top_k, source=source)

    # ── Hybrid (RRF fusion) ─────────────────────────────────────────

    async def _hybrid(
        self, query: str, top_k: int, collection: str, source: Optional[str]
    ) -> list[SearchResult]:
        semantic_task = asyncio.create_task(self._semantic(query, top_k * 2, collection, source))
        keyword_results = self._keyword(query, top_k * 2, source)
        semantic_results = await semantic_task

        fused = self._rrf_merge(semantic_results, keyword_results, top_k)
        logger.debug(
            "Hybrid search '%s...' → %d results (sem=%d, kw=%d)",
            query[:40], len(fused), len(semantic_results), len(keyword_results)
        )
        return fused

    def _rrf_merge(
        self,
        list_a: list[SearchResult],
        list_b: list[SearchResult],
        top_k:  int,
    ) -> list[SearchResult]:
        """Reciprocal Rank Fusion: score(d) = Σ 1 / (k + rank(d))"""
        scores: dict[str, float]     = {}
        by_id:  dict[str, SearchResult] = {}

        for rank, r in enumerate(list_a):
            key = r.chunk_id or r.document_id
            scores[key]  = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
            by_id[key]   = r

        for rank, r in enumerate(list_b):
            key = r.chunk_id or r.document_id
            scores[key]  = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
            if key not in by_id:
                by_id[key] = r

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        results: list[SearchResult] = []
        for i, (key, score) in enumerate(ranked):
            r        = by_id[key]
            r.score  = round(score, 4)
            r.rank   = i
            results.append(r)
        return results
