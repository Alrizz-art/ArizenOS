# ArizenOS Wallpaper Specification

> **Layer:** Environment — desktop/lockscreen/OOBE surfaces  
> **Contributors:** Core Team + approved contributors (Issue approval required)  
> **Formats:** JPG (photo wallpapers) · PNG (graphic wallpapers)

---

## Overview

ArizenOS wallpapers are the environmental canvas of the desktop experience. They must be designed to work *beneath* the Liquid Glass shell — they are backdrops for translucent glass surfaces, not standalone artworks. This is the most critical distinction: a wallpaper that looks beautiful in isolation may destroy the usability of the glass UI overlaid on top of it.

---

## Wallpaper Categories

### 1. Desktop Wallpapers (`wallpapers/desktop/`)

The primary desktop background. Required for all major releases.

#### Dark Variant (`wallpapers/desktop/dark/`)
The flagship ArizenOS aesthetic. Deep, luminous, composed around the Void palette.

| File | Resolution | Required |
|------|-----------|---------|
| `arizenos-wall-dark-4k.jpg` | 3840×2160 | Yes |
| `arizenos-wall-dark-2k.jpg` | 2560×1440 | Yes |
| `arizenos-wall-dark-fhd.jpg` | 1920×1080 | Yes (minimum) |
| `arizenos-wall-dark-hd.jpg` | 1280×720 | Optional |

#### Light Variant (`wallpapers/desktop/light/`)
For users who prefer a light system theme.

| File | Resolution | Required |
|------|-----------|---------|
| `arizenos-wall-light-4k.jpg` | 3840×2160 | Optional |
| `arizenos-wall-light-2k.jpg` | 2560×1440 | Optional |
| `arizenos-wall-light-fhd.jpg` | 1920×1080 | Yes if light theme is supported |
| `arizenos-wall-light-hd.jpg` | 1280×720 | Optional |

#### Liquid Glass Variant (`wallpapers/desktop/glass/`)
Premium wallpaper with integrated Liquid Glass compositional elements — designed to look like the desktop surface is itself made of glass.

| File | Resolution | Required |
|------|-----------|---------|
| `arizenos-wall-glass-4k.jpg` | 3840×2160 | Yes |
| `arizenos-wall-glass-2k.jpg` | 2560×1440 | Yes |
| `arizenos-wall-glass-fhd.jpg` | 1920×1080 | Yes |

### 2. Lockscreen Wallpapers (`wallpapers/lockscreen/`)

Displayed on the Windows lockscreen. Fullscreen, no UI chrome overlaid.

| File | Resolution | Required |
|------|-----------|---------|
| `arizenos-lock-dark-fhd.jpg` | 1920×1080 | Yes |
| `arizenos-lock-dark-4k.jpg` | 3840×2160 | Yes |
| `arizenos-lock-light-fhd.jpg` | 1920×1080 | Optional |
| `arizenos-lock-light-4k.jpg` | 3840×2160 | Optional |

Lockscreen wallpapers may feature the ArizenOS wordmark or glyph in a subtle, low-opacity treatment.

### 3. OOBE Wallpapers (`wallpapers/oobe/`)

Out-of-box experience background. Displayed during initial setup. Must be calm, welcoming, and legible behind white OOBE UI chrome.

| File | Resolution | Required |
|------|-----------|---------|
| `arizenos-oobe-bg-fhd.jpg` | 1920×1080 | Yes |
| `arizenos-oobe-bg-4k.jpg` | 3840×2160 | Yes |

---

## Design Standards

### Composition Rules for Glass Compatibility

Wallpapers must be designed with the glass shell in mind:

1. **Avoid high-contrast clutter in taskbar zones.** The bottom 48px (standard DPI) and top 32px are occupied by the ArizenOS shell. These regions must be visually calm — no text, no bright objects, no high-frequency detail.

2. **Avoid horizontal bands of high contrast.** The Liquid Glass taskbar and launcher use blur compositing. Horizontal stripes of alternating light/dark break the glass illusion.

3. **The "stage" principle.** The center of the wallpaper is where the user's windows live. It should recede — darker, less detailed, lower saturation — so that app windows read clearly on top.

4. **Depth through light.** ArizenOS's aesthetic favors light sources at distance — stars, gradients from deep space, glow from a horizon. Avoid flat gradients and geometric patterns as the sole compositional element.

### Color Constraints

| Constraint | Rule |
|-----------|------|
| Brightness range | 8%–65% luminance for dark wallpapers; 55%–92% for light |
| Saturation | Wallpaper saturation ≤ 40% in taskbar zones to preserve glass legibility |
| Brand blue | `arizen-500` (#1470CC) may appear as accent light source |
| Prohibited colors | No pure `#000000` or `#FFFFFF` in final export |

### Resolution Requirements

| Resolution | DPI | Aspect Ratio |
|-----------|-----|-------------|
| 3840×2160 (4K) | 72 screen | 16:9 |
| 2560×1440 (2K) | 72 screen | 16:9 |
| 1920×1080 (FHD) | 72 screen | 16:9 |
| 1280×720 (HD) | 72 screen | 16:9 |

All wallpapers must be 16:9. Other aspect ratios (21:9, 16:10) are not in scope for v1.0.

### Export Specification

| Setting | Value |
|---------|-------|
| Format | JPEG |
| Quality | 92 minimum (prefer 95 for 4K) |
| Color Space | sRGB |
| Encoding | Baseline JPEG (no progressive) |
| Metadata | Strip all EXIF/IPTC before commit |
| File size | ≤ 8MB for FHD; ≤ 20MB for 4K |

---

## Wallpaper Design References

**Primary Reference:** macOS Tahoe 26 — study the relationship between the wallpaper and the frosted glass menu bar. The wallpaper supports the glass; it does not compete with it.

**Secondary Reference:** Solo Leveling System UI — dark, luminous, depth with controlled neon accent. Use sparingly.

**Tertiary Reference:** JARVIS — ambient intelligence aesthetics. Light emerging from within the composition, not illuminating from outside.

---

## Scripts

Wallpapers are applied via `scripts/wallpaper.ps1`. When adding new wallpapers, update the script to reference the new paths in `branding/wallpapers/`.
