"""
Archivist — Knowledge Agent.
Answers questions using RAG over the local Knowledge Vault.
"""
from __future__ import annotations

import logging
from typing import AsyncIterator

logger = logging.getLogger(__name__)


class ArchivistAgent:
    """Retrieves and synthesizes knowledge from the local vault."""

    def __init__(self, vault, llm) -> None:
        self._vault = vault
        self._llm   = llm
        logger.info("Archivist initialized")

    async def answer(self, query: str, top_k: int = 5) -> AsyncIterator[str]:
        """Answer a question using RAG."""
        results = self._vault.search(query, top_k=top_k)

        if not results:
            yield "I could not find relevant information in the local knowledge base."
            return

        context = "\n\n---\n\n".join(
            f"[{r.chunk.source}]\n{r.chunk.text}" for r in results
        )
        prompt = (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer (cite sources as [filename]):"
        )
        async for token in self._llm.stream(prompt):
            yield token
