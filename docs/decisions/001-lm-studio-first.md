# ADR-001: LM Studio as Primary LLM Backend

**Date:** 2025-06  
**Status:** Accepted  
**Owner:** AI Platform team

## Context

ArizenOS needs a local LLM inference backend. Candidates evaluated:
- LM Studio (OpenAI-compatible API, GUI, wide model support)
- Ollama (headless daemon, CLI-first)
- llama-cpp-python (embedded, no separate process)

## Decision

**LM Studio is the primary backend.** All LLM calls attempt LM Studio first.

## Rationale

1. **Windows-native UX.** LM Studio has a polished Windows installer and GUI, which aligns with our Windows-first posture. Users without technical backgrounds can download and configure models through a familiar interface.

2. **OpenAI-compatible API.** LM Studio exposes an OpenAI-compatible server at `localhost:1234`. This means our `integrations/lm-studio` client is also fully compatible with OpenAI's SDK — zero abstraction cost.

3. **Model flexibility.** LM Studio supports GGUF, MLX, and soon other formats. Users can switch models in LM Studio's UI without touching ArizenOS config.

4. **Embedding support.** LM Studio's API includes an `/embeddings` endpoint using the loaded model. We can use the same server for both completion and embedding, reducing resource overhead.

5. **User adoption.** Many Windows power users already have LM Studio installed. ArizenOS treats LM Studio as an assumed prerequisite rather than something to compete with.

## Fallback Order

```
LM Studio (localhost:1234) → Ollama (localhost:11434) → llama-cpp-python (embedded)
```

Fallback triggers on:
- Connection refused (service not running)
- Timeout > configured threshold
- Explicit `backend` config override

## Consequences

- Our CI/CD tests against a mock OpenAI-compatible server (no real LM Studio in CI)
- `integrations/lm-studio/` is a first-class module with full documentation
- `docs/guides/lm-studio-setup.md` is a required part of the getting-started guide
- All new LLM features are tested against LM Studio first
