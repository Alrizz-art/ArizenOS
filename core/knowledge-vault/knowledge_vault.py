"""
Knowledge Vault — Local RAG system.
ChromaDB (semantic) + SQLite FTS5 (keyword) hybrid search.
Ingests local files with automatic chunking and embedding.
"""
from __future__ import annotations

import hashlib
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

CHUNK_SIZE    = 512   # tokens (approximated as chars/4)
CHUNK_OVERLAP = 64


@dataclass
class Chunk:
    doc_id:   str
    chunk_id: str
    text:     str
    source:   str
    metadata: dict = field(default_factory=dict)


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


class KnowledgeVault:
    """Local knowledge store — hybrid semantic + keyword search."""

    def __init__(self, data_dir: Path) -> None:
        self._dir  = data_dir
        self._col  = chromadb.PersistentClient(
            path=str(data_dir / "vectors"),
            settings=Settings(anonymized_telemetry=False),
        ).get_or_create_collection("arizen_knowledge", metadata={"hnsw:space": "cosine"})
        self._db   = self._init_sqlite(data_dir / "knowledge.db")
        logger.info("Knowledge Vault ready at %s", data_dir)

    def _init_sqlite(self, path: Path) -> sqlite3.Connection:
        conn = sqlite3.connect(str(path), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts
                        USING fts5(doc_id, chunk_id, text, source)""")
        conn.commit()
        return conn

    def ingest(self, path: Path, text: str) -> int:
        doc_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]
        chunks = self._chunk(text, str(path), doc_id)
        self._col.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "doc_id": c.doc_id} for c in chunks],
        )
        self._db.executemany(
            "INSERT OR REPLACE INTO docs_fts VALUES (?, ?, ?, ?)",
            [(c.doc_id, c.chunk_id, c.text, c.source) for c in chunks],
        )
        self._db.commit()
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        sem = self._semantic(query, top_k)
        kw  = self._keyword(query, top_k)
        seen:    set[str]           = set()
        merged: list[SearchResult]  = []
        for r in sem + kw:
            if r.chunk.chunk_id not in seen:
                seen.add(r.chunk.chunk_id)
                merged.append(r)
        return sorted(merged, key=lambda r: r.score, reverse=True)[:top_k]

    def _semantic(self, query: str, top_k: int) -> list[SearchResult]:
        res = self._col.query(query_texts=[query], n_results=top_k)
        return [
            SearchResult(
                chunk=Chunk(doc_id=m["doc_id"], chunk_id=ids, text=doc, source=m["source"]),
                score=1 - dist,
            )
            for ids, doc, m, dist in zip(
                res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
            )
        ]

    def _keyword(self, query: str, top_k: int) -> list[SearchResult]:
        rows = self._db.execute(
            "SELECT doc_id, chunk_id, text, source FROM docs_fts WHERE docs_fts MATCH ? LIMIT ?",
            (query, top_k),
        ).fetchall()
        return [
            SearchResult(chunk=Chunk(r[0], r[1], r[2], r[3]), score=0.5)
            for r in rows
        ]

    def _chunk(self, text: str, source: str, doc_id: str) -> list[Chunk]:
        cs, co = CHUNK_SIZE * 4, CHUNK_OVERLAP * 4
        chunks, i = [], 0
        while i < len(text):
            t = text[i : i + cs].strip()
            if t:
                chunks.append(Chunk(doc_id, f"{doc_id}_{len(chunks):04d}", t, source))
            i += cs - co
        return chunks
