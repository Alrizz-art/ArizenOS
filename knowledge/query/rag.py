"""
RAG Pipeline — Retrieval-Augmented Generation for the Arizen Knowledge Engine.

Phases:
  1. Retrieve — semantic/hybrid search for top-k relevant chunks
  2. Rerank   — optional cross-encoder reranking (or score-based pruning)
  3. Pack     — assemble context string within token budget
  4. Inject   — format for injection into an LLM prompt

Output: a ready-to-use context string the LLM can reference when answering.

Usage:
    rag     = RAGPipeline(search_engine)
    context = await rag.build_context("how does checkpoint resume work?")
    prompt  = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {query}"
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from knowledge.ingestion.base import SearchResult
from knowledge.query.semantic_search import SemanticSearch

logger = logging.getLogger("arizen.knowledge.rag")

DEFAULT_CONTEXT_TOKENS = 3000   # ~12 000 chars at 4 chars/token
DEFAULT_CHUNK_SEP      = "\n\n---\n\n"


@dataclass
class RAGContext:
    """The assembled retrieval context, ready for prompt injection."""
    query:         str
    sources:       list[SearchResult]
    context_str:   str                # formatted text block
    token_budget:  int
    tokens_used:   int
    strategy:      str

    @property
    def source_citations(self) -> str:
        lines = []
        for i, s in enumerate(self.sources, 1):
            ref = s.url or s.title or s.document_id[:8]
            lines.append(f"[{i}] {s.source.upper()}: {ref} (score={s.score:.3f})")
        return "\n".join(lines)

    @property
    def prompt_block(self) -> str:
        """Full block ready for insertion into an LLM system/user prompt."""
        return (
            f"<knowledge_context>\n"
            f"{self.context_str}\n"
            f"</knowledge_context>\n\n"
            f"<sources>\n{self.source_citations}\n</sources>"
        )


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Retrieves relevant chunks, prunes by score threshold, packs within a
    token budget, and returns a formatted RAGContext ready for LLM injection.
    """

    def __init__(
        self,
        search:          SemanticSearch,
        top_k:           int   = 8,
        score_threshold: float = 0.30,
        context_tokens:  int   = DEFAULT_CONTEXT_TOKENS,
        strategy:        str   = "hybrid",
    ) -> None:
        self._search    = search
        self._top_k     = top_k
        self._threshold = score_threshold
        self._ctx_tokens = context_tokens
        self._strategy  = strategy

    async def build_context(
        self,
        query:      str,
        source:     Optional[str] = None,
        collection: str           = "arizen_knowledge",
        extra_top_k: int          = 0,
    ) -> RAGContext:
        """
        Retrieve and assemble a RAGContext for the given query.
        
        Args:
            query:      The user question / task description
            source:     Optional — restrict retrieval to one source
            collection: ChromaDB collection name
            extra_top_k: Additional results beyond default top_k
        """
        top_k = self._top_k + extra_top_k
        results = await self._search.search(
            query=query, top_k=top_k * 2,
            strategy=self._strategy, source=source, collection=collection,
        )

        # Score filtering
        filtered = [r for r in results if r.score >= self._threshold]
        if not filtered and results:
            filtered = results[:3]   # always include at least 3 results

        # Deduplicate by content (avoid near-duplicate chunks)
        filtered = self._deduplicate(filtered)

        # Pack within token budget
        packed, tokens_used = self._pack(filtered, self._ctx_tokens)

        context_str = self._format_chunks(packed)
        logger.info(
            "RAG: query='%s...' → %d/%d chunks, ~%d tokens",
            query[:40], len(packed), len(filtered), tokens_used
        )

        return RAGContext(
            query=query, sources=packed, context_str=context_str,
            token_budget=self._ctx_tokens, tokens_used=tokens_used,
            strategy=self._strategy,
        )

    # ── Packing ───────────────────────────────────────────────────

    def _pack(self, results: list[SearchResult], budget: int) -> tuple[list[SearchResult], int]:
        packed, used = [], 0
        chars_budget = budget * 4   # 4 chars/token approximation
        for r in results:
            chunk_chars = len(r.content)
            if used + chunk_chars > chars_budget:
                break
            packed.append(r)
            used += chunk_chars
        return packed, used // 4

    # ── Formatting ────────────────────────────────────────────────

    def _format_chunks(self, results: list[SearchResult]) -> str:
        if not results:
            return "(No relevant knowledge found)"
        parts: list[str] = []
        for i, r in enumerate(results, 1):
            header = f"[{i}] {r.title or r.source} (score={r.score:.3f})"
            parts.append(f"{header}\n{r.content.strip()}")
        return DEFAULT_CHUNK_SEP.join(parts)

    # ── Deduplication ─────────────────────────────────────────────

    def _deduplicate(self, results: list[SearchResult]) -> list[SearchResult]:
        seen_docs: set[str] = set()
        unique: list[SearchResult] = []
        for r in results:
            key = r.document_id
            # Allow up to 2 chunks from the same document
            doc_chunks = sum(1 for u in unique if u.document_id == key)
            if doc_chunks >= 2:
                continue
            unique.append(r)
        return unique


class MemoryRAGPipeline(RAGPipeline):
    """
    RAG pipeline specialised for memory queries.
    Uses the arizen_memory ChromaDB collection and memory_records SQLite table.
    """

    async def build_context(self, query: str, source: Optional[str] = None, **kwargs) -> RAGContext:
        return await super().build_context(
            query=query, source=source, collection="arizen_memory", **kwargs
        )
