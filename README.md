<div align="center">

<br />

<!-- LOGO -->
<img src="branding/logos/svg/arizen-full-dark.svg" alt="ArizenOS" width="280" />

<br />
<br />

**The AI-first desktop experience layer for Windows.**

Open source. Local-first. Built for builders.

<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Alrizz-art/ArizenOS?style=flat-square&color=blue)](https://github.com/Alrizz-art/ArizenOS/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Alrizz-art/ArizenOS?style=flat-square)](https://github.com/Alrizz-art/ArizenOS/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows)](https://github.com/Alrizz-art/ArizenOS)
[![Status](https://img.shields.io/badge/Status-Pre--Alpha-orange?style=flat-square)](CHANGELOG.md)

<br />

[**Documentation**](https://docs.arizenos.dev) · [**Discord**](https://discord.gg/arizenos) · [**Roadmap**](#-roadmap) · [**Contributing**](#-contributing)

<br />

---

</div>

## What is ArizenOS?

ArizenOS is an **open-source desktop experience platform** for Windows 10 and Windows 11.

It is not a new operating system. It is not a Windows mod or a custom ISO. It is an **intelligence layer** — a complete reimagining of the Windows desktop surface, built from the ground up around local AI, GPU-accelerated glass rendering, and a developer ecosystem that ships at startup speed.

Windows is infrastructure. ArizenOS is the experience.

```
Windows 10 / Windows 11 (your existing installation)
        +
ArizenOS (drop-in shell, AI layer, glass rendering)
        =
The desktop you've always wanted.
```

> **ArizenOS is in pre-alpha.** It is not production-ready. If you want to help build it, you're in the right place.

<br />

---

## ✦ Features

<table>
<tr>
<td width="50%">

### 🪟 Glass Shell
A complete taskbar, launcher, and window manager replacement powered by a custom GPU compositing pipeline. Depth, blur, and translucency that respond to context — not decoration applied on top of decoration.

</td>
<td width="50%">

### 🧠 Local AI — ArizenMind
Full LLM inference on your machine. Llama 3, Phi-3, Mistral, Gemma — streaming, context-aware, zero cloud dependency. Your prompts never leave your device unless you explicitly choose otherwise.

</td>
</tr>
<tr>
<td width="50%">

### 🎨 Theming SDK — ArizenSkin
A live-reloading theme engine built on compiled design tokens. Swap the entire visual identity of your desktop from a single TOML file. Community themes hot-load without a restart.

</td>
<td width="50%">

### 🤖 Arizen Agent
An autonomous task runner. Natural language → OS actions. File operations, browser control, shell commands — executed with an explicit, auditable permission model. You always stay in control.

</td>
</tr>
<tr>
<td width="50%">

### 🎙️ Arizen Voice
Wake-word detection, speech-to-text, and text-to-speech — all running locally via Whisper.cpp and Piper. No cloud. No subscription. Just voice.

</td>
<td width="50%">

### 🔌 Widget Runtime
A sandboxed JavaScript widget runtime with a permission model and hot-reload. Build and distribute desktop widgets. Ship them to the community through Arizen Hub.

</td>
</tr>
<tr>
<td width="50%">

### 🏪 Arizen Hub
The control center for everything ArizenOS: extensions, themes, model downloads, system settings, and updates — all in one glass panel.

</td>
<td width="50%">

### 🔒 Privacy by Default
No telemetry. No analytics. No phoning home. ArizenOS runs on your hardware, for you. Opt-in sync uses end-to-end encryption. The key never leaves your device.

</td>
</tr>
</table>

<br />

---

## 📸 Screenshots

> Screenshots will be added at the first alpha release. Follow [@ArizenOS](https://x.com/arizenos) for previews.

<table>
<tr>
<td align="center" width="33%">
<img src="branding/press/screenshots/desktop-dark.png" alt="Desktop — Dark" /><br/>
<sub><b>Desktop — Dark Mode</b></sub>
</td>
<td align="center" width="33%">
<img src="branding/press/screenshots/launcher-open.png" alt="Launcher" /><br/>
<sub><b>Arizen Launcher</b></sub>
</td>
<td align="center" width="33%">
<img src="branding/press/screenshots/assistant-chat.png" alt="Assistant" /><br/>
<sub><b>Arizen Assistant</b></sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<img src="branding/press/screenshots/hub-extensions.png" alt="Hub" /><br/>
<sub><b>Arizen Hub</b></sub>
</td>
<td align="center" width="33%">
<img src="branding/press/screenshots/desktop-light.png" alt="Desktop — Light" /><br/>
<sub><b>Desktop — Light Mode</b></sub>
</td>
<td align="center" width="33%">
<img src="branding/press/screenshots/agent-tasks.png" alt="Agent" /><br/>
<sub><b>Arizen Agent</b></sub>
</td>
</tr>
</table>

<br />

---

## 🚀 Installation

> **Requirements:** Windows 10 Build 19041+ or Windows 11. 8 GB RAM minimum (16 GB recommended for local AI). GPU optional but recommended for glass effects.

### Option 1 — Installer (Recommended)

Download the latest release from [GitHub Releases](https://github.com/Alrizz-art/ArizenOS/releases):

```
ArizenOS-Setup-x.y.z.exe
```

Run the installer. ArizenOS integrates with your existing Windows installation — no partitioning, no ISO, no dual boot.

### Option 2 — Build from Source

**Prerequisites:** Node.js 20 LTS, pnpm 8+, Git 2.40+, Visual Studio Build Tools 2022 (for native modules)

```bash
# 1. Clone the repository
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS

# 2. Install dependencies
pnpm install

# 3. Build all packages
pnpm build

# 4. Launch the development environment
pnpm dev
```

To run a specific product in development:

```bash
# Launcher
pnpm --filter @arizen/launcher dev

# Assistant
pnpm --filter @arizen/assistant dev

# Hub (control center)
pnpm --filter @arizen/hub dev
```

### Setting Up Local AI

ArizenOS uses [llama.cpp](https://github.com/ggerganov/llama.cpp) for local inference. Download a GGUF model and configure it through Arizen Hub, or via config:

```toml
# ~/.arizen/config.toml
[mind]
model = "llama-3-8b-instruct-q4_k_m"
model_path = "C:/Users/you/.arizen/models/"
context_length = 8192
gpu_layers = 32   # 0 for CPU-only
```

Recommended starter models (via Arizen Hub model browser):
- **Llama 3 8B Q4** — Best balance of quality and speed (~5 GB)
- **Phi-3 Mini Q4** — Fastest, great for quick tasks (~2 GB)
- **Mistral 7B Q4** — Strong coding performance (~4 GB)

<br />

---

## 🗺️ Roadmap

<table>
<tr>
<th width="33%">Phase 1 — Foundation</th>
<th width="33%">Phase 2 — Ecosystem</th>
<th width="33%">Phase 3 — Platform</th>
</tr>
<tr>
<td>

**Target: v0.1.0 alpha**

- [x] Repository architecture
- [x] Governance model
- [x] Brand guidelines
- [ ] `@arizen/core` — primitives
- [ ] `@arizen/glass` — blur engine
- [ ] `@arizen/shell` — Win32 bindings
- [ ] `@arizen/mind` — local inference
- [ ] `@arizen/ui` — component library
- [ ] Arizen Launcher MVP
- [ ] Arizen Assistant MVP
- [ ] Arizen Hub MVP

</td>
<td>

**Target: v0.4.0**

- [ ] `@arizen/widgets` runtime
- [ ] Widget SDK + marketplace
- [ ] Arizen Voice (Whisper STT)
- [ ] Arizen Agent + tool system
- [ ] Theme marketplace in Hub
- [ ] `@arizen/sync` (opt-in)
- [ ] Plugin API stable release
- [ ] Community extension directory
- [ ] Documentation site launch

</td>
<td>

**Target: v1.0.0 GA**

- [ ] LTS release program
- [ ] ARM64 support (Snapdragon X)
- [ ] Arizen Foundation governance
- [ ] Enterprise pilot program
- [ ] ArizenOS AI Runtime (public API)
- [ ] University partnership program
- [ ] Localization (10+ languages)
- [ ] Accessibility certification

</td>
</tr>
</table>

Track progress on the [public GitHub Project board](https://github.com/Alrizz-art/ArizenOS/projects).

<br />

---

## 💡 Vision

The personal computer is the most powerful tool humanity has ever created. And it has been criminally under-reimagined for the last twenty years.

AI arrived. Nothing changed on the screen.

**ArizenOS exists to fix that.**

We believe the best computing experience in the world should be:

- **Free and open** — not locked to a $3,000 laptop or a closed ecosystem
- **Local and private** — your AI runs on your machine, your data goes nowhere
- **Built for builders** — developers are first-class citizens, not an afterthought
- **Genuinely beautiful** — glass, depth, and motion as a design language, not a gimmick
- **Intelligent by default** — AI woven into the fabric of the desktop, not bolted on top

We are building the macOS moment for the AI generation. On the operating system 1.4 billion people already own.

Read the full [Product Charter](PRODUCT_CHARTER.md).

<br />

---

## 🏛️ Architecture

ArizenOS is a **pnpm monorepo** with a Turborepo build pipeline, organized into apps and shared packages.

```
ArizenOS/
├── apps/
│   ├── launcher/          # @arizen/launcher  — Shell replacement
│   ├── assistant/         # @arizen/assistant — AI command layer
│   ├── voice/             # @arizen/voice     — Speech interface
│   ├── hub/               # @arizen/hub       — Control center
│   └── agent/             # @arizen/agent     — Autonomous task runner
│
├── packages/
│   ├── core/              # @arizen/core      — Primitives, logger, event bus
│   ├── glass/             # @arizen/glass     — GPU rendering engine
│   ├── mind/              # @arizen/mind      — Local AI inference
│   ├── shell/             # @arizen/shell     — Win32 / WinUI3 bindings
│   ├── flow/              # @arizen/flow      — Physics animation engine
│   ├── skin/              # @arizen/skin      — Theming and token system
│   ├── ui/                # @arizen/ui        — Shared component library
│   ├── widgets/           # @arizen/widgets   — Widget runtime
│   ├── sync/              # @arizen/sync      — Cross-device sync (E2E encrypted)
│   └── agent-sdk/         # @arizen/agent-sdk — Agent plugin API
│
├── branding/              # Logos, fonts, icons, design tokens
├── docs/                  # Documentation site + ADRs + RFCs
├── tests/                 # E2E, integration, visual regression, a11y
└── tools/                 # Internal scaffolding and build tools
```

**Dependency rules — enforced by CI:**

```
@arizen/core      (no internal deps)
     ↓
@arizen/glass, @arizen/mind, @arizen/shell, @arizen/flow, @arizen/skin
     ↓
@arizen/ui
     ↓
@arizen/widgets, @arizen/sync, @arizen/agent-sdk
     ↓
apps/* (consume packages, never each other)
```

Full architecture documentation: [`ARCHITECTURE.md`](ARCHITECTURE.md)
Architecture decisions: [`docs/architecture/`](docs/architecture/)

<br />

---

## 🤝 Contributing

ArizenOS is built by its community. Every contribution matters — code, documentation, design, testing, triage, or community support.

### Quick Start

```bash
# Fork the repo, then:
git clone https://github.com/<your-username>/ArizenOS.git
cd ArizenOS
pnpm install

# Create a branch
git checkout -b feat/your-feature-name

# Make your changes, then:
pnpm lint && pnpm typecheck && pnpm test

# Open a pull request against main
```

### Ways to Contribute

| Track | Where to Start |
|---|---|
| 🐛 **Bug fixes** | [Issues tagged `good first issue`](https://github.com/Alrizz-art/ArizenOS/labels/good%20first%20issue) |
| ✨ **Features** | Open an issue first, get alignment, then build |
| 📖 **Documentation** | [`docs/`](docs/) — any improvement welcome |
| 🎨 **Design** | Open a discussion in the `design` category |
| 🔌 **Extensions** | Read the [`@arizen/agent-sdk`](packages/agent-sdk/README.md) and [`@arizen/widgets`](packages/widgets/README.md) docs |
| 🌍 **Localization** | Watch for the i18n milestone |

### Before You Open a PR

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) — especially the PR policy and code review standards
- For significant changes, open an RFC first via the [RFC issue template](.github/ISSUE_TEMPLATE/rfc.md)
- All PRs must pass `pnpm lint && pnpm typecheck && pnpm test`
- Every new function needs a unit test and JSDoc

### Community

- **GitHub Discussions** — Q&A, RFCs, announcements, ideas
- **Discord** — [discord.gg/arizenos](https://discord.gg/arizenos)
- **X (Twitter)** — [@ArizenOS](https://x.com/arizenos)

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). All contributors are expected to read and follow it.

<br />

---

## 📋 Governance

ArizenOS is governed by the **Arizen Technologies Steering Committee** and an elected **Technical Council**, with community-elected roles (Reviewer, Core Team, Module Owner) earned through contribution.

Decisions are made in public, on GitHub, via lazy consensus and formal voting where needed.

Read the full governance model: [`GOVERNANCE.md`](GOVERNANCE.md)

<br />

---

## 🔐 Security

ArizenOS takes security seriously.

**To report a vulnerability:** Email [`security@arizenos.dev`](mailto:security@arizenos.dev) or use [GitHub's private vulnerability reporting](https://github.com/Alrizz-art/ArizenOS/security/advisories/new). **Do not open a public issue.**

We follow a 90-day coordinated disclosure policy. All confirmed vulnerabilities are credited in our Security Hall of Fame.

Read the full policy: [`SECURITY.md`](SECURITY.md)

<br />

---

## 📦 Packages

| Package | Version | Description |
|---|---|---|
| [`@arizen/core`](packages/core) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Primitives, logger, event bus |
| [`@arizen/glass`](packages/glass) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | GPU glass rendering engine |
| [`@arizen/mind`](packages/mind) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Local AI inference layer |
| [`@arizen/shell`](packages/shell) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Windows OS integration |
| [`@arizen/flow`](packages/flow) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Physics animation engine |
| [`@arizen/skin`](packages/skin) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Theming SDK |
| [`@arizen/ui`](packages/ui) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Shared component library |
| [`@arizen/widgets`](packages/widgets) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Widget runtime |
| [`@arizen/sync`](packages/sync) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Cross-device sync (E2E encrypted) |
| [`@arizen/agent-sdk`](packages/agent-sdk) | ![pre-alpha](https://img.shields.io/badge/pre--alpha-gray?style=flat-square) | Agent plugin API |

<br />

---

## 📚 Documentation

| Document | Description |
|---|---|
| [`PRODUCT_CHARTER.md`](PRODUCT_CHARTER.md) | Vision, mission, principles, market positioning |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Monorepo structure, package layout, CI/CD design |
| [`BRAND_GUIDELINES.md`](BRAND_GUIDELINES.md) | Design system, typography, color, logo rules |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Roles, decision-making, RFC process |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute, PR policy, code review standards |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Community standards and enforcement |
| [`SECURITY.md`](SECURITY.md) | Vulnerability disclosure policy |
| [`RELEASE.md`](RELEASE.md) | Release process, versioning, LTS policy |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed in each release |
| [`docs/architecture/`](docs/architecture/) | Architecture Decision Records (ADRs) |

<br />

---

## ⭐ Support the Project

If ArizenOS resonates with you:

- **Star this repo** — it helps people discover the project
- **Share it** — post it, tweet it, send it to a developer friend
- **Contribute** — code, docs, design, or community support
- **Sponsor** — sustaining contributors coming soon

The best way to support ArizenOS is to help build it.

<br />

---

## 📄 License

ArizenOS is licensed under the **MIT License** — free to use, modify, and distribute.

```
MIT License

Copyright (c) 2025 Arizen Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

<br />

---

<div align="center">

Built with conviction by **[Arizen Technologies](https://arizenos.dev)** and its contributors.

<br />

*The system has arisen.*

<br />

[Website](https://arizenos.dev) · [Docs](https://docs.arizenos.dev) · [Discord](https://discord.gg/arizenos) · [Twitter](https://x.com/arizenos) · [GitHub](https://github.com/Alrizz-art/ArizenOS)

</div>
