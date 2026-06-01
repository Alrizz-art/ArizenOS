"""
Knowledge Engine — the central ingestion, indexing, and retrieval orchestrator.

Responsibilities:
  - Manage all source connectors (GitHub, Telegram, Discord, Notion, Markdown, PDF, Local)
  - Run incremental ingestion (new/changed docs only via checksum)
  - Chunk, embed, and dual-write to ChromaDB + SQLite
  - Expose unified search (semantic + keyword + hybrid)
  - Expose RAG pipeline for agent context injection
  - Provide stats and connector health checks

Usage:
    engine = KnowledgeEngine.from_config("config/knowledge.yaml")
    await engine.ingest("github")          # ingest one source
    await engine.ingest_all()             # ingest all sources
    results = await engine.search("ArizenOS checkpoint design", top_k=8)
    ctx     = await engine.rag_context("how does retry work?")
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document, IngestResult
from knowledge.processing.chunker import Chunker
from knowledge.processing.embedder import Embedder
from knowledge.processing.metadata import MetadataExtractor
from knowledge.storage.chroma_store import ChromaStore
from knowledge.storage.sqlite_store import SQLiteStore
from knowledge.query.semantic_search import SemanticSearch
from knowledge.query.rag import RAGContext, RAGPipeline
from knowledge.ingestion.base import SearchResult

logger = logging.getLogger("arizen.knowledge.engine")


# ─── Engine Configuration ─────────────────────────────────────────────────────

@dataclass
class KnowledgeEngineConfig:
    chroma_path:   str = "memory/chroma"
    sqlite_path:   str = "memory/persistent/knowledge.db"
    embed_model:   str = "nomic-embed-text"
    chunk_size:    int = 1200
    chunk_overlap: int = 200
    rag_top_k:     int = 8
    rag_threshold: float = 0.30
    rag_tokens:    int   = 3000


# ─── Knowledge Engine ─────────────────────────────────────────────────────────

class KnowledgeEngine:
    """
    Unified ingestion + retrieval engine for all ArizenOS knowledge sources.

    All agents call this engine for knowledge retrieval.
    Commander calls `rag_context()` before composing every response.
    The Memory agent calls `ingest()` on a schedule.
    """

    def __init__(self, config: KnowledgeEngineConfig = None) -> None:
        self._cfg       = config or KnowledgeEngineConfig()
        self._chroma    = ChromaStore(self._cfg.chroma_path)
        self._sqlite    = SQLiteStore(self._cfg.sqlite_path)
        self._embedder  = Embedder(model=self._cfg.embed_model)
        self._chunker   = Chunker(self._cfg.chunk_size, self._cfg.chunk_overlap)
        self._metadata  = MetadataExtractor()
        self._search    = SemanticSearch(self._chroma, self._sqlite, self._embedder)
        self._rag       = RAGPipeline(
            self._search,
            top_k=self._cfg.rag_top_k,
            score_threshold=self._cfg.rag_threshold,
            context_tokens=self._cfg.rag_tokens,
        )
        self._connectors: dict[str, BaseConnector] = {}
        logger.info("KnowledgeEngine ready")

    # ── Connector Registry ────────────────────────────────────────

    def register(self, name: str, connector: BaseConnector) -> None:
        """Register a data source connector."""
        self._connectors[name] = connector
        logger.info("Registered connector: %s", name)

    def register_all_from_config(self, config_path: str) -> None:
        """Load connector configs from a YAML file and register connectors."""
        raw = yaml.safe_load(Path(config_path).read_text())
        for source_name, source_cfg in raw.get("sources", {}).items():
            if not source_cfg.get("enabled", True):
                continue
            connector = self._build_connector(source_name, source_cfg)
            if connector:
                self.register(source_name, connector)

    def _build_connector(self, name: str, cfg: dict) -> Optional[BaseConnector]:
        cc = ConnectorConfig(
            source_name   = name,
            enabled       = cfg.get("enabled", True),
            max_documents = cfg.get("max_documents", 5000),
            since_days    = cfg.get("since_days", 365),
            batch_size    = cfg.get("batch_size", 50),
            credentials   = cfg.get("credentials", {}),
        )
        match name:
            case "github":
                from knowledge.ingestion.github import GitHubConnector
                return GitHubConnector(cc)
            case "telegram":
                from knowledge.ingestion.telegram import TelegramConnector
                return TelegramConnector(cc)
            case "discord":
                from knowledge.ingestion.discord_connector import DiscordConnector
                return DiscordConnector(cc)
            case "notion":
                from knowledge.ingestion.notion import NotionConnector
                return NotionConnector(cc)
            case "markdown":
                from knowledge.ingestion.markdown import MarkdownConnector
                return MarkdownConnector(cc)
            case "pdf":
                from knowledge.ingestion.pdf import PDFConnector
                return PDFConnector(cc)
            case "local":
                from knowledge.ingestion.local_files import LocalFilesConnector
                return LocalFilesConnector(cc)
            case _:
                logger.warning("Unknown source type: %s", name)
                return None

    # ── Ingestion ─────────────────────────────────────────────────

    async def ingest(self, source: str) -> IngestResult:
        """Ingest all documents from a single registered source."""
        connector = self._connectors.get(source)
        if not connector:
            raise LookupError(f"Connector '{source}' not registered")

        result = IngestResult(source=source)
        start  = time.monotonic()
        log_id = str(uuid.uuid4())
        self._sqlite.log_ingest({"id": log_id, "source": source, "started_at": time.time()})

        try:
            async for doc in connector.ingest():
                try:
                    await self._index_document(doc, result)
                except Exception as exc:
                    logger.error("Failed to index doc '%s': %s", doc.source_id[:40], exc)
                    result.errors.append(str(exc))
        except Exception as exc:
            logger.error("Ingestion error for source '%s': %s", source, exc)
            result.errors.append(str(exc))

        result.duration_sec = time.monotonic() - start
        self._sqlite.log_ingest({
            "id": log_id, "source": source,
            "started_at": time.time() - result.duration_sec,
            "completed_at": time.time(),
            "docs_new": result.documents_new,
            "docs_updated": result.documents_updated,
            "docs_skipped": result.documents_skipped,
            "chunks_created": result.chunks_created,
            "errors": result.errors,
        })
        logger.info(
            "Ingested %s: +%d new, ~%d updated, =%d skipped, %d chunks (%.1fs)",
            source, result.documents_new, result.documents_updated,
            result.documents_skipped, result.chunks_created, result.duration_sec,
        )
        return result

    async def ingest_all(self, parallel: bool = False) -> dict[str, IngestResult]:
        """Ingest all registered sources. parallel=True runs them concurrently."""
        results: dict[str, IngestResult] = {}
        if parallel:
            tasks = {name: asyncio.create_task(self.ingest(name)) for name in self._connectors}
            for name, task in tasks.items():
                try:
                    results[name] = await task
                except Exception as exc:
                    logger.error("Ingest '%s' failed: %s", name, exc)
                    results[name] = IngestResult(source=name, errors=[str(exc)])
        else:
            for name in self._connectors:
                results[name] = await self.ingest(name)
        return results

    async def _index_document(self, doc: Document, result: IngestResult) -> None:
        # Enrich metadata
        doc.metadata = self._metadata.extract(doc)

        # Dedup check
        is_new = self._sqlite.upsert_document(doc)
        if not is_new:
            # If document was unchanged (same checksum), skip
            existing_check = self._sqlite._db.execute(
                "SELECT checksum FROM documents WHERE source=? AND source_id=?",
                (doc.source, doc.source_id)
            ).fetchone()
            if existing_check and existing_check["checksum"] == doc.checksum:
                result.documents_skipped += 1
                return
            result.documents_updated += 1
            # Delete old chunks from ChromaDB
            existing_id = self._sqlite.document_exists(doc.source, doc.source_id)
            if existing_id:
                await asyncio.to_thread(self._chroma.delete_by_document, existing_id)
        else:
            result.documents_new += 1

        # Chunk
        chunks = self._chunker.chunk(doc)

        # Embed
        chunks = await self._embedder.embed_all(chunks)

        # Store
        await asyncio.to_thread(self._chroma.upsert_chunks, chunks)
        self._sqlite.upsert_chunks(chunks)
        result.chunks_created += len(chunks)

    # ── Search ────────────────────────────────────────────────────

    async def search(
        self,
        query:    str,
        top_k:    int           = 8,
        strategy: str           = "hybrid",
        source:   Optional[str] = None,
    ) -> list[SearchResult]:
        """Hybrid semantic + keyword search across all indexed knowledge."""
        return await self._search.search(query, top_k=top_k, strategy=strategy, source=source)

    async def rag_context(
        self,
        query:    str,
        source:   Optional[str] = None,
        top_k:    int           = 8,
    ) -> RAGContext:
        """
        Build a RAG context block ready for LLM injection.
        Returns a RAGContext with .prompt_block property.
        """
        return await self._rag.build_context(query=query, source=source, extra_top_k=max(0, top_k - self._cfg.rag_top_k))

    # ── Connector Health ──────────────────────────────────────────

    async def health_check(self) -> dict[str, bool]:
        results = await asyncio.gather(*[
            c.health_check() for c in self._connectors.values()
        ], return_exceptions=True)
        return {
            name: (r if isinstance(r, bool) else False)
            for name, r in zip(self._connectors.keys(), results)
        }

    # ── Stats ─────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        chroma_stats = self._chroma.stats()
        sqlite_stats = self._sqlite.stats()
        return {
            "connectors":     list(self._connectors.keys()),
            "chroma":         chroma_stats,
            "sqlite":         sqlite_stats,
            "embed_model":    self._cfg.embed_model,
        }

    # ── Deletion ──────────────────────────────────────────────────

    async def delete_source(self, source: str) -> int:
        """Remove all indexed documents from a source."""
        deleted = await asyncio.to_thread(self._chroma.delete_by_source, source)
        logger.warning("Deleted %d chunks for source '%s'", deleted, source)
        return deleted

    # ── Factory ───────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config_path: str) -> "KnowledgeEngine":
        """Load engine + connectors from a YAML config file."""
        raw = yaml.safe_load(Path(config_path).read_text())
        engine_cfg = raw.get("engine", {})
        engine = cls(KnowledgeEngineConfig(
            chroma_path   = engine_cfg.get("chroma_path", "memory/chroma"),
            sqlite_path   = engine_cfg.get("sqlite_path", "memory/persistent/knowledge.db"),
            embed_model   = engine_cfg.get("embed_model", "nomic-embed-text"),
            chunk_size    = engine_cfg.get("chunk_size", 1200),
            chunk_overlap = engine_cfg.get("chunk_overlap", 200),
            rag_top_k     = engine_cfg.get("rag_top_k", 8),
            rag_threshold = engine_cfg.get("rag_threshold", 0.30),
            rag_tokens    = engine_cfg.get("rag_tokens", 3000),
        ))
        engine.register_all_from_config(config_path)
        return engine
