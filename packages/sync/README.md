# @arizen/sync

> Cross-device preference and context synchronization for ArizenOS.

ArizenSync is opt-in. By default, ArizenOS is fully local. When enabled, Sync serializes user preferences, theme config, assistant conversation history, and widget layouts — and replicates them across devices via end-to-end encrypted sync.

## What's in Here

| Export | Description |
|---|---|
| `SyncEngine` | Core sync engine — connect, push, pull |
| `SyncStore` | Typed key-value store with conflict resolution |
| `E2EEncryption` | AES-256-GCM encryption layer (key never leaves device) |
| `SyncStatus` | React hook — sync state and error surface |
| `ConflictResolver` | Last-write-wins with manual override option |

## Sync Scope

What is synced (user-configured, all opt-in):
- Theme and skin preferences
- Keyboard shortcut customizations
- Widget layouts and configurations
- Assistant conversation history (encrypted)
- Extension list (not extension data)

What is NEVER synced:
- AI model files
- File system data
- Passwords or credentials
- Clipboard contents
- System configuration

## Privacy

All sync data is end-to-end encrypted before leaving the device. Arizen Technologies cannot read synced data. The encryption key is derived from a user passphrase and never transmitted. See [`/SECURITY.md`](../../SECURITY.md).
