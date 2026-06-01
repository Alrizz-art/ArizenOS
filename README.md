<div align="center">

# ArizenOS

**Privacy-first. Developer-ready. Visually refined.**

A Windows 10 / 11 customization playbook built with [AME Wizard](https://ameliorated.io/).
Transform a bloated Windows installation into a clean, branded, developer-friendly desktop.

[![Windows 10](https://img.shields.io/badge/Windows%2010-22H2%2B-blue?logo=windows)](https://github.com/Alrizz-art/ArizenOS)
[![Windows 11](https://img.shields.io/badge/Windows%2011-22H2%2B-blue?logo=windows11)](https://github.com/Alrizz-art/ArizenOS)
[![AME Wizard](https://img.shields.io/badge/AME%20Wizard-.apbx-purple)](https://ameliorated.io/)
[![Version](https://img.shields.io/badge/version-2.0.0-green)](https://github.com/Alrizz-art/ArizenOS/releases)

</div>

---

## What is ArizenOS?

ArizenOS is an AME Wizard playbook that applies a curated set of tweaks, branding,
and debloat operations to a stock Windows installation. It is **not** a custom ISO —
it runs on top of your existing licensed Windows copy.

---

## Features

| Feature | Description |
|---------|-------------|
| 🎨 **OEM Branding** | Custom System Info, About page, and lock screen identity |
| 🖼️ **ArizenOS Wallpapers** | 4K branded wallpapers for desktop and lock screen |
| 🌑 **Dark Theme** | System-wide dark mode with deep slate accent (#0F172A) |
| 💎 **Transparency Tweaks** | Acrylic/Mica effects, OLED taskbar translucency |
| 🧹 **Safe Debloat** | Removes telemetry, ads, and bloatware — never touches core OS |
| 💻 **Developer Setup** | WSL2, WinGet, Git, VS Code, Node.js, PowerShell 7, Docker |
| 🔒 **Security Reviewed** | Defender, Firewall, UAC, and Secure Boot are never touched |
| ↩️ **Rollback Ready** | System Restore Point created before any changes |

---

## Requirements

- Windows 10 **22H2** (Build 19045) or Windows 11 **22H2 / 23H2 / 24H2**
- [AME Wizard](https://ameliorated.io/) v0.6.7+
- Administrator account
- 500MB free disk space
- Internet connection (Developer Setup only)

---

## Quick Start

```
1. Download AME Wizard from https://ameliorated.io/
2. Download ArizenOS.apbx from Releases
3. Open AME Wizard → Load Playbook → select ArizenOS.apbx
4. Review and confirm each option
5. Click Apply
6. Reboot when prompted
```

> ⚠️ **Always run on a fresh Windows install or have a backup.**  
> ArizenOS creates a System Restore Point automatically before applying changes.

---

## Asset Requirements

Before building the `.apbx`, add your assets to:

```
assets/
├── logos/
│   ├── arizenOS_logo_oem.bmp      ← 120×120px, 24-bit BMP (required for OEM page)
│   ├── arizenOS_logo_white.png    ← 800×200px transparent
│   └── arizenOS_logo_dark.png     ← 800×200px transparent
└── wallpapers/
    ├── arizenOS_default.jpg       ← 3840×2160, ≤2MB (primary desktop)
    ├── arizenOS_dark.jpg          ← 3840×2160 dark variant
    ├── arizenOS_lockscreen.jpg    ← 1920×1080 lock screen
    └── arizenOS_alt.jpg           ← optional alternate
```

See [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) for full asset specs and color palette.

---

## Building the .apbx

The `.apbx` format is a renamed ZIP file:

```powershell
# PowerShell — run from repo root
Compress-Archive -Path .\* -DestinationPath .\ArizenOS.zip
Rename-Item .\ArizenOS.zip .\ArizenOS.apbx
```

Or use the included build script:
```powershell
.\scripts\build-apbx.ps1
```

---

## Rollback

```powershell
# Full rollback (registry + re-provision apps)
.\scripts\rollback.ps1 -Full

# Use System Restore Point (safest)
.\scripts\rollback.ps1 -UseRestorePoint

# Registry only
.\scripts\rollback.ps1 -RestoreRegistry
```

---

## Security

ArizenOS follows a **"touch only what's necessary"** policy:

- ✅ Windows Defender — **untouched**
- ✅ Windows Firewall — **untouched**
- ✅ UAC — **untouched**
- ✅ Windows Update — **untouched**
- ✅ BitLocker / Secure Boot / TPM — **untouched**
- ❌ Telemetry / Advertising / Cortana — **disabled**
- ❌ Remote Registry / DiagTrack — **disabled**

See [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) for the full security review.

---

## File Structure

```
ArizenOS/
├── playbook.yaml          ← AME Wizard manifest
├── README.md
├── scripts/               ← PowerShell scripts
│   ├── debloat.ps1
│   ├── oem-branding.ps1
│   ├── apply-theme.ps1
│   ├── wallpaper.ps1
│   ├── developer-setup.ps1
│   ├── rollback.ps1
│   └── security-audit.ps1
├── registry/              ← .reg files
│   ├── dark-theme.reg
│   ├── transparency.reg
│   ├── oem-branding.reg
│   └── performance.reg
├── assets/                ← Logos & wallpapers (add your own)
│   ├── logos/
│   └── wallpapers/
└── docs/
    └── SPECIFICATION.md   ← Enterprise-grade spec
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made for Windows by <a href="https://github.com/Alrizz-art">Alrizz-art</a>
</div>
