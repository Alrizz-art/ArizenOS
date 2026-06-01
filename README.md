<div align="center">

<img src="docs/assets/arizen-banner.svg" width="100%" alt="ArizenOS Banner" />

# ArizenOS

### Local-First AI Operating Layer

**The intelligence layer your OS was always missing.**

ArizenOS is a sovereign, offline-first AI platform that transforms Windows 10 AME into an AI-native computing environment. No cloud. No telemetry. No compromises.

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Windows 10 AME](https://img.shields.io/badge/Windows-10%20AME-blue.svg)](https://ameliorated.io)
[![Rust](https://img.shields.io/badge/Rust-1.79%2B-orange.svg)](https://rustlang.org)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Alpha-red.svg)](ROADMAP.md)

---

[Vision](docs/VISION.md) · [Architecture](docs/ARCHITECTURE.md) · [Roadmap](docs/ROADMAP.md) · [Principles](docs/PRINCIPLES.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## What is ArizenOS?

ArizenOS is not a new operating system. It is an **AI Operating Layer** — a sovereign runtime that lives on top of Windows 10 AME and rewires how you interact with your machine.

At its core:

- **Agent Mesh** — A graph of specialized AI agents that think, plan, and act autonomously or collaboratively
- **Workflow Engine** — YAML-defined automation pipelines triggered by time, events, or natural language
- **Knowledge Vault** — A local RAG system that turns your files, notes, and history into a living knowledge base
- **LLM Gateway** — A unified interface to local language models (Ollama, llama.cpp, LM Studio)
- **Command Nexus** — A keyboard-first AI command center that replaces the Start Menu as your primary interface

ArizenOS is **for power users who demand sovereignty** over their data, compute, and intelligence.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      COMMAND NEXUS                          │
│              (Tauri 2.0 + React + TypeScript)               │
└─────────────────────┬───────────────────────────────────────┘
                      │  IPC (Named Pipes / gRPC)
┌─────────────────────▼───────────────────────────────────────┐
│                    ARIZEN DAEMON                             │
│     Central process manager & subsystem orchestrator         │
│                     (Rust / Tokio)                           │
└──┬──────────────┬──────────────┬──────────────┬─────────────┘
   │              │              │              │
┌──▼──────┐  ┌───▼──────┐  ┌───▼──────┐  ┌───▼──────────┐
│  AGENT  │  │  WORKFLOW │  │KNOWLEDGE │  │  LLM GATEWAY │
│  MESH   │  │  ENGINE   │  │  VAULT   │  │              │
│(Python) │  │  (Python) │  │(Python)  │  │ Ollama / CPP │
└──┬──────┘  └───────────┘  └──────────┘  └──────────────┘
   │
   ├── Monarch   (Orchestrator)
   ├── Archivist (Knowledge)
   ├── Executor  (Task Runner)
   ├── Sentinel  (System Monitor)
   ├── Weaver    (Workflow Composer)
   └── Oracle    (Research & Synthesis)
```

---

## Quick Start

```powershell
# 1. Clone the repository
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS

# 2. Run the bootstrap installer (requires Windows 10 AME, PowerShell 7+)
.\scripts\bootstrap.ps1

# 3. Launch the daemon
arizen start

# 4. Open Command Nexus
arizen nexus
```

---

## Repository Structure

```
ArizenOS/
├── core/
│   ├── arizen-daemon/          # Central Rust daemon (Tokio)
│   ├── llm-gateway/            # LLM abstraction layer
│   ├── workflow-engine/        # Workflow automation runtime
│   └── knowledge-vault/        # RAG + vector + relational store
├── agents/
│   ├── monarch/                # Master orchestrator agent
│   ├── archivist/              # Knowledge management agent
│   ├── executor/               # Task execution agent
│   ├── sentinel/               # System monitoring agent
│   ├── weaver/                 # Workflow composition agent
│   └── oracle/                 # Research & synthesis agent
├── ui/
│   └── command-nexus/          # Tauri 2.0 + React command center
├── plugins/
│   ├── plugin-sdk/             # Plugin development SDK
│   └── official/               # Official ArizenOS plugins
├── models/
│   └── profiles/               # LLM model configuration profiles
├── scripts/
│   ├── bootstrap.ps1           # Windows setup script
│   ├── install-models.ps1      # Model download helper
│   └── dev-setup.ps1           # Developer environment setup
├── docs/
│   ├── VISION.md
│   ├── ARCHITECTURE.md
│   ├── PRINCIPLES.md
│   ├── FEATURE_MATRIX.md
│   ├── ROADMAP.md
│   └── NAMING_CONVENTIONS.md
└── tests/
    ├── integration/
    ├── unit/
    └── e2e/
```

---

## Core Agents

| Agent | Codename | Role | Model Tier |
|-------|----------|------|------------|
| Orchestrator | **Monarch** | Plans and delegates tasks across the mesh | High (Phi-3 / Mistral 7B) |
| Knowledge | **Archivist** | Indexes, retrieves, and synthesizes local knowledge | Mid (TinyLlama / Phi-3 Mini) |
| Executor | **Executor** | Runs shell commands, scripts, and OS-level tasks | Mid |
| Monitor | **Sentinel** | Watches system health, alerts, and resource usage | Low (rule-based + LLM) |
| Workflow | **Weaver** | Composes and schedules automation workflows | Mid |
| Research | **Oracle** | Deep research and multi-source synthesis | High |

---

## Design Philosophy

> *"Sovereignty first. Intelligence second. Speed always."*

1. **Local-First** — Every computation runs on your hardware. Nothing leaves your machine without explicit permission.
2. **AME-Native** — Designed for Windows 10 Ameliorated. Zero telemetry. Zero bloat.
3. **Agent Sovereignty** — Agents run as isolated processes. No agent can access another's memory without a declared channel.
4. **Composable** — Every component is independently replaceable. Swap the LLM. Swap the UI. Swap an agent.
5. **Observable** — Every decision, every tool call, every workflow step is logged and inspectable.

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 AME 22H2 | Windows 10 AME 22H2 (latest) |
| CPU | 8-core x86_64 | 16-core (Ryzen 7 / i7+) |
| RAM | 16 GB | 32 GB |
| GPU | None (CPU inference) | NVIDIA RTX 3060+ (CUDA) or AMD RX 7800 (ROCm) |
| Storage | 40 GB free | 100 GB NVMe SSD |
| PowerShell | 7.0+ | 7.4+ |

---

## License

MIT License — See [LICENSE](LICENSE)

---

<div align="center">
<sub>Built with sovereignty in mind. Made for power users who refuse to compromise.</sub>
</div>
