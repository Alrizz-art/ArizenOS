# ArizenOS — Feature Matrix

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Planned for v1.0 (MVP) |
| 🔄 | Planned for v1.x (post-MVP) |
| 🔮 | Future / experimental |
| ❌ | Explicitly out of scope |

---

## Core Platform

### Arizen Daemon

| Feature | Status | Notes |
|---------|--------|-------|
| Process lifecycle management | ✅ | Start/stop/restart all subsystems |
| Named pipe IPC bus | ✅ | Windows-native, sub-ms latency |
| gRPC internal API | ✅ | Structured RPC for agent communication |
| Health monitoring | ✅ | Per-component health checks |
| Auto-restart on crash | ✅ | Supervised process tree |
| Hot reload for agents | 🔄 | Reload agent without daemon restart |
| Plugin sandboxing | 🔄 | Process-level isolation per plugin |
| Remote control (LAN) | 🔮 | Optional, disabled by default |

### LLM Gateway

| Feature | Status | Notes |
|---------|--------|-------|
| Ollama backend | ✅ | Primary LLM backend |
| llama.cpp backend | ✅ | Fallback / CUDA direct |
| LM Studio backend | 🔄 | Via OpenAI-compatible API |
| Tiered model routing | ✅ | Auto-select model by task tier |
| CUDA acceleration | ✅ | NVIDIA RTX |
| ROCm acceleration | 🔄 | AMD RX 7000 series |
| Prompt template library | ✅ | Per-agent, per-task templates |
| Streaming token output | ✅ | Real-time streaming to UI |
| Context window management | ✅ | Auto-truncation, summarization |
| Model hot-swap | 🔄 | Change model without restart |
| Quantization selection | ✅ | Q4, Q5, Q8 per model |

### Knowledge Vault

| Feature | Status | Notes |
|---------|--------|-------|
| File indexing (text, MD, code) | ✅ | Watches configured directories |
| Semantic search (ChromaDB) | ✅ | Vector similarity search |
| Keyword search (SQLite FTS5) | ✅ | Fast exact/fuzzy text search |
| Browser history ingestion | 🔄 | Chrome/Firefox/Brave |
| Terminal history ingestion | ✅ | PowerShell 7 command history |
| PDF ingestion | 🔄 | Extract text from PDFs |
| Note-taking integration | 🔄 | Obsidian vault compatible |
| Conversation memory | ✅ | Per-agent, per-session |
| Knowledge graph | 🔮 | Entity linking between documents |

---

## Agent Mesh

### Monarch (Orchestrator)

| Feature | Status | Notes |
|---------|--------|-------|
| Natural language task decomposition | ✅ | Break NL requests into agent tasks |
| Agent delegation & result synthesis | ✅ | Route to specialist agents |
| Multi-step planning (LangGraph style) | ✅ | DAG-based execution plans |
| Plan visualization in Nexus | 🔄 | Show execution graph in UI |
| Retry & fallback logic | ✅ | Auto-retry failed agent calls |
| Human-in-the-loop approval gates | ✅ | Pause for confirmation on critical tasks |
| Parallel agent execution | 🔄 | Run independent sub-tasks concurrently |

### Archivist (Knowledge Agent)

| Feature | Status | Notes |
|---------|--------|-------|
| Semantic document retrieval (RAG) | ✅ | Query knowledge vault |
| Document summarization | ✅ | Summarize files/folders |
| Knowledge synthesis | ✅ | Answer questions from local corpus |
| Automatic re-indexing | ✅ | Watch for file changes |
| Citation tracking | 🔄 | Show sources for answers |

### Executor (Task Agent)

| Feature | Status | Notes |
|---------|--------|-------|
| PowerShell command execution | ✅ | Sandboxed, audited |
| File system operations | ✅ | Read, write, move, delete (with approval) |
| Application launching | ✅ | Open apps, URLs, documents |
| Clipboard management | ✅ | Read/write clipboard |
| Screenshot capture | ✅ | Full screen or region |
| Process management | 🔄 | Kill/prioritize processes |
| Registry operations | 🔮 | Gated behind elevated approval |

### Sentinel (Monitor Agent)

| Feature | Status | Notes |
|---------|--------|-------|
| CPU/GPU/RAM/Disk monitoring | ✅ | Continuous system metrics |
| Anomaly detection | 🔄 | LLM-assisted pattern detection |
| Alert rules (rule-based) | ✅ | Threshold-based alerts |
| Process watchdog | ✅ | Restart configured processes on crash |
| Performance history | ✅ | SQLite-backed metrics storage |
| Network usage monitoring | 🔄 | Per-process network stats |

### Weaver (Workflow Agent)

| Feature | Status | Notes |
|---------|--------|-------|
| YAML workflow definitions | ✅ | Declarative workflow language |
| Time-based triggers (cron) | ✅ | Standard cron expressions |
| Event-based triggers | ✅ | File change, process start, hotkey |
| NL workflow composition | 🔄 | Describe a workflow in plain language |
| Workflow library (built-in) | ✅ | 20+ pre-built workflow templates |
| Workflow version control | 🔄 | Git-tracked workflow changes |
| Conditional branches | ✅ | if/else in workflow steps |
| Error handling & retry | ✅ | Per-step retry configuration |

### Oracle (Research Agent)

| Feature | Status | Notes |
|---------|--------|-------|
| Local knowledge research | ✅ | Query + synthesize from local corpus |
| Multi-document synthesis | ✅ | Combine info from multiple sources |
| Structured report generation | ✅ | Markdown reports |
| Optional web search (offline-first) | 🔄 | Requires explicit opt-in |

---

## Command Nexus (UI)

| Feature | Status | Notes |
|---------|--------|-------|
| Global hotkey activation | ✅ | Win+Space or custom binding |
| Natural language input | ✅ | Primary interaction mode |
| Command palette (Ctrl+K) | ✅ | Searchable command list |
| System status HUD | ✅ | CPU/GPU/RAM + agent status |
| Conversation history | ✅ | Per-session, searchable |
| Workflow trigger panel | ✅ | List and trigger workflows |
| Agent status panel | 🔄 | Live agent activity view |
| File quick-launch | ✅ | Fuzzy file search |
| Dark mode only | ✅ | AME aesthetic |
| Themes (community) | 🔮 | CSS-overridable components |
| Multi-monitor awareness | 🔄 | Nexus on any display |
| Floating overlay mode | 🔄 | Transparent overlay on desktop |

---

## Plugin System

| Feature | Status | Notes |
|---------|--------|-------|
| Plugin SDK (Python) | ✅ | Create custom agents and tools |
| Plugin SDK (Rust) | 🔄 | Performance-critical plugins |
| Plugin manifest (TOML) | ✅ | Declarative capability declaration |
| Plugin hot-install | 🔄 | Install without daemon restart |
| Plugin store | 🔮 | Community plugin registry |
| Plugin sandboxing | 🔄 | Process-level isolation |
