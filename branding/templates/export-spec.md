# ArizenOS Branding Export Specification

> **Version:** 1.0.0  
> **Applies To:** All assets exported from `templates/figma/` for use in `branding/`

---

## Figma Export Settings by Asset Type

### Logos — SVG

| Setting | Value |
|---------|-------|
| Format | SVG |
| Include "id" attribute | Off |
| Outline text | On |
| Simplify stroke | On |
| Include artboard background | Off |
| Remove hidden layers | On |
| Content only | On |
| Post-process | Run through SVGO (optional but recommended) |

### Logos — PNG @2x

| Setting | Value |
|---------|-------|
| Format | PNG |
| Scale | 2× |
| Background | Transparent |
| Color profile | sRGB |
| Suffix | `@2x` |

### Logos — PNG @1x

| Setting | Value |
|---------|-------|
| Format | PNG |
| Scale | 1× |
| Background | Transparent |
| Color profile | sRGB |
| Suffix | `@1x` |

### OEM BMP

Figma cannot export BMP directly. Export workflow:

1. Export the OEM logo frame as PNG @1x at exact pixel dimensions (120×120 or 96×96)
2. Convert PNG to 24-bit BMP using ImageMagick:
   ```
   magick arizenos-oem-logo.png -type TrueColor -compress None BMP3:arizenos-oem-logo.bmp
   ```
3. Verify dimensions and bit depth before committing

### App Icons — PNG

| Setting | Value |
|---------|-------|
| Format | PNG |
| Scale | 1× |
| Size | Artboard size (256, 128, or 64) |
| Background | Transparent |
| Color profile | sRGB |

For each icon, export three artboards (256, 128, 64) simultaneously.

### Favicon — SVG

| Setting | Value |
|---------|-------|
| Format | SVG |
| Outline text | On |
| Content only | On |
| Artboard background | Off |

### Favicon — PNG

Export at exact pixel dimensions: 32×32 and 16×16.

### Wallpapers — JPG

Wallpapers are not typically produced in Figma — they are produced in Photoshop, Blender, or equivalent. If using Figma:

| Setting | Value |
|---------|-------|
| Format | JPG |
| Quality | 92 |
| Color profile | sRGB |
| Progressive | Off (baseline only) |
| Post-process | Strip all EXIF metadata |

### Social / OG Images — PNG

| Setting | Value |
|---------|-------|
| Format | PNG |
| Scale | 1× |
| Background | Include (no transparency) |
| Color profile | sRGB |

### Screenshots

Screenshots are not produced in Figma. See `branding/screenshots/README.md` for the capture procedure.

---

## Post-Export Checklist

Before committing any exported asset:

- [ ] File named per `NAMING_CONVENTIONS.md`
- [ ] Placed in the correct subdirectory per `ARCHITECTURE.md`
- [ ] All EXIF/metadata stripped from JPGs
- [ ] SVGs checked for any embedded raster images or `<image>` tags (not permitted)
- [ ] PNG files do not contain a color profile chunk (use sRGB IEC61966 implicitly)
- [ ] File size within limits (see individual README files for limits)
- [ ] Asset reviewed against design language checklist in `ARCHITECTURE.md` §4
