# ArizenOS Branding Contributor Guide

> **Version:** 1.0.0  
> **Audience:** Any contributor who wants to add, update, or review branding assets

---

## 1. Who Can Contribute Branding Assets

| Asset Type | Who Can Contribute |
|-----------|-------------------|
| Logos, wordmarks, glyphs | Core Team only (submit via issue requesting change) |
| Wallpapers | Core Team + approved contributors |
| App icons | Core Team only |
| System icons / cursors | Core Team only |
| Screenshots | Any contributor (with spec compliance) |
| OEM assets | Core Team only |
| Marketing social assets | Core Team + Marketing contributors |
| Templates (Figma) | Core Team only |

---

## 2. Before You Start

Read these documents first — in order:

1. `branding/ARCHITECTURE.md` — understand the full structure
2. `branding/NAMING_CONVENTIONS.md` — your file will be rejected if it breaks naming rules
3. `branding/VERSIONING.md` — understand when and how to version your asset
4. `BRAND_GUIDELINES.md` — the master design handbook

---

## 3. Contribution Workflow

### Step 1 — Open an Issue First

Before producing any branding asset, open a GitHub Issue:

- Use the label `brand`
- Describe the asset needed: type, variant, context, intended use
- Link to the relevant section of `BRAND_GUIDELINES.md`
- Attach rough sketches or references if applicable
- Wait for approval from a Core Team maintainer before proceeding

**Why:** The branding system is a coordinated whole. Uncoordinated contributions create inconsistency that is expensive to reverse.

### Step 2 — Work from the Templates

All assets must originate from official Figma templates in `branding/templates/figma/`:

| Template | Use For |
|----------|---------|
| `arizenos-brand-kit.fig` | All logo and identity work |
| `arizenos-screenshot-template.fig` | Product screenshots |
| `arizenos-social-templates.fig` | Marketing / social assets |

Do not produce branding assets from scratch without using the template as a base.

### Step 3 — Export Correctly

Follow the export specifications in `branding/templates/export-spec.md`.

**General rules:**
- SVG: exported from Figma with "Include id attribute" off, "Outline text" on for logos
- PNG: exported at @2x minimum. Use PNG-24 (no palette compression)
- JPG: quality setting 92+. No progressive encoding.
- Never export with invisible layers, artboard backgrounds baked in, or guide lines visible

### Step 4 — Name the File Correctly

Follow `branding/NAMING_CONVENTIONS.md` exactly.

Run this mental checklist before saving:
- [ ] All lowercase?
- [ ] Hyphens only (no underscores, spaces, camelCase)?
- [ ] Product prefix present (`arizenos-`)?
- [ ] Category code correct?
- [ ] Variant specified (`-dark`, `-light`, `-glass`)?
- [ ] Resolution code present for wallpapers?
- [ ] `@2x` suffix on raster logo exports?
- [ ] Version suffix present on screenshots?
- [ ] No "final", "new", "v2", "copy" in name?

### Step 5 — Submit a Pull Request

Branch name: `branding/{description}`

PR checklist (copy this into your PR description):

```markdown
## Branding Asset PR

- [ ] Issue linked and approved by Core Team maintainer
- [ ] Asset produced from official Figma template
- [ ] Naming conventions followed (NAMING_CONVENTIONS.md)
- [ ] Export settings followed (export-spec.md)
- [ ] Dark variant included (light variant if applicable)
- [ ] No pure #000000 or #FFFFFF used
- [ ] Colors from branding/tokens/source/color.json only
- [ ] Design language compliance checked (see ARCHITECTURE.md §4)
- [ ] CHANGELOG.md updated under [Branding]
```

---

## 4. Design Language Checklist

Every asset submitted to `branding/` must comply:

### Color
- [ ] All colors are from `branding/tokens/source/color.json`
- [ ] No pure black (`#000000`) or pure white (`#FFFFFF`)
- [ ] Glass surfaces use `glass-white-*` or `glass-black-*` tokens, not custom opacity values
- [ ] Tested against both dark (`void-900`) and light backgrounds

### Typography
- [ ] UI assets use Inter Variable
- [ ] Code/terminal assets use Geist Mono
- [ ] Marketing assets may use Instrument Serif for headlines only
- [ ] No fonts outside the approved three families

### Glass / Depth
- [ ] Blur radius follows the 6-layer depth system (see `BRAND_GUIDELINES.md` §3)
- [ ] No flat opaque surfaces where glass treatment is expected
- [ ] Depth shadows are consistent with the layer they represent

### Logo Usage
- [ ] Clear space around logo ≥ height of the "A" glyph
- [ ] Logo is not stretched, rotated, or recolored
- [ ] Dark variant on backgrounds darker than `void-500` (#444C56)
- [ ] Light variant on backgrounds lighter than `void-500`

---

## 5. Review Process

| Stage | Reviewer | SLA |
|-------|----------|-----|
| Initial PR review | Any Core Team member | 3 business days |
| Design review | Lead Design maintainer | 5 business days |
| Merge approval | Core Team maintainer | 2 business days after design approval |

---

## 6. What Gets Rejected

PRs are closed without merge if:

- No issue was opened and approved before the PR
- File naming does not follow `NAMING_CONVENTIONS.md`
- Colors are not from the approved token system
- Asset was not produced from an official template
- PR description is missing the checklist
- The asset uses pure black or white
- The asset introduces a new font not in the approved stack
- The logo has been modified in any way not explicitly approved

---

## 7. Questions

Open a GitHub Issue with the label `brand` and `question`.

For urgent brand matters, tag `@Alrizz-art` directly in the issue.
