# ADR-0001: Monorepo Architecture with Turborepo

**Status**: Accepted
**Date**: 2025-06-01
**Deciders**: @Alrizz-art

---

## Context

ArizenOS is being designed from day one to ship as multiple products (Launcher, Assistant, Voice, Hub, Agent) sharing significant infrastructure (glass rendering, AI inference, theming, UI components, shell integration).

The question was: **poly-repo or monorepo?**

## Decision

We use a **pnpm workspace monorepo** with **Turborepo** as the build orchestration layer.

## Rationale

1. **Shared code is the core value proposition.** The glass engine, AI layer, and component library must stay in sync. In a poly-repo, a breaking change to `@arizen/glass` requires coordinating PRs across 5 app repos simultaneously. In a monorepo, it's one atomic commit.

2. **Single contribution entry point.** Contributors file one PR, one issue, read one CONTRIBUTING.md. In a poly-repo, figuring out which repo to contribute to is a real barrier — we saw this kill contribution momentum in many open-source projects.

3. **CI/CD is simpler to maintain.** One pipeline definition, one secret store, one set of rules. Not five.

4. **Turborepo's remote cache.** CI builds are fast because unchanged packages are restored from cache. In a poly-repo, every repo runs full CI independently.

5. **pnpm workspaces** eliminate symlink complexity. `@arizen/glass` can be imported in `apps/launcher` like a published package, with zero publishing step during development.

## Consequences

**Easier:**
- Cross-package refactors are atomic commits
- Dependency upgrades apply everywhere at once
- Contributors have one place to start

**Harder:**
- The repo is larger — shallow clones recommended for CI
- Module boundary discipline must be enforced by tooling (we use the dep-graph CI job)
- Some contributors unfamiliar with monorepos will need onboarding

## Alternatives Considered

**Poly-repo (one repo per product + one per shared package)**
Rejected. Coordination cost dominates for a small team. The tooling overhead (npm publishing, version pinning, cross-repo PRs) exceeds the benefit of isolation.

**Single flat repo (no workspace, all code in src/)**
Rejected. Cannot version products independently. Cannot extract shared packages cleanly over time. Does not scale past ~5 contributors.
