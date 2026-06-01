# Arizen Assistant

> `@arizen/assistant` — The ArizenOS AI command layer.

A floating, always-available AI interface powered by local inference. Answers questions, summarizes content, runs agentic tasks, and maintains conversation context across your desktop session.

## Responsibilities

- Conversational AI interface (streaming, local-first)
- Desktop context awareness (active window, clipboard, screen)
- Conversation history with semantic search
- Local model management (download, switch, benchmark)
- Cloud AI opt-in (OpenAI, Anthropic — never default)

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Electron (floating always-on-top window) |
| Inference | `@arizen/mind` (llama.cpp, GGUF) |
| UI | React 18 + `@arizen/ui` |
| State | Zustand + persisted history |
| Sync | `@arizen/sync` (optional cross-device) |

## Development

```bash
pnpm --filter @arizen/assistant dev
pnpm --filter @arizen/assistant test
pnpm --filter @arizen/assistant build
```

## Module Owner

See [`/MAINTAINERS.md`](../../MAINTAINERS.md)
