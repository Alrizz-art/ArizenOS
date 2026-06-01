# ArizenOS — Development Roadmap

## Philosophy

> Ship working software. Iterate in public. Never sacrifice sovereignty.

Releases follow **Calendar Versioning**: `YYYY.MM.MICRO`

Codenames are named after celestial phenomena.

---

## v0.1 — "Ignition" *(Foundation)*

**Timeline:** Month 1–2  
**Theme:** Prove the architecture works end-to-end

### Goals
- [ ] Arizen Daemon boots and manages process lifecycle
- [ ] LLM Gateway connects to Ollama with streaming output
- [ ] Command Nexus renders and accepts text input
- [ ] Monarch agent receives a task and calls a tool
- [ ] End-to-end smoke test: "Open Notepad" via natural language

### Deliverables
- `core/arizen-daemon` — v0.1 (process management, IPC)
- `core/llm-gateway` — v0.1 (Ollama backend only)
- `ui/command-nexus` — v0.1 (input + basic output display)
- `agents/monarch` — v0.1 (basic task delegation)
- `agents/executor` — v0.1 (PowerShell tool only)
- `scripts/bootstrap.ps1` — Initial AME setup

---

## v0.2 — "Kindling" *(Knowledge)*

**Timeline:** Month 3–4  
**Theme:** Make the system know things

### Goals
- [ ] Knowledge Vault indexes a watched directory
- [ ] Archivist answers questions from local files
- [ ] Semantic search returns relevant chunks
- [ ] Terminal history is ingested automatically

### Deliverables
- `core/knowledge-vault` — v0.1 (ChromaDB + SQLite)
- `agents/archivist` — v0.1 (RAG over local files)
- File watcher integration with Vault

---

## v0.3 — "Circuit" *(Automation)*

**Timeline:** Month 5–6  
**Theme:** Make the system act on your behalf

### Goals
- [ ] Weaver runs a 3-step workflow from YAML definition
- [ ] Time-based and file-change triggers work
- [ ] Sentinel monitors CPU/RAM and fires threshold alerts
- [ ] 10 pre-built workflow templates ship in the box

### Deliverables
- `core/workflow-engine` — v0.1
- `agents/weaver` — v0.1
- `agents/sentinel` — v0.1
- Workflow template library (v1)

---

## v0.4 — "Prism" *(Intelligence)*

**Timeline:** Month 7–8  
**Theme:** Make agents smarter and cooperative

### Goals
- [ ] Monarch decomposes multi-step NL tasks into agent graphs
- [ ] Oracle synthesizes multi-document research reports
- [ ] Human-in-the-loop approval gates implemented
- [ ] Tiered LLM routing (Tier 0–2) works automatically

### Deliverables
- `agents/monarch` — v0.2 (planning + delegation)
- `agents/oracle` — v0.1
- LLM tier routing in gateway
- Approval gate system

---

## v0.5 — "Eclipse" *(Experience)*

**Timeline:** Month 9–10  
**Theme:** Make the UI feel native and fast

### Goals
- [ ] Command Nexus launches in < 100ms
- [ ] System HUD overlay on desktop
- [ ] Command palette with full keyboard navigation
- [ ] Conversation history with search
- [ ] Workflow trigger panel

### Deliverables
- `ui/command-nexus` — v0.5 (full feature set)
- HUD overlay component
- Performance optimization pass

---

## v1.0 — "Sovereign" *(Production)*

**Timeline:** Month 11–12  
**Theme:** Ready for daily use by power users

### Goals
- [ ] All v0.x features stable and tested
- [ ] Plugin SDK v1.0 documented and shipped
- [ ] Installer package (WiX) for clean AME installs
- [ ] Performance budgets met across all components
- [ ] Security audit of IPC and agent sandbox
- [ ] Complete documentation
- [ ] 3 community plugins as examples

### Deliverables
- `plugins/plugin-sdk` — v1.0
- Windows installer (.msi)
- Full documentation site
- Launch blog post

---

## v1.x — "Horizon" *(Expansion)*

Post-launch roadmap (community-driven):

- [ ] ROCm GPU support (AMD)
- [ ] LM Studio backend
- [ ] Hot-reload agents without daemon restart
- [ ] Multi-monitor Nexus
- [ ] Obsidian vault integration
- [ ] Browser history ingestion
- [ ] NL workflow composition via Weaver
- [ ] Plugin store

---

## v2.0 — "Continuum" *(Vision)*

Long-term moonshots:

- [ ] ArizenOS on Windows 11 (with telemetry-stripped install)
- [ ] Network mesh — multiple ArizenOS nodes on LAN sharing knowledge
- [ ] Voice interface (Whisper + local TTS)
- [ ] Mobile companion app
- [ ] Knowledge graph with entity linking
