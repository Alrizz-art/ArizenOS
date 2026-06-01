# ArizenOS Icon Specification

> **Layer:** Interface — pixel-precise, format-strict  
> **Contributors:** Core Team only  
> **Formats:** PNG · SVG · .cur · .ani

---

## Overview

ArizenOS icons are interface atoms. They must be pixel-precise, optically balanced, and designed within a strict grid. Icons are never decorative — each one communicates a specific function or represents a specific application. They must be legible on Liquid Glass surfaces at all defined sizes.

---

## Icon Categories

### 1. App Icons (`icons/app/`)

Application icons for first-party ArizenOS applications.

| Application | Icon Files | Sizes |
|-------------|-----------|-------|
| ArizenHub | `arizenos-hub-256.png`, `arizenos-hub-128.png`, `arizenos-hub-64.png` | 256, 128, 64 |
| ArizenAgent | `arizenos-agent-256.png`, `arizenos-agent-128.png`, `arizenos-agent-64.png` | 256, 128, 64 |
| ArizenLauncher | `arizenos-launcher-256.png`, `arizenos-launcher-128.png` | 256, 128 |
| ArizenMind | `arizenos-mind-256.png`, `arizenos-mind-128.png` | 256, 128 |
| ArizenVoice | `arizenos-voice-256.png`, `arizenos-voice-128.png` | 256, 128 |

All app icons must be exported in the sizes listed. The 256px version is the primary.

### 2. System Icons (`icons/system/`)

Windows cursor set for the ArizenOS shell theme.

| File | Format | State |
|------|--------|-------|
| `arizenos-cursor-default.cur` | Windows Cursor | Normal select |
| `arizenos-cursor-pointer.cur` | Windows Cursor | Link/button hover |
| `arizenos-cursor-wait.ani` | Animated Cursor | Busy / loading |
| `arizenos-cursor-text.cur` | Windows Cursor | Text input |

### 3. Source Files (`icons/source/`)

| File | Contents |
|------|---------|
| `icons.fig` | Master Figma source for all icons — all sizes, all states |

---

## Icon Grid System

All app icons are designed on a **256×256 grid** with the following zones:

```
┌────────────────────────────────────────┐ 256px
│  8px margin                            │
│  ┌──────────────────────────────────┐  │
│  │  16px safe zone (inner padding)  │  │
│  │  ┌──────────────────────────┐    │  │
│  │  │                          │    │  │
│  │  │   192×192 content area   │    │  │
│  │  │   (icon body lives here) │    │  │
│  │  │                          │    │  │
│  │  └──────────────────────────┘    │  │
│  └──────────────────────────────────┘  │
│                                        │
└────────────────────────────────────────┘
```

- **8px outer margin:** Clear space, no visual content
- **16px safe zone:** Soft content (glows, halos, shadows allowed)
- **192×192 content area:** All primary icon shapes

This grid scales proportionally: at 128px = 96×96 content area, at 64px = 48×48.

---

## Design Standards

### Shape Language

ArizenOS app icons use a **rounded rectangle container** (squircle) with:
- Corner radius: 22.4% of icon width (57px at 256px)
- Matches Apple's icon shape for cross-platform visual harmony

### Glass Treatment

App icons use a subtle Liquid Glass treatment on the container:
- Background: `glass-white-12` to `glass-white-16` over a brand-colored base
- Border: 1px inner stroke at `glass-white-16`
- Depth shadow: `rgba(0,0,0,0.24)` at 0px X, 8px Y, 24px blur, 0px spread

### Symbol Design

The icon symbol (the visual inside the container) must:
- Be optically centered (not mathematically — adjust for visual weight)
- Use 2-weight strokes at 256px (scale proportionally)
- Use `void-100` (#CDD9E5) for icon tint on dark containers
- Use `arizen-400` (#3D8FE0) as the signature accent color
- Not use gradients unless explicitly approved for a specific icon

### Prohibited in Icons
- No more than 3 colors (excluding transparency)
- No raster elements at any size (icons are built from vectors, exported as PNG)
- No text in icons
- No real-world photography or illustration in icons
- No pure `#000000` or `#FFFFFF`

---

## Export Specification

| Size | Format | Color Mode | Notes |
|------|--------|-----------|-------|
| 256×256 | PNG-32 | sRGB | Transparent background |
| 128×128 | PNG-32 | sRGB | Transparent background |
| 64×64 | PNG-32 | sRGB | Transparent background |

Export at exactly the specified pixel dimensions. No floating-point coordinates in the source — snap all paths to the pixel grid at each target size.

### ICO Bundle (for Windows)

Each app icon has a corresponding `.ico` file bundled for Windows:

```
arizenos-hub.ico     contains: 256, 128, 64, 32, 16 (all from PNG sources)
```

ICO files are generated from PNG sources using a build script — they are not stored in the repository. See `scripts/build-icons.ps1` (to be created in Phase 1).

---

## Cursor Specification

Cursors follow the Windows cursor format:
- Standard size: 32×32 pixels
- Hotspot: defined in `.cur` file header
- Animated cursors (`.ani`): 8 frames at 60ms per frame for wait animation
- Color: Uses `arizen-400` (#3D8FE0) as accent on `void-900` base
- Supports high-DPI via Windows cursor scaling (design at 32px, system scales)
