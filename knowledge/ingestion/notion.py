"""
Notion Connector — ingests pages and databases from Notion via the REST API.

Ingests:
  - Pages (recursive, including child pages)
  - Database rows (title + all property values + page content)
  - Block content (paragraphs, headings, code, callouts, toggles)

Credentials:
  token       : Notion integration token (starts with secret_)
  page_ids    : list of root page IDs to ingest (recursively)
  database_ids: list of database IDs to ingest

Notion API docs: https://developers.notion.com/reference
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import AsyncIterator, Optional

import httpx

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.notion")

NOTION_API     = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionConnector(BaseConnector):
    """
    Ingests Notion pages and databases.

    Example config:
        ConnectorConfig(
            source_name="notion",
            credentials={
                "token":        "secret_xxxx",
                "page_ids":     ["page-uuid-1"],
                "database_ids": ["db-uuid-1"],
            }
        )
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        token = config.credentials.get("token", "")
        self._http = httpx.AsyncClient(
            base_url=NOTION_API,
            headers={
                "Authorization":    f"Bearer {token}",
                "Notion-Version":   NOTION_VERSION,
                "Content-Type":     "application/json",
            },
            timeout=30,
        )
        self._page_ids    = config.credentials.get("page_ids", [])
        self._database_ids = config.credentials.get("database_ids", [])
        self._visited: set[str] = set()

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/users/me")
            return r.status_code == 200
        except Exception:
            return False

    async def ingest(self) -> AsyncIterator[Document]:
        for page_id in self._page_ids:
            async for doc in self._ingest_page(page_id):
                yield doc
        for db_id in self._database_ids:
            async for doc in self._ingest_database(db_id):
                yield doc

    # ── Pages ─────────────────────────────────────────────────────

    async def _ingest_page(self, page_id: str) -> AsyncIterator[Document]:
        clean_id = page_id.replace("-", "")
        if clean_id in self._visited:
            return
        self._visited.add(clean_id)

        r = await self._http.get(f"/pages/{clean_id}")
        if r.status_code != 200:
            logger.warning("Notion page %s: %s", clean_id, r.status_code)
            return
        page = r.json()

        title   = self._extract_title(page)
        content = await self._get_blocks_text(clean_id)
        edited  = page.get("last_edited_time", "")
        created = page.get("created_time", "")

        if content.strip():
            yield Document(
                id        = "",
                source    = "notion",
                source_id = clean_id,
                title     = title,
                content   = f"# {title}\n\n{content}",
                url       = page.get("url", ""),
                created_at = _parse_notion_dt(created),
                updated_at = _parse_notion_dt(edited),
                metadata  = {
                    "type": "notion_page",
                    "notion_id": clean_id,
                    "extension": ".md",
                },
            )

        # Recurse into child pages
        children_r = await self._http.get(f"/blocks/{clean_id}/children")
        if children_r.status_code == 200:
            for block in children_r.json().get("results", []):
                if block.get("type") == "child_page":
                    async for child_doc in self._ingest_page(block["id"]):
                        yield child_doc

    # ── Databases ─────────────────────────────────────────────────

    async def _ingest_database(self, db_id: str) -> AsyncIterator[Document]:
        clean_id = db_id.replace("-", "")
        cursor: Optional[str] = None
        while True:
            body: dict = {"page_size": 100}
            if cursor:
                body["start_cursor"] = cursor
            r = await self._http.post(f"/databases/{clean_id}/query", json=body)
            if r.status_code != 200:
                break
            data = r.json()
            for page in data.get("results", []):
                async for doc in self._ingest_page(page["id"]):
                    yield doc
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")

    # ── Block extraction ──────────────────────────────────────────

    async def _get_blocks_text(self, block_id: str, depth: int = 0) -> str:
        if depth > 5:
            return ""
        r = await self._http.get(f"/blocks/{block_id}/children")
        if r.status_code != 200:
            return ""
        lines: list[str] = []
        for block in r.json().get("results", []):
            text = self._block_to_text(block)
            if text:
                indent = "  " * depth
                lines.append(f"{indent}{text}")
            if block.get("has_children"):
                child_text = await self._get_blocks_text(block["id"], depth + 1)
                if child_text:
                    lines.append(child_text)
        return "\n".join(lines)

    def _block_to_text(self, block: dict) -> str:
        btype = block.get("type", "")
        data  = block.get(btype, {})
        rt    = data.get("rich_text", [])
        text  = "".join(span.get("plain_text", "") for span in rt)
        match btype:
            case "heading_1":    return f"# {text}"
            case "heading_2":    return f"## {text}"
            case "heading_3":    return f"### {text}"
            case "paragraph":    return text
            case "bulleted_list_item": return f"- {text}"
            case "numbered_list_item": return f"1. {text}"
            case "code":         lang = data.get("language",""); return f"```{lang}\n{text}\n```"
            case "callout":      return f"> {text}"
            case "quote":        return f"> {text}"
            case "divider":      return "---"
            case "to_do":        done = data.get("checked", False); return f"[{'x' if done else ' '}] {text}"
            case _:              return text

    def _extract_title(self, page: dict) -> str:
        props = page.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title":
                parts = prop.get("title", [])
                title = "".join(p.get("plain_text", "") for p in parts)
                if title:
                    return title
        return "Untitled"

    async def close(self) -> None:
        await self._http.aclose()


def _parse_notion_dt(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()
