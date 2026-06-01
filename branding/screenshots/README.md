# ArizenOS Screenshot Specification

> **Layer:** Evidence — curated product representation  
> **Contributors:** Any contributor (Issue approval + spec compliance required)  
> **Format:** PNG

---

## Overview

Official screenshots are the primary trust signal for new users, press, and contributors evaluating ArizenOS. They must be production-quality captures of a running ArizenOS installation — never mocked up in Figma or edited to show states the software cannot achieve. Authenticity is non-negotiable.

---

## Required Screenshot Set

A complete release requires the following 8 screenshots minimum. All are at 1920×1080 FHD resolution.

| # | Feature | File | Required |
|---|---------|------|---------|
| 1 | Desktop — full view, dark | `arizenos-ss-desktop-dark-v{x}.{y}.png` | Yes |
| 2 | Desktop — full view, glass | `arizenos-ss-desktop-glass-v{x}.{y}.png` | Yes |
| 3 | Launcher — open, dark | `arizenos-ss-launcher-dark-v{x}.{y}.png` | Yes |
| 4 | AI Layer — panel open, dark | `arizenos-ss-ailayer-dark-v{x}.{y}.png` | Yes |
| 5 | Settings UI — main view | `arizenos-ss-settings-dark-v{x}.{y}.png` | Yes |
| 6 | Widgets panel | `arizenos-ss-widgets-dark-v{x}.{y}.png` | Yes |
| 7 | Onboarding / OOBE | `arizenos-ss-oobe-dark-v{x}.{y}.png` | Yes |
| 8 | Desktop — full view, light | `arizenos-ss-desktop-light-v{x}.{y}.png` | Yes (if light theme ships) |

Optional additional screenshots:
- Voice interface: `arizenos-ss-voice-dark-v{x}.{y}.png`
- Agent panel: `arizenos-ss-agent-dark-v{x}.{y}.png`
- Personalization settings: `arizenos-ss-personalization-dark-v{x}.{y}.png`

---

## Capture Standards

### System State

Before taking any screenshot:

- [ ] ArizenOS is running on a clean installation (no personal files, no third-party apps visible)
- [ ] Display scaling is 100% (no DPI scaling)
- [ ] Resolution is set to 1920×1080
- [ ] ArizenOS glass effects are fully enabled
- [ ] System theme is set to the correct variant (dark/light) for the screenshot
- [ ] No personal data is visible anywhere on screen
- [ ] Clock shows a visually clean time (e.g. 9:41 — the Apple standard; or a contextually appropriate time)
- [ ] No notifications or system trays showing personal information
- [ ] No browser tabs with personal URLs visible
- [ ] Wallpaper is the official ArizenOS wallpaper for the variant

### Composition

- **Desktop screenshots:** Taskbar visible, at least 2 windows open in a realistic workflow state
- **Launcher:** Search field focused, showing results (use sample/dummy queries)
- **AI Layer:** Shows a meaningful, non-personal conversation or task output
- **Settings:** Clean, no personal info in any field
- **Widgets:** Clock, calendar showing clean placeholder data

### What is Prohibited in Screenshots
- Personal files, names, emails, or identifiers
- Third-party app windows that are not part of ArizenOS
- Error states, broken UI, placeholder "Lorem Ipsum" text in visible UI
- Screenshots taken with DPI scaling enabled (introduces blur artifacts)
- Screenshots cropped from a larger capture (must be full 1920×1080)
- Watermarks, copyright notices, or any overlay added in post-production

---

## Capture Procedure

1. Boot Windows with a clean ArizenOS installation
2. Apply official ArizenOS wallpaper via `scripts/wallpaper.ps1`
3. Set display to 1920×1080 at 100% scaling
4. Set up the system state per the checklist above
5. Use the Windows Snipping Tool or `Win + Shift + S` (full screen) — **not third-party tools**
6. Save directly as PNG (never screenshot to clipboard and paste into an editor)
7. Do not apply any post-processing, sharpening, color correction, or watermarking
8. Name the file per `NAMING_CONVENTIONS.md`

---

## File Specification

| Attribute | Value |
|-----------|-------|
| Format | PNG (PNG-24 minimum) |
| Resolution | 1920×1080 (standard); 3840×2160 (4K optional) |
| Color mode | sRGB |
| Bit depth | 24-bit (no transparency needed) |
| Compression | Standard PNG deflate (no lossy compression) |
| Metadata | Strip all EXIF before commit |
| Max file size | 6MB per screenshot |

---

## Screenshot Lifecycle

Screenshots are version-stamped. When a new product version ships:

1. New screenshots are captured at the new version
2. New files are added with the new version suffix (e.g. `-v1.2`)
3. Previous version screenshots are retained until 2 major versions old
4. See `VERSIONING.md` for the archiving policy
