# Architecture Overview

ArizenOS is built as a **pnpm monorepo** with a Turborepo build pipeline. This document describes the high-level architecture, the relationship between components, and the key design decisions that shape the system.

For implementation detail on specific components, see the [API Reference](../api/README.md). For the reasoning behind major decisions, see the [Architecture Decision Records](ADR-0001-monorepo.md).

---

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Experience Layer                     │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────┐ ┌───────────┐  │
│  │   Launcher   │ │  Assistant  │ │  Voice   │ │    Hub    │  │
│  │ @arizen/     │ │ @arizen/    │ │ @arizen/ │ │ @arizen/  │  │
│  │ launcher     │ │ assistant   │ │ voice    │ │ hub       │  │
│  └──────┬───────┘ └──────┬──────┘ └────┬─────┘ └─────┬─────┘  │
│         │                │             │              │         │
│  ┌──────▼────────────────▼─────────────▼──────────────▼──────┐ │
│  │                   @arizen/ui (component library)           │ │
│  └───────────────────────────────────┬────────────────────────┘ │
└──────────────────────────────────────┼──────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────┐
│                       Platform Services Layer                    │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────┐ ┌───────────┐  │
│  │ @arizen/mind │ │@arizen/glass│ │@arizen/  │ │ @arizen/  │  │
│  │ (local AI)   │ │ (rendering) │ │ shell    │ │ flow      │  │
│  └──────┬───────┘ └──────┬──────┘ └────┬─────┘ └─────┬─────┘  │
│         │                │             │              │         │
│  ┌──────▼────────────────▼─────────────▼──────────────▼──────┐ │
│  │                   @arizen/core (primitives)                │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────┐
│                         Windows Platform                         │
│  Win32 API · DWM · DirectComposition · Direct2D · WinRT         │
└───────────────────────────────────────────────────────────────────┘
```

---

## Monorepo Structure

```
ArizenOS/
├── apps/                    # End-user Electron applications
│   ├── launcher/            # @arizen/launcher
│   ├── assistant/           # @arizen/assistant
│   ├── voice/               # @arizen/voice
│   ├── hub/                 # @arizen/hub
│   └── agent/               # @arizen/agent
│
├── packages/                # Shared libraries (internal + public SDK)
│   ├── core/                # @arizen/core       — zero-dep primitives
│   ├── glass/               # @arizen/glass      — GPU rendering
│   ├── mind/                # @arizen/mind       — local AI inference
│   ├── shell/               # @arizen/shell      — Win32 bindings
│   ├── flow/                # @arizen/flow       — animation engine
│   ├── skin/                # @arizen/skin       — theming SDK
│   ├── ui/                  # @arizen/ui         — component library
│   ├── widgets/             # @arizen/widgets    — widget runtime
│   ├── sync/                # @arizen/sync       — cross-device sync
│   ├── agent-sdk/           # @arizen/agent-sdk  — public plugin API
│   └── config/              # @arizen/config     — shared tooling config
│
├── branding/                # Design tokens, logos, fonts, press assets
├── docs/                    # This documentation tree
├── tests/                   # E2E, integration, visual regression, a11y
├── tools/                   # Internal build scripts and scaffolding
├── turbo.json               # Turborepo pipeline definition
└── pnpm-workspace.yaml      # pnpm workspace manifest
```

---

## Dependency Rules

The dependency graph is strictly enforced by CI. Violations cause build failures.

```
@arizen/core          → (no internal dependencies)
      ↓
@arizen/glass         → @arizen/core
@arizen/mind          → @arizen/core
@arizen/shell         → @arizen/core
@arizen/flow          → @arizen/core
@arizen/skin          → @arizen/core
      ↓
@arizen/ui            → @arizen/core, @arizen/glass, @arizen/flow, @arizen/skin
      ↓
@arizen/widgets       → @arizen/ui, @arizen/core
@arizen/sync          → @arizen/core
@arizen/agent-sdk     → @arizen/core
      ↓
apps/*                → any packages/* (never each other)
```

**Rules:**
- `@arizen/core` has no internal dependencies. It is the foundation everything else builds on.
- Apps may not import each other. They communicate through IPC channels managed by `@arizen/core`.
- `@arizen/agent-sdk` is the only package with a public stability guarantee. All other packages are internal APIs subject to change.

---

## Key Components

### @arizen/core — Primitives

The foundation layer. Every other package depends on it.

- **Logger** — structured logging with log-level filtering and rotation
- **EventBus** — typed pub/sub used for cross-component communication
- **IPC** — Electron main/renderer bridge with typed message schemas
- **Config** — hierarchical configuration system (user → machine → defaults)
- **Error types** — typed error hierarchy used across all packages

Stability level: **Stable**. No breaking changes without a major version bump.

### @arizen/glass — GPU Rendering Engine

The visual differentiation of ArizenOS.

Built on DirectComposition and Direct2D via N-API bindings. Key capabilities:
- **Real-time gaussian blur** — rendered at native resolution on supported GPUs
- **Depth layers** — UI elements cast depth shadows computed from the Z-order
- **Light response** — ambient light simulation based on window position
- **Fallback renderer** — CSS `backdrop-filter` fallback for unsupported hardware

### @arizen/mind — Local AI Inference

The AI brain of ArizenOS.

Wraps `llama.cpp` with a Node.js N-API binding. Key capabilities:
- **Streaming inference** — tokens stream as they are generated, not all-at-once
- **Multi-model** — multiple models loaded simultaneously at configurable memory budgets
- **Context management** — automatic context window management with priority-based eviction
- **Tool calling** — structured output for LLM function calling (used by Arizen Agent)
- **Embeddings** — vector embedding for semantic search (used by Arizen Hub)

### @arizen/shell — Windows Integration

The layer that connects ArizenOS to Windows.

N-API bindings to:
- **DWM (Desktop Window Manager)** — window composition, thumbnail generation
- **Win32 Shell APIs** — taskbar, start menu, system tray, jump lists
- **DirectComposition** — off-screen surface management for glass rendering
- **WinRT** — Windows 10/11 native APIs for notifications, calendar, and system state
- **Windows Search** — deep integration with Windows Search index

### @arizen/agent-sdk — Public Plugin API

The extension point for third-party tools in Arizen Agent.

Provides:
- **Tool registration** — declare a tool's name, description, schema, and handler
- **Permission declarations** — tools declare the permissions they require
- **Sandboxed execution** — tools run in a restricted context
- **Result types** — typed return values for text, files, UI, and errors

This is the only package with a public stability SemVer guarantee.

---

## Build Pipeline

Turborepo manages the build pipeline with task dependency resolution and aggressive caching.

```json
// turbo.json (simplified)
{
  "pipeline": {
    "build":     { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "dev":       { "dependsOn": ["^build"], "persistent": true },
    "test":      { "dependsOn": ["^build"] },
    "lint":      { "outputs": [] },
    "typecheck": { "dependsOn": ["^build"] }
  }
}
```

**Build order** (resolved automatically by Turborepo):
1. `@arizen/core`
2. `@arizen/glass`, `@arizen/mind`, `@arizen/shell`, `@arizen/flow`, `@arizen/skin` (parallel)
3. `@arizen/ui`, `@arizen/sync`, `@arizen/agent-sdk`, `@arizen/widgets` (parallel)
4. `apps/*` (parallel)

---

## Inter-Process Communication

ArizenOS apps are Electron applications. Each app has a main process (Node.js) and renderer process(es) (Chromium). Communication uses Electron's `ipcMain` / `ipcRenderer`, wrapped by `@arizen/core` IPC utilities with:

- **Typed channels** — TypeScript schemas enforced at compile time
- **Request-response** — for operations with a single response
- **Streaming** — for AI token streaming and real-time data
- **Broadcast** — for system-wide events (theme change, model loaded, etc.)

Apps communicate with each other through a **Hub process** that acts as the system broker — apps do not call each other directly.

---

## Further Reading

- [ADR-0001 — Monorepo Architecture](ADR-0001-monorepo.md)
- [ADR-0002 — Glass Rendering Engine](ADR-0002-glass-rendering.md)
- [ADR-0003 — Local AI Inference Stack](ADR-0003-local-ai.md)
- [Dependency Graph](dependency-graph.md)
- [API Reference](../api/README.md)
