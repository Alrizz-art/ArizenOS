# ArizenOS — Product & Technical Vision

## Product Vision

### The Problem

Modern computing is broken for power users who care about privacy and sovereignty:

- Cloud AI assistants send everything to remote servers — your files, your prompts, your patterns
- Windows 11 is increasingly a surveillance platform, not a tool
- Existing automation tools (Zapier, n8n) are cloud-dependent or too fragile for AI workflows
- Knowledge management is fragmented — notes, files, browser history, terminal output all live in silos
- There is no unified AI interface that feels like a natural extension of the OS

### The Solution

ArizenOS is an **AI Operating Layer** that runs entirely on your hardware.

It does not replace Windows. It **augments** it — adding an intelligence layer that:

- Understands your context (files, tasks, history, preferences)
- Acts on your behalf through specialized agents
- Automates repetitive workflows with AI-composed pipelines
- Provides a command center that speaks natural language AND keyboard shortcuts
- Runs local LLMs with sub-second latency on consumer hardware

### Target User

**Primary:** Technical power users who:
- Run Windows 10 AME for privacy/performance
- Are comfortable with terminal and scripting
- Want AI assistance without cloud dependency
- Are frustrated by fragmented tools

**Secondary:** Developers building on top of the ArizenOS plugin SDK

---

## Technical Vision

### Architecture Philosophy

ArizenOS is built on a **layered, message-passing architecture** with clean separation between:

1. **The Daemon Layer** (Rust) — Stable, fast, minimal. Manages process lifecycle, IPC, health.
2. **The Intelligence Layer** (Python) — Agents, LLMs, RAG, workflow execution. Flexible, hot-reloadable.
3. **The Presentation Layer** (TypeScript/Tauri) — UI, overlays, keyboard hooks. Native-feeling, theme-able.

### Key Technical Decisions

#### Why Rust for the Daemon?
- Sub-millisecond IPC latency
- Zero GC pauses — critical for real-time system overlay
- Memory safety without runtime overhead
- Native Windows API access for keyboard hooks, process management, named pipes

#### Why Python for the Intelligence Layer?
- Best ecosystem for LLM tooling (Ollama, llama-cpp-python, ChromaDB, LangChain)
- Rapid iteration on agent logic
- Clean async model (asyncio) matches event-driven architecture
- Agents can be replaced/updated without recompiling the daemon

#### Why Tauri + React for the UI?
- Native Windows performance (no Electron memory overhead)
- React for component-driven UI development
- Tauri's Rust backend bridges to the daemon
- Sub-100ms launch time

#### Why SQLite + ChromaDB?
- SQLite: zero-config, transactional, perfect for structured knowledge
- ChromaDB: local vector storage for semantic search
- Both are file-based — no daemon processes, easy backup

### LLM Strategy

ArizenOS uses a **tiered model strategy** based on task complexity:

```
Tier 0 (Rule-based):  Pattern matching, simple triggers, no LLM
Tier 1 (Nano):        TinyLlama Q4, Phi-3 Mini Q4 (1-3B params)
Tier 2 (Standard):    Phi-3 Medium, Mistral 7B Q4 (7-14B params)
Tier 3 (Power):       Llama 3 70B Q4, Mistral Large (32-70B params, GPU required)
```

The **LLM Gateway** automatically routes tasks to the appropriate tier based on:
- Task complexity score
- Available hardware resources
- User-configured preferences
- Response time requirements

### Agent Architecture

Inspired by LangGraph's graph-based execution model and CrewAI's role-based agent system:

```
                    ┌─────────────┐
                    │   MONARCH   │
                    │ Orchestrator│
                    └──────┬──────┘
                           │ delegates
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌────────────┐    ┌─────────┐
    │ARCHIVIST │    │  EXECUTOR  │    │ ORACLE  │
    │Knowledge │    │Task Runner │    │Research │
    └──────────┘    └────────────┘    └─────────┘
          │
    ┌─────▼────────────────────────────┐
    │          KNOWLEDGE VAULT          │
    │  ChromaDB (vectors) + SQLite      │
    └───────────────────────────────────┘
```

Each agent has:
- **A defined role and capability set** — declared in a TOML manifest
- **Memory scopes** — session (RAM), persistent (SQLite), semantic (ChromaDB)
- **Tool registry** — explicit list of permitted tools/capabilities
- **Audit trail** — every action logged with timestamp, reasoning, and output

### Communication Protocol

Internal IPC uses a **named pipe + message bus** pattern:

```
arizen-daemon (Rust)
  ├── Pipe: \\.\pipe\arizen-control    (daemon control)
  ├── Pipe: \\.\pipe\arizen-agents     (agent bus)
  ├── Pipe: \\.\pipe\arizen-events     (event stream)
  └── gRPC: localhost:50051              (structured RPC)
```

All messages are **MessagePack encoded** for performance (no JSON overhead in hot paths).
