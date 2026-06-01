"""
Embedder — generates vector embeddings for Chunks using Ollama local models.

Embedding models used (tiered):
  - nomic-embed-text   : fast, 768-dim, default for all text
  - mxbai-embed-large  : high-quality, 1024-dim, for deep knowledge indexing

Batch embedding is supported to minimise round-trips to Ollama.
Falls back to a deterministic zero-vector + warning if Ollama is unavailable
(preserves the pipeline — keyword search still works without vectors).
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from knowledge.ingestion.base import Chunk

logger = logging.getLogger("arizen.knowledge.embedder")

OLLAMA_BASE  = "http://localhost:11434"
DEFAULT_MODEL = "nomic-embed-text"
EMBED_DIM     = 768   # nomic-embed-text dimension
BATCH_SIZE    = 32    # chunks per Ollama request


@dataclass
class EmbedStats:
    chunks_embedded:  int   = 0
    chunks_skipped:   int   = 0
    model:            str   = DEFAULT_MODEL
    duration_sec:     float = 0.0
    ollama_available: bool  = True


class Embedder:
    """
    Generates dense vector embeddings for Chunk objects via Ollama.

    Usage:
        embedder = Embedder()
        chunks   = await embedder.embed_all(chunks)  # fills chunk.embedding
    """

    def __init__(
        self,
        model:       str = DEFAULT_MODEL,
        ollama_base: str = OLLAMA_BASE,
        timeout:     int = 30,
    ) -> None:
        self.model   = model
        self.base    = ollama_base
        self.timeout = timeout
        self._client = httpx.AsyncClient(base_url=ollama_base, timeout=timeout)
        self._cache: dict[str, list[float]] = {}   # content_hash → embedding

    async def embed_all(self, chunks: list[Chunk]) -> list[Chunk]:
        """Embed all chunks in batches. Returns the same list with .embedding filled."""
        start = time.monotonic()
        ok = await self._ping()
        if not ok:
            logger.warning("Ollama unavailable — chunks stored without embeddings (keyword search only)")
            for c in chunks:
                c.embedding = [0.0] * EMBED_DIM
            return chunks

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            await self._embed_batch(batch)

        logger.info("Embedded %d chunks via %s (%.1fs)", len(chunks), self.model,
                    time.monotonic() - start)
        return chunks

    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query string for similarity search."""
        ok = await self._ping()
        if not ok:
            return [0.0] * EMBED_DIM
        try:
            r = await self._client.post("/api/embeddings", json={"model": self.model, "prompt": query})
            r.raise_for_status()
            return r.json()["embedding"]
        except Exception as exc:
            logger.error("Query embedding failed: %s", exc)
            return [0.0] * EMBED_DIM

    async def _embed_batch(self, chunks: list[Chunk]) -> None:
        tasks = [self._embed_one(c) for c in chunks]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _embed_one(self, chunk: Chunk) -> None:
        key = hashlib.md5(chunk.content.encode()).hexdigest()
        if key in self._cache:
            chunk.embedding = self._cache[key]
            return
        try:
            r = await self._client.post(
                "/api/embeddings",
                json={"model": self.model, "prompt": chunk.content}
            )
            r.raise_for_status()
            emb = r.json()["embedding"]
            self._cache[key] = emb
            chunk.embedding  = emb
        except Exception as exc:
            logger.warning("Embedding chunk %s failed: %s — using zero vector", chunk.id[:8], exc)
            chunk.embedding = [0.0] * EMBED_DIM

    async def _ping(self) -> bool:
        try:
            r = await self._client.get("/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()
