# @arizen/core

> Primitives, logger, event bus, and error base classes for all ArizenOS packages.

The foundation of the entire monorepo. Every other package and app depends on `@arizen/core`. It has zero internal dependencies and changes infrequently by design.

## What's in Here

| Export | Description |
|---|---|
| `logger` | Structured logger (JSON in prod, pretty in dev) |
| `EventBus` | Typed cross-process event bus |
| `ArizenError` | Base error class with error codes |
| `invariant()` | Runtime assertion with typed messages |
| `Result<T, E>` | Rust-style Result type for error handling |
| Constants | App IDs, version constants, platform detection |

## Rules

- Zero runtime dependencies (only `devDependencies`)
- No DOM APIs — must run in main process, renderer, and Node.js
- 100% test coverage required
- No breaking changes without a MAJOR version bump
