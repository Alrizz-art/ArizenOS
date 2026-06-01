# @arizen/mind

> Local-first AI inference layer for ArizenOS.

ArizenMind is the intelligence backbone of the entire platform. It manages local LLM inference via llama.cpp, handles context, routes streaming output, and exposes a clean API to every product that needs AI.

## What's in Here

| Export | Description |
|---|---|
| `ArizenMind` | Main client — initialize, query, stream |
| `ModelManager` | Download, cache, and switch GGUF models |
| `ContextEngine` | Conversation memory + desktop context injection |
| `StreamParser` | Token stream → structured output parser |
| `ModelNotFoundError` | Typed error classes |
| `ContextLengthError` | |

## Supported Model Families

- Llama 3 (8B, 70B)
- Phi-3 (mini, small, medium)
- Mistral 7B / Mixtral
- Gemma 2 (2B, 9B)
- Any GGUF-format model

## API

```typescript
const mind = await ArizenMind.create({ model: "llama-3-8b-q4" });

// Streaming (preferred)
const stream = await mind.query("Summarize my open PRs");
for await (const token of stream) process.stdout.write(token);

// One-shot
const text = await mind.ask("What time is it?");
```

## Privacy

All inference runs locally. No data is sent to any external server without explicit user opt-in. See [`/SECURITY.md`](../../SECURITY.md).
