# playbook/scripts/ — Playbook-Scoped PowerShell Scripts

> **Purpose:** AME Wizard entry scripts, organized by function  
> **Ownership:** Core Team + approved contributors (entry-level)  
> **Release Process:** Scripts sync to root `scripts/` on PR merge for build inclusion

---

## Purpose and Distinction

There are two `scripts/` directories in ArizenOS:

| Directory | Contents | Run By |
|-----------|---------|--------|
| `scripts/` (root) | Build utilities, CI helpers, maintenance tools | Developers / CI |
| `playbook/scripts/` | AME entry scripts, organized by function | AME Wizard / `scripts/*.ps1` |

Root `scripts/*.ps1` are the canonical files consumed by the build process and AME entry YAMLs. `playbook/scripts/` is the organized source layer where scripts are designed and documented before syncing to root.

---

## Directory Structure

```
playbook/scripts/
├── README.md
├── setup/
│   ├── oem-branding.ps1       ← Applied by oem-branding entry
│   ├── wallpaper.ps1          ← Applied by wallpaper entry
│   ├── apply-theme.ps1        ← Applied by dark-theme entry
│   └── developer-setup.ps1   ← Applied by developer-setup entry
├── branding/
│   └── apply-oem-assets.ps1  ← Validates + copies OEM BMP assets
├── cleanup/
│   └── final-cleanup.ps1     ← gpupdate, Explorer restart, summary log
└── utilities/
    └── common.ps1             ← Shared Write-Log, error handling, constants
```

---

## Script Inventory

### setup/oem-branding.ps1

**Called by:** `oem-branding.yaml`  
**Purpose:** Copies OEM BMP to `C:\ArizenOS\OEM\`, validates dimensions, logs OEM registry state  
**Admin required:** Yes  
**Rollback:** Registry backup + remove OEM keys  

Key operations:
1. Create `C:\ArizenOS\OEM\` directory
2. Copy `assets/oem/arizenOS_logo_oem.bmp` → `C:\ArizenOS\OEM\`
3. Validate BMP is 120×120, 24-bit
4. Export pre-install OEM registry keys to `C:\ArizenOS\Backups\registry\oem-pre-install.reg`
5. Log success/failure

### setup/wallpaper.ps1

**Called by:** `wallpaper.yaml`  
**Purpose:** Copies wallpaper assets and sets desktop + lockscreen  
**Admin required:** Partial (lockscreen is HKLM)  
**Rollback:** Reset via SystemParametersInfo to img0.jpg  

Key operations:
1. Create `C:\ArizenOS\Wallpapers\`
2. Copy wallpaper assets
3. Set desktop via `SystemParametersInfo(20, 0, path, 3)`
4. Set lockscreen via registry `HKLM\...\PersonalizationCSP\LockScreenImagePath`

### setup/apply-theme.ps1

**Called by:** `dark-theme.yaml`  
**Purpose:** Post-registry theme application — restarts Explorer to apply theme immediately  
**Admin required:** No (user context)  
**Rollback:** Re-apply light theme registry + restart Explorer  

### setup/developer-setup.ps1

**Called by:** `developer-setup.yaml`  
**Purpose:** Full developer environment setup  
**Admin required:** Yes  
**Rollback:** `winget uninstall` per package; disable Windows features  

Key operations:
1. Enable WSL2 (`wsl --install --no-distribution`)
2. Enable Developer Mode (`AllowDevelopmentWithoutDevLicense = 1`)
3. Verify WinGet availability
4. Install tools via WinGet (offline-safe: wraps in try/catch)
5. Configure PowerShell 7 as default shell
6. Flag restart required (for WSL2) in completion log

### branding/apply-oem-assets.ps1

**Called by:** `oem-branding.yaml` (secondary action)  
**Purpose:** OEM asset validation and placement  
**Admin required:** Yes  

### cleanup/final-cleanup.ps1

**Called by:** `final-cleanup.yaml`  
**Purpose:** Finalize installation  
**Admin required:** Yes  

Key operations:
1. `gpupdate /force` — flush all group policies
2. Restart Explorer: `Stop-Process -Name explorer -Force; Start-Process explorer`
3. Clear Windows Store cache (optional, if debloat ran)
4. Write installation summary to `C:\ArizenOS\Logs\install_summary_{timestamp}.txt`
5. Run smoke checks (inline subset of `playbook/tests/smoke/run-smoke.ps1`)

### utilities/common.ps1

**Dot-sourced by all other scripts**  
**Purpose:** Shared infrastructure  

Contents:
- `Write-Log` function with `[INFO]`, `[OK]`, `[WARN]`, `[FAIL]` levels
- `$LogPath` initialization pattern
- `$ArizenRoot` = `C:\ArizenOS\` constant
- `Test-AdminElevation` function
- `Invoke-WithRetry` — retry wrapper for flaky operations

---

## Script Standards

Every script in `playbook/scripts/` must meet the standards in `LIFECYCLE.md §2.3`:

```powershell
#Requires -RunAsAdministrator   # Only if admin truly needed

<#
.SYNOPSIS    One line
.DESCRIPTION Multi-line description
.VERSION     0.1.0
#>

# Dot-source shared utilities
. "$PSScriptRoot\..\utilities\common.ps1"

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# All paths via variables — never hardcoded
$LogPath = "$ArizenRoot\Logs\feature_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
```

---

## Sync Policy

`playbook/scripts/` → `scripts/` (root) sync happens:
1. Automatically on PR merge via CI (`.github/workflows/ci.yml`)
2. Manually via `make sync-scripts` (Makefile target — to be added)

The root `scripts/` files are the canonical versions consumed by the build.
