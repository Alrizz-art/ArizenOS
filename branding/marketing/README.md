# ArizenOS Marketing Asset Specification

> **Layer:** Outreach — campaign-bound, brand-voice governed  
> **Contributors:** Core Team + Marketing contributors (Issue approval required)  
> **Formats:** PNG · JPG

---

## Overview

Marketing assets are the outward face of ArizenOS across social media, press, and the web. They must embody the ArizenOS brand voice — confident, intelligent, forward — and comply strictly with the brand color and typography system. Every marketing asset has a defined purpose and composition standard. No "random" creative work is accepted.

---

## Asset Categories

### 1. Social Assets (`marketing/social/`)

| File | Dimensions | Format | Platform |
|------|-----------|--------|---------|
| `arizenos-og-image.png` | 1200×630 | PNG | Open Graph (website, Discord, Slack link previews) |
| `arizenos-twitter-card.png` | 1200×628 | PNG | Twitter/X summary card |
| `arizenos-banner-github.png` | 1280×640 | PNG | GitHub org/profile/README banner |
| `arizenos-avatar.png` | 400×400 | PNG | GitHub, Twitter, Discord profile avatar |

### 2. Press Assets (`marketing/press/`)

| File | Dimensions | Format | Usage |
|------|-----------|--------|-------|
| `arizenos-press-hero.png` | 1920×1080 | PNG | Press kit hero image |
| `arizenos-press-screenshot-01.png` | 1920×1080 | PNG | Press kit screenshot 1 |
| `arizenos-press-screenshot-02.png` | 1920×1080 | PNG | Press kit screenshot 2 |

Press screenshots are hand-selected from the `screenshots/` collection and copied here for press kit distribution. They are not independently produced.

### 3. Release Assets (`marketing/release/`)

| File | Dimensions | Format | Usage |
|------|-----------|--------|-------|
| `arizenos-release-banner-v{x}.{y}.png` | 1200×630 | PNG | Release announcement (GitHub, Twitter, Reddit) |
| `arizenos-release-banner-template.fig` | — | Figma | Editable source for release banners |

Release banners are versioned (`-v1.0`, `-v1.2`) because they are announcement-specific. Previous versions are retained in the repository.

---

## Composition Standards

### Open Graph Image (`arizenos-og-image.png`)

The OG image appears when any link to the ArizenOS website or repo is shared. It is the most widely seen marketing asset.

**Layout:**
- Background: `void-900` (#0D1117) with subtle Liquid Glass texture
- Left zone (60%): ArizenOS Primary Logo (dark variant), vertically centered, left-padded 80px
- Right zone (40%): Product tagline "The Future of Personal AI Computing" in Inter Variable SemiBold 28px, `void-100` (#CDD9E5), right-padded 80px
- Bottom strip (40px): `arizen-500` (#1470CC) accent line, full width

**Do not:** include screenshots, feature lists, or third-party logos.

### GitHub Banner (`arizenos-banner-github.png`)

Displayed at the top of the GitHub organization page and README.

**Layout:**
- Background: `void-900` with horizontal gradient to `arizen-950`
- Center: ArizenOS Primary Logo (dark) at 40% of banner height
- Bottom-right: Tagline in Inter Variable 18px, `void-300` (#768390)

### Avatar (`arizenos-avatar.png`)

Used on all official ArizenOS social accounts.

**Layout:**
- Background: `arizen-600` (#1057A8) to `arizen-800` (#0A2D57) radial gradient
- Center: ArizenOS Glyph (light variant) at 60% of canvas size
- No text, no wordmark

### Release Banner (`arizenos-release-banner-v{x}.{y}.png`)

Announcement-specific. Must communicate version number and key highlight.

**Layout:**
- Background: `void-950` to `arizen-900` diagonal gradient
- Top-left: ArizenOS glyph, 64×64px
- Center: Release headline (Inter Variable Bold 48px) — "ArizenOS v1.0"
- Below: One-line description (Inter Variable Regular 24px)
- Bottom-right: Version badge — pill shape, `arizen-500` fill, white text
- Optional: Subtle Liquid Glass overlay element

---

## Typography in Marketing Assets

| Element | Font | Weight | Size | Color |
|---------|------|--------|------|-------|
| Primary headline | Inter Variable | 700–800 | 48–64px | `void-50` (#E6EDF4) |
| Sub-headline | Inter Variable | 400–500 | 24–32px | `void-200` (#ADBAC7) |
| Tagline | Instrument Serif | 400 | 28–36px | `void-100` (#CDD9E5) |
| Label / badge | Inter Variable | 600 | 14–16px | `void-50` |
| Version number | Geist Mono | 500 | 20–24px | `arizen-300` (#6AABEE) |

Marketing assets are the **only** context where Instrument Serif is used. It must not appear in product UI or developer documentation.

---

## Design Voice for Marketing Assets

From `BRAND_GUIDELINES.md` §10:

- **Lead with outcome, not feature.** Not "local LLM support" — "Your AI runs on your machine."
- **White space is a feature.** Marketing assets should not be dense with text or elements.
- **Show the product.** Screenshots and demos outperform illustration or abstract graphics.
- **The community is the product.** Credit contributors in release materials by @handle.

---

## Export Specification

| Format | Settings |
|--------|---------|
| PNG | PNG-24, no interlacing, sRGB, strip metadata |
| JPEG (press only) | Quality 95+, baseline, sRGB, strip EXIF |
| Max file sizes | OG/Twitter: ≤ 800KB; Banner: ≤ 1.5MB; Press hero: ≤ 4MB |

---

## Press Kit

A complete press kit for each major release includes:
1. This `marketing/press/` folder (all press assets)
2. `branding/logos/primary/` (all logo variants)
3. `branding/screenshots/` (current version screenshots)
4. `BRAND_GUIDELINES.md` (design handbook)

Press kits are distributed as a ZIP archive named `arizenos-press-kit-v{x}.{y}.zip`. The archive is attached to GitHub Releases. It is not stored in the repository itself.
