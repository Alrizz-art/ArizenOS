# @arizen/shell

> Windows OS integration layer for ArizenOS.

ArizenShell wraps Win32, WinUI3, and DWM APIs into a clean TypeScript interface. Every product that needs to talk to Windows — hotkeys, system tray, window management, process enumeration — does it through this package.

## What's in Here

| Export | Description |
|---|---|
| `WindowManager` | Enumerate, focus, move, resize, tile windows |
| `HotkeySystem` | Global hotkey registration and routing |
| `SystemTray` | Tray icon, context menu, balloon notifications |
| `ProcessList` | Running process enumeration with metadata |
| `DisplayManager` | Monitor topology, DPI, refresh rate |
| `PowerEvents` | Sleep/wake/lid events |
| `AppLaunch` | Launch, pin, and track applications |

## Platform Requirements

- Windows 10 Build 19041+ (20H1)
- Windows 11 Build 22000+
- ARM64 support: planned v0.6.0

## Native Bindings

ArizenShell uses N-API to call Win32 APIs from Node.js. Native bindings are prebuilt for distribution. To build from source:

```bash
pnpm --filter @arizen/shell build:native
```

Requires: Visual Studio Build Tools 2022, Windows SDK 10.0.22621
