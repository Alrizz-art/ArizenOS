# ArizenOS Asset Naming Conventions

> **Version:** 1.0.0  
> **Scope:** All files inside `branding/`  
> **Rule:** Every file that violates this spec will be rejected at PR review.

---

## 1. Universal Pattern

All branding assets follow a single base pattern:

```
{product}-{category}-{variant}-{modifier}{@scale}.{ext}
```

| Segment | Required | Description | Values |
|---------|----------|-------------|--------|
| `{product}` | Always | Product or sub-product name | `arizenos`, `arizenagent`, `arizenmind` |
| `{category}` | Always | Asset functional category | `logo`, `wall`, `icon`, `ss`, `oem`, `og` |
| `{variant}` | Always | Visual variant | `dark`, `light`, `glass`, `monochrome`, `black`, `white` |
| `{modifier}` | When applicable | Sub-variant, resolution, or version | `primary`, `wordmark`, `glyph`, `4k`, `2k`, `fhd`, `hd` |
| `{@scale}` | For raster only | Pixel density suffix | `@1x`, `@2x`, `@3x` |
| `{ext}` | Always | File extension | See §3 |

**Separator:** always hyphen `-`. Never underscore, camelCase, or spaces.  
**Case:** always `lowercase-kebab-case`.

---

## 2. Category Codes

| Category Code | Full Name | Used In |
|--------------|-----------|---------|
| `logo` | Logo (full lockup) | `logos/primary/` |
| `wordmark` | Wordmark only | `logos/wordmark/` |
| `glyph` | Symbol/glyph only | `logos/glyph/` |
| `wall` | Wallpaper | `wallpapers/` |
| `lock` | Lockscreen wallpaper | `wallpapers/lockscreen/` |
| `oobe` | Out-of-box experience | `wallpapers/oobe/` |
| `icon` | Application icon | `icons/app/` |
| `cursor` | Cursor asset | `icons/system/` |
| `ss` | Screenshot | `screenshots/` |
| `oem` | OEM asset | `oem/` |
| `og` | Open Graph image | `marketing/social/` |
| `banner` | Banner image | `marketing/social/` or `marketing/press/` |
| `release` | Release announcement | `marketing/release/` |
| `press` | Press kit asset | `marketing/press/` |

---

## 3. File Extensions

| Asset Type | Extension | Notes |
|-----------|-----------|-------|
| Vector logo / icon | `.svg` | Source of truth for all logos |
| Raster export (standard) | `.png` | Lossless, transparency supported |
| Raster (photo/wallpaper) | `.jpg` | JPEG quality minimum 92 |
| Windows OEM logo | `.bmp` | 24-bit BMP, exact Windows spec |
| Windows cursor | `.cur` or `.ani` | Animated: `.ani` |
| Figma source | `.fig` | Stored in `templates/figma/` only |
| Registry entries | `.reg` | UTF-16 LE encoding |
| Template config | `.ini.template` or `.md` | |

**Never:** `.gif`, `.webp`, `.tiff`, `.psd`, `.ai`, `.eps` in `branding/`.  
Photoshop and Illustrator sources belong in `templates/` only if exported to approved formats.

---

## 4. Variant Codes

| Variant | Code | When to Use |
|---------|------|-------------|
| Dark background variant | `dark` | Default — always required |
| Light background variant | `light` | Optional, for light contexts |
| Liquid Glass treatment | `glass` | ArizenOS-specific premium variant |
| Single color black | `black` | Print, monochrome contexts |
| Single color white | `white` | Print, reversed contexts |
| Combined monochrome | `monochrome` | When black+white are bundled |

---

## 5. Resolution / Size Codes

### Wallpapers

| Code | Resolution | Notes |
|------|-----------|-------|
| `4k` | 3840×2160 | UHD 4K |
| `2k` | 2560×1440 | QHD / 2K |
| `fhd` | 1920×1080 | Full HD — minimum required |
| `hd` | 1280×720 | HD — optional |

### Icons

| Code | Size | Notes |
|------|------|-------|
| (no code) | `.svg` | Vector source |
| `256` | 256×256 | App icons standard |
| `128` | 128×128 | |
| `64` | 64×64 | |
| `32` | 32×32 | Favicon |
| `16` | 16×16 | Favicon small |
| `180` | 180×180 | Apple touch icon |

### Logo PNG Exports

| Code | Scale | Usage |
|------|-------|-------|
| `@2x` | 2× (high-DPI) | Retina displays, default export |
| `@1x` | 1× (standard) | Standard displays |

---

## 6. Screenshot Naming

Screenshots include a **version suffix** to tie them to a product release:

```
arizenos-ss-{feature}-{variant}-v{major}.{minor}.png
```

**Examples:**
```
arizenos-ss-desktop-dark-v1.0.png
arizenos-ss-launcher-dark-v1.0.png
arizenos-ss-ailayer-light-v0.4.png
arizenos-ss-settings-dark-v1.0.png
```

**Feature codes:**

| Feature | Code |
|---------|------|
| Desktop / taskbar view | `desktop` |
| Launcher / search | `launcher` |
| AI overlay / panel | `ailayer` |
| Settings UI | `settings` |
| Widgets panel | `widgets` |
| Onboarding / OOBE | `oobe` |
| Voice interface | `voice` |

---

## 7. Marketing Asset Naming

| Asset | Name Pattern | Example |
|-------|-------------|---------|
| Open Graph image | `arizenos-og-image.png` | Standard 1200×630 |
| Twitter card | `arizenos-twitter-card.png` | 1200×628 |
| GitHub banner | `arizenos-banner-github.png` | 1280×640 |
| Profile avatar | `arizenos-avatar.png` | 400×400 |
| Release banner | `arizenos-release-banner-v{major}.{minor}.png` | `arizenos-release-banner-v1.0.png` |
| Press hero | `arizenos-press-hero.png` | |

---

## 8. OEM Asset Naming

OEM assets follow a stricter pattern because they are consumed by Windows system components:

```
arizenos-oem-{type}{-size}.{ext}
```

| Asset | Filename | Spec |
|-------|---------|------|
| System Properties logo | `arizenos-oem-logo.bmp` | 120×120, 24-bit BMP |
| Small system logo | `arizenos-oem-logo-sm.bmp` | 96×96, 24-bit BMP |
| Support banner | `arizenos-oem-banner.jpg` | 2048×120 |

---

## 9. Forbidden Patterns

The following naming patterns are **rejected at PR review**:

```
❌ ArizenOS_Logo_Dark.png          # Uppercase and underscores
❌ logo-final-FINAL-v2.png         # "final" in filename
❌ arizen-logo copy.svg            # Spaces
❌ logo.svg                        # No product prefix
❌ arizenos-logo-dark_2x.png       # Underscore before @2x
❌ ArizenLogoWhite.png             # camelCase
❌ arizen-logo-dark-new.png        # "new" in filename
❌ arizenos-logo-dark-v3.svg       # Version on SVG source (use VERSIONING.md)
```

---

## 10. Template / Source Files

Source and template files are exempt from the category-code system and use descriptive PascalCase:

```
branding/templates/figma/arizenos-brand-kit.fig
branding/templates/figma/arizenos-screenshot-template.fig
branding/templates/figma/arizenos-social-templates.fig
branding/templates/export-spec.md
```
