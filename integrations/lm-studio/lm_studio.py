"""
LM Studio Client — Primary LLM + Embedding backend.

LM Studio exposes an OpenAI-compatible API at localhost:1234.
This is the authoritative integration — all other backends are fallbacks.

Endpoint reference:
  POST /v1/chat/completions  — Chat with streaming
  POST /v1/completions       — Raw completion
  POST /v1/embeddings        — Text embeddings
  GET  /v1/models            — List loaded models
"""
from __future__ import annotations

import json
import logging
from enum import IntEnum
from typing import AsyncIterator, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger("arizen.lm_studio")

DEFAULT_BASE_URL = "http://localhost:1234"


class ModelTier(IntEnum):
    RULE_BASED = 0
    NANO       = 1   # 1–3B  (Phi-3 Mini, TinyLlama)
    STANDARD   = 2   # 7–14B (Phi-3 Medium, Mistral 7B)
    POWER      = 3   # 30B+  (Llama 3 70B)


class ChatMessage(BaseModel):
    role:    str
    content: str


class LMStudioClient:
    """
    OpenAI-compatible client for LM Studio.
    Primary LLM backend for all ArizenOS intelligence modules.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout:  float = 120.0,
    ) -> None:
        self._base    = base_url.rstrip("/")
        self._client  = httpx.AsyncClient(
            base_url=self._base,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        logger.info("LM Studio client ready → %s", self._base)

    # ── Chat Completions ─────────────────────────────────────────────────────

    async def chat(
        self,
        messages:    list[ChatMessage],
        model:       Optional[str] = None,
        temperature: float = 0.7,
        max_tokens:  int   = 2048,
        stream:      bool  = True,
    ) -> AsyncIterator[str]:
        """Stream chat completion tokens."""
        payload = {
            "model":       model or await self._default_model(),
            "messages":    [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens":  max_tokens,
            "stream":      stream,
        }
        async with self._client.stream("POST", "/v1/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line.removeprefix("data: ").strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    if token := chunk["choices"][0]["delta"].get("content"):
                        yield token
                except (json.JSONDecodeError, KeyError):
                    continue

    # ── Embeddings ───────────────────────────────────────────────────────────

    async def embed(
        self,
        texts: list[str],
        model: Optional[str] = None,
    ) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        payload = {
            "input": texts,
            "model": model or "nomic-ai/nomic-embed-text-v1.5-GGUF",
        }
        resp = await self._client.post("/v1/embeddings", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]

    # ── Model Management ─────────────────────────────────────────────────────

    async def list_models(self) -> list[str]:
        """Return model IDs currently loaded in LM Studio."""
        try:
            resp = await self._client.get("/v1/models")
            resp.raise_for_status()
            return [m["id"] for m in resp.json().get("data", [])]
        except Exception as e:
            logger.warning("Could not list models: %s", e)
            return []

    async def health_check(self) -> bool:
        """Return True if LM Studio server is reachable."""
        try:
            resp = await self._client.get("/v1/models", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def _default_model(self) -> str:
        models = await self.list_models()
        return models[0] if models else "local-model"

    # ── Convenience helpers ──────────────────────────────────────────────────

    async def ask(
        self,
        prompt:  str,
        system:  Optional[str] = None,
        tier:    ModelTier = ModelTier.STANDARD,
    ) -> AsyncIterator[str]:
        """High-level: send a user prompt, optionally with a system message."""
        messages: list[ChatMessage] = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=prompt))
        async for token in self.chat(messages):
            yield token

    async def close(self) -> None:
        await self._client.aclose()
