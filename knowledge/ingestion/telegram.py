"""
Telegram Connector — ingests messages and media from Telegram channels/chats
using the Telethon async client library.

Supports:
  - Personal chat history (with yourself — Saved Messages)
  - Channel messages (public channels by username, private by invite)
  - Group messages
  - Message text, forwarded content, and reply chains

Credentials:
  api_id     : Telegram API ID (from my.telegram.org)
  api_hash   : Telegram API hash
  session    : session string (from StringSession)
  targets    : list of chat usernames / IDs to ingest
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.telegram")


class TelegramConnector(BaseConnector):
    """
    Ingests message history from Telegram chats and channels.

    Authentication uses a session string — generate once with Telethon's
    StringSession, then store as an ArizenOS secret.

    Example config:
        ConnectorConfig(
            source_name="telegram",
            since_days=90,
            credentials={
                "api_id":   12345,
                "api_hash": "abc123...",
                "session":  "1Bv...",           # StringSession
                "targets":  ["@arizendev", "me"]  # me = Saved Messages
            }
        )
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        self._api_id   = config.credentials.get("api_id")
        self._api_hash = config.credentials.get("api_hash", "")
        self._session  = config.credentials.get("session", "")
        self._targets  = config.credentials.get("targets", ["me"])
        self._since    = datetime.now(timezone.utc) - timedelta(days=config.since_days)

    async def health_check(self) -> bool:
        try:
            from telethon import TelegramClient  # noqa
            return bool(self._api_id and self._api_hash and self._session)
        except ImportError:
            logger.warning("telethon not installed — pip install telethon")
            return False

    async def ingest(self) -> AsyncIterator[Document]:
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
        except ImportError:
            logger.error("telethon not installed — skipping Telegram ingestion")
            return

        async with TelegramClient(StringSession(self._session), self._api_id, self._api_hash) as client:
            for target in self._targets:
                try:
                    entity = await client.get_entity(target)
                    name   = getattr(entity, "title", None) or getattr(entity, "username", str(target))
                    logger.info("Telegram: ingesting %s (%s)", target, name)
                    async for doc in self._ingest_entity(client, entity, name, target):
                        yield doc
                except Exception as exc:
                    logger.error("Failed to ingest Telegram target %s: %s", target, exc)

    async def _ingest_entity(self, client, entity, name: str, target_id) -> AsyncIterator[Document]:
        batch: list[str] = []
        batch_meta: dict = {}
        batch_date: datetime | None = None

        async for msg in client.iter_messages(entity, offset_date=None, reverse=False):
            if msg.date and msg.date.replace(tzinfo=timezone.utc) < self._since:
                break
            if not msg.text:
                continue

            text = msg.text.strip()
            if not text or len(text) < 10:
                continue

            # Group messages into daily batches (fewer, denser documents)
            msg_date = msg.date.date() if msg.date else None
            if batch_date and msg_date != batch_date and batch:
                yield self._make_document(batch, batch_meta, name, target_id, batch_date)
                batch = []

            batch.append(f"[{msg.date.strftime('%H:%M')}] {text}")
            batch_meta = {
                "sender_id": getattr(msg, "sender_id", ""),
                "chat_id":   str(entity.id),
                "chat_name": name,
            }
            batch_date = msg_date

        if batch:
            yield self._make_document(batch, batch_meta, name, target_id, batch_date)

    def _make_document(self, messages: list[str], meta: dict, name: str, target, date) -> Document:
        content = "\n".join(messages)
        date_str = str(date) if date else "unknown"
        return Document(
            id        = "",
            source    = "telegram",
            source_id = f"telegram:{meta.get('chat_id',str(target))}:{date_str}",
            title     = f"Telegram: {name} — {date_str}",
            content   = content,
            url       = "",
            metadata  = {**meta, "type": "telegram_messages", "date": date_str, "message_count": len(messages)},
        )
