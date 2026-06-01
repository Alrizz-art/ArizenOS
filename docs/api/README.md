# API Reference

This section documents the TypeScript APIs for every `@arizen/*` package. All packages are written in strict TypeScript and ship full type definitions.

---

## Package Overview

| Package | Stability | Description |
|---|---|---|
| [`@arizen/core`](core.md) | Stable | Primitives, logger, event bus, IPC, config |
| [`@arizen/glass`](glass.md) | Beta | GPU glass rendering engine |
| [`@arizen/mind`](mind.md) | Beta | Local AI inference |
| [`@arizen/shell`](shell.md) | Beta | Windows OS integration |
| [`@arizen/flow`](flow.md) | Beta | Physics animation engine |
| [`@arizen/skin`](skin.md) | Beta | Theming and design token system |
| [`@arizen/ui`](ui.md) | Beta | Shared React component library |
| [`@arizen/widgets`](widgets.md) | Beta | Widget runtime and SDK |
| [`@arizen/sync`](sync.md) | Alpha | Cross-device sync (E2E encrypted) |
| [`@arizen/agent-sdk`](agent-sdk.md) | Beta | Public Agent extension API |

---

## Stability Levels

| Level | Meaning |
|---|---|
| **Stable** | Fully stable. No breaking changes without a major version bump. |
| **Beta** | API is mostly settled. Breaking changes are possible with deprecation notice. |
| **Alpha** | API is evolving. Breaking changes can happen between minor versions. |
| **Internal** | Not intended for external use. May change at any time. |

---

## Public API Contract

Only `@arizen/agent-sdk` and `@arizen/widgets` are considered **public APIs** — intended for use by third-party extension and widget authors. All other packages are internal to ArizenOS.

The `@arizen/agent-sdk` API follows SemVer strictly:
- **Patch** — bug fixes, no API change
- **Minor** — new capabilities added, fully backward compatible
- **Major** — breaking changes, with a migration guide

---

## Import Conventions

All packages use named exports:

```typescript
// ✅ Correct
import { createLogger, EventBus } from '@arizen/core'
import { MindEngine } from '@arizen/mind'
import { defineTool } from '@arizen/agent-sdk'

// ❌ Avoid default imports from packages
import ArizenCore from '@arizen/core'
```

---

## Error Handling

ArizenOS uses a typed error hierarchy rooted in `@arizen/core`:

```typescript
import { ArizenError, GlassError, MindError } from '@arizen/core'

try {
  await engine.generate(prompt)
} catch (error) {
  if (error instanceof MindError) {
    // Model-specific error — check error.code
    switch (error.code) {
      case 'MODEL_NOT_LOADED':   // ...
      case 'CONTEXT_OVERFLOW':   // ...
      case 'INFERENCE_FAILED':   // ...
    }
  }
  if (error instanceof ArizenError) {
    // Generic ArizenOS error
    console.error(error.message, error.context)
  }
}
```

All `ArizenError` subclasses expose:
- `message` — human-readable description
- `code` — machine-readable error code (string enum)
- `context` — additional structured data for debugging

---

## Versioning

Package versions are managed with [Changesets](https://github.com/changesets/changesets). Each package is versioned independently.

To see the current version of any package:
```bash
pnpm --filter @arizen/core exec node -e "console.log(require('./package.json').version)"
```

---

## TypeDoc

Auto-generated API documentation from JSDoc comments is published at [https://docs.arizenos.dev/api/typedoc](https://docs.arizenos.dev/api/typedoc) and updated on every release.
