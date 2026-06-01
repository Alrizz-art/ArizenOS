# Desktop Setup Guide

This guide walks you through configuring ArizenOS for your specific workflow and hardware.

---

## Shell Mode

ArizenOS offers three levels of desktop integration:

### Full Shell Mode (Recommended)
Replaces the Windows taskbar, start menu, and notification area entirely. ArizenOS Launcher becomes the primary shell.

To enable: **Hub → Settings → Shell → Mode → Full Shell**

A brief screen flash occurs as Windows transitions the shell. No restart required.

### Overlay Mode
ArizenOS Launcher sits on top of the Windows taskbar. Both are visible and functional. Good for trying ArizenOS without committing.

To enable: **Hub → Settings → Shell → Mode → Overlay**

### Headless Mode
No shell replacement. Only Arizen Assistant, Voice, and Agent run. Useful for power users who prefer a custom WM setup or are using third-party shell tools.

To enable: **Hub → Settings → Shell → Mode → Headless**

---

## Arizen Launcher

### Taskbar Position
The taskbar can be positioned at the bottom (default), top, left, or right of each monitor.

**Hub → Settings → Launcher → Taskbar → Position**

### Taskbar Height
Adjust taskbar height between 40px (compact) and 72px (large). On high-DPI displays, the default scales automatically with your display scaling setting.

**Hub → Settings → Launcher → Taskbar → Height**

### Pinned Applications
Drag any application from the Launcher to pin it to the taskbar. Right-click a pinned app for options: Launch at startup, Open as admin, Unpin.

### Spotlight Search
Press **Win + \`** to open the Spotlight launcher. Type to search:
- Applications and documents
- Settings (prefix with `>`, e.g. `> glass quality`)
- Web search (prefix with `?`)
- Calculator (type an expression, e.g. `128 * 1.2`)
- Unit conversion (e.g. `16 USD to EUR`)
- File content search (prefix with `f:`)

### Virtual Desktops
ArizenOS enhances the native Windows virtual desktop system with:
- Named desktops with custom accent colors
- Per-desktop wallpaper and theme overrides
- Smooth animated transitions (configurable in Hub → Settings → Launcher → Animations)
- Keyboard shortcuts: `Win + Ctrl + ←/→` to switch, `Win + Ctrl + D` to create

---

## Display & Glass Settings

### Glass Quality
Controls the resolution and complexity of the glass blur effect.

| Setting | GPU Load | Visual Quality |
|---|---|---|
| Ultra | High | Native resolution, full depth layers |
| High (default) | Medium | Native resolution, 3 depth layers |
| Medium | Low | 75% resolution, 2 depth layers |
| Low | Minimal | 50% resolution, 1 depth layer |
| Off | None | Flat, opaque surfaces |

**Hub → Settings → Display → Glass Quality**

### Blur Radius
Fine-tune the blur strength independently of the quality preset. Range: 4–32px. Default: 16px.

### Depth & Shadow
Toggle depth shadows on/off, and adjust shadow intensity (0–100%). High shadow intensity creates a stronger sense of Z-layering between panels.

### Reduced Motion
ArizenOS respects the Windows system setting `Prefer reduced motion`. When enabled, all animations are replaced with instant transitions. You can also override this independently:

**Hub → Settings → Display → Motion → Prefer Reduced Motion**

---

## Multi-Monitor Setup

ArizenOS automatically detects all connected monitors. Each monitor gets its own taskbar instance.

### Per-Monitor Configuration
Right-click any monitor in **Hub → Settings → Displays** to configure:
- Independent taskbar position and height
- Primary monitor designation
- Glass quality override per monitor
- Wallpaper assignment

### Spanning Wallpaper
To span a single wallpaper across all monitors: **Hub → Settings → Displays → Wallpaper → Span across monitors**

---

## Startup & Performance

### Startup Applications
Manage which applications launch with Windows from **Hub → Settings → Startup**. ArizenOS provides a unified view of all startup entries including those from the Windows registry and Task Scheduler.

### Memory Usage
Monitor ArizenOS's footprint from **Hub → Settings → Performance**. Shows:
- Shell memory usage
- Loaded AI model VRAM/RAM usage
- Widget runtime memory
- Background agent processes

### Performance Profiles
| Profile | Description |
|---|---|
| **Efficiency** | Reduces glass quality and AI context size to minimise resource use |
| **Balanced (default)** | Standard settings — good for most hardware |
| **Performance** | Maximises GPU utilisation for glass and AI response speed |
| **Custom** | Fine-tune every parameter individually |

**Hub → Settings → Performance → Profile**

---

## Notifications

### Notification Center
ArizenOS replaces the Windows notification center with a glass panel accessible from the system tray area. Swipe left on a notification to dismiss. Swipe right to snooze (5/15/60 min options).

### Do Not Disturb
**Win + Shift + D** toggles DND mode. In DND:
- Notifications are received but not displayed
- The taskbar notification badge count continues to increment
- Focus assist apps (e.g. games in fullscreen) automatically trigger DND

### App Notification Priority
Configure per-app notification priority in **Hub → Settings → Notifications → [App Name]**. Priority levels: Urgent (always shown), Normal, Low (batched), Silent (stored only).

---

## Wallpaper & Backgrounds

ArizenOS includes a dynamic wallpaper engine:
- **Static images** — any JPEG, PNG, or WebP
- **Video wallpapers** — MP4/WebM, GPU-decoded, no CPU overhead
- **Live wallpapers** — JavaScript-based interactive wallpapers from the Hub community
- **AI-generated** — Generate a wallpaper with a prompt via Arizen Assistant

**Hub → Wallpapers** to browse and set.
