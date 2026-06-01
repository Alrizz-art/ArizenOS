# ArizenOS Logo Specification

> **Layer:** Identity — immutable, owner-controlled  
> **Contributes:** Core Team only  
> **Format:** SVG (source) + PNG (export)

---

## Overview

The ArizenOS logo is the primary identity mark of Arizen Technologies. It exists in six variant families, each serving a specific context. No variant may be modified, recolored, or recombined outside this specification.

---

## Variant Families

### 1. Primary (`logos/primary/`)

The full logo lockup — symbol + wordmark, horizontally composed.

| File | Format | Size | Usage |
|------|--------|------|-------|
| `arizenos-logo-dark.svg` | SVG | Vector | Documentation, website, default |
| `arizenos-logo-light.svg` | SVG | Vector | Light background contexts |
| `arizenos-logo-dark@2x.png` | PNG | 1024×auto | Retina displays, GitHub |
| `arizenos-logo-light@2x.png` | PNG | 1024×auto | Light mode raster |
| `arizenos-logo-dark@1x.png` | PNG | 512×auto | Standard displays |
| `arizenos-logo-light@1x.png` | PNG | 512×auto | Standard light |

**When to use Primary:** GitHub README header, website navbar, documentation header, press kit cover.

### 2. Wordmark (`logos/wordmark/`)

The "ArizenOS" text mark without the symbol glyph.

| File | Format | Usage |
|------|--------|-------|
| `arizenos-wordmark-dark.svg` | SVG | When symbol is already established in context |
| `arizenos-wordmark-light.svg` | SVG | Light background |
| `arizenos-wordmark-dark@2x.png` | PNG | Raster contexts |
| `arizenos-wordmark-light@2x.png` | PNG | Raster light |

**When to use Wordmark:** Repeated references in a document where the symbol has already appeared; product UI chrome where width is constrained.

### 3. Glyph (`logos/glyph/`)

The symbol mark alone — no text.

| File | Format | Size | Usage |
|------|--------|------|-------|
| `arizenos-glyph-dark.svg` | SVG | Vector | App icon base, social avatar |
| `arizenos-glyph-light.svg` | SVG | Vector | Light contexts |
| `arizenos-glyph-dark@2x.png` | PNG | 512×512 | App icon, avatar |
| `arizenos-glyph-light@2x.png` | PNG | 512×512 | Light context |
| `arizenos-glyph-dark@1x.png` | PNG | 256×256 | Standard size |
| `arizenos-glyph-light@1x.png` | PNG | 256×256 | Standard light |

**When to use Glyph:** Profile avatars, app icons, favicon base, small-space contexts where the wordmark would be illegible (< 120px wide).

### 4. Liquid Glass (`logos/glass/`)

The premium Liquid Glass variant — the signature ArizenOS aesthetic treatment.

| File | Format | Usage |
|------|--------|-------|
| `arizenos-logo-glass.svg` | SVG | Premium contexts, product hero |
| `arizenos-logo-glass@2x.png` | PNG | Hero images, announcement banners |

**When to use Glass:** Product hero sections, release announcements, premium marketing materials, wallpaper overlays. Never in documentation or functional UI.

**Requirements:** Glass treatment must use defined blur/opacity tokens. It must not be applied to contexts smaller than 200px wide.

### 5. Monochrome (`logos/monochrome/`)

Single-color variants for print, embossing, and restricted-palette contexts.

| File | Format | Usage |
|------|--------|-------|
| `arizenos-logo-black.svg` | SVG | Print on white, laser engraving |
| `arizenos-logo-white.svg` | SVG | Print on dark, screen printing |
| `arizenos-logo-black@2x.png` | PNG | Digital monochrome contexts |
| `arizenos-logo-white@2x.png` | PNG | Digital reversed contexts |

**When to use Monochrome:** Print media, merchandise, contexts where color rendering cannot be guaranteed, high-contrast accessibility contexts.

### 6. OEM (`logos/oem/`)

Windows-specific OEM assets for System Properties and Control Panel integration.

| File | Format | Size | Spec |
|------|--------|------|------|
| `arizenos-oem-logo.bmp` | 24-bit BMP | 120×120 | Windows System Properties |
| `arizenos-oem-logo-sm.bmp` | 24-bit BMP | 96×96 | Small system logo |

### 7. Favicon (`logos/favicon/`)

Browser and device favicon set.

| File | Format | Size | Usage |
|------|--------|------|-------|
| `favicon.svg` | SVG | Vector | Modern browsers (primary) |
| `favicon-32.png` | PNG | 32×32 | Standard favicon |
| `favicon-16.png` | PNG | 16×16 | Legacy favicon |
| `apple-touch-icon-180.png` | PNG | 180×180 | iOS home screen icon |

---

## Logo Usage Rules

### Clear Space
Maintain a minimum clear space equal to the cap-height of the letter "A" in the wordmark around all sides of the logo. This space must be free of text, graphics, and other visual elements.

### Minimum Size
| Variant | Minimum Width |
|---------|--------------|
| Primary (with wordmark) | 120px / 32mm |
| Glyph only | 24px / 8mm |
| Wordmark only | 80px / 20mm |
| Favicon | 16px (use favicon set) |

### What Is Prohibited
- Do not stretch or distort the logo
- Do not rotate the logo
- Do not recolor any part of the logo
- Do not add drop shadows, outer glows, or effects not in the approved Glass variant
- Do not place the dark variant on backgrounds lighter than `void-500` (#444C56)
- Do not place the light variant on backgrounds darker than `void-500`
- Do not crop the logo
- Do not animate the logo without explicit Core Team approval
- Do not combine the logo with other brand logos in a composite mark

---

## Export Specification

| Format | Settings |
|--------|---------|
| SVG | Outline text, remove guides, no artboard background, minified |
| PNG @2x | PNG-24, no interlacing, no metadata, transparent background |
| PNG @1x | PNG-24, no interlacing, no metadata, transparent background |
| BMP (OEM) | 24-bit BMP, white background, exact pixel dimensions |
