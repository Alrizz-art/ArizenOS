"""
Arizen Researcher — Web Search, Document Retrieval, and Synthesis Agent.

Researcher handles all information-gathering tasks: querying local SearXNG
instances, fetching and parsing web pages, summarizing documents, and
synthesizing multi-source answers. Network access is opt-in and fully
audited.

All invocations come from Commander — never from the user directly.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import AsyncIterator
from urllib.parse import quote_plus

from agents._base.base_agent import AgentContext, AgentManifest, BaseAgent
from agents._base.tool_registry import tool

logger = logging.getLogger("arizen.researcher")


@dataclass
class Source:
    url:     str   = ""
    title:   str   = ""
    snippet: str   = ""
    content: str   = ""
    score:   float = 0.0


@dataclass
class ResearchResult:
    query:    str          = ""
    answer:   str          = ""
    sources:  list[Source] = field(default_factory=list)
    verified: bool         = False


class ResearcherAgent(BaseAgent):
    """
    Arizen Researcher — searches, retrieves, and synthesises information.

    Execution model:
        1. Parse research query from Commander inputs
        2. Route: local-docs search (Memory) vs. web search
        3. Fetch top sources (parallel, timeout-gated)
        4. Chunk and rank content by relevance
        5. Build RAG context and stream synthesised answer
        6. Attach source citations to result
    """

    MANIFEST = AgentManifest(
        name="researcher",
        display="Arizen Researcher",
        version="1.0.0",
        tier=2,
        tools=[
            "web.search",
            "web.fetch",
            "web.fetch_parallel",
            "docs.local_search",
            "docs.summarize",
        ],
        memory_scopes=["session"],
        fs_access=False,
        net_access=True,       # explicit opt-in; all requests are logged
        llm_tier="standard",
        autostart=True,
        max_restart=5,
    )

    # SearXNG local instance (default; user-configurable)
    SEARXNG_BASE: str = "http://localhost:8888"
    MAX_SOURCES:  int = 5
    FETCH_TIMEOUT: int = 10  # seconds

    def __init__(self, ctx: AgentContext, bus, llm, http_client) -> None:
        super().__init__(ctx)
        self._bus    = bus
        self._llm    = llm
        self._http   = http_client

    async def handle(self, task: dict) -> AsyncIterator[str]:
        action = task.get("tool", "research.web").split(".")[-1]
        query  = task.get("query", "")
        mode   = task.get("mode", "web")   # web | docs | hybrid

        if mode == "docs" or action == "docs":
            result = await self._local_docs(query)
        elif mode == "hybrid":
            result = await self._hybrid(query)
        else:
            result = await self._web_search(query)

        yield self._format_result(result)

    # ------------------------------------------------------------------
    # Search strategies
    # ------------------------------------------------------------------

    async def _web_search(self, query: str) -> ResearchResult:
        sources = await self._searxng(query)
        sources = await self._fetch_all(sources[:self.MAX_SOURCES])
        answer  = await self._synthesize(query, sources)
        return ResearchResult(query=query, answer=answer, sources=sources)

    async def _local_docs(self, query: str) -> ResearchResult:
        raw = await self._bus.delegate(
            "memory", "memory.semantic_search",
            {"query": query, "limit": 5}
        )
        sources = [Source(title=r.get("title",""), content=r.get("text",""), score=r.get("score",0)) for r in (raw or [])]
        answer  = await self._synthesize(query, sources)
        return ResearchResult(query=query, answer=answer, sources=sources, verified=True)

    async def _hybrid(self, query: str) -> ResearchResult:
        import asyncio
        web_task  = asyncio.create_task(self._web_search(query))
        docs_task = asyncio.create_task(self._local_docs(query))
        web, docs = await asyncio.gather(web_task, docs_task)
        merged_sources = docs.sources + web.sources
        answer = await self._synthesize(query, merged_sources)
        return ResearchResult(query=query, answer=answer, sources=merged_sources, verified=True)

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    @tool(name="web.search", side_effects="read_only")
    async def _searxng(self, query: str) -> list[Source]:
        """Query local SearXNG instance. Fully private — no external tracking."""
        url = f"{self.SEARXNG_BASE}/search?q={quote_plus(query)}&format=json"
        try:
            resp = await self._http.get(url, timeout=self.FETCH_TIMEOUT)
            data = resp.json()
            return [
                Source(
                    url=r.get("url",""),
                    title=r.get("title",""),
                    snippet=r.get("content",""),
                    score=r.get("score", 0.0),
                )
                for r in data.get("results", [])
            ]
        except Exception as exc:
            logger.error("SearXNG query failed: %s", exc)
            return []

    @tool(name="web.fetch", side_effects="read_only")
    async def _fetch_page(self, source: Source) -> Source:
        """Fetch and extract main text from a web page."""
        try:
            resp = await self._http.get(source.url, timeout=self.FETCH_TIMEOUT)
            # Basic extraction — strip HTML tags
            import re
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            source.content = text[:4000]  # cap at 4k chars per source
        except Exception as exc:
            logger.debug("Fetch failed for %s: %s", source.url, exc)
        return source

    @tool(name="web.fetch_parallel", side_effects="read_only")
    async def _fetch_all(self, sources: list[Source]) -> list[Source]:
        import asyncio
        return await asyncio.gather(*(self._fetch_page(s) for s in sources))

    async def _synthesize(self, query: str, sources: list[Source]) -> str:
        context_blocks = "\n\n".join(
            f"[{i+1}] {s.title}\n{s.snippet or s.content[:800]}"
            for i, s in enumerate(sources) if s.content or s.snippet
        )
        system = (
            "You are a research synthesizer. Answer the query using only "
            "the provided sources. Cite sources as [1], [2], etc. "
            "If sources are insufficient, say so clearly."
        )
        prompt = f"Query: {query}\n\nSources:\n{context_blocks}\n\nAnswer:"
        return await self._llm.complete(prompt, system=system, tier="standard")

    def _format_result(self, result: ResearchResult) -> str:
        citations = "\n".join(
            f"[{i+1}] {s.title or s.url}"
            for i, s in enumerate(result.sources) if s.url or s.title
        )
        return f"{result.answer}\n\n---\nSources:\n{citations}" if citations else result.answer
