# ArizenOS Installation Workflow

> **Version:** 1.0.0  
> **Runtime:** AME Wizard v0.7.3+ on Windows 10 22H2 / Windows 11 23H2+

---

## Pre-Installation Requirements

Before AME Wizard can run `ArizenOS.apbx`, the user must satisfy:

| Requirement | Why | AME Enforced |
|-------------|-----|-------------|
| Windows 10 Build 19045+ or Windows 11 | `minWindowsBuild: 19045` | ✅ Yes |
| Administrator account | Scripts require elevation | ✅ Yes |
| AME Wizard v0.7.3+ | `.apbx` format compatibility | ✅ Yes |
| TPM not in provisioning mode | Restore point creation | ⚠ Warning |
| ≥ 4GB free disk space | Logs, assets, restore point | ⚠ Warning |
| System Restore enabled | Restore point entry | ⚠ Warning only |

---

## Installation Flow

### Phase 0 — AME Wizard Pre-Flight

```
User opens ArizenOS.apbx in AME Wizard
          │
          ▼
AME Wizard validates:
  ├── playbook.yaml schema
  ├── minWindowsBuild check (blocks if < 19045)
  ├── Administrator privilege check
  └── Configuration UI displayed
          │
          ▼
User selects configuration:
  ├── Edition: Windows 10 (22H2+) OR Windows 11 (22H2+)
  ├── DeveloperMode: [ ] checkbox (default: ON)
  ├── DebloatLevel: Safe (recommended) OR Minimal
  ├── OEMBranding: [ ] checkbox (default: ON)
  ├── Wallpaper: [ ] checkbox (default: ON)
  └── RollbackPoint: [ ] checkbox (default: ON)
          │
          ▼
User clicks "Apply Playbook"
```

---

### Phase 1 — Safety Net (Entry: restore-point.yaml)

```
IF RollbackPoint = ON:
    │
    ▼
Check: System Restore enabled on C:
    ├── Enabled → Proceed
    └── Disabled → Enable it, then proceed (with user notification)
    │
    ▼
Create System Restore Point:
    Name: "ArizenOS Pre-Install — {timestamp}"
    Type: APPLICATION_INSTALL
    │
    ▼
Log restore point sequence number to:
    C:\ArizenOS\Logs\install_{timestamp}.log
    │
    ▼
Continue to Phase 2

IF RollbackPoint = OFF:
    └── Log warning and continue (user accepted risk)
```

**Failure behavior:** If restore point creation fails and `RollbackPoint = ON`, entry returns error. AME Wizard pauses and prompts user to continue or abort. Entry has `ErrorOnFail: false` — user may proceed at their own risk.

---

### Phase 2 — Registry Layer

All registry entries in this phase are applied via AME `ApplyRegistryFile` action.

#### 2.1 OEM Branding (Entry: oem-branding.yaml)

```
IF OEMBranding = ON:
    │
    ▼
Export current OEM registry keys to:
    C:\ArizenOS\Backups\registry\oem-pre-install.reg
    │
    ▼
Copy assets:
    playbook/assets/oem/arizenOS_logo_oem.bmp
        → C:\ArizenOS\OEM\arizenOS_logo.bmp
    │
    ▼
Apply registry/oem-branding.reg:
    ├── HKLM\...\OEMInformation\Manufacturer = "ArizenOS Project"
    ├── HKLM\...\OEMInformation\Model = "ArizenOS Edition"
    ├── HKLM\...\OEMInformation\SupportURL = GitHub URL
    ├── HKLM\...\OEMInformation\Logo = C:\ArizenOS\OEM\arizenOS_logo.bmp
    └── Consumer feature suppression keys
    │
    ▼
Run scripts/oem-branding.ps1
    └── Validates BMP dimensions (120×120)
    └── Logs OEM registration
```

#### 2.2 Dark Theme (Entry: dark-theme.yaml)

```
Apply registry/dark-theme.reg:
    ├── HKLM\...\Themes\Personalize\AppsUseLightTheme = 0
    ├── HKLM\...\Themes\Personalize\SystemUsesLightTheme = 0
    ├── HKCU\...\DWM\AccentColor = #1E293B (Arizen Deep Slate)
    └── HKCU\...\DWM\UseWindowsDarkMode = 1
```

#### 2.3 Transparency (Entry: transparency.yaml)

```
Apply registry/transparency.reg:
    ├── EnableTransparency = 1
    ├── DWM Composition = 1
    ├── GlassOpacity = 55 (0x55)
    ├── UseOLEDTaskbarTransparency = 1  [Win 10/11]
    ├── UseAcrylicSurface = 1           [ImmersiveShell]
    └── EnableMicaEffect = 1            [Win 11 only, no-op on Win 10]
```

---

### Phase 3 — System Cleanup (Entry: debloat.yaml)

```
IF DebloatLevel = Safe OR Minimal:
    │
    ▼
Run scripts/debloat.ps1 -Level {DebloatLevel}
    │
    ├── Phase 1: Set telemetry registry policies
    │       AllowTelemetry = 0
    │       DisableWindowsConsumerFeatures = 1
    │       AdvertisingInfo disabled
    │
    ├── Phase 2: Disable telemetry services
    │       DiagTrack, dmwappushservice, WerSvc, PcaSvc,
    │       RetailDemo, MapsBroker, lfsvc, Fax, RemoteRegistry
    │
    ├── Phase 3: Disable scheduled telemetry tasks
    │       CEIP, Compatibility Appraiser, DiskDiagnostic,
    │       Feedback SIUF, Error Reporting
    │
    └── Phase 4: Remove AppX packages (Safe OR Minimal list)
            Protected guard enforced — Store/WinGet/Edge NEVER removed
```

**Critical protection verification:**
Before any AppX removal, the script checks `$ProtectedApps`. If the package name appears in the protected list, it is skipped with a WARN log entry. This check cannot be bypassed by configuration.

---

### Phase 4 — Visual Layer (Entry: wallpaper.yaml)

```
IF Wallpaper = ON:
    │
    ▼
Copy wallpaper assets:
    playbook/assets/wallpapers/arizenOS_default.jpg
        → C:\ArizenOS\Wallpapers\
    playbook/assets/wallpapers/arizenOS_dark.jpg
        → C:\ArizenOS\Wallpapers\
    playbook/assets/wallpapers/arizenOS_lockscreen.jpg
        → C:\ArizenOS\Wallpapers\
    │
    ▼
Run scripts/wallpaper.ps1:
    ├── Set desktop wallpaper (SystemParametersInfo)
    ├── Set lockscreen image (registry)
    └── Log applied wallpaper path
```

---

### Phase 5 — Developer Environment (Entry: developer-setup.yaml)

```
IF DeveloperMode = ON:
    │
    ▼
Run scripts/developer-setup.ps1:
    │
    ├── [1] Enable WSL2
    │       wsl --install --no-distribution
    │       Requires restart — flagged as deferred
    │
    ├── [2] Enable Windows Developer Mode
    │       Registry: AllowDevelopmentWithoutDevLicense = 1
    │
    ├── [3] Verify WinGet (DesktopAppInstaller present)
    │
    ├── [4] Install via WinGet (with --silent --accept flags):
    │       Git.Git
    │       Microsoft.VisualStudioCode
    │       OpenJS.NodeJS.LTS
    │       Python.Python.3.12
    │       Microsoft.PowerShell
    │       JanDeDobbeleer.OhMyPosh
    │
    └── [5] Configure PowerShell profile
            Set default shell to PowerShell 7
```

**Offline behavior:** If WinGet cannot reach the internet, the step logs a warning and skips WinGet installs. WSL2 and Developer Mode changes are registry/feature-only and work offline.

---

### Phase 6 — Finalize (Entry: final-cleanup.yaml)

```
Run scripts/final-cleanup.ps1:
    │
    ├── Flush Group Policy: gpupdate /force
    ├── Restart Explorer shell (kills and relaunches explorer.exe)
    ├── Clear Windows prefetch (if DebloatLevel = Safe)
    ├── Write installation summary to:
    │       C:\ArizenOS\Logs\install_summary_{timestamp}.txt
    └── Notify AME Wizard: COMPLETE
```

---

## Post-Installation State

After successful completion:

| Location | Contents |
|----------|---------|
| `C:\ArizenOS\Logs\` | Full install log + summary |
| `C:\ArizenOS\OEM\` | OEM BMP asset |
| `C:\ArizenOS\Wallpapers\` | Wallpaper assets |
| `C:\ArizenOS\Backups\registry\` | Pre-install registry exports |
| System Restore | "ArizenOS Pre-Install" restore point |

---

## Error Handling

| Scenario | Behavior |
|---------|---------|
| Restore point fails | Warn + prompt (not hard fail) |
| Registry key already exists | `Set-ItemProperty -Force` overwrites |
| AppX package not found | Log INFO + skip (not an error) |
| WinGet offline | Log WARN + skip installs |
| Script throws unhandled exception | Log FAIL + abort current entry, continue playbook |
| Asset file missing | Log WARN + skip asset operation |
| Admin privilege missing | AME blocks playbook from starting |
