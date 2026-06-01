"""
Base connector and shared Document/Chunk models for the Arizen Knowledge Engine.

Every ingestion source implements BaseConnector and yields Document objects.
The processing pipeline consumes Documents and produces Chunks for storage.
"""
from __future__ import annotations

import hashlib
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Optional


# ─── Core Models ──────────────────────────────────────────────────────────────

@dataclass
class Document:
    """A single unit of knowledge ingested from any source."""
    id:         str
    source:     str              # "github" | "telegram" | "discord" | "notion" | "markdown" | "pdf" | "local"
    source_id:  str              # original ID in the source system
    title:      str
    content:    str              # full extracted text
    metadata:   dict[str, Any]  = field(default_factory=dict)
    url:        str              = ""
    created_at: datetime         = field(default_factory=datetime.utcnow)
    updated_at: datetime         = field(default_factory=datetime.utcnow)
    checksum:   str              = ""   # sha256 of content — for change detection

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.checksum:
            self.checksum = hashlib.sha256(self.content.encode()).hexdigest()

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def char_count(self) -> int:
        return len(self.content)


@dataclass
class Chunk:
    """A semantic chunk of a Document, ready for embedding and storage."""
    id:          str
    document_id: str
    source:      str
    content:     str
    embedding:   list[float]           = field(default_factory=list)
    metadata:    dict[str, Any]        = field(default_factory=dict)
    chunk_index: int                   = 0
    chunk_count: int                   = 1
    token_count: int                   = 0

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class SearchResult:
    """A ranked retrieval result from semantic or keyword search."""
    chunk_id:    str
    document_id: str
    source:      str
    title:       str
    content:     str
    score:       float             # similarity score 0.0–1.0
    metadata:    dict[str, Any]   = field(default_factory=dict)
    url:         str               = ""
    rank:        int               = 0

    @property
    def preview(self) -> str:
        return self.content[:200] + "..." if len(self.content) > 200 else self.content


@dataclass
class IngestResult:
    """Summary of a completed ingestion run."""
    source:         str
    documents_new:  int = 0
    documents_updated: int = 0
    documents_skipped: int = 0
    chunks_created: int = 0
    errors:         list[str] = field(default_factory=list)
    duration_sec:   float = 0.0


# ─── Connector Config ─────────────────────────────────────────────────────────

@dataclass
class ConnectorConfig:
    """Common configuration shared by all connectors."""
    source_name:    str
    enabled:        bool  = True
    max_documents:  int   = 5000
    since_days:     int   = 365         # only ingest docs newer than N days
    batch_size:     int   = 50
    credentials:    dict  = field(default_factory=dict)  # tokens, keys, etc.


# ─── Base Connector ───────────────────────────────────────────────────────────

class BaseConnector(ABC):
    """
    Abstract base class for all ArizenOS knowledge source connectors.

    Subclasses must implement `ingest()` as an async generator that yields
    Document objects. The engine handles chunking, embedding, and storage.

    Example:
        connector = GitHubConnector(config)
        async for doc in connector.ingest():
            await engine.index(doc)
    """

    def __init__(self, config: ConnectorConfig) -> None:
        self.config = config
        self.source = config.source_name

    @abstractmethod
    async def ingest(self) -> AsyncIterator[Document]:
        """Yield Document objects from this source."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the connector can reach its source."""
        ...

    def make_doc_id(self, source_id: str) -> str:
        return hashlib.md5(f"{self.source}:{source_id}".encode()).hexdigest()

    def _now(self) -> datetime:
        return datetime.utcnow()
