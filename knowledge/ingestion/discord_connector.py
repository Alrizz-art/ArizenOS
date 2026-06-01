"""
Discord Connector — ingests channel message history via Discord REST API.

No bot required for DMs / your own servers; bot token allows any accessible guild.
Ingests: channel messages, threads (batched by day)

Credentials:
  token    : Bot token (Bot <token>) or User token (use responsibly)
  guild_ids: list of guild (server) IDs to ingest
  channels : list of specific channel IDs (optional — ingest all text channels if empty)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

import httpx

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.discord")

DISCORD_API = "https://discord.com/api/v10"


class DiscordConnector(BaseConnector):
    """
    Ingests message history from Discord guilds and channels.

    Example config:
        ConnectorConfig(
            source_name="discord",
            since_days=60,
            credentials={
                "token":     "Bot YOUR_BOT_TOKEN",
                "guild_ids": ["1234567890"],
                "channels":  [],  # empty = all text channels
            }
        )
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        token = config.credentials.get("token", "")
        self._http      = httpx.AsyncClient(
            base_url=DISCORD_API,
            headers={"Authorization": token, "Content-Type": "application/json"},
            timeout=30,
        )
        self._guild_ids = config.credentials.get("guild_ids", [])
        self._channels  = set(config.credentials.get("channels", []))
        self._since     = datetime.now(timezone.utc) - timedelta(days=config.since_days)

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/users/@me")
            return r.status_code == 200
        except Exception:
            return False

    async def ingest(self) -> AsyncIterator[Document]:
        for guild_id in self._guild_ids:
            channels = await self._get_channels(guild_id)
            for ch in channels:
                if self._channels and ch["id"] not in self._channels:
                    continue
                if ch.get("type") not in (0, 5, 11, 12):   # text / news / thread
                    continue
                logger.info("Discord: ingesting #%s (%s)", ch["name"], guild_id)
                async for doc in self._ingest_channel(ch, guild_id):
                    yield doc

    async def _get_channels(self, guild_id: str) -> list[dict]:
        r = await self._http.get(f"/guilds/{guild_id}/channels")
        return r.json() if r.status_code == 200 else []

    async def _ingest_channel(self, channel: dict, guild_id: str) -> AsyncIterator[Document]:
        ch_id   = channel["id"]
        ch_name = channel.get("name", ch_id)
        batch_by_day: dict[str, list[str]] = {}

        before = None
        while True:
            params = {"limit": 100}
            if before:
                params["before"] = before
            r = await self._http.get(f"/channels/{ch_id}/messages", params=params)
            if r.status_code != 200:
                break
            messages = r.json()
            if not messages:
                break

            for msg in messages:
                ts_str = msg.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except Exception:
                    continue
                if ts < self._since:
                    # Yield accumulated batches and stop
                    for date_key, lines in sorted(batch_by_day.items()):
                        yield self._make_document(lines, channel, guild_id, date_key)
                    return

                content = msg.get("content", "").strip()
                if not content or len(content) < 5:
                    continue

                author  = msg.get("author", {}).get("username", "unknown")
                date_key = ts.date().isoformat()
                time_str = ts.strftime("%H:%M")
                batch_by_day.setdefault(date_key, []).append(f"[{time_str}] <{author}> {content}")

            before = messages[-1]["id"]
            if len(messages) < 100:
                break

        for date_key, lines in sorted(batch_by_day.items()):
            yield self._make_document(lines, channel, guild_id, date_key)

    def _make_document(self, lines: list[str], channel: dict, guild_id: str, date: str) -> Document:
        ch_name = channel.get("name", "unknown")
        content = "\n".join(lines)
        return Document(
            id        = "",
            source    = "discord",
            source_id = f"discord:{guild_id}:{channel['id']}:{date}",
            title     = f"Discord #{ch_name} — {date}",
            content   = content,
            url       = f"https://discord.com/channels/{guild_id}/{channel['id']}",
            metadata  = {
                "guild_id":    guild_id,
                "channel_id":  channel["id"],
                "channel_name": ch_name,
                "date":        date,
                "type":        "discord_messages",
                "message_count": len(lines),
            },
        )

    async def close(self) -> None:
        await self._http.aclose()
