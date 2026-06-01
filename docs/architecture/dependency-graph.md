# Dependency Graph

This document shows the complete dependency relationship between all `@arizen/*` packages and apps. The graph is enforced by CI — any import that violates these rules fails the build.

---

## Visual Dependency Graph

```
                          Windows Platform
                    ┌────────────────────────┐
                    │ Win32 · DWM · WinRT    │
                    │ DirectComposition       │
                    │ DirectX · Direct2D      │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │     @arizen/core        │
                    │ (zero internal deps)    │
                    └─┬──┬──┬──┬──┬──┬──┬───┘
                      │  │  │  │  │  │  │
          ┌───────────┘  │  │  │  │  │  └─────────────┐
          │              │  │  │  │  │                 │
    ┌─────▼──────┐  ┌────▼─┐ │ │ ┌─▼──────┐  ┌───────▼────┐
    │@arizen/    │  │@arizen│ │ │ │@arizen/│  │ @arizen/   │
    │glass       │  │/mind  │ │ │ │shell   │  │ flow       │
    └──────┬─────┘  └───┬───┘ │ │ └──┬─────┘  └─────┬──────┘
           │             │    │ │    │               │
           │    ┌────────┘    │ └────┤               │
           │    │         ┌───▼──────▼──────────────▼──┐
           │    │         │         @arizen/skin         │
           │    │         └────────────────┬─────────────┘
           │    │                          │
           └────┴──────────────────────────▼─────────────────┐
                                     @arizen/ui               │
                                (glass + flow + skin + core)  │
                                └──────────┬──────────────────┘
                                           │
              ┌────────────────────────────┼─────────────────┐
              │                            │                  │
    ┌─────────▼──────┐          ┌──────────▼────┐  ┌────────▼────────┐
    │@arizen/widgets │          │ @arizen/sync  │  │@arizen/agent-sdk│
    └───────┬─────────┘          └───────┬───────┘  └─────────┬───────┘
            │                            │                      │
            └────────────────────────────┼──────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │                   apps/*                 │
                    │  launcher · assistant · voice · hub      │
                    │  agent                                    │
                    │                                          │
                    │  (apps depend on packages, never on each  │
                    │   other — inter-app via IPC through Hub)  │
                    └──────────────────────────────────────────┘
```

---

## Dependency Table

| Package | Depends On |
|---|---|
| `@arizen/core` | *(nothing — no internal deps)* |
| `@arizen/glass` | `@arizen/core` |
| `@arizen/mind` | `@arizen/core` |
| `@arizen/shell` | `@arizen/core` |
| `@arizen/flow` | `@arizen/core` |
| `@arizen/skin` | `@arizen/core` |
| `@arizen/ui` | `@arizen/core`, `@arizen/glass`, `@arizen/flow`, `@arizen/skin` |
| `@arizen/widgets` | `@arizen/core`, `@arizen/ui` |
| `@arizen/sync` | `@arizen/core` |
| `@arizen/agent-sdk` | `@arizen/core` |
| `@arizen/config` | *(nothing — dev-only tooling)* |
| `apps/launcher` | `@arizen/core`, `@arizen/shell`, `@arizen/glass`, `@arizen/ui`, `@arizen/skin`, `@arizen/flow` |
| `apps/assistant` | `@arizen/core`, `@arizen/mind`, `@arizen/ui`, `@arizen/skin`, `@arizen/flow` |
| `apps/voice` | `@arizen/core`, `@arizen/mind`, `@arizen/shell` |
| `apps/hub` | `@arizen/core`, `@arizen/ui`, `@arizen/skin`, `@arizen/widgets`, `@arizen/sync`, `@arizen/agent-sdk` |
| `apps/agent` | `@arizen/core`, `@arizen/mind`, `@arizen/agent-sdk`, `@arizen/shell` |

---

## Dependency Rules

### Rule 1 — `@arizen/core` has no internal dependencies
`core` is the universal foundation. If any package needs something from `core`, it imports from `core`. `core` never imports from any other `@arizen/*` package.

**Enforcement:** `eslint-plugin-import` rule `no-restricted-imports` in `packages/core/.eslintrc`.

### Rule 2 — Platform packages are independent of each other
`@arizen/glass`, `@arizen/mind`, `@arizen/shell`, `@arizen/flow`, and `@arizen/skin` do not import each other. They all depend only on `@arizen/core`.

**Rationale:** Prevents circular dependencies, keeps each platform package independently testable.

### Rule 3 — `@arizen/ui` is the only package that depends on multiple platform packages
`ui` aggregates the platform packages into a coherent component system. This is its explicit purpose. `ui` depends on `glass` (for GlassPanel components), `flow` (for animated transitions), and `skin` (for design tokens).

### Rule 4 — Apps depend on packages; never on each other
An app may import from any package. Apps never import from other apps. Cross-app communication goes through the Hub IPC broker.

**Rationale:** Apps have independent Electron processes. Cross-app imports would create build-time coupling between separate processes and violate process isolation.

### Rule 5 — `@arizen/agent-sdk` is the only package with external stability guarantees
Third-party extension authors depend on `agent-sdk`. Its API changes follow strict SemVer. All other packages are internal and may change between minor versions.

---

## Turbo Build Order

Turborepo resolves the following build order from the dependency graph:

```
Tier 1 (parallel):  @arizen/core, @arizen/config
Tier 2 (parallel):  @arizen/glass, @arizen/mind, @arizen/shell, @arizen/flow, @arizen/skin
Tier 3 (parallel):  @arizen/ui, @arizen/sync, @arizen/agent-sdk
Tier 4 (parallel):  @arizen/widgets, apps/*
```

Each tier waits for all packages in the previous tier to complete before starting.
