# ArizenOS Branding Architecture

> **Version:** 1.0.0  
> **Status:** Canonical — all branding work follows this specification  
> **Owner:** Arizen Technologies Core Team

---

## 1. Architectural Intent

The ArizenOS branding system is structured as a **layered asset hierarchy** with clear separation between:

- **Identity Layer** — logos, wordmarks, glyphs (immutable, owner-controlled)
- **Environment Layer** — wallpapers, lockscreens, ambient surfaces (high-quality, versioned)
- **Interface Layer** — icons, system assets (pixel-precise, format-strict)
- **Evidence Layer** — screenshots, recordings (curated, composition-governed)
- **Partner Layer** — OEM assets (constrained customization, compliance-gated)
- **Outreach Layer** — marketing collateral (campaign-bound, voice-governed)
- **Production Layer** — templates (editable source files for contributors)

Each layer has independent naming rules, versioning policy, and contributor access level.

---

## 2. Full Directory Specification

```
branding/
│
├── README.md                        Master index + quick reference
├── ARCHITECTURE.md                  This file — structural specification
├── NAMING_CONVENTIONS.md            Unified naming rules
├── VERSIONING.md                    Asset version lifecycle
├── CONTRIBUTOR_GUIDE.md             Contributor onboarding and workflow
├── MIGRATION.md                     Legacy asset migration plan
│
├── logos/
│   ├── README.md                    Logo spec and usage rules
│   ├── primary/
│   │   ├── arizenos-logo-dark.svg          Primary logo, dark variant
│   │   ├── arizenos-logo-light.svg         Primary logo, light variant
│   │   ├── arizenos-logo-dark@2x.png       PNG export 1024×auto, dark
│   │   ├── arizenos-logo-light@2x.png      PNG export 1024×auto, light
│   │   ├── arizenos-logo-dark@1x.png       PNG export 512×auto, dark
│   │   └── arizenos-logo-light@1x.png      PNG export 512×auto, light
│   ├── wordmark/
│   │   ├── arizenos-wordmark-dark.svg
│   │   ├── arizenos-wordmark-light.svg
│   │   ├── arizenos-wordmark-dark@2x.png
│   │   └── arizenos-wordmark-light@2x.png
│   ├── glyph/
│   │   ├── arizenos-glyph-dark.svg         Symbol only, no text
│   │   ├── arizenos-glyph-light.svg
│   │   ├── arizenos-glyph-dark@2x.png      512×512px
│   │   ├── arizenos-glyph-light@2x.png
│   │   ├── arizenos-glyph-dark@1x.png      256×256px
│   │   └── arizenos-glyph-light@1x.png
│   ├── glass/
│   │   ├── arizenos-logo-glass.svg         Liquid Glass treatment variant
│   │   └── arizenos-logo-glass@2x.png
│   ├── monochrome/
│   │   ├── arizenos-logo-black.svg         Single-color (black)
│   │   ├── arizenos-logo-white.svg         Single-color (white)
│   │   ├── arizenos-logo-black@2x.png
│   │   └── arizenos-logo-white@2x.png
│   ├── oem/
│   │   ├── arizenos-oem-logo.bmp           Windows System OEM bitmap
│   │   └── arizenos-oem-logo-sm.bmp        Small OEM variant (96×96)
│   └── favicon/
│       ├── favicon.svg                     SVG favicon (modern browsers)
│       ├── favicon-32.png                  32×32 PNG
│       ├── favicon-16.png                  16×16 PNG
│       └── apple-touch-icon-180.png        180×180 iOS touch icon
│
├── wallpapers/
│   ├── README.md
│   ├── desktop/
│   │   ├── dark/
│   │   │   ├── arizenos-wall-dark-4k.jpg           3840×2160 (4K UHD)
│   │   │   ├── arizenos-wall-dark-2k.jpg           2560×1440 (QHD)
│   │   │   ├── arizenos-wall-dark-fhd.jpg          1920×1080 (FHD)
│   │   │   └── arizenos-wall-dark-hd.jpg           1280×720 (HD)
│   │   ├── light/
│   │   │   ├── arizenos-wall-light-4k.jpg
│   │   │   ├── arizenos-wall-light-2k.jpg
│   │   │   ├── arizenos-wall-light-fhd.jpg
│   │   │   └── arizenos-wall-light-hd.jpg
│   │   └── glass/
│   │       ├── arizenos-wall-glass-4k.jpg          Liquid Glass composition
│   │       ├── arizenos-wall-glass-2k.jpg
│   │       └── arizenos-wall-glass-fhd.jpg
│   ├── lockscreen/
│   │   ├── arizenos-lock-dark-fhd.jpg
│   │   ├── arizenos-lock-dark-4k.jpg
│   │   ├── arizenos-lock-light-fhd.jpg
│   │   └── arizenos-lock-light-4k.jpg
│   └── oobe/
│       ├── arizenos-oobe-bg-fhd.jpg               Out-of-box experience BG
│       └── arizenos-oobe-bg-4k.jpg
│
├── icons/
│   ├── README.md
│   ├── app/
│   │   ├── arizenos-hub-256.png                   ArizenHub app icon
│   │   ├── arizenos-hub-128.png
│   │   ├── arizenos-hub-64.png
│   │   ├── arizenos-agent-256.png
│   │   ├── arizenos-agent-128.png
│   │   ├── arizenos-launcher-256.png
│   │   ├── arizenos-launcher-128.png
│   │   ├── arizenos-mind-256.png
│   │   ├── arizenos-mind-128.png
│   │   ├── arizenos-voice-256.png
│   │   └── arizenos-voice-128.png
│   ├── system/
│   │   ├── arizenos-cursor-default.cur
│   │   ├── arizenos-cursor-pointer.cur
│   │   ├── arizenos-cursor-wait.ani
│   │   └── arizenos-cursor-text.cur
│   └── source/
│       └── icons.fig                              Figma source file
│
├── screenshots/
│   ├── README.md
│   ├── desktop/
│   │   ├── arizenos-ss-desktop-dark-v1.0.png
│   │   ├── arizenos-ss-desktop-light-v1.0.png
│   │   └── arizenos-ss-desktop-glass-v1.0.png
│   ├── launcher/
│   │   ├── arizenos-ss-launcher-dark-v1.0.png
│   │   └── arizenos-ss-launcher-light-v1.0.png
│   ├── ai-layer/
│   │   ├── arizenos-ss-ailayer-dark-v1.0.png
│   │   └── arizenos-ss-ailayer-light-v1.0.png
│   ├── settings/
│   │   └── arizenos-ss-settings-dark-v1.0.png
│   ├── widgets/
│   │   └── arizenos-ss-widgets-dark-v1.0.png
│   └── onboarding/
│       └── arizenos-ss-oobe-dark-v1.0.png
│
├── oem/
│   ├── README.md
│   ├── assets/
│   │   ├── arizenos-oem-logo.bmp                  System Properties logo
│   │   ├── arizenos-oem-logo-sm.bmp               Small system logo
│   │   └── arizenos-oem-banner.jpg                OEM support banner
│   ├── registry/
│   │   └── arizenos-oem-branding.reg              OEM registry entries
│   └── templates/
│       └── oem-info.ini.template                  OEM info template
│
├── marketing/
│   ├── README.md
│   ├── social/
│   │   ├── arizenos-og-image.png                  Open Graph (1200×630)
│   │   ├── arizenos-twitter-card.png              Twitter card (1200×628)
│   │   ├── arizenos-banner-github.png             GitHub profile/org banner
│   │   └── arizenos-avatar.png                    Profile avatar (400×400)
│   ├── press/
│   │   ├── arizenos-press-hero.png                Press kit hero image
│   │   ├── arizenos-press-screenshot-01.png
│   │   └── arizenos-press-screenshot-02.png
│   └── release/
│       ├── arizenos-release-banner-v1.0.png       Release announcement banner
│       └── arizenos-release-banner-template.fig   Editable Figma source
│
└── templates/
    ├── README.md
    ├── figma/
    │   ├── arizenos-brand-kit.fig                 Master Figma brand kit
    │   ├── arizenos-screenshot-template.fig
    │   └── arizenos-social-templates.fig
    └── export-spec.md                             Export settings for each asset type
```

---

## 3. Folder Purpose Summary

| Folder | Purpose | Access Level | Format |
|--------|---------|--------------|--------|
| `logos/` | Identity — all wordmark/glyph variants | Core Team only | SVG + PNG |
| `wallpapers/` | System environments — desktop/lock/OOBE | Core Team + Contributors | JPG/PNG |
| `icons/` | Interface atoms — app/system/cursor | Core Team only | PNG + ICO/CUR |
| `screenshots/` | Product evidence | Contributors (with spec) | PNG |
| `oem/` | Partner channel assets | Core Team only | BMP/REG/JPG |
| `marketing/` | Outreach and social | Core Team + Marketing | PNG/JPG |
| `templates/` | Source files for production | All contributors | .fig + .md |

---

## 4. Design Language Compliance

All assets must pass the following design language checks before merge:

| Check | Requirement |
|-------|-------------|
| **Liquid Glass** | Glass surfaces use defined blur radius and opacity tokens |
| **Color Fidelity** | All colors from `branding/tokens/source/color.json` |
| **Typography** | Inter Variable for UI, Geist Mono for code, Instrument Serif for marketing-only |
| **Hierarchy** | Visual levels follow the 6-layer depth system in `BRAND_GUIDELINES.md` |
| **Dark-first** | Dark variant is required; light variant is optional |
| **No Pure Black/White** | `#000000` and `#FFFFFF` are banned in all product assets |

---

## 5. Platform Targets

| Platform | Resolution | Format | Notes |
|----------|-----------|--------|-------|
| Windows 10 | 1920×1080+ | PNG/BMP/REG | Primary target |
| Windows 11 | 2560×1440+ | PNG/BMP/REG | Primary target |
| GitHub | Various | PNG/SVG | README, social |
| Web (marketing site) | 1200×630 | PNG | OG images |
| Press/Media | Print-ready | SVG/PNG@300dpi | Press kit only |
