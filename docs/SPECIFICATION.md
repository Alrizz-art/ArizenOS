# ArizenOS — Enterprise-Grade Playbook Specification

> Version: 2.0.0  
> Format: AME Wizard `.apbx`  
> Platform: Windows 10 (22H2+) / Windows 11 (22H2, 23H2, 24H2)

---

## 1. Playbook Architecture

```
ArizenOS.apbx (ZIP archive)
├── playbook.yaml                    ← AME Wizard root manifest
├── entries/
│   ├── restore-point.yaml           ← Create system restore point
│   ├── oem-branding.yaml            ← OEM identity application
│   ├── dark-theme.yaml              ← System-wide dark mode
│   ├── transparency.yaml            ← Acrylic/Mica effects
│   ├── debloat.yaml                 ← Safe app + telemetry removal
│   ├── wallpaper.yaml               ← ArizenOS wallpaper deployment
│   ├── developer-setup.yaml         ← Dev toolchain (optional)
│   └── final-cleanup.yaml           ← Explorer restart + log archive
├── scripts/
│   ├── debloat.ps1
│   ├── oem-branding.ps1
│   ├── apply-theme.ps1
│   ├── wallpaper.ps1
│   ├── developer-setup.ps1
│   ├── rollback.ps1
│   └── security-audit.ps1
├── registry/
│   ├── dark-theme.reg
│   ├── transparency.reg
│   ├── oem-branding.reg
│   └── performance.reg
└── assets/
    ├── logos/
    │   ├── arizenOS_logo_oem.bmp    ← 120×120px, 24-bit BMP (OEMInfo)
    │   ├── arizenOS_logo_white.png  ← White variant (800×200px)
    │   └── arizenOS_logo_dark.png   ← Dark variant (800×200px)
    └── wallpapers/
        ├── arizenOS_default.jpg     ← 3840×2160 (4K), <2MB
        ├── arizenOS_dark.jpg        ← Dark minimal variant
        ├── arizenOS_lockscreen.jpg  ← Lock screen, 1920×1080 minimum
        └── arizenOS_alt.jpg         ← Alternate colorway
```

---

## 2. Asset Requirements

### Logos

| File | Format | Size | Notes |
|------|--------|------|-------|
| `arizenOS_logo_oem.bmp` | 24-bit BMP | 120×120 px | Required by OEMInformation registry key |
| `arizenOS_logo_white.png` | PNG (transparent) | 800×200 px | White on transparent |
| `arizenOS_logo_dark.png` | PNG (transparent) | 800×200 px | Dark/colored on transparent |
| `arizenOS_icon.ico` | ICO | 256×256 + multi-res | For shortcuts and file associations |

### Wallpapers

| File | Format | Resolution | Notes |
|------|--------|------------|-------|
| `arizenOS_default.jpg` | JPEG | 3840×2160 | Primary wallpaper, ≤2MB |
| `arizenOS_dark.jpg` | JPEG | 3840×2160 | Minimal dark variant |
| `arizenOS_lockscreen.jpg` | JPEG | 1920×1080 | Lock screen image |
| `arizenOS_alt.jpg` | JPEG | 3840×2160 | Optional alternate |

**Color Palette (for asset creation):**

```
Background Deep:  #0F172A  (slate-950)
Background Card:  #1E293B  (slate-800)
Accent Primary:   #3B82F6  (blue-500)
Accent Bright:    #38BDF8  (sky-400)
Text Primary:     #F8FAFC  (slate-50)
Text Secondary:   #94A3B8  (slate-400)
```

---

## 3. Registry Changes — Complete Index

### Dark Theme
| Key Path | Value Name | Type | Data |
|----------|------------|------|------|
| `HKLM\...\Themes\Personalize` | `AppsUseLightTheme` | DWORD | `0` |
| `HKLM\...\Themes\Personalize` | `SystemUsesLightTheme` | DWORD | `0` |
| `HKCU\...\DWM` | `AccentColor` | DWORD | `0xFF1E293B` |
| `HKCU\...\DWM` | `UseWindowsDarkMode` | DWORD | `1` |

### Transparency
| Key Path | Value Name | Type | Data |
|----------|------------|------|------|
| `HKCU\...\Personalize` | `EnableTransparency` | DWORD | `1` |
| `HKCU\...\Personalize` | `EnableBlurBehind` | DWORD | `1` |
| `HKCU\...\ImmersiveShell` | `UseAcrylicSurface` | DWORD | `1` |
| `HKLM\...\Explorer\Advanced` | `UseOLEDTaskbarTransparency` | DWORD | `1` |

### Telemetry Disable
| Key Path | Value Name | Type | Data |
|----------|------------|------|------|
| `HKLM\...\DataCollection` | `AllowTelemetry` | DWORD | `0` |
| `HKLM\...\CloudContent` | `DisableWindowsConsumerFeatures` | DWORD | `1` |
| `HKLM\...\AdvertisingInfo` | `DisabledByGroupPolicy` | DWORD | `1` |
| `HKCU\...\Privacy` | `TailoredExperiencesWithDiagnosticDataEnabled` | DWORD | `0` |

### OEM Branding
| Key Path | Value Name | Type | Data |
|----------|------------|------|------|
| `HKLM\...\OEMInformation` | `Manufacturer` | SZ | `ArizenOS Project` |
| `HKLM\...\OEMInformation` | `Model` | SZ | `ArizenOS Edition` |
| `HKLM\...\OEMInformation` | `SupportURL` | SZ | `https://github.com/Alrizz-art/ArizenOS` |
| `HKLM\...\CurrentVersion` | `RegisteredOrganization` | SZ | `ArizenOS` |

---

## 4. Installation Flow

```
User launches AME Wizard
        │
        ▼
   Load playbook.yaml
   Display configuration options:
   ├── [x] Windows 10 / Windows 11
   ├── [x] Developer Mode
   ├── Safe / Minimal Debloat
   ├── [x] OEM Branding
   ├── [x] Wallpaper
   └── [x] Create Restore Point
        │
        ▼
   Phase 0: PREFLIGHT CHECKS
   ├── OS build validation (min 19045)
   ├── Admin privilege check
   ├── Disk space check (500MB minimum)
   └── Network check (if Dev Mode selected)
        │
        ▼
   Phase 1: RESTORE POINT
   └── Checkpoint System (if enabled)
        │
        ▼
   Phase 2: REGISTRY + THEME
   ├── Import dark-theme.reg
   ├── Import transparency.reg
   └── Import performance.reg
        │
        ▼
   Phase 3: OEM BRANDING
   ├── Copy logo assets
   └── Run oem-branding.ps1
        │
        ▼
   Phase 4: DEBLOAT
   └── Run debloat.ps1 -Level [Safe|Minimal]
        │
        ▼
   Phase 5: WALLPAPER
   └── Run wallpaper.ps1
        │
        ▼
   Phase 6: DEVELOPER SETUP [optional]
   └── Run developer-setup.ps1
        │
        ▼
   Phase 7: FINAL CLEANUP
   ├── Archive logs to C:\ArizenOS\Logs
   ├── Run security-audit.ps1
   └── Restart Explorer
        │
        ▼
   ✅ COMPLETE — Prompt for reboot
```

---

## 5. Rollback Strategy

Three-tier rollback:

### Tier 1 — System Restore Point (Recommended)
- Created **before** any changes at Phase 0
- Full OS state snapshot
- Revert via `rollback.ps1 -UseRestorePoint`
- Or: `rstrui.exe` → select "ArizenOS Pre-Install" point

### Tier 2 — Registry Backups
- All modified keys exported before change
- Backed up to `C:\ArizenOS\Backups\registry\`
- Revert via `rollback.ps1 -RestoreRegistry`

### Tier 3 — AppX Re-provisioning
- Removed packages logged to `C:\ArizenOS\Logs\removed_apps.txt`
- Can be re-provisioned from Windows ISO source
- Revert via `rollback.ps1 -RestoreApps`

### Full Rollback
```powershell
.\scripts\rollback.ps1 -Full
```

---

## 6. Security Review

### Hardened Surface
| Item | Status | Notes |
|------|--------|-------|
| Telemetry | Disabled | All DataCollection policies set to 0 |
| Remote Registry | Disabled | Stops external registry access |
| DiagTrack Service | Disabled | Connected User Experiences svc |
| Cortana | Disabled | Group Policy enforced |
| Activity History | Disabled | Timeline data not collected |
| Advertising ID | Disabled | Per-user advertising tracking off |

### Preserved Security (NOT modified)
| Item | Status | Reason |
|------|--------|--------|
| Windows Defender | ✅ Untouched | Core antivirus protection |
| Windows Firewall | ✅ Untouched | Network boundary defense |
| UAC | ✅ Untouched | Privilege escalation guard |
| SmartScreen | ✅ Untouched | Download reputation checks |
| Windows Update | ✅ Untouched | Security patch delivery |
| BitLocker | ✅ Untouched | Disk encryption |
| Secure Boot | ✅ Untouched | Boot integrity |
| UEFI Isolation | ✅ Untouched | VBS/HVCI stack |
| Credential Guard | ✅ Untouched | LSASS memory protection |
| TPM | ✅ Untouched | Hardware security module |

### Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| AppX removal breaks OS | Protected list prevents removal of Store, WinGet, VCLibs, UI.Xaml |
| Service disable causes boot failure | Only non-critical services disabled; tested against clean installs |
| Registry import corrupts theme | System Restore Point created pre-application |
| Dev toolchain introduces attack surface | Docker/WSL2 are optional, user-consented |
| OEM branding persists on reinstall | Documented removal via `rollback.ps1 -Full` |

### Compliance Notes
- No third-party telemetry introduced
- No unsigned scripts (all scripts carry inline documentation)
- No scheduled tasks added
- No network callbacks during installation
- AME Wizard itself requires user-initiated execution (no silent install)
