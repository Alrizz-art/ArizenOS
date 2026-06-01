# ArizenOS Rollback Workflow

> **Version:** 1.0.0  
> **Script:** `scripts/rollback.ps1`  
> **Log location:** `C:\ArizenOS\Logs\rollback_{timestamp}.log`

---

## Rollback Philosophy

ArizenOS is designed for safe, reversible operation. Every change that cannot be reversed automatically has a documented manual procedure. The rollback system has three tiers:

```
Tier 1 — Windows System Restore     (full system state, pre-install snapshot)
Tier 2 — Registry Revert            (undo all registry changes individually)
Tier 3 — Component Rollback         (targeted undo of specific features)
```

Tier 1 is always tried first. Tiers 2 and 3 exist for cases where Tier 1 is unavailable (user skipped restore point, restore point was deleted, or only partial revert is needed).

---

## Tier 1 — System Restore

**When to use:** Full rollback to exact pre-install state.  
**Prereq:** User enabled `RollbackPoint` during installation (default: ON).  
**Script:** `scripts/rollback.ps1 -UseRestorePoint`

### Procedure

```
1. Open scripts/rollback.ps1 -UseRestorePoint as Administrator
        │
        ▼
2. Script lists available restore points:
   SequenceNumber  Description                    CreationTime
   ──────────────  ─────────────────────────────  ───────────────────
   N               ArizenOS Pre-Install — YYYYMMDD_HHMMSS   [target]
   N-1             Previous point...
        │
        ▼
3. User enters sequence number of "ArizenOS Pre-Install" point
        │
        ▼
4. Restore-Computer initiates — system will restart automatically
        │
        ▼
5. Windows restores to pre-install state
   └── Registry reverted
   └── Services restored
   └── AppX packages potentially restored (Windows handles this)
        │
        ▼
6. Post-restore: verify at Settings → System → About
   └── OEM info should show Windows defaults
   └── Apps removed by debloat may NOT be restored by this method
       (see Tier 3 for app re-provisioning)
```

### Limitations

- Does NOT restore removed AppX packages from provisioned store
- May not restore packages silently removed from Windows image
- Requires System Restore service was enabled at time of install

---

## Tier 2 — Registry Revert

**When to use:** Undo visual/branding/performance changes without a full restore.  
**Prereq:** Registry backups in `C:\ArizenOS\Backups\registry\`  
**Script:** `scripts/rollback.ps1 -RestoreRegistry`

### Registry Backup Files

During installation, the following pre-install registry exports are created:

| Backup File | Keys Covered |
|------------|-------------|
| `oem-pre-install.reg` | `HKLM\...\OEMInformation` |
| `theme-pre-install.reg` | `HKCU\...\Themes\Personalize`, `HKCU\...\DWM` |
| `transparency-pre-install.reg` | DWM Composition, GlassOpacity |
| `telemetry-pre-install.reg` | DataCollection policies |
| `services-pre-install.reg` | Disabled service startup types |

### Procedure

```
scripts/rollback.ps1 -RestoreRegistry
        │
        ▼
Scans C:\ArizenOS\Backups\registry\ for *.reg files
        │
        ▼
For each backup file:
    reg import {file.reg}
    Log result
        │
        ▼
Rollback complete — Explorer restart may be needed:
    Stop-Process -Name explorer -Force
    Start-Process explorer
```

### Manual Registry Revert Reference

If backup files are unavailable, use these manual reverts:

**Revert OEM Branding:**
```
Remove-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation -Name Manufacturer,Model,SupportURL,Logo
```

**Revert Dark Theme:**
```
Set-ItemProperty HKCU:\...\Themes\Personalize -Name AppsUseLightTheme -Value 1
Set-ItemProperty HKCU:\...\Themes\Personalize -Name SystemUsesLightTheme -Value 1
```

**Revert Transparency:**
```
Set-ItemProperty HKCU:\...\Themes\Personalize -Name EnableTransparency -Value 0
```

**Re-enable telemetry services:**
```
@("DiagTrack","dmwappushservice","WerSvc","PcaSvc") | ForEach-Object {
    Set-Service $_ -StartupType Automatic; Start-Service $_
}
```

---

## Tier 3 — Component Rollback

### 3.1 Re-provision Removed AppX Packages

**When to use:** Specific apps were removed by debloat and the user wants them back.  
**Script:** `scripts/rollback.ps1 -RestoreApps`

```
Procedure:
1. Mount Windows installation ISO (or insert Windows install media)
2. Run: scripts/rollback.ps1 -RestoreApps
3. Enter path to Windows source (e.g. D:\)
4. Script re-provisions .msix packages from Windows image

Alternative (individual apps):
    winget install Microsoft.Teams         # Re-install Teams
    winget install Microsoft.OneDrive      # Re-install OneDrive
    winget install Spotify.Spotify         # (if removed)
```

**Note:** Microsoft Store apps can always be re-downloaded from the Store after debloat. The Store itself (`Microsoft.WindowsStore`) is NEVER removed by ArizenOS.

### 3.2 Revert Wallpaper

```
# Restore Windows default wallpaper
$imgPath = "C:\Windows\Web\Wallpaper\Windows\img0.jpg"
Add-Type -TypeDefinition @"
using System.Runtime.InteropServices;
public class Wallpaper {
    [DllImport("user32.dll")]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
"@
[Wallpaper]::SystemParametersInfo(20, 0, $imgPath, 3)
```

### 3.3 Revert Developer Setup

WinGet-installed applications must be uninstalled individually:
```
winget uninstall Git.Git
winget uninstall Microsoft.VisualStudioCode
winget uninstall OpenJS.NodeJS.LTS
```

WSL2 removal:
```
wsl --unregister {distro-name}    # Remove any installed distros
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Disable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

### 3.4 Revert Performance Tweaks

The performance registry tweaks in `registry/performance.reg` can be reverted via Tier 2 backup. Manual restoration of key defaults:

```
# Restore Explorer delays
Set-ItemProperty "HKCU:\Control Panel\Desktop" -Name MenuShowDelay -Value 400
Set-ItemProperty "HKCU:\Control Panel\Desktop" -Name WaitToKillAppTimeout -Value 20000

# Restore NTFS timestamps
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name NtfsDisableLastAccessUpdate -Value 0

# Re-enable Prefetch/Superfetch
Set-ItemProperty "HKLM:\...\PrefetchParameters" -Name EnablePrefetcher -Value 3
Set-ItemProperty "HKLM:\...\PrefetchParameters" -Name EnableSuperfetch -Value 3
```

---

## Rollback Decision Matrix

```
Something is wrong after install
            │
            ▼
Is it a visual issue only? (theme, wallpaper, branding)
YES → Tier 2: Registry Revert (-RestoreRegistry)
NO  ↓
            ▼
Is it a missing app?
YES → Tier 3: RestoreApps (-RestoreApps) or re-install from Store
NO  ↓
            ▼
Is there a system stability issue?
YES → Tier 1: System Restore (-UseRestorePoint)
NO  ↓
            ▼
Is it a service-related issue?
YES → Re-enable services manually (see Tier 2 §telemetry)
      OR Tier 1 if services are broken
NO  ↓
            ▼
Open GitHub Issue with tag [bug][playbook] + attach C:\ArizenOS\Logs\
```

---

## Rollback Log Location

All rollback operations are logged to:
```
C:\ArizenOS\Logs\rollback_{YYYYMMDD_HHmmss}.log
```

The log captures every action, its result (OK / WARN / FAIL), and timestamps. Include this file in any bug report.

---

## What Cannot Be Rolled Back Automatically

| Component | Why | Manual Solution |
|-----------|-----|----------------|
| Disabled scheduled tasks | Re-enable via Task Scheduler |  `Enable-ScheduledTask` per task |
| `LongPathsEnabled = 1` in registry | Safe to leave, no functional impact | Set back to 0 |
| WSL2 feature state | Feature install is non-destructive | Disable via Windows Features |
| WinGet package installs | Installed as user apps | `winget uninstall {id}` |
| Power plan changes | Plans not modified, only hint provided | `powercfg /setactive BALANCED` |
