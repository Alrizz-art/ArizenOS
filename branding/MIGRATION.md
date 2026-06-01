# ArizenOS Branding Migration Plan

> **Version:** 1.0.0  
> **Status:** Active — migration from legacy `assets/` to `branding/`  
> **Target Completion:** ArizenOS v1.0.0

---

## 1. Context

Prior to the branding architecture formalization, assets were stored in:

```
assets/
├── logos/
│   ├── arizenOS_logo_dark.png
│   ├── arizenOS_logo_white.png
│   └── arizenOS_logo_oem.bmp
└── wallpapers/
    ├── arizenOS_dark.jpg
    ├── arizenOS_default.jpg
    └── arizenOS_lockscreen.jpg
```

These files were produced without a formal naming system, resolution spec, or variant policy. They remain in the repository for backward compatibility (scripts reference them) but are superseded by assets produced under the `branding/` architecture.

---

## 2. Legacy Asset Inventory

| Legacy Path | Status | New Canonical Path |
|------------|--------|--------------------|
| `assets/logos/arizenOS_logo_dark.png` | Superseded | `branding/logos/primary/arizenos-logo-dark@2x.png` |
| `assets/logos/arizenOS_logo_white.png` | Superseded | `branding/logos/monochrome/arizenos-logo-white@2x.png` |
| `assets/logos/arizenOS_logo_oem.bmp` | Superseded | `branding/oem/assets/arizenos-oem-logo.bmp` |
| `assets/wallpapers/arizenOS_dark.jpg` | Superseded | `branding/wallpapers/desktop/dark/arizenos-wall-dark-fhd.jpg` |
| `assets/wallpapers/arizenOS_default.jpg` | Superseded | `branding/wallpapers/desktop/dark/arizenos-wall-dark-fhd.jpg` |
| `assets/wallpapers/arizenOS_lockscreen.jpg` | Superseded | `branding/wallpapers/lockscreen/arizenos-lock-dark-fhd.jpg` |

---

## 3. Migration Phases

### Phase 0 — Architecture (Complete)
- [x] Define `branding/` folder structure
- [x] Write `ARCHITECTURE.md`
- [x] Write `NAMING_CONVENTIONS.md`
- [x] Write `VERSIONING.md`
- [x] Write `CONTRIBUTOR_GUIDE.md`
- [x] Write all subfolder `README.md` specs

### Phase 1 — Asset Production (Next)
- [ ] Produce SVG logo master (`logos/primary/arizenos-logo-dark.svg`)
- [ ] Export PNG variants at @1x and @2x
- [ ] Produce wordmark and glyph variants
- [ ] Produce Liquid Glass logo variant
- [ ] Produce monochrome (black/white) variants
- [ ] Produce favicon set (SVG + 32px + 16px + 180px)
- [ ] Produce OEM BMP assets to Windows spec
- [ ] Produce desktop wallpapers (dark, light, glass) at FHD minimum
- [ ] Produce lockscreen wallpapers
- [ ] Produce app icons for all five core apps
- [ ] Take screenshots at v1.0 spec
- [ ] Produce Open Graph and Twitter card images

### Phase 2 — Script Migration
- [ ] Update `scripts/oem-branding.ps1` to reference `branding/oem/assets/`
- [ ] Update `scripts/wallpaper.ps1` to reference `branding/wallpapers/`
- [ ] Update registry template `registry/oem-branding.reg` paths
- [ ] Update `README.md` screenshot references to `branding/screenshots/`

### Phase 3 — Legacy Retirement
- [ ] After Phase 1 and 2 complete, deprecate `assets/logos/` and `assets/wallpapers/`
- [ ] Add deprecation notice to `assets/logos/README.md` and `assets/wallpapers/README.md`
- [ ] Legacy files retained in Git history — not deleted from working tree until v2.0.0

---

## 4. Breaking Change Policy

The migration **must not break any existing scripts** that reference `assets/` paths.

Before Phase 3:
- Scripts are updated to use `branding/` paths
- A compatibility period of one minor version is maintained
- `assets/` READMEs are updated with deprecation warnings pointing to `branding/`

No files in `assets/` are deleted during this migration cycle. Deletion is scoped to v2.0.0.

---

## 5. Script Reference Map

| Script | Current Asset Reference | Target Reference |
|--------|------------------------|-----------------|
| `scripts/oem-branding.ps1` | `assets/logos/arizenOS_logo_oem.bmp` | `branding/oem/assets/arizenos-oem-logo.bmp` |
| `scripts/wallpaper.ps1` | `assets/wallpapers/arizenOS_dark.jpg` | `branding/wallpapers/desktop/dark/arizenos-wall-dark-fhd.jpg` |
| `registry/oem-branding.reg` | Referenced BMP paths | Updated BMP paths |

---

## 6. Migration Tracking

Migration progress is tracked in GitHub Issues with the label `branding-migration`.

Milestone: `v1.0.0 — Branding System`
