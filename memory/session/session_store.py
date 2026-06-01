"""
Session Store — Ephemeral in-process memory.

Cleared on daemon restart. Used for active conversation context,
working variables, and per-task intermediate state.
Thread-safe via asyncio.Lock.
"""
from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from typing import Any, Optional


class SessionStore:
    """
    Scoped key-value store for a single session.
    Each agent gets its own scoped view via scope().
    """

    def __init__(self, max_entries: int = 10_000) -> None:
        self._data:  dict[str, Any] = {}
        self._times: OrderedDict[str, float] = OrderedDict()
        self._lock  = asyncio.Lock()
        self._max   = max_entries

    async def get(self, key: str, default: Any = None) -> Any:
        async with self._lock:
            return self._data.get(key, default)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            if key not in self._data and len(self._data) >= self._max:
                oldest = next(iter(self._times))
                del self._data[oldest]
                del self._times[oldest]
            self._data[key] = value
            self._times[key] = time.monotonic()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)
            self._times.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()
            self._times.clear()

    def scope(self, prefix: str) -> "ScopedSessionStore":
        """Return a scoped view of this store for a specific agent."""
        return ScopedSessionStore(self, prefix)


class ScopedSessionStore:
    """Agent-scoped view into the global session store."""

    def __init__(self, store: SessionStore, prefix: str) -> None:
        self._store  = store
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    async def get(self, key: str, default: Any = None) -> Any:
        return await self._store.get(self._key(key), default)

    async def set(self, key: str, value: Any) -> None:
        await self._store.set(self._key(key), value)

    async def delete(self, key: str) -> None:
        await self._store.delete(self._key(key))
