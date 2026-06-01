# ArizenOS Test Suites

> Global test infrastructure for cross-package and end-to-end testing.

Unit tests live co-located with source (`src/**/*.test.ts`). This directory contains everything that spans package or app boundaries.

## Structure

| Directory | Runner | When |
|---|---|---|
| `e2e/` | Playwright + Electron | Pre-release only |
| `integration/` | Vitest | Every PR |
| `visual/` | Playwright screenshots | Every PR (UI changes) |
| `perf/` | Vitest bench | Nightly |
| `accessibility/` | axe-core + Playwright | Every PR (UI changes) |

## Running Tests

```bash
# All integration tests
pnpm test:integration

# Visual regression
pnpm test:visual

# Accessibility audit
pnpm test:a11y

# E2E (requires Windows + built apps)
pnpm test:e2e

# Performance benchmarks
pnpm test:perf
```

## Visual Regression

Golden snapshots are committed in `visual/snapshots/`. When a UI change causes a visual diff:
1. Review the diff in the CI artifact
2. If intended: run `pnpm test:visual:update` to accept new snapshots
3. Commit the updated snapshots in the same PR

Never auto-accept visual diffs without reviewing them.

## Performance Budgets

Budgets are defined in `perf/budgets.json`. CI warns (does not block) when a benchmark exceeds its budget. TC reviews performance regressions as part of release sign-off.
