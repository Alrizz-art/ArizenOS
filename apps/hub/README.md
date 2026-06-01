# Arizen Hub

> `@arizen/hub` — The ArizenOS control center.

The central management interface for everything ArizenOS: extensions, themes, AI models, system settings, and updates. Think of it as the App Store + System Preferences + Update Manager, built for ArizenOS.

## Responsibilities

- Extension marketplace (browse, install, uninstall, update)
- Theme browser and live preview
- AI model downloader and manager (GGUF models)
- ArizenOS system-wide settings
- Update manager (all ArizenOS products)
- Module health dashboard

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Electron |
| UI | React 18 + `@arizen/ui` |
| Theming | `@arizen/skin` |
| Sync | `@arizen/sync` |
| State | Zustand |

## Development

```bash
pnpm --filter @arizen/hub dev
pnpm --filter @arizen/hub test
pnpm --filter @arizen/hub build
```

## Module Owner

See [`/MAINTAINERS.md`](../../MAINTAINERS.md)
