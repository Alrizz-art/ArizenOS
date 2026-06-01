# ArizenOS — Architecture

## System Overview

ArizenOS is structured as a **layered microkernel** — a minimal Rust daemon managing a mesh of Python-based intelligence processes, bridged to a native Windows UI via Tauri.

```
╔═══════════════════════════════════════════════════════════════════╗
║                        PRESENTATION LAYER                         ║
║                                                                   ║
║   ┌─────────────────────────────────────────────────────────┐    ║
║   │                    COMMAND NEXUS                         │    ║
║   │         Tauri 2.0 + React 18 + TypeScript               │    ║
║   │                                                          │    ║
║   │  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  │    ║
║   │  │  Chat    │  │ Workflow │  │  HUD    │  │ Command │  │    ║
║   │  │  Panel   │  │ Trigger  │  │Overlay  │  │Palette  │  │    ║
║   │  └──────────┘  └──────────┘  └─────────┘  └─────────┘  │    ║
║   └─────────────────────────┬───────────────────────────────┘    ║
╚═════════════════════════════╪═════════════════════════════════════╝
                              │  Named Pipes / gRPC (localhost:50051)
╔═════════════════════════════╪═════════════════════════════════════╗
║                     DAEMON LAYER (Rust)                           ║
║                                                                   ║
║   ┌─────────────────────────▼───────────────────────────────┐    ║
║   │                   ARIZEN DAEMON                          │    ║
║   │                  (Tokio async runtime)                   │    ║
║   │                                                          │    ║
║   │  Process Manager │ IPC Router │ Health Monitor │ Config  │    ║
║   └──────────────────────────────────────────────────────────┘    ║
║         │              │              │              │             ║
║    Unix Pipe       gRPC Chan       Event Bus       REST            ║
╚═════════╪══════════════╪══════════════╪══════════════╪═════════════╝
          │              │              │              │
╔═════════╪══════════════╪══════════════╪══════════════╪═════════════╗
║                   INTELLIGENCE LAYER (Python 3.12)                ║
║                                                                   ║
║  ┌───────────┐  ┌────────────┐  ┌──────────────┐  ┌───────────┐  ║
║  │LLM GATEWAY│  │AGENT MESH  │  │  WORKFLOW    │  │KNOWLEDGE  │  ║
║  │           │  │            │  │  ENGINE      │  │  VAULT    │  ║
║  │ Ollama ──►│  │ Monarch    │  │              │  │           │  ║
║  │ llama.cpp►│  │ Archivist  │  │ YAML Parser  │  │ChromaDB   │  ║
║  │           │  │ Executor   │  │ Step Runner  │  │SQLite FTS │  ║
║  │ Tier 0–3  │  │ Sentinel   │  │ Trigger Sys  │  │File Watch │  ║
║  │ Routing   │  │ Weaver     │  │              │  │           │  ║
║  │           │  │ Oracle     │  │              │  │           │  ║
║  └───────────┘  └────────────┘  └──────────────┘  └───────────┘  ║
╚═══════════════════════════════════════════════════════════════════╝
                              │
╔═════════════════════════════╪═════════════════════════════════════╗
║                        STORAGE LAYER                              ║
║                                                                   ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    ║
║  │   ChromaDB   │  │   SQLite     │  │   File System        │    ║
║  │  (vectors)   │  │  (structured)│  │  (models, plugins,   │    ║
║  │              │  │              │  │   config, logs)       │    ║
║  │ Embeddings   │  │ Conversations│  │                      │    ║
║  │ Doc chunks   │  │ Workflows    │  │ GGUF models          │    ║
║  │ Semantic idx │  │ Audit log    │  │ Plugin dirs          │    ║
║  └──────────────┘  └──────────────┘  └──────────────────────┘    ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## IPC Protocol

### Named Pipes (Windows)

```
\\.\pipe\arizen-control     →  Daemon control (start/stop/status)
\\.\pipe\arizen-agents      →  Agent message bus
\\.\pipe\arizen-events      →  System event stream (pub/sub)
\\.\pipe\arizen-nexus       →  UI ↔ Daemon channel
```

### Message Format

All messages are **MessagePack** encoded with an envelope:

```toml
[envelope]
version = 1
message_id = "uuid-v4"
timestamp = 1720000000000   # Unix ms
source = "monarch"
target = "executor"
type = "TASK_REQUEST"

[payload]
# MessagePack-encoded task body
```

### gRPC Services

```protobuf
service ArizenDaemon {
  rpc GetStatus(Empty) returns (DaemonStatus);
  rpc ListAgents(Empty) returns (AgentList);
  rpc SendTask(Task) returns (TaskHandle);
  rpc StreamEvents(EventFilter) returns (stream Event);
}

service AgentMesh {
  rpc DelegateTask(DelegationRequest) returns (stream TaskUpdate);
  rpc GetAgentStatus(AgentId) returns (AgentStatus);
  rpc SetAgentConfig(AgentConfig) returns (Ack);
}
```

---

## Agent Graph Execution

Monarch uses a **directed acyclic graph (DAG)** model for multi-step tasks:

```
User: "Summarize all my meeting notes from this week and create action items"

Monarch Planning Phase:
┌─────────────────────────────────────────────┐
│  PLAN: summarize-weekly-meetings            │
│                                             │
│  Node 1: archivist.search                  │
│    query: "meeting notes"                  │
│    filter: date_range=this_week            │
│    output: [file_list]                     │
│         │                                  │
│  Node 2: archivist.summarize (parallel)    │
│    inputs: [file_list]                     │
│    for each: summarize(file)               │
│    output: [summaries]                     │
│         │                                  │
│  Node 3: monarch.synthesize               │
│    inputs: [summaries]                    │
│    output: combined_summary               │
│         │                                  │
│  Node 4: executor.create_file             │
│    path: ~/Documents/weekly-actions.md    │
│    content: combined_summary + actions    │
│    approval: REQUIRED                     │
└─────────────────────────────────────────────┘
```

---

## Knowledge Vault Architecture

```
Ingestion Pipeline:
  File Change Event
       │
  ┌────▼─────────┐
  │ Text Extractor│   (.txt, .md, .py, .rs, .ts, .pdf*)
  └────┬──────────┘
       │
  ┌────▼──────────┐
  │ Chunker       │   512-token chunks with 64-token overlap
  └────┬──────────┘
       │
  ┌────▼──────────────────────────────┐
  │ Embedding (nomic-embed-text v1.5) │   Local embedding model
  └────┬──────────────────────────────┘
       │              │
  ┌────▼──────┐  ┌────▼──────────┐
  │ ChromaDB  │  │ SQLite FTS5   │
  │ (vectors) │  │ (text index)  │
  └───────────┘  └───────────────┘

Query Pipeline:
  User Query
       │
  ┌────▼──────────┐
  │ Query Embed   │
  └────┬──────────┘
       │
  ┌────▼─────────────────────────────┐
  │ Hybrid Search (vector + keyword) │
  └────┬─────────────────────────────┘
       │
  ┌────▼──────────┐
  │ Rerank (MMR)  │   Maximal Marginal Relevance
  └────┬──────────┘
       │
  ┌────▼──────────┐
  │ Context Build │   Assemble prompt context
  └────┬──────────┘
       │
     LLM Response
```

---

## Data Flow — "Ask a Question"

```
User types: "What did I decide about the API design last Tuesday?"

1. [Nexus UI]       → Sends text via named pipe to daemon
2. [Daemon]         → Routes to Agent Mesh (TASK_REQUEST)
3. [Monarch]        → Classifies: knowledge query, tier 1
4. [Monarch]        → Delegates to Archivist
5. [Archivist]      → Queries Knowledge Vault
6. [Vault]          → Hybrid search: "API design decision Tuesday"
7. [Vault]          → Returns top 5 chunks + metadata
8. [Archivist]      → Builds RAG prompt
9. [LLM Gateway]    → Routes to Tier 1 (Phi-3 Mini)
10. [Ollama]        → Streams response tokens
11. [Archivist]     → Streams tokens back through mesh
12. [Daemon]        → Forwards stream to Nexus pipe
13. [Nexus UI]      → Renders streaming response with sources
```

---

## Security Model

| Boundary | Mechanism |
|----------|-----------|
| Agent ↔ Filesystem | Declared path allowlist in agent manifest |
| Agent ↔ Network | Disabled by default, opt-in per agent |
| Plugin ↔ System | Process-level isolation (separate user context) |
| Agent ↔ Agent | Message bus only — no shared memory |
| Destructive actions | Approval gate (logged, undoable) |
| LLM prompts | Stored locally, opt-out hash logging |
| Config secrets | Windows DPAPI encrypted at rest |
