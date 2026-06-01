# ArizenOS — Repository Structure

> **Platform posture:** Windows-first · LM Studio-first · Local AI-first

---

## Guiding Laws

1. **Tier cannot import upward.** Tier 0 never knows about Tier 3. Tier 1 never knows about Tier 2.
2. **Apps talk to everything via IPC only.** No app module imports a Python package directly.
3. **LM Studio is the primary LLM backend.** All `integrations/lm-studio` paths are first-class citizens; all others are fallbacks.
4. **Every public API is declared in `core/primitives`.** Cross-module contracts live there, not in the modules themselves.
5. **`branding/` is a one-way dependency.** It exports — nothing imports it except apps.

---

## Tier Map

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 4 — Support        branding · docs · scripts              │
├─────────────────────────────────────────────────────────────────┤
│  TIER 3 — Product        apps · voice · playbooks               │
├─────────────────────────────────────────────────────────────────┤
│  TIER 2 — Intelligence   agents · memory · knowledge · skills   │
├─────────────────────────────────────────────────────────────────┤
│  TIER 1 — Platform       runtime · services · integrations      │
├─────────────────────────────────────────────────────────────────┤
│  TIER 0 — Foundation     core                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Reference

### `apps/`

> **Owner:** Product team · **Lang:** TypeScript (Tauri/React) + Rust (Tauri backend) · **Tier:** 3

User-facing applications. Each app is an independently deployable unit.
All communication with the daemon is through IPC (named pipes / gRPC). Apps never import Python packages.

```
apps/
├── command-nexus/          # Primary AI command center (Tauri 2.0 + React 18 + TypeScript)
│   ├── src/                #   React components and state
│   ├── src-tauri/          #   Rust Tauri backend — bridges IPC to UI
│   ├── public/
│   └── package.json
│
├── hud-overlay/            # Always-on desktop HUD (system stats, agent status, alerts)
│   ├── src/
│   ├── src-tauri/
│   └── package.json
│
├── settings-panel/         # ArizenOS settings UI (preferences, agent config, model selection)
│   ├── src/
│   ├── src-tauri/
│   └── package.json
│
└── installer/              # Windows installer package
    ├── wix/                #   WiX toolset XML definitions
    ├── assets/             #   Installer assets (banner, icons)
    └── build.ps1           #   Build script → .msi output
```

**Responsibilities:**
- Render UI and handle user interaction
- Subscribe to event streams from the daemon
- Send commands to the daemon via IPC
- Manage app window state (show/hide, hotkey activation)

**Forbidden:**
- Direct imports from `agents/`, `memory/`, `knowledge/` — must go through runtime IPC
- Network calls that bypass the daemon

---

### `agents/`

> **Owner:** AI team · **Lang:** Python 3.12+ · **Tier:** 2

The AI agent mesh. Each agent is a self-contained process with declared capabilities.
Agents communicate only through the `runtime/` IPC bus — never with direct function calls across agents.

```
agents/
├── _base/                  # Abstract base agent class and agent manifest spec
│   ├── base_agent.py       #   BaseAgent ABC — all agents inherit this
│   ├── manifest.py         #   AgentManifest dataclass
│   └── tool_registry.py    #   Declarative tool registration decorator
│
├── monarch/                # Master orchestrator — plans, delegates, synthesizes
│   ├── monarch_agent.py    #   Core agent implementation
│   ├── planner.py          #   DAG task planner (LangGraph-inspired)
│   ├── delegator.py        #   Sub-task delegation and result collection
│   ├── synthesizer.py      #   Response synthesis from multi-agent results
│   └── manifest.toml       #   Capability declaration
│
├── archivist/              # Knowledge agent — RAG over local corpus
│   ├── archivist_agent.py
│   ├── retriever.py        #   Query → Knowledge Vault
│   ├── summarizer.py       #   Document/folder summarization
│   └── manifest.toml
│
├── executor/               # OS task agent — shell, filesystem, app launch
│   ├── executor_agent.py
│   ├── approval_gate.py    #   Destructive action approval
│   ├── tool_shell.py       #   PowerShell execution
│   ├── tool_filesystem.py  #   File operations
│   ├── tool_appcontrol.py  #   App launch / window management
│   └── manifest.toml
│
├── sentinel/               # System monitor — health, alerts, resource watch
│   ├── sentinel_agent.py
│   ├── metrics.py          #   CPU/GPU/RAM/disk collection
│   ├── alert_rules.py      #   Rule-based and LLM-based alerting
│   ├── watchdog.py         #   Process restart watchdog
│   └── manifest.toml
│
├── weaver/                 # Workflow agent — runs playbooks, composes automations
│   ├── weaver_agent.py
│   ├── playbook_runner.py  #   Delegates to playbooks/ engine
│   ├── composer.py         #   NL → YAML workflow composition (v1.x)
│   └── manifest.toml
│
└── oracle/                 # Research agent — multi-source synthesis
    ├── oracle_agent.py
    ├── researcher.py       #   Query decomposition and source aggregation
    ├── synthesizer.py      #   Multi-document synthesis
    └── manifest.toml
```

**Responsibilities:**
- Implement agent role logic using declared tools
- Maintain agent-scoped memory via `memory/`
- Retrieve knowledge via `knowledge/`
- Execute low-level operations through `skills/`
- Report health to sentinel

**Forbidden:**
- Cross-agent function imports (use IPC bus)
- Direct filesystem access outside declared sandbox paths
- Any network call not in `manifest.toml` capability list

---

### `core/`

> **Owner:** Platform team · **Lang:** Rust · **Tier:** 0

The foundational layer. Contains types, traits, error definitions, configuration schema, and structured logging.
**No business logic. No external dependencies beyond std and serde.**

```
core/
├── primitives/             # Canonical types used across all modules
│   ├── src/
│   │   ├── agent.rs        #   AgentId, AgentStatus, AgentManifest types
│   │   ├── task.rs         #   Task, TaskHandle, TaskStatus types
│   │   ├── message.rs      #   Envelope, MessageType — IPC wire format
│   │   ├── model.rs        #   ModelTier, ModelProfile, LLMRequest/Response
│   │   ├── knowledge.rs    #   Chunk, SearchResult, SearchQuery types
│   │   └── lib.rs
│   └── Cargo.toml
│
├── config/                 # Configuration management
│   ├── src/
│   │   ├── schema.rs       #   ArizenConfig TOML schema (serde)
│   │   ├── loader.rs       #   Config file discovery + loading
│   │   ├── watcher.rs      #   Hot-reload config on file change
│   │   └── lib.rs
│   └── Cargo.toml
│
├── errors/                 # Canonical error types (thiserror)
│   ├── src/
│   │   ├── daemon.rs
│   │   ├── ipc.rs
│   │   ├── agent.rs
│   │   └── lib.rs
│   └── Cargo.toml
│
└── logging/                # Structured logging setup (tracing + tracing-subscriber)
    ├── src/
    │   ├── init.rs         #   Log init (JSON for prod, pretty for dev)
    │   ├── fields.rs       #   Standard log field names
    │   └── lib.rs
    └── Cargo.toml
```

**Responsibilities:**
- Define all cross-module data contracts in Rust types
- Provide configuration loading with validation
- Provide consistent error handling primitives
- Setup structured logging for the entire daemon process

**Forbidden:**
- Business logic of any kind
- Imports from runtime/, agents/, integrations/
- Network or filesystem I/O (except config file reading)

---

### `runtime/`

> **Owner:** Platform team · **Lang:** Rust · **Tier:** 1

The process spine of ArizenOS. The Tokio daemon that manages everything.

```
runtime/
├── daemon/                 # Main entry point — the arizen.exe binary
│   ├── src/
│   │   ├── main.rs         #   Tokio entry, subsystem startup sequence
│   │   ├── lifecycle.rs    #   Boot, ready, shutdown state machine
│   │   └── health.rs       #   Daemon health endpoint
│   └── Cargo.toml
│
├── ipc/                    # IPC layer — named pipes + gRPC
│   ├── src/
│   │   ├── pipe_server.rs  #   Windows named pipe server (async)
│   │   ├── pipe_client.rs  #   Named pipe client for Tauri apps
│   │   ├── grpc_server.rs  #   tonic gRPC service impl
│   │   ├── router.rs       #   Route messages to subsystems
│   │   ├── codec.rs        #   MessagePack encode/decode
│   │   └── lib.rs
│   ├── proto/
│   │   └── arizen.proto    #   gRPC service definitions
│   └── Cargo.toml
│
├── process-manager/        # Python agent process lifecycle
│   ├── src/
│   │   ├── manager.rs      #   Spawn, kill, restart agent processes
│   │   ├── registry.rs     #   Running process registry
│   │   ├── supervisor.rs   #   Auto-restart on crash with backoff
│   │   └── lib.rs
│   └── Cargo.toml
│
├── scheduler/              # Cron + event-driven task scheduling
│   ├── src/
│   │   ├── scheduler.rs    #   tokio-cron-scheduler integration
│   │   ├── triggers.rs     #   Trigger types: Time, Event, Hotkey, FileChange
│   │   ├── queue.rs        #   Priority task queue
│   │   └── lib.rs
│   └── Cargo.toml
│
└── sandbox/                # Agent process isolation
    ├── src/
    │   ├── profile.rs      #   Sandbox capability profiles
    │   ├── enforcer.rs     #   Capability enforcement at process level
    │   └── lib.rs
    └── Cargo.toml
```

**Responsibilities:**
- Boot and manage all subsystems
- Provide IPC for app ↔ daemon and daemon ↔ agent communication
- Manage Python agent process lifecycle (spawn, kill, supervise)
- Schedule time-based and event-based task execution
- Enforce agent process sandboxing

**Dependency rule:** imports `core/` only. Never imports `agents/` directly.

---

### `memory/`

> **Owner:** AI team · **Lang:** Python 3.12+ · **Tier:** 2

Three-tier memory architecture. Every agent gets a scoped view into all three tiers.

```
memory/
├── session/                # Ephemeral in-process memory (cleared on restart)
│   ├── session_store.py    #   Thread-safe dict-backed context store
│   ├── message_buffer.py   #   Rolling conversation window with token count
│   └── context_window.py   #   LLM context assembly + overflow truncation
│
├── persistent/             # Long-lived SQLite memory
│   ├── store.py            #   SQLite connection pool + migrations
│   ├── conversations.py    #   Conversation history with full-text search
│   ├── agent_state.py      #   Per-agent persistent state
│   ├── facts.py            #   Extracted facts / preferences
│   └── migrations/         #   SQL migration files (001_init.sql, ...)
│
├── semantic/               # Vector memory (ChromaDB)
│   ├── vector_store.py     #   ChromaDB client wrapper
│   ├── embedder.py         #   Local embedding via LM Studio or sentence-transformers
│   ├── collections.py      #   Collection management per agent/context
│   └── search.py           #   Similarity search with MMR reranking
│
└── working/                # Active working memory (current task context buffer)
    ├── working_memory.py   #   Short-lived scratchpad for multi-step tasks
    ├── scratch.py          #   Intermediate reasoning storage
    └── token_budget.py     #   Token budget tracker per LLM call
```

**Responsibilities:**
- Provide agents with consistent memory read/write API regardless of tier
- Manage context window assembly for LLM calls
- Store and retrieve conversation history
- Maintain per-agent semantic memory with vector search

**Dependency rule:** imports `core/` (for config path) only.

---

### `knowledge/`

> **Owner:** AI team · **Lang:** Python 3.12+ · **Tier:** 2

The local knowledge base. Turns files, notes, and terminal history into a queryable corpus.

```
knowledge/
├── vault/                  # Unified knowledge store interface
│   ├── vault.py            #   KnowledgeVault — single API over all backends
│   ├── namespace.py        #   Namespace management (per-project, global)
│   └── permissions.py      #   Namespace access control
│
├── indexer/                # Ingestion pipeline
│   ├── pipeline.py         #   Orchestrates: load → extract → chunk → embed → store
│   ├── watcher.py          #   File system watcher → incremental re-index
│   ├── chunker.py          #   Token-aware recursive text splitter
│   └── deduplicator.py     #   Content-hash dedup before embedding
│
├── embedder/               # Local embedding models
│   ├── embedder.py         #   Embedding interface
│   ├── lmstudio.py         #   LM Studio embedding endpoint (primary)
│   ├── sentence_transformers.py  # Sentence-transformers (offline fallback)
│   └── cache.py            #   Embedding cache (SQLite-backed)
│
├── retrieval/              # Query and search
│   ├── hybrid_search.py    #   BM25 (keyword) + vector (semantic) fusion
│   ├── reranker.py         #   Cross-encoder MMR reranking
│   ├── query_expander.py   #   LLM-assisted query expansion (HyDE)
│   └── citation.py         #   Source citation and evidence tracking
│
└── ingestors/              # File type handlers
    ├── base.py             #   BaseIngestor ABC
    ├── text.py             #   .txt, .md, .rst
    ├── code.py             #   .py, .rs, .ts, .js, .go, .cs
    ├── pdf.py              #   PDF text extraction (pdfplumber)
    ├── docx.py             #   Word documents (python-docx)
    ├── powershell_history.py  # PSReadLine history ingestion
    └── browser_history.py  #   Chrome/Firefox/Edge history (opt-in)
```

**Responsibilities:**
- Ingest and index local files incrementally
- Provide hybrid BM25 + vector search over indexed corpus
- Manage knowledge namespaces per project/context
- Expose embedding API that routes to LM Studio first

**LM Studio note:** All embedding calls attempt `integrations/lm-studio` first;
fall back to `sentence_transformers` if LM Studio is not running.

---

### `playbooks/`

> **Owner:** Product team · **Lang:** Python 3.12+ · **Tier:** 3

Declarative workflow automation. A playbook is a YAML file that defines a sequence of steps,
conditions, triggers, and error handling — executable by Weaver agent or directly by the scheduler.

```
playbooks/
├── schema/                 # Playbook YAML schema definition
│   ├── schema.py           #   Pydantic v2 schema — validates YAML at load time
│   ├── playbook_schema.yaml  # JSON Schema (machine-readable)
│   └── examples/           #   Example playbook YAML files
│
├── engine/                 # Runtime execution
│   ├── executor.py         #   Step-by-step playbook runner (async)
│   ├── step_runner.py      #   Individual step execution with retry
│   ├── context.py          #   Playbook execution context and variable scope
│   ├── conditions.py       #   Condition evaluator (if/else/switch)
│   └── audit.py            #   Execution audit trail (SQLite)
│
├── triggers/               # Trigger system
│   ├── trigger_registry.py #   Register and resolve triggers
│   ├── cron_trigger.py     #   Time-based (standard cron syntax)
│   ├── file_trigger.py     #   File create/modify/delete
│   ├── event_trigger.py    #   Daemon event bus subscription
│   ├── hotkey_trigger.py   #   Global hotkey trigger
│   └── agent_trigger.py    #   Triggered by agent request
│
├── library/                # Built-in playbook library (ships with ArizenOS)
│   ├── daily_brief.yaml    #   Morning digest: calendar + tasks + news
│   ├── code_review.yaml    #   Auto summarize recent git changes
│   ├── backup_notes.yaml   #   Nightly knowledge base backup
│   ├── clip_processor.yaml #   Process clipboard content with AI
│   ├── focus_mode.yaml     #   Enable focus: close apps, mute notifications
│   └── ...                 #   20+ built-in playbooks
│
└── user/                   # User-defined playbooks (created at runtime)
    └── .gitkeep            #   Populated by user — not committed to repo
```

**Playbook YAML format:**

```yaml
# Example: playbooks/library/clip_processor.yaml
name: Clip Processor
version: "1.0"
description: Process clipboard content with the selected agent
trigger:
  type: hotkey
  binding: "Win+Shift+A"
variables:
  agent: archivist
steps:
  - id: read_clip
    skill: clipboard.read
    output: clip_content

  - id: process
    agent: "{{ variables.agent }}"
    prompt: "Summarize and extract action items from: {{ clip_content }}"
    output: result

  - id: write_back
    skill: clipboard.write
    input: "{{ result }}"
    approval: false

on_error:
  action: notify
  message: "Clip Processor failed at step {{ step.id }}: {{ error }}"
```

---

### `skills/`

> **Owner:** AI team · **Lang:** Python 3.12+ · **Tier:** 2

Atomic, reusable capabilities callable by any agent or playbook.
A skill is a single function with a declared schema, side-effect profile, and approval requirement.

```
skills/
├── sdk/                    # Skill development SDK
│   ├── base_skill.py       #   @skill decorator + BaseSkill ABC
│   ├── manifest.py         #   SkillManifest — name, schema, side_effects, requires_approval
│   ├── registry.py         #   Global skill registry
│   └── testing.py          #   Skill unit test harness
│
├── filesystem/             # File system operations
│   ├── read.py             #   Read file/directory
│   ├── write.py            #   Write file (requires approval)
│   ├── move.py             #   Move/rename (requires approval)
│   ├── delete.py           #   Delete (requires approval + confirmation)
│   ├── search.py           #   Glob/regex file search
│   └── metadata.py         #   File metadata (size, dates, hash)
│
├── shell/                  # Shell execution
│   ├── powershell.py       #   PowerShell 7 command execution
│   ├── cmd.py              #   Legacy cmd.exe (minimal, sandboxed)
│   └── output_parser.py    #   Structured output parsing
│
├── clipboard/              # Clipboard
│   ├── read.py             #   Read current clipboard
│   ├── write.py            #   Write to clipboard
│   └── history.py          #   Clipboard history (opt-in)
│
├── browser/                # Browser control
│   ├── open_url.py         #   Open URL in default browser
│   ├── screenshot.py       #   Capture browser screenshot (Playwright)
│   └── extract.py          #   Extract text from URL (local only)
│
├── windows/                # Windows-specific skills
│   ├── process.py          #   List/kill/prioritize processes
│   ├── window_manager.py   #   Window focus, minimize, tile
│   ├── notifications.py    #   Windows toast notifications
│   ├── registry.py         #   Registry read (write requires approval)
│   └── power.py            #   Sleep, hibernate, shutdown (requires approval)
│
└── _manifest/              # Canonical skill manifests (TOML)
    ├── filesystem.toml
    ├── shell.toml
    ├── clipboard.toml
    ├── browser.toml
    └── windows.toml
```

**Side-effect profiles** (declared in each skill manifest):

| Profile | Description | Requires Approval Default |
|---------|-------------|--------------------------|
| `read_only` | No state change | No |
| `idempotent` | Safe to repeat | No |
| `write` | Modifies files/clipboard | Yes (configurable) |
| `destructive` | Deletes or overwrites | Always yes |
| `system` | Changes OS state | Always yes |

---

### `voice/`

> **Owner:** Product team · **Lang:** Python 3.12+ · **Tier:** 3

Complete voice interaction pipeline. Entirely local — no cloud STT/TTS.

```
voice/
├── pipeline/               # Main pipeline orchestrator
│   ├── pipeline.py         #   Orchestrates: wake → STT → process → TTS → output
│   ├── state_machine.py    #   States: IDLE, LISTENING, PROCESSING, SPEAKING
│   └── config.py           #   Voice pipeline configuration
│
├── stt/                    # Speech-to-text
│   ├── whisper_stt.py      #   faster-whisper (local, GPU-accelerated)
│   ├── vad.py              #   Voice activity detection (silero-vad)
│   └── streaming.py        #   Real-time audio → text streaming
│
├── tts/                    # Text-to-speech
│   ├── piper_tts.py        #   Piper TTS (local, fast, ONNX)
│   ├── kokoro_tts.py       #   Kokoro TTS (higher quality, heavier)
│   └── audio_output.py     #   Audio playback via sounddevice
│
├── wake-word/              # Hotword detection
│   ├── detector.py         #   OpenWakeWord integration
│   ├── models/             #   Wake word model files (.onnx)
│   └── trainer.py          #   Custom wake word training (v1.x)
│
└── audio-device/           # Audio device management
    ├── device_manager.py   #   List/select input-output devices
    ├── mixer.py            #   Audio stream mixing
    └── noise_reduction.py  #   RNNoise-based noise suppression
```

**Voice pipeline flow:**

```
Microphone
    │
[VAD] ──────────────── silence? → sleep
    │ speech detected
[Wake Word Detector]
    │ "Arizen" heard
[Whisper STT] ─────── stream to text
    │
[Monarch Agent] ────── process query
    │
[Piper TTS] ────────── synthesize response
    │
Speaker Output
```

---

### `branding/`

> **Owner:** Design team · **Lang:** JSON/CSS/SVG · **Tier:** 4

Single source of truth for all visual identity. Consumed by `apps/`.
No code module imports from branding — assets are bundled at build time.

```
branding/
├── tokens/                 # Design token definitions
│   ├── colors.json         #   Color palette (void, surface, cyan, purple, ...)
│   ├── typography.json     #   Font families, sizes, weights, line heights
│   ├── spacing.json        #   Spacing scale (4px base grid)
│   ├── shadows.json        #   Elevation system
│   ├── animation.json      #   Duration, easing curves
│   └── tokens.css          #   Compiled CSS custom properties (auto-generated)
│
├── assets/                 # Visual assets
│   ├── logo/               #   ArizenOS logo variants (SVG, PNG @1x, @2x, @3x)
│   ├── icons/              #   App icons (16/32/64/128/256/512px + .ico + .icns)
│   ├── wallpapers/         #   Default wallpapers
│   └── illustrations/      #   Onboarding and empty-state illustrations
│
├── themes/                 # UI themes
│   ├── arizen-dark.css     #   Default dark theme (primary)
│   ├── arizen-midnight.css #   Deeper dark variant
│   ├── arizen-light.css    #   Light theme (accessibility)
│   └── theme-schema.json   #   Theme variable spec for community themes
│
└── fonts/                  # Typography
    ├── JetBrainsMono/      #   Monospace (code, HUD, terminal output)
    ├── Inter/              #   UI sans-serif
    └── CalSans/            #   Display headings
```

---

### `integrations/`

> **Owner:** Platform team · **Lang:** Rust (primary) + Python (LM Studio client) · **Tier:** 1

All external system interfaces. **LM Studio is Tier 1 here — the primary, most-tested path.**

```
integrations/
├── lm-studio/              # LM Studio — PRIMARY LLM + embedding backend
│   ├── src/                #   (Rust) HTTP client for LM Studio OpenAI-compat API
│   │   ├── client.rs       #   Async reqwest client + connection pool
│   │   ├── chat.rs         #   Chat completions with streaming
│   │   ├── embeddings.rs   #   Embedding endpoint
│   │   ├── models.rs       #   Model listing and health check
│   │   └── lib.rs
│   ├── lm_studio.py        #   (Python) Mirror client for agent-side use
│   └── Cargo.toml
│
├── ollama/                 # Ollama — secondary LLM backend (fallback)
│   ├── src/
│   │   ├── client.rs
│   │   ├── generate.rs
│   │   └── lib.rs
│   ├── ollama.py
│   └── Cargo.toml
│
├── windows-api/            # Windows API wrappers (windows-rs)
│   ├── src/
│   │   ├── keyboard.rs     #   Global hotkey registration (RegisterHotKey)
│   │   ├── processes.rs    #   Process enumeration and management
│   │   ├── windows_mgr.rs  #   Window enumeration, focus, z-order
│   │   ├── clipboard.rs    #   Clipboard read/write (OpenClipboard API)
│   │   ├── shell.rs        #   ShellExecute, IShellLink
│   │   └── lib.rs
│   └── Cargo.toml
│
├── windows-registry/       # Registry access
│   ├── src/
│   │   ├── reader.rs       #   Registry key/value read
│   │   ├── writer.rs       #   Registry write (requires elevation)
│   │   └── lib.rs
│   └── Cargo.toml
│
├── taskbar/                # Windows taskbar integration
│   ├── src/
│   │   ├── tray_icon.rs    #   System tray icon via tray-icon crate
│   │   ├── jump_list.rs    #   Windows Jump List for quick actions
│   │   └── lib.rs
│   └── Cargo.toml
│
└── notifications/          # Windows toast notifications
    ├── src/
    │   ├── toast.rs        #   WinRT Toast notifications (windows-rs)
    │   ├── action_center.rs
    │   └── lib.rs
    └── Cargo.toml
```

**LM Studio-first policy:**
Every component that makes an LLM inference call **must** try `integrations/lm-studio` first.
Fallback order: LM Studio → Ollama → llama-cpp-python (embedded).
This order is hardcoded in `core/config/schema.rs` and cannot be overridden without explicit `fallback_override` config flag.

---

### `services/`

> **Owner:** Platform team · **Lang:** Rust · **Tier:** 1

Background services that feed the intelligence layer with real-time OS signals.
Each service runs as a Tokio task inside the daemon, publishing events to the IPC event bus.

```
services/
├── file-watcher/           # File system change events
│   ├── src/
│   │   ├── watcher.rs      #   notify crate wrapper with debouncing
│   │   ├── filter.rs       #   Include/exclude path filters
│   │   └── lib.rs
│   └── Cargo.toml
│
├── clipboard-monitor/      # Clipboard change stream
│   ├── src/
│   │   ├── monitor.rs      #   Clipboard change listener (Windows API)
│   │   ├── content.rs      #   Content type detection
│   │   └── lib.rs
│   └── Cargo.toml
│
├── process-monitor/        # System process lifecycle
│   ├── src/
│   │   ├── monitor.rs      #   Process start/exit events (WMI)
│   │   ├── metrics.rs      #   Per-process resource metrics (sysinfo)
│   │   └── lib.rs
│   └── Cargo.toml
│
├── hotkey-service/         # Global hotkey registration
│   ├── src/
│   │   ├── registry.rs     #   RegisterHotKey/UnregisterHotKey lifecycle
│   │   ├── bindings.rs     #   Binding config → Windows VK codes
│   │   └── lib.rs
│   └── Cargo.toml
│
└── update-service/         # Self-update (from GitHub Releases)
    ├── src/
    │   ├── checker.rs      #   Version check (offline-safe, rate-limited)
    │   ├── downloader.rs   #   Authenticated download + SHA256 verify
    │   ├── installer.rs    #   In-place .msi patch
    │   └── lib.rs
    └── Cargo.toml
```

---

### `docs/`

> **Owner:** Everyone · **Lang:** Markdown · **Tier:** 4

```
docs/
├── VISION.md               # Product + Technical Vision
├── PRINCIPLES.md           # Core Principles (non-negotiable)
├── STRUCTURE.md            # ← This file
├── ARCHITECTURE.md         # System architecture diagrams
├── FEATURE_MATRIX.md       # Feature status matrix
├── ROADMAP.md              # Release roadmap
├── NAMING_CONVENTIONS.md   # Naming rules across all layers
│
├── architecture/           # Deep-dive architecture documents
│   ├── agent-mesh.md       #   Agent communication model
│   ├── ipc-protocol.md     #   IPC wire format and protocol
│   ├── memory-model.md     #   Three-tier memory architecture
│   ├── knowledge-pipeline.md  # Ingestion and retrieval pipeline
│   └── lmstudio-integration.md  # LM Studio-first LLM strategy
│
├── api/                    # API reference
│   ├── grpc/               #   Generated gRPC docs
│   ├── ipc-messages.md     #   IPC message type reference
│   └── skill-sdk.md        #   Skill development reference
│
├── guides/                 # How-to guides
│   ├── getting-started.md
│   ├── build-from-source.md
│   ├── writing-an-agent.md
│   ├── writing-a-playbook.md
│   ├── writing-a-skill.md
│   └── lm-studio-setup.md  #   LM Studio configuration guide
│
├── decisions/              # Architecture Decision Records (ADR)
│   ├── 001-lm-studio-first.md
│   ├── 002-rust-daemon.md
│   ├── 003-named-pipes-ipc.md
│   ├── 004-sqlite-chromadb.md
│   └── 005-tauri-ui.md
│
└── specs/                  # Technical specifications
    ├── playbook-schema.md  #   Playbook YAML spec
    ├── agent-manifest.md   #   Agent manifest TOML spec
    ├── skill-manifest.md   #   Skill manifest TOML spec
    └── ipc-envelope.md     #   IPC envelope format spec
```

---

### `scripts/`

> **Owner:** Platform team · **Lang:** PowerShell 7 · **Tier:** 4

```
scripts/
├── bootstrap/
│   ├── bootstrap.ps1       # Full AME setup (Rust, Python, Node, LM Studio, Ollama)
│   ├── check-deps.ps1      # Pre-flight dependency checker
│   └── install-models.ps1  # Pull and configure recommended LLM models
│
├── build/
│   ├── build-all.ps1       # Full repo build (Rust + Python + Tauri)
│   ├── build-daemon.ps1    # Build Rust daemon only
│   ├── build-apps.ps1      # Build all Tauri apps
│   └── sign.ps1            # Code signing for release binaries
│
├── dev/
│   ├── dev-setup.ps1       # Developer environment setup
│   ├── watch-daemon.ps1    # cargo watch + auto-restart
│   ├── watch-nexus.ps1     # Vite dev server for Command Nexus
│   └── seed-knowledge.ps1  # Seed knowledge vault with sample data
│
└── release/
    ├── bump-version.ps1    # Bump version in all Cargo.toml + package.json
    ├── changelog.ps1       # Generate changelog from conventional commits
    ├── package.ps1         # Build .msi installer
    └── publish.ps1         # Create GitHub release + upload artifacts
```
