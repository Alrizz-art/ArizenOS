"""
Chunker — splits Documents into semantic chunks for embedding.

Strategies:
  - recursive   : recursive character splitting (default for prose)
  - sentence    : split on sentence boundaries
  - code        : preserve function/class blocks (language-aware)
  - fixed       : fixed token/character window with overlap
  - markdown    : split on headers (##, ###)

All strategies produce Chunk objects with metadata linking back to the parent Document.
"""
from __future__ import annotations

import re
import uuid
from enum import Enum
from typing import Optional

from knowledge.ingestion.base import Chunk, Document


class ChunkStrategy(str, Enum):
    RECURSIVE = "recursive"
    SENTENCE  = "sentence"
    CODE      = "code"
    FIXED     = "fixed"
    MARKDOWN  = "markdown"


CODE_EXTENSIONS = {".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".go", ".c", ".cpp", ".h"}

# Approximate token count: 1 token ≈ 4 chars
def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class Chunker:
    """
    Splits a Document into Chunks using a configurable strategy.

    chunk_size  : target chunk size in characters
    chunk_overlap: overlap between consecutive chunks (for context continuity)
    """

    def __init__(
        self,
        chunk_size:    int = 1200,
        chunk_overlap: int = 200,
        strategy:      ChunkStrategy = ChunkStrategy.RECURSIVE,
    ) -> None:
        self.chunk_size    = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy      = strategy

    def chunk(self, doc: Document) -> list[Chunk]:
        """Split a Document into Chunks, auto-selecting strategy when appropriate."""
        strategy = self._select_strategy(doc)
        match strategy:
            case ChunkStrategy.MARKDOWN:
                splits = self._split_markdown(doc.content)
            case ChunkStrategy.CODE:
                splits = self._split_code(doc.content)
            case ChunkStrategy.SENTENCE:
                splits = self._split_sentences(doc.content)
            case ChunkStrategy.FIXED:
                splits = self._split_fixed(doc.content)
            case _:
                splits = self._split_recursive(doc.content)

        # Filter empty
        splits = [s.strip() for s in splits if s.strip()]
        if not splits:
            splits = [doc.content[:self.chunk_size]] if doc.content else ["(empty)"]

        total = len(splits)
        chunks: list[Chunk] = []
        for i, text in enumerate(splits):
            chunk_meta = {
                **doc.metadata,
                "document_id":  doc.id,
                "source":       doc.source,
                "source_id":    doc.source_id,
                "title":        doc.title,
                "url":          doc.url,
                "chunk_index":  i,
                "chunk_count":  total,
                "strategy":     strategy.value,
            }
            chunks.append(Chunk(
                id          = str(uuid.uuid4()),
                document_id = doc.id,
                source      = doc.source,
                content     = text,
                metadata    = chunk_meta,
                chunk_index = i,
                chunk_count = total,
                token_count = _approx_tokens(text),
            ))
        return chunks

    # ── Strategy selection ──────────────────────────────────────────

    def _select_strategy(self, doc: Document) -> ChunkStrategy:
        if self.strategy != ChunkStrategy.RECURSIVE:
            return self.strategy
        src  = doc.source
        meta = doc.metadata
        ext  = meta.get("extension", "")
        if ext in CODE_EXTENSIONS or src in ("github",):
            return ChunkStrategy.CODE
        if src == "markdown" or ext == ".md":
            return ChunkStrategy.MARKDOWN
        return ChunkStrategy.RECURSIVE

    # ── Recursive (default prose) ───────────────────────────────────

    def _split_recursive(self, text: str) -> list[str]:
        separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                return self._merge_splits(parts, sep)
        return self._split_fixed(text)

    def _merge_splits(self, parts: list[str], sep: str) -> list[str]:
        chunks, current = [], ""
        for part in parts:
            candidate = (current + sep + part).strip() if current else part.strip()
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(part) > self.chunk_size:
                    chunks.extend(self._split_fixed(part))
                    current = ""
                else:
                    current = part
        if current:
            chunks.append(current)
        return chunks

    # ── Fixed window ────────────────────────────────────────────────

    def _split_fixed(self, text: str) -> list[str]:
        chunks, start = [], 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    # ── Sentence ────────────────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return self._merge_splits(sentences, " ")

    # ── Markdown header-aware ───────────────────────────────────────

    def _split_markdown(self, text: str) -> list[str]:
        header_re = re.compile(r'^(#{1,4}\s.+)$', re.MULTILINE)
        parts, positions = [], list(header_re.finditer(text))
        if not positions:
            return self._split_recursive(text)
        for i, m in enumerate(positions):
            start = m.start()
            end   = positions[i + 1].start() if i + 1 < len(positions) else len(text)
            section = text[start:end].strip()
            if len(section) <= self.chunk_size:
                parts.append(section)
            else:
                parts.extend(self._split_recursive(section))
        if positions[0].start() > 0:
            parts.insert(0, text[:positions[0].start()].strip())
        return parts

    # ── Code block-aware ────────────────────────────────────────────

    def _split_code(self, text: str) -> list[str]:
        # Split on top-level def / class / fn / impl / function boundaries
        boundary_re = re.compile(
            r'^(?:def |class |async def |fn |impl |function |export function |export default)',
            re.MULTILINE
        )
        positions = [m.start() for m in boundary_re.finditer(text)]
        if not positions:
            return self._split_fixed(text)
        parts = []
        if positions[0] > 0:
            parts.append(text[:positions[0]])
        for i, pos in enumerate(positions):
            end = positions[i + 1] if i + 1 < len(positions) else len(text)
            block = text[pos:end].strip()
            if len(block) <= self.chunk_size:
                parts.append(block)
            else:
                parts.extend(self._split_fixed(block))
        return parts
