# ArizenOS Documentation

Welcome to the ArizenOS documentation. This is your complete reference for using, configuring, and building on the ArizenOS platform.

---

## Getting Started

New to ArizenOS? Start here.

| Document | Description |
|---|---|
| [Introduction](getting-started/introduction.md) | What ArizenOS is, who it's for, and the core philosophy |
| [System Requirements](getting-started/system-requirements.md) | Hardware and software requirements before you install |
| [Installation](getting-started/installation.md) | Installer and source build instructions |
| [Quick Start](getting-started/quick-start.md) | Up and running in 10 minutes |
| [FAQ](getting-started/faq.md) | Answers to common questions |

---

## Architecture

How ArizenOS is built.

| Document | Description |
|---|---|
| [Architecture Overview](architecture/overview.md) | System layers, monorepo structure, build pipeline |
| [Dependency Graph](architecture/dependency-graph.md) | Full package dependency rules and build order |
| [ADR-0001 — Monorepo](architecture/ADR-0001-monorepo.md) | Decision record: pnpm + Turborepo monorepo |
| [ADR-0002 — Glass Rendering](architecture/ADR-0002-glass-rendering.md) | Decision record: DirectComposition + Direct2D |
| [ADR-0003 — Local AI Inference](architecture/ADR-0003-local-ai.md) | Decision record: llama.cpp N-API binding |

---

## User Guides

How to use ArizenOS products.

| Guide | Description |
|---|---|
| [Desktop Setup](guides/user/desktop-setup.md) | Shell mode, Launcher, glass settings, multi-monitor |
| [Arizen Assistant](guides/user/ai-assistant.md) | AI interface, context, models, conversation |
| [Themes & Customisation](guides/user/themes-and-customization.md) | Applying, installing, and creating themes |
| [Arizen Agent](guides/user/arizen-agent.md) | Autonomous task runner, permissions, scheduled tasks |

---

## Developer Guides

How to build on ArizenOS.

| Guide | Description |
|---|---|
| [Local Development](guides/developer/local-development.md) | Setting up a dev environment, workflow, debugging |
| [Building Extensions](guides/developer/building-extensions.md) | Creating Agent tools with `@arizen/agent-sdk` |
| [Building Widgets](guides/developer/building-widgets.md) | Creating desktop widgets with `@arizen/widgets` |

---

## API Reference

TypeScript API documentation for every `@arizen/*` package.

| Package | Description |
|---|---|
| [`@arizen/core`](api/core.md) | Logger, EventBus, IPC, Config — the foundation |
| [`@arizen/mind`](api/mind.md) | Local AI inference — MindEngine, ModelManager |
| [`@arizen/skin`](api/skin.md) | Theming SDK — SkinEngine, tokens, hot-reload |
| [`@arizen/agent-sdk`](api/agent-sdk.md) | Public extension API — defineTool, createExtension |
| [API Overview](api/README.md) | Stability levels, conventions, error handling |

---

## Roadmap

Where ArizenOS is going.

| Document | Description |
|---|---|
| [Roadmap Overview](roadmap/README.md) | Milestone overview and current status |
| [v0.1.0 — First Alpha](roadmap/v0.1.0.md) | Core packages, shell, assistant, hub |
| [v0.4.0 — Public Beta](roadmap/v0.4.0.md) | Extension marketplace, sync, cloud AI opt-in |
| [v1.0.0 — General Availability](roadmap/v1.0.0.md) | LTS, ARM64, Foundation governance |

---

## Reference

| Document | Description |
|---|---|
| [Configuration Schema](reference/config-schema.md) | Full `config.toml` reference with all options |
| [Glossary](reference/glossary.md) | Terms and concepts used across the codebase |
| [Troubleshooting](reference/troubleshooting.md) | Common issues and solutions |

---

## Contributing to the Docs

Documentation improvements are always welcome. The docs live in `docs/` in the main repository.

- **Fix a typo or broken link** — open a PR directly
- **Add missing documentation** — open a [Documentation Issue](https://github.com/Alrizz-art/ArizenOS/issues/new?template=documentation.yml) first, or send a PR
- **Propose a structural change** — open a [Discussion](https://github.com/Alrizz-art/ArizenOS/discussions) first

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution guide.

---

*Documentation is versioned with the codebase. For older versions, browse the [GitHub tag archive](https://github.com/Alrizz-art/ArizenOS/tags).*
