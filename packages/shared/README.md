# @arizen/shared

> Cross-cutting runtime utilities for ArizenOS.

Provides config management, storage abstraction, IPC bridge utilities,
file system helpers, system info collectors, notification service,
keyboard shortcut registry, and telemetry primitives.

**Depends on:** `@arizen/core`

## Packages

| Export | Description |
|---|---|
| `ConfigManager` | Read/write user config with schema validation |
| `StorageAdapter` | Unified interface for local, session, secure storage |
| `TypedIPC` | Typed wrapper for Electron ipcMain/ipcRenderer |
| `SystemInfo` | Hardware, Windows edition, AME state detection |
| `NotificationService` | System tray + in-app toast notifications |
| `HotkeyRegistry` | Platform-agnostic keyboard shortcut binding |
