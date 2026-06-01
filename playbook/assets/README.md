# playbook/assets/ — Packaged Binary Assets

> **Purpose:** Binary assets bundled directly into `ArizenOS.apbx`  
> **Ownership:** Core Team only  
> **Release Process:** Updated with each minor/patch release when assets change

---

## Purpose

`playbook/assets/` contains production-ready copies of all binary files referenced inside AME Wizard entry YAML files. These are distinct from `branding/` (the design source layer) and `assets/` (the raw legacy assets) — everything here is **prepared, sized, and validated for playbook packaging**.

When `scripts/build-apbx.ps1` packages the `.apbx`, it includes files from this directory (or their equivalents at root `assets/`) directly in the archive.

**Rule:** If an entry YAML references an asset file, that file must exist in `playbook/assets/` and be validated before it ships.

---

## Directory Structure

```
playbook/assets/
├── oem/
│   ├── arizenOS_logo_oem.bmp      ← Windows OEM logo: 120×120, 24-bit BMP
│   └── arizenOS_logo_sm.bmp       ← Small OEM logo: 96×96, 24-bit BMP
├── wallpapers/
│   ├── arizenOS_default.jpg       ← Default desktop wallpaper (1920×1080 min)
│   ├── arizenOS_dark.jpg          ← Dark variant desktop wallpaper
│   └── arizenOS_lockscreen.jpg    ← Lock screen wallpaper (1920×1080)
└── branding/
    ├── arizenOS_w10.png            ← Windows 10 edition selector (used in playbook.yaml config)
    └── arizenOS_w11.png            ← Windows 11 edition selector
```

---

## File Specifications

### OEM Assets (`assets/oem/`)

| File | Spec | Windows Surface |
|------|------|----------------|
| `arizenOS_logo_oem.bmp` | 120×120px, 24-bit BMP, white BG, no alpha | System Properties dialog |
| `arizenOS_logo_sm.bmp` | 96×96px, 24-bit BMP, white BG, no alpha | About panel (small logo) |

**Critical:** Windows rejects OEM logos that don't meet exact BMP specifications. Before adding or updating:
1. Verify dimensions exactly (not 119×120, not 121×120)
2. Verify 24-bit BMP format (not 32-bit, not PNG-embedded-in-BMP)
3. Verify white background (Windows composites on white — no transparency)
4. Test in System Properties before committing

Source: `branding/oem/assets/` → export and place here.

### Wallpapers (`assets/wallpapers/`)

| File | Resolution | Format | Max Size |
|------|-----------|--------|---------|
| `arizenOS_default.jpg` | 1920×1080+ | JPEG, quality 92+ | 4MB |
| `arizenOS_dark.jpg` | 1920×1080+ | JPEG, quality 92+ | 4MB |
| `arizenOS_lockscreen.jpg` | 1920×1080+ | JPEG, quality 92+ | 4MB |

Source: `branding/wallpapers/desktop/dark/` and `branding/wallpapers/lockscreen/` → prepared copies here.

### Edition Branding (`assets/branding/`)

| File | Spec | Used In |
|------|------|---------|
| `arizenOS_w10.png` | PNG, any resolution (displayed in AME Wizard config UI) | `playbook.yaml` configuration options |
| `arizenOS_w11.png` | PNG, any resolution | `playbook.yaml` configuration options |

---

## Asset Validation

Before committing any new or updated asset, run:

```powershell
# Validate OEM BMP dimensions and format
$bmp = [System.Drawing.Image]::FromFile(".\playbook\assets\oem\arizenOS_logo_oem.bmp")
if ($bmp.Width -ne 120 -or $bmp.Height -ne 120) { Write-Error "OEM logo must be 120x120" }
if ($bmp.PixelFormat -ne "Format24bppRgb") { Write-Error "OEM logo must be 24-bit BMP" }
$bmp.Dispose()
```

The CI unit test `playbook/tests/unit/test-oem-branding.ps1` runs this check automatically on every PR.

---

## Update Workflow

1. Produce new asset in `branding/` following `branding/NAMING_CONVENTIONS.md`
2. Export/copy the production-ready version to `playbook/assets/`
3. Rename to match the legacy filename expected by scripts (e.g. `arizenOS_logo_oem.bmp`)
4. Run asset validation
5. Update `playbook/releases/manifests/v{x}.json` if asset changes are release-relevant
6. Submit PR with `playbook` label
