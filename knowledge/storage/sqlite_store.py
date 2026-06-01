"""
SQLite FTS5 store for the Arizen Knowledge Engine.

Provides:
  - Full-text keyword search (FTS5 BM25 ranking)
  - Document metadata registry (change detection, source tracking)
  - Chunk registry (chunk_id ↔ document_id mapping)
  - Memory records table (long-term + project memory)
  - Ingestion audit log

WAL mode + synchronous=NORMAL for safe concurrent reads with fast writes.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from knowledge.ingestion.base import Chunk, Document, SearchResult

logger = logging.getLogger("arizen.knowledge.sqlite")

DB_PATH = "memory/persistent/knowledge.db"


class SQLiteStore:
    """
    SQLite-backed metadata + FTS5 full-text search store.

    Complements ChromaDB: ChromaDB handles semantic (vector) search,
    SQLite handles keyword search, deduplication, and metadata queries.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = self._init_db(db_path)
        logger.info("SQLiteStore ready at %s", db_path)

    def _init_db(self, path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id          TEXT PRIMARY KEY,
            source      TEXT NOT NULL,
            source_id   TEXT NOT NULL,
            title       TEXT,
            url         TEXT,
            checksum    TEXT,
            word_count  INTEGER DEFAULT 0,
            metadata    TEXT,
            created_at  REAL,
            updated_at  REAL,
            indexed_at  REAL
        );

        CREATE INDEX IF NOT EXISTS idx_doc_source    ON documents(source);
        CREATE INDEX IF NOT EXISTS idx_doc_source_id ON documents(source, source_id);
        CREATE INDEX IF NOT EXISTS idx_doc_checksum  ON documents(checksum);

        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            doc_id UNINDEXED,
            title,
            content,
            source UNINDEXED,
            tokenize = 'porter unicode61'
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id          TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            source      TEXT NOT NULL,
            chunk_index INTEGER,
            chunk_count INTEGER,
            token_count INTEGER,
            has_embedding INTEGER DEFAULT 0,
            created_at  REAL
        );

        CREATE TABLE IF NOT EXISTS memory_records (
            id         TEXT PRIMARY KEY,
            scope      TEXT NOT NULL,
            content    TEXT NOT NULL,
            tags       TEXT,
            source     TEXT,
            project    TEXT,
            created_at REAL,
            ttl_sec    INTEGER DEFAULT 0,
            importance REAL DEFAULT 0.5,
            access_count INTEGER DEFAULT 0,
            last_accessed REAL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            record_id UNINDEXED,
            content,
            tags,
            scope UNINDEXED,
            tokenize = 'porter unicode61'
        );

        CREATE TABLE IF NOT EXISTS ingest_log (
            id            TEXT PRIMARY KEY,
            source        TEXT,
            started_at    REAL,
            completed_at  REAL,
            docs_new      INTEGER DEFAULT 0,
            docs_updated  INTEGER DEFAULT 0,
            docs_skipped  INTEGER DEFAULT 0,
            chunks_created INTEGER DEFAULT 0,
            errors        TEXT
        );
        """)
        conn.commit()
        return conn

    # ── Documents ─────────────────────────────────────────────────

    def upsert_document(self, doc: Document) -> bool:
        """Returns True if this is a new document, False if updated."""
        existing = self._db.execute(
            "SELECT id, checksum FROM documents WHERE source=? AND source_id=?",
            (doc.source, doc.source_id)
        ).fetchone()

        now = time.time()
        if existing:
            if existing["checksum"] == doc.checksum:
                return False   # unchanged, skip
            # Content changed — update
            self._db.execute(
                "UPDATE documents SET title=?, checksum=?, word_count=?, metadata=?, updated_at=?, indexed_at=? WHERE id=?",
                (doc.title, doc.checksum, doc.word_count, json.dumps(doc.metadata), now, now, existing["id"])
            )
            # Refresh FTS
            self._db.execute("DELETE FROM documents_fts WHERE doc_id=?", (existing["id"],))
            self._db.execute(
                "INSERT INTO documents_fts(doc_id, title, content, source) VALUES (?,?,?,?)",
                (existing["id"], doc.title, doc.content[:50000], doc.source)
            )
            self._db.commit()
            return False
        else:
            self._db.execute(
                "INSERT INTO documents(id, source, source_id, title, url, checksum, word_count, metadata, created_at, updated_at, indexed_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (doc.id, doc.source, doc.source_id, doc.title, doc.url, doc.checksum,
                 doc.word_count, json.dumps(doc.metadata), now, now, now)
            )
            self._db.execute(
                "INSERT INTO documents_fts(doc_id, title, content, source) VALUES (?,?,?,?)",
                (doc.id, doc.title, doc.content[:50000], doc.source)
            )
            self._db.commit()
            return True

    def document_exists(self, source: str, source_id: str) -> Optional[str]:
        """Returns document_id if found, else None."""
        row = self._db.execute(
            "SELECT id FROM documents WHERE source=? AND source_id=?", (source, source_id)
        ).fetchone()
        return row["id"] if row else None

    def get_document(self, doc_id: str) -> Optional[dict]:
        row = self._db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else None

    # ── Chunks ────────────────────────────────────────────────────

    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        now = time.time()
        self._db.executemany(
            "INSERT OR REPLACE INTO chunks(id, document_id, source, chunk_index, chunk_count, token_count, has_embedding, created_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            [(c.id, c.document_id, c.source, c.chunk_index, c.chunk_count, c.token_count,
              int(bool(c.embedding and any(v != 0 for v in c.embedding))), now) for c in chunks]
        )
        self._db.commit()

    # ── Full-Text Search ──────────────────────────────────────────

    def fts_search(self, query: str, top_k: int = 8, source: Optional[str] = None) -> list[SearchResult]:
        safe_query = query.replace('"', '""')
        where_clause = "AND source=?" if source else ""
        params = [f'"{safe_query}"', top_k]
        if source:
            params.insert(1, source)
        try:
            rows = self._db.execute(
                f"""SELECT doc_id, title, content, source, bm25(documents_fts) AS score
                    FROM documents_fts
                    WHERE documents_fts MATCH ?
                    {where_clause}
                    ORDER BY score
                    LIMIT ?""",
                params
            ).fetchall()
        except sqlite3.OperationalError:
            return []

        results: list[SearchResult] = []
        for i, row in enumerate(rows):
            meta_row = self._db.execute("SELECT url, metadata FROM documents WHERE id=?", (row["doc_id"],)).fetchone()
            url   = meta_row["url"] if meta_row else ""
            meta  = json.loads(meta_row["metadata"]) if meta_row and meta_row["metadata"] else {}
            results.append(SearchResult(
                chunk_id    = row["doc_id"],
                document_id = row["doc_id"],
                source      = row["source"],
                title       = row["title"],
                content     = row["content"][:1000],
                score       = max(0.0, 1.0 / (1.0 + abs(row["score"]))),
                metadata    = meta,
                url         = url,
                rank        = i,
            ))
        return results

    # ── Memory Records ────────────────────────────────────────────

    def store_memory(
        self,
        record_id:  str,
        scope:      str,
        content:    str,
        tags:       list[str] = None,
        source:     str = "",
        project:    str = "",
        ttl_sec:    int = 0,
        importance: float = 0.5,
    ) -> None:
        now = time.time()
        tags_str = ",".join(tags or [])
        self._db.execute(
            "INSERT OR REPLACE INTO memory_records(id, scope, content, tags, source, project, created_at, ttl_sec, importance, access_count, last_accessed) "
            "VALUES (?,?,?,?,?,?,?,?,?,0,?)",
            (record_id, scope, content, tags_str, source, project, now, ttl_sec, importance, now)
        )
        self._db.execute(
            "INSERT OR REPLACE INTO memory_fts(record_id, content, tags, scope) VALUES (?,?,?,?)",
            (record_id, content, tags_str, scope)
        )
        self._db.commit()

    def search_memory(self, query: str, scope: Optional[str] = None, project: Optional[str] = None, limit: int = 10) -> list[dict]:
        safe_q = query.replace('"', '""')
        conditions, params = [], [f'"{safe_q}"']
        if scope:
            conditions.append("scope=?")
            params.append(scope)
        if project:
            conditions.append("project=?")
            params.append(project)
        where = ("AND " + " AND ".join(conditions)) if conditions else ""
        params.append(limit)
        try:
            rows = self._db.execute(
                f"""SELECT mr.* FROM memory_fts mf
                    JOIN memory_records mr ON mr.id = mf.record_id
                    WHERE mf MATCH ? {where}
                    ORDER BY bm25(memory_fts), mr.importance DESC
                    LIMIT ?""",
                params
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []

        # Prune expired
        now = time.time()
        results = []
        for row in rows:
            r = dict(row)
            if r["ttl_sec"] > 0 and (r["created_at"] + r["ttl_sec"]) < now:
                self._db.execute("DELETE FROM memory_records WHERE id=?", (r["id"],))
                continue
            self._db.execute(
                "UPDATE memory_records SET access_count=access_count+1, last_accessed=? WHERE id=?", (now, r["id"])
            )
            results.append(r)
        self._db.commit()
        return results

    def prune_expired_memory(self) -> int:
        now = time.time()
        cursor = self._db.execute(
            "DELETE FROM memory_records WHERE ttl_sec > 0 AND (created_at + ttl_sec) < ?", (now,)
        )
        self._db.commit()
        return cursor.rowcount

    # ── Stats ─────────────────────────────────────────────────────

    def stats(self) -> dict:
        docs     = self._db.execute("SELECT source, COUNT(*) as cnt FROM documents GROUP BY source").fetchall()
        chunks   = self._db.execute("SELECT COUNT(*) as cnt FROM chunks").fetchone()
        memory   = self._db.execute("SELECT scope, COUNT(*) as cnt FROM memory_records GROUP BY scope").fetchall()
        return {
            "documents": {r["source"]: r["cnt"] for r in docs},
            "total_chunks": chunks["cnt"] if chunks else 0,
            "memory_by_scope": {r["scope"]: r["cnt"] for r in memory},
        }

    def log_ingest(self, log: dict) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO ingest_log(id, source, started_at, completed_at, docs_new, docs_updated, docs_skipped, chunks_created, errors) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (log.get("id",""), log.get("source",""), log.get("started_at",0), log.get("completed_at",0),
             log.get("docs_new",0), log.get("docs_updated",0), log.get("docs_skipped",0),
             log.get("chunks_created",0), json.dumps(log.get("errors",[])))
        )
        self._db.commit()
