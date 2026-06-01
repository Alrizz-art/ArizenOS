# ArizenOS Branding Templates

> **Layer:** Production — editable source files for contributors  
> **Contributors:** Core Team manages source; all contributors may use  
> **Formats:** Figma (.fig) · Markdown (.md)

---

## Overview

This directory contains the production-grade source files and export specifications from which all ArizenOS branding assets are derived. These are the single source of truth for every visual decision in the branding system.

**Rule:** If a branding asset cannot be traced back to a file in `templates/figma/`, it does not belong in the repository.

---

## Template Inventory

### Figma Source Files (`templates/figma/`)

| File | Contents | Used For |
|------|---------|---------|
| `arizenos-brand-kit.fig` | Master brand system — logos, color palette, type scale, component library, glass tokens | All logo work, identity assets, design reference |
| `arizenos-screenshot-template.fig` | Screenshot frame, device mockup, annotation system | All official product screenshots |
| `arizenos-social-templates.fig` | OG image, Twitter card, GitHub banner, avatar, release banner | All marketing/social assets |

### Export Specification (`templates/export-spec.md`)

The export specification defines the exact settings to use when exporting from Figma for every asset type in `branding/`.

---

## `arizenos-brand-kit.fig` — Contents

The master brand kit contains the following pages:

| Page | Contents |
|------|---------|
| `Cover` | Version, owner, last updated |
| `Color System` | Full palette with tokens, glass values, semantic colors |
| `Typography` | Full type scale with specimens at each level |
| `Logo — Primary` | All primary logo variants with clear space guides |
| `Logo — Wordmark` | Wordmark variants with sizing guides |
| `Logo — Glyph` | Glyph variants with grid |
| `Logo — Glass` | Liquid Glass treatment specification |
| `Logo — Monochrome` | Black and white variants |
| `Logo — OEM` | OEM BMP variants with Windows placement preview |
| `Logo — Favicon` | Favicon set with browser preview |
| `Icon Grid` | App icon grid system, squircle template, glass treatment |
| `Cursors` | Cursor design at 32×32 and 64×64 (for design) |
| `Glass Depth System` | 6-level depth hierarchy with material specifications |
| `Usage Rules` | DOs and DON'Ts with visual examples |

---

## `arizenos-screenshot-template.fig` — Contents

| Page | Contents |
|------|---------|
| `Desktop Frame` | 1920×1080 capture frame with safe zones marked |
| `Taskbar Zones` | Overlay showing glass zone boundaries |
| `Annotation System` | Callout styles, pointer arrows, labels |
| `Mockup — Window` | Clean window frame for UI detail shots |
| `Screenshot Checklist` | Pre-capture checklist embedded in file |

---

## `arizenos-social-templates.fig` — Contents

| Page | Contents |
|------|---------|
| `OG Image` | 1200×630 — editable layout |
| `Twitter Card` | 1200×628 — editable layout |
| `GitHub Banner` | 1280×640 — editable layout |
| `Avatar` | 400×400 — editable layout |
| `Release Banner` | 1200×630 — editable with version number, headline fields |
| `Press Hero` | 1920×1080 — press kit hero |

---

## How to Use Templates

### Accessing the Templates

Templates are stored as Figma files in this directory. To use them:

1. Open Figma Desktop or Web
2. File → Import → select the `.fig` file
3. The file opens in your Drafts — make a copy before editing
4. Never edit the template file directly — always work from a copy

### Producing a New Asset

1. Open the relevant template (see inventory above)
2. Duplicate the appropriate artboard/frame
3. Make only the changes necessary for the asset type
4. Follow export settings in `templates/export-spec.md`
5. Name the output file per `NAMING_CONVENTIONS.md`
6. Submit via PR

### Updating the Templates

Template updates require Core Team approval and are submitted as a PR with:
- The updated `.fig` file
- A summary of what changed and why
- Updated `export-spec.md` if export settings changed
- Issue linked with `brand` label

---

## export-spec.md — Quick Reference

The full export specification is in `templates/export-spec.md`. Key settings:

| Asset | Format | Scale | Settings |
|-------|--------|-------|---------|
| SVG logos | SVG | 1× | Outline text, no artboard BG, remove hidden layers |
| PNG logos @2x | PNG | 2× | Transparent BG, PNG-24, no metadata |
| PNG logos @1x | PNG | 1× | Transparent BG, PNG-24 |
| Wallpapers | JPG | 1× | Quality 92, sRGB, baseline, strip EXIF |
| App icons | PNG | 1× (per size) | Transparent BG, exact dimensions |
| OG/social | PNG | 1× | No transparency needed, sRGB |
| Press hero | PNG | 1× | sRGB, no transparency |

---

## File Versioning

Figma source files are versioned alongside the product in Git. When a major branding update ships:
1. The `.fig` file is updated in place (overwrite existing)
2. The change is documented in `CHANGELOG.md` under `[Branding]`
3. The commit is tagged `branding/vMAJOR.MINOR.PATCH`

Figma has internal version history — Git history of the `.fig` binary is a secondary backup only.
