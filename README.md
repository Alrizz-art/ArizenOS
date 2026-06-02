<div align="center">
  <img src="assets/logos/arizenOS_logo_dark.png" alt="ArizenOS Logo" width="200" />

  <h1>ArizenOS</h1>
  <p><em>"The desktop, reimagined for the age of intelligence."</em></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/Alrizz-art/ArizenOS?style=social)](https://github.com/Alrizz-art/ArizenOS/stargazers)
  [![GitHub Issues](https://img.shields.io/github/issues/Alrizz-art/ArizenOS)](https://github.com/Alrizz-art/ArizenOS/issues)

</div>

---

## What is ArizenOS?

**ArizenOS** is an AI-first desktop experience platform for **Windows 10 and Windows 11**.

It is not a new operating system — it is the experience layer Windows was never built to be. ArizenOS sits on top of Windows and transforms the desktop into an intelligent, fluid, glass-rendered workspace where AI is a first-class citizen.

---

## Primary Product

ArizenOS ships as a suite of integrated Windows applications:

| Component | Description |
|---|---|
| **Launcher** | AI-powered application launcher and command palette |
| **Assistant** | Conversational AI assistant with full desktop context |
| **Voice** | Voice-activated desktop control |
| **Agent** | Autonomous task agent with tool access |
| **Hub** | Extension manager and integration center |

### Platform Roadmap

- [x] ArizenOS Playbook (`.apbx`) — declarative desktop configuration system
- [x] Branding System — design tokens, logo system, icon set
- [x] Wallpaper System — curated wallpaper collection with light/dark variants
- [x] OEM Branding — partner customization layer
- [ ] Desktop Experience Layer — glass rendering, blur, motion
- [ ] Launcher — AI command palette
- [ ] Assistant — conversational desktop AI
- [ ] Voice — voice control layer
- [ ] Agent — autonomous agent runtime
- [ ] LM Studio Integration — local AI model backend

---

## Repository Structure

```
ArizenOS/
├── apps/                    # End-user Windows applications
│   ├── launcher/
│   ├── assistant/
│   ├── voice/
│   ├── hub/
│   └── agent/
│
├── packages/                # Shared platform libraries (@arizen/*)
│   ├── core/                # Core types and utilities
│   ├── glass/               # Glass rendering engine
│   ├── mind/                # AI/LLM integration layer
│   ├── shell/               # Desktop shell integration
│   ├── ui/                  # Component library
│   ├── skin/                # Design token system
│   ├── flow/                # Animation and transitions
│   ├── sync/                # State synchronization
│   ├── widgets/             # Widget framework
│   └── agent-sdk/           # Agent plugin SDK
│
├── branding/                # Brand assets, design tokens, wallpapers
├── docs/                    # Architecture docs, ADRs, guides
├── playbook/                # ArizenOS Playbook system (.apbx)
├── scripts/                 # Build, release, and maintenance scripts
├── tools/                   # Developer tooling
│
└── research/                # ⚗️ Experimental research
    └── kernel/              # Bare-metal OS kernel prototype (x86_64)
```

> **Two domains, one repository.** The `research/kernel/` directory contains an experimental bare-metal OS prototype — separate from the Windows platform product. See [ADR-0004](docs/architecture/ADR-0004-kernel-research-strategy.md) for the full rationale.

---

## Getting Started

### System Requirements

- Windows 10 (build 19041+) or Windows 11
- Node.js 18+
- pnpm 8+

### Development Setup

```bash
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS
pnpm install
pnpm build
```

> **Kernel research setup** is documented separately at [`research/kernel/README.md`](research/kernel/README.md) and requires a different toolchain (cross-compiler, NASM, QEMU).

---

## Contributing

We welcome contributions to both domains. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

- **Platform contributions** — TypeScript, React, design tokens, Windows shell APIs
- **Kernel research contributions** — C, Assembly, systems programming

Each domain has its own maintainers and review process. See [GOVERNANCE.md](GOVERNANCE.md) for details.

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full architecture document, including:

- Package dependency graph
- CI/CD pipelines
- Release structure
- Design token system

Architecture decisions are recorded as ADRs in [`docs/architecture/`](docs/architecture/):

| ADR | Decision |
|---|---|
| [ADR-0001](docs/architecture/ADR-0001-monorepo.md) | Monorepo structure |
| [ADR-0002](docs/architecture/ADR-0002-glass-rendering.md) | Glass rendering engine |
| [ADR-0003](docs/architecture/ADR-0003-local-ai.md) | Local-first AI |
| [ADR-0004](docs/architecture/ADR-0004-kernel-research-strategy.md) | Kernel research separation |

---

## License

[MIT](LICENSE) — Copyright © 2026 ArizenOS Contributors
