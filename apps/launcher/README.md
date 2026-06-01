# Arizen Launcher

> `@arizen/launcher` — The ArizenOS desktop shell replacement.

Replaces the Windows taskbar, Start menu, and application launcher with the ArizenOS glass experience. The Launcher is the primary entry point for every ArizenOS user.

## Responsibilities

- Taskbar replacement (system tray, pinned apps, running apps, clock)
- Application launcher / Start menu replacement
- Spotlight-style command palette (`Win + Space`)
- Notification center
- Quick settings panel
- Virtual desktop management

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Electron + Win32 native bindings |
| UI | React 18 + `@arizen/ui` |
| Rendering | `@arizen/glass` (GPU-accelerated blur) |
| Animation | `@arizen/flow` |
| Theming | `@arizen/skin` |
| Widgets | `@arizen/widgets` |
| State | Zustand |
| IPC | Electron contextBridge |

## Development

```bash
# From repo root
pnpm --filter @arizen/launcher dev

# Run tests
pnpm --filter @arizen/launcher test

# Build installer
pnpm --filter @arizen/launcher build
```

## Architecture

See [`/ARCHITECTURE.md`](../../ARCHITECTURE.md) — Apps Layout section.

## Module Owner

See [`/MAINTAINERS.md`](../../MAINTAINERS.md)
