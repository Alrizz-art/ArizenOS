# ArizenOS OEM Asset Specification

> **Layer:** Partner — constrained customization, compliance-gated  
> **Contributors:** Core Team only  
> **Formats:** BMP · JPG · REG · INI

---

## Overview

OEM assets integrate ArizenOS branding into Windows system surfaces — specifically the System Properties dialog, About panel, and Control Panel manufacturer section. These assets are injected via registry entries and must conform to exact Windows API specifications. Any deviation causes Windows to silently reject the asset.

**All OEM assets are produced and maintained by Core Team only.** Partner OEM customization is scoped separately (see §5).

---

## Asset Inventory

### System Logo (`oem/assets/`)

| File | Dimensions | Format | Windows Surface |
|------|-----------|--------|----------------|
| `arizenos-oem-logo.bmp` | 120×120 | 24-bit BMP | System Properties (large) |
| `arizenos-oem-logo-sm.bmp` | 96×96 | 24-bit BMP | System Properties (small) |
| `arizenos-oem-banner.jpg` | 2048×120 | JPEG | Support banner |

### Registry Template (`oem/registry/`)

| File | Contents |
|------|---------|
| `arizenos-oem-branding.reg` | OEM branding registry entries |

### Configuration Template (`oem/templates/`)

| File | Contents |
|------|---------|
| `oem-info.ini.template` | Template for OEM info file |

---

## Windows OEM Logo Specification

### Exact BMP Requirements

Windows System Properties reads OEM logos with strict requirements. These are Windows API constraints — not ArizenOS preferences.

| Property | Value | Source |
|----------|-------|--------|
| Format | BMP (Device-Independent Bitmap) | Windows API |
| Bit depth | 24-bit (no alpha channel) | Windows API |
| Compression | None (BI_RGB) | Windows API |
| Large logo size | 120×120 pixels | Windows 10/11 |
| Small logo size | 96×96 pixels | Windows 10/11 |
| Background color | White (`#FFFFFF`) | Windows API composites on white |
| Color profile | sRGB | |

**Critical:** The OEM logo BMP must NOT use transparency or alpha channels. Windows composites the logo on a white background. Design the logo against white.

This means:
- The OEM logo uses the `arizenos-logo-black.svg` base (dark symbol on white)
- OR uses the full-color primary logo with white background, no glass treatment
- Padding: 8px on all sides within the BMP canvas

### OEM Banner Specification

| Property | Value |
|----------|-------|
| Dimensions | 2048×120px |
| Format | JPEG, quality 92+ |
| Content | ArizenOS wordmark (left-aligned) on `void-900` background |
| Safe zone | 64px from left and right edges |

---

## Registry Entry Specification

`oem/registry/arizenos-oem-branding.reg` structure:

```
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation]
"Logo"="C:\\ArizenOS\\branding\\oem\\assets\\arizenos-oem-logo.bmp"
"Manufacturer"="Arizen Technologies"
"Model"="ArizenOS"
"SupportURL"="https://github.com/Alrizz-art/ArizenOS"
"SupportPhone"=""
"SupportHours"=""
```

Path conventions:
- Registry paths assume ArizenOS is installed to `C:\ArizenOS\`
- The installer script (`scripts/oem-branding.ps1`) dynamically resolves the installation path
- Do not hardcode paths in the registry template — use the `$ARIZENOS_PATH` variable in the PS1 script

---

## OEM INI Template

`oem/templates/oem-info.ini.template`:

```ini
[General]
Manufacturer=Arizen Technologies
Model=ArizenOS
SupportURL=https://github.com/Alrizz-art/ArizenOS

[Support]
Hours=Community support via GitHub Issues
Phone=
URL=https://github.com/Alrizz-art/ArizenOS/issues
```

---

## 5. Partner OEM Customization

ArizenOS supports a partner channel where hardware vendors or enterprise deployers may apply their own branding alongside ArizenOS. This is a future capability — not in scope for v1.0.

**Rules for future partner OEM:**
- Partner logo may appear in the OEM banner alongside the ArizenOS glyph (never replacing it)
- Partner may not modify the ArizenOS registry `Manufacturer` or `Model` fields
- Partner branding must not appear in System Properties logo — ArizenOS logo only
- Partner customization ships via a separate registry layer, not by modifying `arizenos-oem-branding.reg`
- Any partner OEM customization requires a written agreement with Arizen Technologies

---

## Compliance Checklist

Before committing any OEM asset:

- [ ] BMP is exactly 120×120 or 96×96 pixels
- [ ] BMP is 24-bit with no alpha channel
- [ ] BMP has white background (no transparency)
- [ ] Logo is centered with 8px padding
- [ ] Registry template uses `$ARIZENOS_PATH` placeholder, not hardcoded path
- [ ] Banner is exactly 2048×120 JPEG
- [ ] All files tested via `scripts/oem-branding.ps1` on Windows 10 and Windows 11
