"""
LLM Gateway — Unified interface to local language models.
Routes tasks to the appropriate model tier automatically.
Supports: Ollama (primary), llama-cpp-python (fallback).
"""
from __future__ import annotations

import json
import logging
from enum import IntEnum
from typing import AsyncIterator, Optional

import httpx

logger = logging.getLogger(__name__)


class ModelTier(IntEnum):
    RULE_BASED = 0   # No LLM — pattern matching only
    NANO       = 1   # 1-3B params  (TinyLlama, Phi-3 Mini)
    STANDARD   = 2   # 7-14B params (Phi-3 Medium, Mistral 7B)
    POWER      = 3   # 32-70B params (Llama 3 70B)


TIER_MODELS: dict[ModelTier, list[str]] = {
    ModelTier.NANO:     ["phi3:mini", "tinyllama"],
    ModelTier.STANDARD: ["phi3:medium", "mistral"],
    ModelTier.POWER:    ["llama3:70b-instruct-q4_K_M"],
}


class LLMGateway:
    """Routes inference requests to the right local LLM backend."""

    def __init__(self, ollama_url: str = "http://localhost:11434") -> None:
        self._ollama = ollama_url
        self._client = httpx.AsyncClient(timeout=120)
        logger.info("LLM Gateway initialized (Ollama: %s)", ollama_url)

    async def stream(
        self,
        prompt: str,
        tier:   ModelTier = ModelTier.STANDARD,
        system: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from the appropriate local model."""
        model    = await self._select_model(tier)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with self._client.stream(
            "POST",
            f"{self._ollama}/api/chat",
            json={"model": model, "messages": messages, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if token := chunk.get("message", {}).get("content"):
                    yield token
                if chunk.get("done"):
                    break

    async def _select_model(self, tier: ModelTier) -> str:
        candidates = TIER_MODELS.get(tier, TIER_MODELS[ModelTier.NANO])
        available  = await self._list_models()
        for c in candidates:
            if any(c in m for m in available):
                return c
        return candidates[0]

    async def _list_models(self) -> list[str]:
        try:
            r = await self._client.get(f"{self._ollama}/api/tags")
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    async def close(self) -> None:
        await self._client.aclose()
