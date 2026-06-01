# ArizenOS — Repository Architecture

> Arizen Technologies — Principal Architecture v1.0
> Designed for scale: 6 products, 8 core modules, N contributors.

---

## Table of Contents

1. [Architecture Philosophy](#1-architecture-philosophy)
2. [Monorepo Structure](#2-monorepo-structure)
3. [Package Layout](#3-package-layout)
4. [Apps Layout](#4-apps-layout)
5. [Documentation Layout](#5-documentation-layout)
6. [Assets Layout](#6-assets-layout)
7. [Release Layout](#7-release-layout)
8. [Testing Layout](#8-testing-layout)
9. [CI/CD Layout](#9-cicd-layout)
10. [Dependency Graph](#10-dependency-graph)

---

## 1. Architecture Philosophy

### Why a Monorepo

ArizenOS ships as six products that share core infrastructure — a glass rendering engine, an AI inference layer, a theming system, and a common UI component library. Splitting these into separate repos would mean:

- Coordinating breaking changes across six repos simultaneously
- Duplicating CI/CD infrastructure six times
- Making cross-cutting refactors take weeks instead of hours
- Fragmenting the contributor experience

A monorepo with a turborepo-powered build pipeline gives us atomic cross-package commits, shared tooling, unified CI, and a single contribution entry point — without sacrificing the ability to version and release each product independently.

### Structural Principles

1. **Packages own their own types.** No shared `types/` directory at root. Each package exports its types.
2. **Apps consume packages, never each other.** Cross-app imports are banned. Shared code goes into a package first.
3. **No circular dependencies.** The dependency graph is a DAG. CI enforces this.
4. **Every directory is a package.** Even documentation has a `package.json` for tooling.
5. **Configuration is DRY at root, overridable at package.** `tsconfig.base.json`, `eslint.config.base.js`, `vitest.config.base.ts` live at root. Packages extend, not rewrite.
6. **Assets are versioned alongside code.** Design tokens, icon sets, and branding files live in the repo, not in external design tools.

---

## 2. Monorepo Structure

```
ArizenOS/
│
├── .github/                          # GitHub platform configuration
│   ├── workflows/                    # CI/CD pipelines
│   │   ├── ci.yml                   # Main CI: lint, typecheck, test
│   │   ├── release.yml              # Release automation
│   │   ├── nightly.yml              # Nightly build
│   │   ├── security.yml             # Security audit (Dependabot + CodeQL)
│   │   └── preview.yml              # PR preview deployments
│   ├── ISSUE_TEMPLATE/              # Issue forms (already live)
│   ├── PULL_REQUEST_TEMPLATE.md     # PR template (already live)
│   ├── CODEOWNERS                   # Auto-assign reviewers by path
│   ├── dependabot.yml               # Dependency update automation
│   └── labeler.yml                  # Auto-label PRs by path
│
├── apps/                             # Runnable end-user applications
│   ├── launcher/                    # Arizen Launcher
│   ├── assistant/                   # Arizen Assistant
│   ├── voice/                       # Arizen Voice
│   ├── hub/                         # Arizen Hub
│   └── agent/                       # Arizen Agent
│
├── packages/                         # Shared libraries and modules
│   ├── core/                        # @arizen/core — primitives, constants, logger
│   ├── ui/                          # @arizen/ui — shared component library
│   ├── glass/                       # @arizen/glass — GPU rendering engine
│   ├── mind/                        # @arizen/mind — AI inference layer
│   ├── shell/                       # @arizen/shell — OS integration layer
│   ├── flow/                        # @arizen/flow — animation system
│   ├── skin/                        # @arizen/skin — theming SDK
│   ├── widgets/                     # @arizen/widgets — widget runtime
│   ├── sync/                        # @arizen/sync — cross-device sync
│   ├── agent-sdk/                   # @arizen/agent-sdk — agent plugin API
│   └── config/                      # @arizen/config — shared build config
│
├── branding/                         # ArizenOS Branding
│   ├── logos/                       # All logo variants (SVG, PNG)
│   ├── fonts/                       # Licensed typefaces (Inter, Geist, Instrument Serif)
│   ├── icons/                       # System icon set
│   ├── tokens/                      # Design tokens (JSON + CSS)
│   ├── wallpapers/                  # Default wallpaper collection
│   └── press/                       # Press kit assets
│
├── docs/                             # All documentation
│   ├── site/                        # Docusaurus documentation site
│   ├── api/                         # Auto-generated API reference
│   ├── guides/                      # User and developer guides
│   ├── architecture/                # Architecture decision records (ADRs)
│   ├── rfcs/                        # Accepted RFCs
│   └── migration/                   # Version migration guides
│
├── tests/                            # Global test suites
│   ├── e2e/                         # End-to-end tests (Playwright)
│   ├── integration/                 # Cross-package integration tests
│   ├── visual/                      # Visual regression tests
│   ├── perf/                        # Performance benchmarks
│   └── accessibility/               # Automated a11y audit suite
│
├── tools/                            # Internal tooling and scripts
│   ├── scaffold/                    # Package/app scaffolding CLI
│   ├── tokens/                      # Design token compiler
│   ├── release/                     # Release automation scripts
│   ├── audit/                       # Dependency graph auditor
│   └── ci/                          # CI helper scripts
│
├── releases/                         # Release artifacts and manifests
│   ├── manifests/                   # Per-version release manifests (JSON)
│   ├── changelogs/                  # Per-product changelogs
│   └── checksums/                   # SHA256 checksums for release artifacts
│
├── ARCHITECTURE.md                  # This document
├── BRAND_GUIDELINES.md              # Brand handbook
├── CHANGELOG.md                     # Root changelog (ArizenOS umbrella)
├── CODE_OF_CONDUCT.md               # Community standards
├── CONTRIBUTING.md                  # Contribution guide
├── GOVERNANCE.md                    # Project governance
├── LICENSE                          # MIT License
├── MAINTAINERS.md                   # Maintainer registry
├── PRODUCT_CHARTER.md               # Product charter
├── README.md                        # Repository home page
├── RELEASE.md                       # Release standards
├── SECURITY.md                      # Security policy
│
├── package.json                     # Root workspace config (pnpm)
├── pnpm-workspace.yaml              # pnpm workspace manifest
├── turbo.json                       # Turborepo pipeline config
├── tsconfig.base.json               # Base TypeScript config
├── eslint.config.base.js            # Base ESLint config
├── vitest.config.base.ts            # Base Vitest config
├── .editorconfig                    # Editor consistency
├── .gitignore                       # Git ignores
└── .nvmrc                           # Node version pin
```

---

## 3. Package Layout

Each package under `packages/` follows an identical internal structure — enforced by the scaffold tool.

### Standard Package Structure

```
packages/<name>/
├── src/
│   ├── index.ts               # Public API barrel — only export what consumers need
│   ├── types.ts               # All exported types/interfaces for this package
│   ├── constants.ts           # Package-level constants
│   ├── errors.ts              # Typed error classes
│   └── <feature>/             # Feature-grouped subdirectories
│       ├── index.ts           # Feature barrel
│       ├── <feature>.ts       # Implementation
│       └── <feature>.test.ts  # Co-located unit tests
├── tests/
│   └── integration/           # Integration tests for this package
├── docs/
│   └── README.md              # Package-level documentation
├── package.json               # Package manifest (@arizen/<name>)
├── tsconfig.json              # Extends ../../tsconfig.base.json
└── vitest.config.ts           # Extends ../../vitest.config.base.ts
```

### Package Catalog

| Package | Name | Purpose | Consumers |
|---|---|---|---|
| `core` | `@arizen/core` | Primitives, logger, event bus, error base classes | All packages |
| `config` | `@arizen/config` | Shared build configs (TS, ESLint, Vitest) | All packages |
| `glass` | `@arizen/glass` | GPU-accelerated blur, depth, and light rendering | `ui`, `shell`, `launcher`, `hub` |
| `mind` | `@arizen/mind` | Local LLM inference, context management, streaming | `assistant`, `agent`, `hub`, `widgets` |
| `shell` | `@arizen/shell` | Win32/WinUI3 OS integration, DWM, tray, hotkeys | `launcher`, `hub` |
| `flow` | `@arizen/flow` | Physics-based animation engine | `ui`, `glass` |
| `skin` | `@arizen/skin` | Design token loader, theme engine, hot reload | `ui`, all apps |
| `ui` | `@arizen/ui` | Shared component library (React) | All apps |
| `widgets` | `@arizen/widgets` | Widget runtime, widget plugin API | `launcher`, `hub` |
| `sync` | `@arizen/sync` | Cross-device preference and context sync | `hub`, `assistant` |
| `agent-sdk` | `@arizen/agent-sdk` | Public API for ArizenAgent plugins | `agent`, third-party |

### Package Dependency Rules (enforced by CI)

```
@arizen/core        → (no internal deps)
@arizen/config      → (no internal deps)
@arizen/glass       → @arizen/core
@arizen/flow        → @arizen/core
@arizen/skin        → @arizen/core
@arizen/mind        → @arizen/core
@arizen/shell       → @arizen/core
@arizen/ui          → @arizen/core, @arizen/glass, @arizen/flow, @arizen/skin
@arizen/widgets     → @arizen/core, @arizen/ui, @arizen/mind
@arizen/sync        → @arizen/core
@arizen/agent-sdk   → @arizen/core, @arizen/mind
```

No package may import from `apps/`. Cross-package circular imports fail CI.

---

## 4. Apps Layout

Each app under `apps/` is a deployable, releasable product.

### Standard App Structure

```
apps/<name>/
├── src/
│   ├── main.ts                # Entry point (Electron main / Tauri main / Node)
│   ├── renderer/              # UI layer (React)
│   │   ├── App.tsx
│   │   ├── pages/             # Route-level components
│   │   ├── components/        # App-specific components (not in @arizen/ui)
│   │   ├── hooks/             # App-specific React hooks
│   │   ├── stores/            # State management (Zustand)
│   │   └── styles/            # App-specific styles
│   ├── preload/               # Electron preload scripts
│   ├── ipc/                   # IPC handlers (main ↔ renderer)
│   └── services/              # App-specific services
├── tests/
│   ├── unit/
│   └── e2e/                   # App-level E2E (symlinked from /tests/e2e/<app>)
├── build/                     # Build output (gitignored)
├── resources/                 # App icons, manifests, installers
│   ├── icons/                 # App icon (all sizes)
│   ├── installer/             # NSIS / WiX installer config
│   └── manifest.json          # Windows app manifest
├── docs/
│   └── README.md
├── package.json               # @arizen/<app-name>
├── tsconfig.json
├── electron.config.ts         # (if Electron-based)
└── vite.config.ts             # Renderer build config
```

### App Catalog

#### `apps/launcher/` — Arizen Launcher
The primary desktop shell replacement. Replaces the Windows taskbar, Start menu, and launcher with the ArizenOS experience.

- **Runtime**: Electron + Win32 native bindings
- **Key deps**: `@arizen/shell`, `@arizen/glass`, `@arizen/ui`, `@arizen/widgets`, `@arizen/skin`
- **Audience**: All ArizenOS users
- **Release channel**: Bundled with ArizenOS core installer

```
apps/launcher/src/
├── main.ts                    # Electron main: tray, hotkeys, IPC
├── renderer/
│   ├── pages/
│   │   ├── Taskbar/           # Taskbar replacement
│   │   ├── StartMenu/         # Launcher / start menu
│   │   ├── Spotlight/         # Command palette
│   │   └── Notification/      # Notification center
│   └── components/
│       ├── AppGrid/
│       ├── SearchBar/
│       ├── SystemTray/
│       └── QuickSettings/
└── ipc/
    ├── window.ipc.ts
    ├── apps.ipc.ts
    └── system.ipc.ts
```

#### `apps/assistant/` — Arizen Assistant
The AI command layer. Answers questions, runs agentic tasks, summarizes, and connects to the local inference engine.

- **Runtime**: Electron (floating window, always-on-top)
- **Key deps**: `@arizen/mind`, `@arizen/glass`, `@arizen/ui`, `@arizen/sync`
- **Audience**: All ArizenOS users
- **Release channel**: Bundled with ArizenOS core installer

```
apps/assistant/src/
├── renderer/
│   ├── pages/
│   │   ├── Chat/              # Primary chat interface
│   │   ├── History/           # Conversation history
│   │   ├── Models/            # Local model management
│   │   └── Settings/          # Assistant configuration
│   └── components/
│       ├── MessageBubble/
│       ├── StreamingText/
│       ├── ModelSelector/
│       ├── ContextPanel/
│       └── ActionSuggestions/
└── services/
    ├── inference.service.ts   # Wraps @arizen/mind
    ├── context.service.ts     # Desktop context gathering
    └── history.service.ts     # Conversation persistence
```

#### `apps/voice/` — Arizen Voice
Wake-word detection, speech-to-text, and voice command routing. Integrates with ArizenMind for voice-driven AI.

- **Runtime**: Node.js native module + Electron tray app
- **Key deps**: `@arizen/mind`, `@arizen/core`
- **Audience**: Voice workflow users
- **Release channel**: Optional add-on, installable from Arizen Hub

```
apps/voice/src/
├── services/
│   ├── wake-word/             # Local wake word detection (Picovoice / Porcupine)
│   ├── stt/                   # Speech-to-text (Whisper.cpp GGUF)
│   ├── tts/                   # Text-to-speech (Kokoro / Piper)
│   └── router/                # Command routing to assistant/agent
└── renderer/
    └── pages/
        ├── VoiceStatus/       # Listening indicator overlay
        └── Settings/
```

#### `apps/hub/` — Arizen Hub
The ArizenOS control center: extension marketplace, settings, update manager, module status dashboard.

- **Runtime**: Electron
- **Key deps**: `@arizen/ui`, `@arizen/skin`, `@arizen/sync`, `@arizen/widgets`
- **Audience**: All ArizenOS users
- **Release channel**: Bundled with ArizenOS core installer

```
apps/hub/src/
├── renderer/
│   ├── pages/
│   │   ├── Dashboard/         # Module status, system health
│   │   ├── Extensions/        # Extension marketplace + installed
│   │   ├── Themes/            # Theme browser and applier
│   │   ├── Updates/           # Update manager
│   │   ├── Models/            # AI model downloader
│   │   └── Settings/          # System-wide ArizenOS settings
│   └── components/
│       ├── ExtensionCard/
│       ├── ThemePreview/
│       ├── UpdateBadge/
│       └── ModuleStatusBar/
└── services/
    ├── extensions.service.ts
    ├── updates.service.ts
    └── marketplace.service.ts
```

#### `apps/agent/` — Arizen Agent
Autonomous task execution. The Agent can take actions on the OS — open apps, read files, write outputs, browse the web — using a structured tool-call system built on ArizenMind.

- **Runtime**: Node.js service + Electron control panel
- **Key deps**: `@arizen/agent-sdk`, `@arizen/mind`, `@arizen/shell`
- **Audience**: Power users, developers
- **Release channel**: Optional add-on

```
apps/agent/src/
├── runtime/
│   ├── executor.ts            # Task execution engine
│   ├── planner.ts             # LLM-based task planner
│   ├── memory.ts              # Agent working memory
│   └── tools/                 # Built-in tool implementations
│       ├── filesystem.tool.ts
│       ├── browser.tool.ts
│       ├── shell.tool.ts
│       ├── clipboard.tool.ts
│       └── calendar.tool.ts
└── renderer/
    └── pages/
        ├── Tasks/             # Active and completed tasks
        ├── Logs/              # Execution trace viewer
        └── Permissions/       # Tool permission management
```

---

## 5. Documentation Layout

```
docs/
├── site/                             # Docusaurus documentation site
│   ├── docusaurus.config.ts
│   ├── sidebars.ts
│   ├── src/
│   │   ├── pages/                   # Custom pages (home, showcase)
│   │   ├── components/              # Doc site components
│   │   └── css/
│   │       └── custom.css           # ArizenOS branded doc theme
│   ├── docs/                        # All markdown content
│   │   ├── intro.md
│   │   ├── getting-started/
│   │   │   ├── installation.md
│   │   │   ├── quick-start.md
│   │   │   └── first-extension.md
│   │   ├── concepts/
│   │   │   ├── glass-engine.md
│   │   │   ├── mind-layer.md
│   │   │   ├── skin-system.md
│   │   │   └── agent-runtime.md
│   │   ├── guides/
│   │   │   ├── building-extensions.md
│   │   │   ├── creating-themes.md
│   │   │   ├── local-ai-setup.md
│   │   │   └── keyboard-shortcuts.md
│   │   └── api/                     # Auto-generated (do not hand-edit)
│   └── static/
│       └── img/
│
├── architecture/                     # Architecture Decision Records (ADRs)
│   ├── README.md                    # How to read and write ADRs
│   ├── ADR-0001-monorepo.md
│   ├── ADR-0002-electron-runtime.md
│   ├── ADR-0003-local-first-ai.md
│   ├── ADR-0004-glass-rendering.md
│   └── ADR-NNNN-<title>.md          # Template
│
├── rfcs/                             # Accepted RFCs (moved from Discussions)
│   ├── RFC-0001-plugin-api.md
│   └── RFC-NNNN-<title>.md
│
└── migration/                        # Version migration guides
    ├── v0.3-to-v0.4.md
    └── v0.4-to-v0.5.md
```

### Architecture Decision Records (ADR)

Every non-obvious architectural decision gets an ADR. Format:

```markdown
# ADR-NNNN: <Title>

**Status**: Accepted | Superseded by ADR-XXXX | Deprecated
**Date**: YYYY-MM-DD
**Deciders**: @github-handle, @github-handle

## Context
What situation forced this decision?

## Decision
What did we decide?

## Rationale
Why this over alternatives?

## Consequences
What becomes easier? What becomes harder? What do we accept?

## Alternatives Considered
What else was on the table?
```

---

## 6. Assets Layout

```
branding/
├── logos/
│   ├── svg/
│   │   ├── arizen-full-light.svg        # Full lockup, light variant
│   │   ├── arizen-full-dark.svg         # Full lockup, dark variant
│   │   ├── arizen-mark-light.svg        # Logomark only, light
│   │   ├── arizen-mark-dark.svg         # Logomark only, dark
│   │   ├── arizen-wordmark-light.svg    # Wordmark only, light
│   │   └── arizen-wordmark-dark.svg     # Wordmark only, dark
│   └── png/
│       ├── 1x/                          # 1× (72 DPI)
│       ├── 2x/                          # 2× (144 DPI)
│       └── 3x/                          # 3× (216 DPI)
│
├── fonts/
│   ├── Inter/                           # Inter Variable (OFL License)
│   ├── GeistMono/                       # Geist Mono (OFL License)
│   └── InstrumentSerif/                 # Instrument Serif (OFL License)
│
├── icons/
│   ├── system/                          # System icon set (SVG source)
│   │   ├── 16/
│   │   ├── 20/
│   │   ├── 24/
│   │   └── 32/
│   ├── app/                             # Per-app icons
│   │   ├── launcher.ico
│   │   ├── assistant.ico
│   │   ├── voice.ico
│   │   ├── hub.ico
│   │   └── agent.ico
│   └── generated/                       # Auto-generated icon sprites (gitignored, CI-built)
│
├── tokens/
│   ├── source/                          # Source of truth (JSON)
│   │   ├── color.json                   # Color palette tokens
│   │   ├── typography.json              # Type scale tokens
│   │   ├── spacing.json                 # Spacing scale
│   │   ├── radius.json                  # Border radius
│   │   ├── shadow.json                  # Shadow definitions
│   │   ├── motion.json                  # Animation duration/easing
│   │   └── blur.json                    # Blur radius scale
│   └── generated/                       # Compiled outputs (gitignored, CI-built)
│       ├── tokens.css                   # CSS custom properties
│       ├── tokens.js                    # ESM JS object
│       └── tokens.json                  # Raw JSON for tooling
│
├── wallpapers/
│   ├── default/                         # Default wallpaper set (light + dark)
│   └── community/                       # Community-submitted wallpapers
│
└── press/
    ├── press-kit-v1.0.zip               # Complete press kit archive
    ├── screenshots/                     # Official product screenshots
    │   ├── desktop-dark.png
    │   ├── desktop-light.png
    │   ├── launcher-open.png
    │   ├── assistant-chat.png
    │   └── hub-extensions.png
    └── descriptions/
        ├── one-liner.txt                # 1-sentence description
        ├── short.txt                    # 2-paragraph description
        └── long.txt                     # Full press description
```

### Token Compiler

Design tokens flow in one direction only:

```
branding/tokens/source/*.json
         ↓
    tools/tokens/ (compiler)
         ↓
branding/tokens/generated/      → packages/skin/  → all apps
```

The `@arizen/skin` package imports generated tokens. Apps never import raw token JSON directly.

---

## 7. Release Layout

```
releases/
├── manifests/                        # Per-release machine-readable manifests
│   ├── v0.4.0.json
│   ├── v0.4.1.json
│   └── latest.json                  # Symlink to current stable
│
├── changelogs/                       # Per-product changelogs
│   ├── CHANGELOG.md                 # Root (umbrella)
│   ├── launcher/CHANGELOG.md
│   ├── assistant/CHANGELOG.md
│   ├── voice/CHANGELOG.md
│   ├── hub/CHANGELOG.md
│   └── agent/CHANGELOG.md
│
└── checksums/
    ├── v0.4.0-SHA256SUMS.txt
    └── v0.4.1-SHA256SUMS.txt
```

### Release Manifest Schema

```json
{
  "$schema": "https://arizenos.dev/schemas/release-manifest/v1.json",
  "version": "0.5.0",
  "channel": "stable",
  "date": "2025-09-15T00:00:00Z",
  "products": {
    "launcher": { "version": "0.5.0", "sha256": "...", "url": "..." },
    "assistant": { "version": "0.5.0", "sha256": "...", "url": "..." },
    "voice": { "version": "0.5.0", "sha256": "...", "url": "..." },
    "hub": { "version": "0.5.0", "sha256": "...", "url": "..." },
    "agent": { "version": "0.5.0", "sha256": "...", "url": "..." }
  },
  "packages": {
    "@arizen/core": "1.5.0",
    "@arizen/glass": "0.5.0",
    "@arizen/mind": "0.5.0",
    "@arizen/ui": "0.5.0"
  },
  "minWindows": "10.0.19041",
  "releaseNotes": "https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.5.0",
  "rollback": "0.4.2"
}
```

### GitHub Releases Structure

Each GitHub Release is tagged and contains:

```
v0.5.0
├── ArizenOS-Setup-0.5.0.exe          # Full installer (all apps)
├── ArizenOS-Setup-0.5.0.exe.sig      # GPG signature
├── ArizenOS-Launcher-0.5.0.exe       # Standalone launcher installer
├── ArizenOS-Assistant-0.5.0.exe      # Standalone assistant installer
├── ArizenOS-Hub-0.5.0.exe            # Standalone hub installer
├── ArizenOS-Agent-0.5.0.exe          # Standalone agent installer
├── ArizenOS-Voice-0.5.0.exe          # Standalone voice installer
├── Source-0.5.0.zip                  # Source archive
└── SHA256SUMS.txt                    # Checksums for all artifacts
```

---

## 8. Testing Layout

```
tests/
├── e2e/                              # End-to-end tests (Playwright + Electron)
│   ├── playwright.config.ts
│   ├── launcher/
│   │   ├── taskbar.spec.ts
│   │   ├── launcher.spec.ts
│   │   └── spotlight.spec.ts
│   ├── assistant/
│   │   ├── chat.spec.ts
│   │   └── models.spec.ts
│   ├── hub/
│   │   ├── extensions.spec.ts
│   │   └── updates.spec.ts
│   └── fixtures/                    # Shared test fixtures
│       ├── clean-windows/           # Clean Windows VM snapshots (CI only)
│       └── mock-models/             # Tiny test models for CI inference
│
├── integration/                      # Cross-package integration tests
│   ├── mind-shell.test.ts           # ArizenMind ↔ ArizenShell integration
│   ├── glass-flow.test.ts           # ArizenGlass ↔ ArizenFlow integration
│   ├── skin-ui.test.ts              # ArizenSkin ↔ ArizenUI token resolution
│   └── agent-mind.test.ts           # ArizenAgent ↔ ArizenMind tool calls
│
├── visual/                           # Visual regression (Playwright screenshots)
│   ├── visual.config.ts
│   ├── snapshots/                   # Golden snapshots (committed)
│   │   ├── launcher-dark/
│   │   ├── launcher-light/
│   │   ├── assistant-chat/
│   │   └── hub-extensions/
│   └── specs/
│       ├── launcher.visual.spec.ts
│       ├── assistant.visual.spec.ts
│       └── hub.visual.spec.ts
│
├── perf/                             # Performance benchmarks
│   ├── benchmarks/
│   │   ├── glass-render.bench.ts    # FPS under load
│   │   ├── mind-inference.bench.ts  # Tokens/sec
│   │   └── startup.bench.ts         # Cold/warm launch time
│   └── budgets.json                 # Performance budgets (CI enforces)
│
└── accessibility/                    # Automated a11y audit
    ├── axe.config.ts
    └── specs/
        ├── launcher.a11y.spec.ts
        ├── assistant.a11y.spec.ts
        └── hub.a11y.spec.ts
```

### Test Execution Strategy

| Suite | When Runs | Blocking | Timeout |
|---|---|---|---|
| Unit (per package) | Every commit | ✅ Yes | 60s |
| Integration | Every PR | ✅ Yes | 5min |
| Visual regression | Every PR (UI changes) | ✅ Yes | 10min |
| Accessibility | Every PR (UI changes) | ✅ Yes | 5min |
| E2E | Pre-release only | ✅ Yes | 30min |
| Performance | Nightly | ⚠️ Warn only | 20min |

---

## 9. CI/CD Layout

```
.github/workflows/
│
├── ci.yml                            # Main CI — runs on every PR and push to main
├── release.yml                       # Release pipeline — triggered by version tags
├── nightly.yml                       # Nightly build — runs 02:00 UTC daily
├── security.yml                      # Security audit — Dependabot + CodeQL weekly
├── preview.yml                       # PR preview deployments (docs site)
├── token-compile.yml                 # Design token compilation on branding changes
└── dep-graph.yml                     # Dependency graph audit on package changes
```

### `ci.yml` — Main CI Pipeline

```yaml
# Triggered on: pull_request (main), push (main)
# Strategy: matrix across Node LTS versions, fail-fast: false

jobs:
  lint:          # ESLint + Prettier check
  typecheck:     # tsc --noEmit across all packages
  test-unit:     # pnpm turbo test:unit (all packages, parallelized)
  test-integ:    # pnpm turbo test:integration
  test-visual:   # Playwright visual regression (conditional: UI files changed)
  test-a11y:     # axe-core accessibility audit (conditional: UI files changed)
  dep-graph:     # Circular dependency check
  build:         # pnpm turbo build (verify all packages build cleanly)
  size-check:    # Bundle size budget check
```

**Turbo Pipeline Config (`turbo.json`):**

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test:unit": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "test:integration": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": { "outputs": [] },
    "typecheck": { "dependsOn": ["^build"], "outputs": [] },
    "dev": { "cache": false, "persistent": true }
  }
}
```

### `release.yml` — Release Pipeline

```yaml
# Triggered on: push of tag matching v*.*.* or v*.*.*-*
# Steps:

jobs:
  validate:
    - Verify tag matches CHANGELOG.md entry
    - Verify all CI checks passed on tagged commit
    - Verify release manifest exists in releases/manifests/

  build-artifacts:
    strategy:
      matrix: [launcher, assistant, voice, hub, agent]
    - pnpm build --filter @arizen/<product>
    - Code sign with Arizen Technologies certificate
    - Generate installer (NSIS)
    - Compute SHA256 checksum

  publish-release:
    - Upload artifacts to GitHub Release
    - Upload SHA256SUMS.txt
    - Update releases/manifests/latest.json
    - Trigger docs site deployment

  notify:
    - Post to GitHub Discussions (announcements)
    - Update nightly channel pointer
```

### `security.yml` — Security Pipeline

```yaml
# Triggered on: schedule (weekly, Mon 03:00 UTC) + push to main

jobs:
  codeql:
    - CodeQL analysis (JavaScript, TypeScript)
    - SARIF upload to GitHub Security tab

  dependency-audit:
    - pnpm audit --audit-level=moderate
    - Fail on high/critical severity unfixed deps

  secret-scan:
    - trufflesecurity/trufflehog action
    - Blocks any accidental secret commits
```

### `CODEOWNERS`

```
# Global fallback — Technical Council
*                               @Alrizz-art

# Core packages
/packages/core/                 @Alrizz-art
/packages/glass/                @Alrizz-art
/packages/mind/                 @Alrizz-art
/packages/shell/                @Alrizz-art
/packages/ui/                   @Alrizz-art

# Apps
/apps/launcher/                 @Alrizz-art
/apps/assistant/                @Alrizz-art
/apps/voice/                    @Alrizz-art
/apps/hub/                      @Alrizz-art
/apps/agent/                    @Alrizz-art

# Branding and design — Design Review Committee
/branding/                      @Alrizz-art

# Governance documents
/GOVERNANCE.md                  @Alrizz-art
/CODE_OF_CONDUCT.md             @Alrizz-art
/SECURITY.md                    @Alrizz-art
```

---

## 10. Dependency Graph

```
                         ┌────────────────┐
                         │  @arizen/core  │
                         └───────┬────────┘
              ┌──────────────────┼────────────────────────┐
              │                  │                         │
    ┌─────────▼──────┐  ┌────────▼───────┐  ┌────────────▼───────┐
    │ @arizen/glass  │  │  @arizen/mind  │  │  @arizen/shell     │
    └────────┬───────┘  └────────┬───────┘  └────────────┬───────┘
             │                   │                        │
    ┌────────▼───────┐           │                        │
    │ @arizen/flow   │           │                        │
    └────────┬───────┘           │                        │
             │                   │                        │
    ┌────────▼───────────────────┼────────────────────────┼────────┐
    │                      @arizen/ui                              │
    └────────────────────────────┬─────────────────────────────────┘
                                 │
            ┌────────────────────┼──────────────────────┐
            │                    │                       │
    ┌───────▼──────┐   ┌─────────▼──────┐    ┌─────────▼──────┐
    │  @arizen/    │   │   @arizen/      │    │   @arizen/     │
    │   widgets    │   │    sync         │    │   agent-sdk    │
    └───────┬──────┘   └─────────┬──────┘    └─────────┬──────┘
            │                    │                       │
    ┌───────▼──────────────────────────────────────────▼──┐
    │                       APPS                           │
    │  launcher | assistant | voice | hub | agent          │
    └─────────────────────────────────────────────────────┘
```

### Rules Enforced by CI

1. No app may import from another app
2. No package may import from any app
3. No circular imports anywhere in the graph
4. `@arizen/core` has zero internal dependencies
5. All imports cross module boundaries through `index.ts` barrels only (no deep imports)

---

*ArizenOS Architecture Document v1.0 — June 2025*
*Maintained by the Technical Council*
*Any structural changes require an ADR and TC vote*
