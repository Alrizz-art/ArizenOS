# ArizenOS v0.1 — Product Specification

**Document Type**: Production Specification  
**Version**: v0.1.0  
**Status**: Draft → Pending Approval  
**Date**: 2026-06-02  
**Author**: Technical Council, ArizenOS  
**Scope**: ArizenOS v0.1 Distribution Package (`.apbx`)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Target Platforms](#2-target-platforms)
3. [Feature Matrix](#3-feature-matrix)
4. [User Experience Flow](#4-user-experience-flow)
5. [Installation Flow](#5-installation-flow)
6. [Rollback Flow](#6-rollback-flow)
7. [Asset Requirements](#7-asset-requirements)
8. [Script Requirements](#8-script-requirements)
9. [Registry Requirements](#9-registry-requirements)
10. [Testing Requirements](#10-testing-requirements)
11. [Release Checklist](#11-release-checklist)

---

## 1. Executive Summary

### 1.1 Product Identity

**ArizenOS v0.1** is the first public distribution of the ArizenOS experience layer — a curated, non-destructive Windows customization package that transforms a stock Windows 10 or Windows 11 installation into the ArizenOS aesthetic baseline.

It ships as a single `.apbx` playbook file, applied via AME Wizard. The package is fully reversible via the bundled rollback mechanism.

### 1.2 Design Philosophy

> **Non-destructive first.** Every change applied by ArizenOS v0.1 must be reversible with a single rollback action. No system files are permanently modified. No services required for Windows operation are disabled.

> **Appearance-forward.** v0.1 is about look, feel, and identity — not performance optimization or security hardening. Those are post-v0.1 concerns.

> **Honest branding.** ArizenOS v0.1 is a Windows overlay. It does not misrepresent itself as a standalone OS. OEM branding reflects ArizenOS identity, not a fabricated hardware vendor.

### 1.3 Scope Boundaries

| In Scope (v0.1) | Out of Scope (post-v0.1) |
|---|---|
| OEM branding | App installation |
| Wallpaper system | Taskbar customization (ExplorerPatcher) |
| Lock screen branding | Privacy/telemetry tweaks |
| Dark theme enforcement | Network stack changes |
| Transparency tweaks | Security hardening |
| Safe performance tweaks | Driver installation |
| Developer setup (optional) | Windows feature removal |
| Rollback support | Service disable/removal |

---

## 2. Target Platforms

### 2.1 Supported Versions

| Platform | Version | Build | Architecture | Support Level |
|---|---|---|---|---|
| Windows 10 | 22H2 | 19045.xxxx | x64 | ✅ Full |
| Windows 11 | 23H2 | 22631.xxxx | x64 | ✅ Full |
| Windows 11 | 24H2 | 26100.xxxx | x64 | ✅ Full |
| Windows 10 | 21H2 | 19044.xxxx | x64 | ⚠️ Best-effort |
| ARM64 | Any | Any | ARM64 | ❌ Not supported in v0.1 |

### 2.2 Minimum Requirements

| Requirement | Minimum |
|---|---|
| RAM | 4 GB |
| Storage (free) | 500 MB |
| AME Wizard | v1.0.0 or later |
| Administrator privileges | Required |
| Internet connection | Not required for apply |

### 2.3 Known Incompatibilities

| Scenario | Behavior |
|---|---|
| Windows S Mode | Playbook will abort — S Mode blocks registry writes |
| Windows LTSC/LTSB | Partial — transparency effects may not apply |
| Non-English locale | Supported, but OEM strings display in English |
| Active enterprise GPO | OEM branding GPO may be overridden by domain policy |

---

## 3. Feature Matrix

### 3.1 v0.1 Features

| # | Feature | Category | Reversible | Risk Level | Priority |
|---|---|---|---|---|---|
| F-01 | OEM Manufacturer Name | Branding | ✅ Yes | Low | P0 |
| F-02 | OEM Manufacturer Logo | Branding | ✅ Yes | Low | P0 |
| F-03 | OEM Support URL | Branding | ✅ Yes | Low | P0 |
| F-04 | OEM Support Phone | Branding | ✅ Yes | Low | P1 |
| F-05 | OEM Support Hours | Branding | ✅ Yes | Low | P1 |
| F-06 | OEM Model Name | Branding | ✅ Yes | Low | P0 |
| F-07 | Default Wallpaper (Dark) | Wallpaper | ✅ Yes | Low | P0 |
| F-08 | Default Wallpaper (Light) | Wallpaper | ✅ Yes | Low | P0 |
| F-09 | Lock Screen Wallpaper | Wallpaper | ✅ Yes | Low | P0 |
| F-10 | Lock Screen Branding Text | Branding | ✅ Yes | Low | P1 |
| F-11 | System Dark Theme | Theme | ✅ Yes | Low | P0 |
| F-12 | App Dark Theme | Theme | ✅ Yes | Low | P0 |
| F-13 | Acrylic Transparency (Taskbar) | Transparency | ✅ Yes | Low | P1 |
| F-14 | Acrylic Transparency (Start) | Transparency | ✅ Yes | Low | P1 |
| F-15 | Window Transparency | Transparency | ✅ Yes | Low | P2 |
| F-16 | Visual Effects Optimization | Performance | ✅ Yes | Low | P1 |
| F-17 | Prefetch / Superfetch Tuning | Performance | ✅ Yes | Low | P2 |
| F-18 | Developer Mode (Optional) | Developer | ✅ Yes | Low | P1 |
| F-19 | Execution Policy (Optional) | Developer | ✅ Yes | Medium | P1 |
| F-20 | Long Path Support (Optional) | Developer | ✅ Yes | Low | P1 |
| F-21 | Restore Point Creation | Rollback | ✅ N/A | Low | P0 |
| F-22 | Registry Backup | Rollback | ✅ N/A | Low | P0 |
| F-23 | Rollback Entry Point | Rollback | ✅ N/A | Low | P0 |

### 3.2 Feature Groups

**Group A — Branding (P0)**: F-01, F-02, F-03, F-06, F-07, F-08, F-09  
**Group B — Branding (P1)**: F-04, F-05, F-10  
**Group C — Theme**: F-11, F-12  
**Group D — Transparency**: F-13, F-14, F-15  
**Group E — Performance**: F-16, F-17  
**Group F — Developer (Optional, user-prompted)**: F-18, F-19, F-20  
**Group G — Rollback Infrastructure**: F-21, F-22, F-23

> **P0 features are release blockers.** The v0.1 release cannot ship without all P0 features passing QA.  
> **P1 features are release goals.** If a P1 feature fails QA, it is disabled (not removed) and tracked for v0.1.1.  
> **P2 features are best-effort.** May be disabled if stability concerns arise.

---

## 4. User Experience Flow

### 4.1 Pre-Installation

```
User downloads ArizenOS.apbx
          │
          ▼
User opens AME Wizard
          │
          ▼
AME Wizard validates .apbx integrity (checksum)
          │
          ├── FAIL → Error: "This playbook file is corrupted. Please re-download."
          │
          ▼
AME Wizard displays ArizenOS Welcome Screen
│
│  ┌─────────────────────────────────────────────────┐
│  │  Welcome to ArizenOS                            │
│  │                                                 │
│  │  This playbook will apply the ArizenOS         │
│  │  experience layer to your Windows installation.│
│  │                                                 │
│  │  What will change:                              │
│  │  • System branding and identity                 │
│  │  • Wallpapers and lock screen                   │
│  │  • Dark theme and transparency                  │
│  │  • Optional: Developer setup                    │
│  │                                                 │
│  │  A restore point will be created before        │
│  │  any changes are applied.                       │
│  │                                                 │
│  │  [ Continue ]  [ Cancel ]                       │
│  └─────────────────────────────────────────────────┘
```

### 4.2 Option Selection (Optional Features)

```
          │
          ▼
Optional Feature Selection Screen
│
│  ┌─────────────────────────────────────────────────┐
│  │  Optional: Developer Setup                      │
│  │                                                 │
│  │  ☑ Enable Windows Developer Mode               │
│  │  ☑ Enable long file path support               │
│  │  ☐ Set PowerShell execution policy             │
│  │    to RemoteSigned                              │
│  │                                                 │
│  │  These settings can be reversed at any time.   │
│  │                                                 │
│  │  [ Continue ]  [ Skip ]                         │
│  └─────────────────────────────────────────────────┘
```

### 4.3 Progress Display

```
          │
          ▼
Installation Progress
│
│  ┌─────────────────────────────────────────────────┐
│  │  Applying ArizenOS...                           │
│  │                                                 │
│  │  [████████████░░░░░░░░]  58%                    │
│  │                                                 │
│  │  ✅ Restore point created                       │
│  │  ✅ Registry backup saved                       │
│  │  ✅ OEM branding applied                        │
│  │  ⚙  Applying wallpapers...                      │
│  │  ○  Theme and transparency                      │
│  │  ○  Performance tweaks                          │
│  │  ○  Developer setup                             │
│  │                                                 │
│  └─────────────────────────────────────────────────┘
```

### 4.4 Completion

```
          │
          ▼
Completion Screen
│
│  ┌─────────────────────────────────────────────────┐
│  │  ArizenOS Applied Successfully                  │
│  │                                                 │
│  │  ✅ 23 changes applied                          │
│  │  ✅ Restore point saved                         │
│  │  ✅ Rollback available                          │
│  │                                                 │
│  │  A restart is required to complete the          │
│  │  experience.                                    │
│  │                                                 │
│  │  [ Restart Now ]  [ Restart Later ]             │
│  └─────────────────────────────────────────────────┘
```

---

## 5. Installation Flow

### 5.1 Step-by-Step Execution Order

The playbook MUST execute steps in this exact order. Order is not advisory — it is required.

```
Step 1 — PREFLIGHT
  1.1  Verify OS version (abort if < Windows 10 22H2)
  1.2  Verify administrator privileges (abort if not elevated)
  1.3  Verify S Mode is inactive (abort if S Mode)
  1.4  Verify disk space ≥ 500 MB free on %SystemDrive% (warn if < 1 GB)
  1.5  Verify AME Wizard version (warn if < v1.0.0)

Step 2 — SAFETY NET
  2.1  Create Windows Restore Point ("Before ArizenOS v0.1")
  2.2  Export current registry keys to %APPDATA%\ArizenOS\backup\registry-backup.reg
         Keys: HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation
               HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes
               HKCU\Control Panel\Desktop
               HKCU\SOFTWARE\Microsoft\Windows\DWM
               HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters
  2.3  Log backup locations to %APPDATA%\ArizenOS\backup\manifest.json

Step 3 — ASSET DEPLOYMENT
  3.1  Create directory: %ProgramData%\ArizenOS\branding\
  3.2  Copy OEM logo:
         Source:  assets/logos/arizenOS_logo_oem.bmp
         Dest:    %ProgramData%\ArizenOS\branding\oemlogo.bmp
  3.3  Copy wallpapers:
         Source:  assets/wallpapers/arizenOS_dark.jpg
         Dest:    %ProgramData%\ArizenOS\wallpapers\arizenOS_dark.jpg
         Source:  assets/wallpapers/arizenOS_default.jpg
         Dest:    %ProgramData%\ArizenOS\wallpapers\arizenOS_default.jpg
         Source:  assets/wallpapers/arizenOS_lockscreen.jpg
         Dest:    %ProgramData%\ArizenOS\wallpapers\arizenOS_lockscreen.jpg

Step 4 — OEM BRANDING
  4.1  Write OEM registry keys (see §9.1)
  4.2  Set wallpaper registry value to deployed dark wallpaper path

Step 5 — LOCK SCREEN
  5.1  Disable Windows Spotlight (registry)
  5.2  Set lock screen image to deployed lock screen wallpaper

Step 6 — THEME
  6.1  Apply system-wide dark theme (registry: AppsUseLightTheme = 0, SystemUsesLightTheme = 0)
  6.2  Apply app dark theme (registry: per-user)

Step 7 — TRANSPARENCY
  7.1  Enable transparency effects (registry: EnableTransparency = 1)
  7.2  Apply DWM acrylic composition tweaks (registry: see §9.3)

Step 8 — PERFORMANCE TWEAKS
  8.1  Optimize visual effects for best appearance + performance balance (registry: see §9.4)
  8.2  Tune prefetch parameters (if applicable to OS version)

Step 9 — DEVELOPER SETUP (conditional on user selection)
  9.1  If Developer Mode selected: enable via registry
  9.2  If Long Path selected: set LongPathsEnabled = 1
  9.3  If Execution Policy selected: set PowerShell RemoteSigned policy

Step 10 — FINALIZATION
  10.1  Write ArizenOS installation manifest to %ProgramData%\ArizenOS\manifest.json
          Fields: version, date, features_applied[], backup_path, rollback_script
  10.2  Register rollback shortcut in Start Menu:
          %ProgramData%\Microsoft\Windows\Start Menu\Programs\ArizenOS\Rollback ArizenOS.lnk
  10.3  Prompt for restart
```

### 5.2 Error Handling Policy

| Error Type | Behavior |
|---|---|
| Preflight failure (hard) | Abort immediately, no changes made, display error |
| Preflight warning (soft) | Display warning, allow user to continue or abort |
| Asset copy failure | Abort step, log error, continue if non-critical |
| Registry write failure | Log error, mark feature as failed, continue remaining steps |
| Restore point failure | Warn user, prompt to abort or continue without restore point |
| Any P0 feature failure | Abort installation, report failed step |

---

## 6. Rollback Flow

### 6.1 Rollback Trigger Points

| Method | Description |
|---|---|
| Start Menu shortcut | "Rollback ArizenOS" shortcut in Programs\ArizenOS |
| AME Wizard | Re-open ArizenOS.apbx, select "Rollback" option |
| Windows Recovery | Windows Restore Point created in Step 2.1 |
| Manual registry restore | Import registry-backup.reg from backup directory |

### 6.2 Rollback Execution Order

```
Step 1 — VERIFY BACKUP
  1.1  Read %APPDATA%\ArizenOS\backup\manifest.json
  1.2  Verify registry backup file exists
  1.3  Verify backup was created by this version of ArizenOS
       (abort rollback if version mismatch — use Restore Point instead)

Step 2 — REGISTRY RESTORE
  2.1  Import registry-backup.reg (restores all modified keys to pre-ArizenOS state)
  2.2  Verify critical registry keys restored correctly

Step 3 — ASSET CLEANUP (optional, user-prompted)
  3.1  Prompt: "Remove ArizenOS wallpapers and branding files?"
  3.2  If confirmed:
         Remove %ProgramData%\ArizenOS\ (entire directory)
  3.3  If declined:
         Leave files in place (harmless if registry no longer points to them)

Step 4 — DEVELOPER SETTINGS (conditional)
  4.1  If Developer Mode was enabled by ArizenOS: offer to revert
  4.2  If Execution Policy was changed: offer to revert to Restricted

Step 5 — FINALIZATION
  5.1  Remove Start Menu rollback shortcut
  5.2  Remove %APPDATA%\ArizenOS\backup\ directory
  5.3  Display rollback summary
  5.4  Prompt for restart
```

### 6.3 Rollback Limitations

| Limitation | Notes |
|---|---|
| Wallpaper active session | Wallpaper change takes effect after restart, not during rollback |
| Third-party changes | Changes made by other tools after ArizenOS installation are not rolled back |
| Deleted backup | If backup directory was manually deleted, use Windows Restore Point |
| Version mismatch | Rolling back v0.1 files using v0.2 rollback script is unsupported |

---

## 7. Asset Requirements

### 7.1 OEM Logo

| Property | Requirement |
|---|---|
| File name | `arizenOS_logo_oem.bmp` |
| Format | BMP (Windows DIB, 24-bit color) |
| Dimensions | 120 × 120 pixels (Windows standard OEM logo size) |
| Background | Transparent-equivalent: match Windows System Properties background |
| Color mode | RGB, no alpha channel (BMP does not support alpha in OEM context) |
| Max file size | 256 KB |
| Location in repo | `assets/logos/arizenOS_logo_oem.bmp` |

### 7.2 Desktop Wallpapers

| Property | Dark Variant | Default Variant |
|---|---|---|
| File name | `arizenOS_dark.jpg` | `arizenOS_default.jpg` |
| Format | JPEG (progressive, high quality) |
| Dimensions | 3840 × 2160 (4K UHD) |
| Aspect ratio | 16:9 |
| Color profile | sRGB |
| Quality | JPEG Q90 minimum |
| Max file size | 8 MB |
| Content | ArizenOS branded abstract composition |
| Location in repo | `assets/wallpapers/` |

### 7.3 Lock Screen Wallpaper

| Property | Requirement |
|---|---|
| File name | `arizenOS_lockscreen.jpg` |
| Format | JPEG |
| Dimensions | 3840 × 2160 (4K UHD) |
| Aspect ratio | 16:9 |
| Color profile | sRGB |
| Max file size | 8 MB |
| Content | More minimal than desktop wallpaper — lock screen is the first thing a user sees |
| Location in repo | `assets/wallpapers/` |

### 7.4 Asset Delivery Checklist

| Asset | Status | Verified By |
|---|---|---|
| `arizenOS_logo_oem.bmp` — 120×120px BMP | ⬜ Pending | |
| `arizenOS_dark.jpg` — 4K JPEG | ✅ Present | |
| `arizenOS_default.jpg` — 4K JPEG | ✅ Present | |
| `arizenOS_lockscreen.jpg` — 4K JPEG | ✅ Present | |

> **Blocker**: The OEM logo (`arizenOS_logo_oem.bmp`) must be verified at exactly 120×120 pixels in 24-bit BMP format before v0.1 release. The current file has not been validated against Windows OEM display requirements.

---

## 8. Script Requirements

### 8.1 Script Overview

All scripts are embedded within the `.apbx` playbook. No external script files are required at runtime. Scripts run in the AME Wizard execution context (elevated, system-level PowerShell).

| Script ID | Name | Language | Trigger | Purpose |
|---|---|---|---|---|
| SCR-01 | preflight-check | PowerShell | Pre-install | Validate OS, privileges, disk space |
| SCR-02 | create-restore-point | PowerShell | Pre-install | Create Windows Restore Point |
| SCR-03 | backup-registry | PowerShell | Pre-install | Export registry keys to backup |
| SCR-04 | deploy-assets | PowerShell | Install | Copy branding assets to ProgramData |
| SCR-05 | apply-oem-branding | PowerShell | Install | Write OEM registry keys |
| SCR-06 | apply-wallpaper | PowerShell | Install | Set wallpaper and lock screen |
| SCR-07 | apply-theme | PowerShell | Install | Apply dark theme registry values |
| SCR-08 | apply-transparency | PowerShell | Install | Apply DWM and transparency settings |
| SCR-09 | apply-performance | PowerShell | Install | Write safe performance registry values |
| SCR-10 | apply-developer | PowerShell | Conditional | Optional developer settings |
| SCR-11 | write-manifest | PowerShell | Post-install | Write installation manifest JSON |
| SCR-12 | register-rollback | PowerShell | Post-install | Create Start Menu rollback shortcut |
| SCR-13 | rollback | PowerShell | On-demand | Full rollback sequence |

### 8.2 Script Constraints

- All scripts must be **idempotent** — running them twice produces the same result as running once
- All scripts must **not** modify or delete Windows system files (`C:\Windows\System32`, etc.)
- All scripts must handle errors with `try/catch` and log to `%APPDATA%\ArizenOS\logs\install.log`
- All scripts must **not** disable Windows Defender, Windows Update, or Windows Firewall
- All scripts must exit with code `0` on success and a non-zero code on failure
- Scripts that modify the registry must use `Test-Path` before reading values to avoid exceptions

### 8.3 Script: preflight-check (SCR-01) — Behavior Specification

```
Input:   None
Output:  Exit code 0 (pass) | 1 (hard fail — abort) | 2 (soft warn — prompt user)

Checks:
  1. Current Windows build number ≥ 19045 (Win10 22H2)
     → Fail (hard) if below minimum
  2. Current process is running as Administrator
     → Fail (hard) if not elevated
  3. Windows edition is not S Mode
     → Fail (hard) if S Mode detected
  4. Free disk space on %SystemDrive% ≥ 500 MB
     → Fail (hard) if < 500 MB
     → Warn (soft) if < 1 GB
  5. Detect conflicting active group policies for OEM branding
     → Warn (soft) if domain-joined machine
```

### 8.4 Script: rollback (SCR-13) — Behavior Specification

```
Input:   --version (string, ArizenOS version to roll back)
         --force   (bool, skip version check)
Output:  Exit code 0 (success) | 1 (failure)

Steps:
  1. Read manifest.json — verify version matches
  2. Confirm rollback with user (Y/N prompt)
  3. Import registry backup (.reg file)
  4. Prompt to remove assets (optional)
  5. Prompt to revert developer settings (if applicable)
  6. Remove rollback shortcut
  7. Write rollback log entry
  8. Prompt restart
```

---

## 9. Registry Requirements

### 9.1 OEM Branding Keys

**Hive**: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation`

| Value Name | Type | Data | Notes |
|---|---|---|---|
| `Manufacturer` | REG_SZ | `ArizenOS` | Appears in System Properties |
| `Model` | REG_SZ | `ArizenOS Experience Layer v0.1` | Appears in System Properties |
| `SupportURL` | REG_SZ | `https://github.com/Alrizz-art/ArizenOS` | Clickable in System Properties |
| `SupportPhone` | REG_SZ | (empty) | Not used in v0.1 |
| `SupportHours` | REG_SZ | (empty) | Not used in v0.1 |
| `Logo` | REG_SZ | `%ProgramData%\ArizenOS\branding\oemlogo.bmp` | Full expanded path at write time |

### 9.2 Theme Keys

**Hive**: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `AppsUseLightTheme` | REG_DWORD | `0` | Dark mode for apps |
| `SystemUsesLightTheme` | REG_DWORD | `0` | Dark mode for system UI (taskbar, Start) |
| `EnableTransparency` | REG_DWORD | `1` | Enable acrylic transparency |
| `ColorPrevalence` | REG_DWORD | `0` | Disable accent color on taskbar (cleaner look) |

### 9.3 DWM / Transparency Keys

**Hive**: `HKCU\SOFTWARE\Microsoft\Windows\DWM`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `EnableAeroPeek` | REG_DWORD | `1` | Enable Aero Peek (hover taskbar thumbnails) |
| `AlwaysHibernateThumbnails` | REG_DWORD | `0` | Live taskbar thumbnails |
| `Composition` | REG_DWORD | `1` | DWM composition enabled |
| `ColorPrevalence` | REG_DWORD | `0` | No accent on title bars |

### 9.4 Visual Effects / Performance Keys

**Hive**: `HKCU\Control Panel\Desktop`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `UserPreferencesMask` | REG_BINARY | See note below | Controls all visual effects bitmap |
| `MenuShowDelay` | REG_SZ | `200` | Menu animation delay (ms). Default is 400 |
| `DragFullWindows` | REG_SZ | `1` | Show window contents while dragging |

**Hive**: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `VisualFXSetting` | REG_DWORD | `3` | Custom visual effects (not "best performance") |

> **UserPreferencesMask note**: The mask enables the following effects and disables the rest:  
> ✅ Animate windows when minimizing/maximizing  
> ✅ Smooth edges of screen fonts  
> ✅ Show thumbnails instead of icons  
> ✅ Show translucent selection rectangle  
> ❌ Animate controls and elements inside windows  
> ❌ Fade or slide menus into view  
> ❌ Fade out menu items after clicking  
> The exact bitmask value must be validated on both Win10 22H2 and Win11 23H2 before release.

### 9.5 Prefetch / Superfetch Keys

**Hive**: `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `EnablePrefetcher` | REG_DWORD | `3` | Enable both app and boot prefetch |
| `EnableSuperfetch` | REG_DWORD | `3` | Enable Superfetch (SysMain service) |

> **Note**: These keys restore standard Windows behavior — they are not modified from defaults on a clean Windows install. Applied here to ensure correct state after any previous debloating tools.

### 9.6 Lock Screen Keys

**Hive**: `HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `LockScreenImage` | REG_SZ | `%ProgramData%\ArizenOS\wallpapers\arizenOS_lockscreen.jpg` | Lock screen wallpaper |
| `LockScreenOverlaysDisabled` | REG_DWORD | `1` | Disable Windows Spotlight overlay (if Spotlight was on) |

**Hive**: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `LockScreenImagePath` | REG_SZ | `%ProgramData%\ArizenOS\wallpapers\arizenOS_lockscreen.jpg` | Win11 lock screen path |
| `LockScreenImageUrl` | REG_SZ | `%ProgramData%\ArizenOS\wallpapers\arizenOS_lockscreen.jpg` | Win11 lock screen URL field |
| `LockScreenImageStatus` | REG_DWORD | `1` | Activate the custom lock screen |

### 9.7 Developer Setup Keys (Optional)

**Hive**: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `AllowDevelopmentWithoutDevLicense` | REG_DWORD | `1` | Enable Developer Mode |
| `AllowAllTrustedApps` | REG_DWORD | `1` | Allow sideloading |

**Hive**: `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`

| Value Name | Type | Data | Effect |
|---|---|---|---|
| `LongPathsEnabled` | REG_DWORD | `1` | Enable paths > 260 characters |

---

## 10. Testing Requirements

### 10.1 Test Environments

| Environment ID | OS | Build | Type | Required |
|---|---|---|---|---|
| ENV-01 | Windows 10 22H2 | 19045 | Clean VM (VMware/Hyper-V) | ✅ Required |
| ENV-02 | Windows 11 23H2 | 22631 | Clean VM | ✅ Required |
| ENV-03 | Windows 11 24H2 | 26100 | Clean VM | ✅ Required |
| ENV-04 | Windows 10 22H2 | 19045 | Physical machine | ✅ Required |
| ENV-05 | Windows 11 23H2 | 22631 | Physical machine | ✅ Required |
| ENV-06 | Windows 10 S Mode | Any | VM | ✅ Required (abort test) |

### 10.2 Test Cases

#### Group A — Preflight

| TC-ID | Test Case | Environment | Expected Result | Blocker |
|---|---|---|---|---|
| TC-A01 | Run as standard user (no elevation) | ENV-01 | Playbook aborts with elevation error | ✅ P0 |
| TC-A02 | Run on Windows 10 21H1 (below minimum) | VM | Playbook aborts with OS version error | ✅ P0 |
| TC-A03 | Run on Windows S Mode | ENV-06 | Playbook aborts with S Mode error | ✅ P0 |
| TC-A04 | Run with < 500 MB free disk space | ENV-01 | Playbook aborts with disk space error | ✅ P0 |
| TC-A05 | Run on domain-joined machine | VM | Warning displayed, user can continue | ⚠️ P1 |

#### Group B — Installation

| TC-ID | Test Case | Environment | Expected Result | Blocker |
|---|---|---|---|---|
| TC-B01 | Full install, all features | ENV-01, ENV-02 | All 23 changes applied, no errors | ✅ P0 |
| TC-B02 | Full install without developer setup | ENV-01, ENV-02 | 20 changes applied, dev skipped | ✅ P0 |
| TC-B03 | Restore point created | ENV-01, ENV-02 | Restore point visible in System Properties | ✅ P0 |
| TC-B04 | Registry backup file created | ENV-01, ENV-02 | .reg file exists at expected backup path | ✅ P0 |
| TC-B05 | OEM info visible in System Properties | ENV-01, ENV-02, ENV-04 | Manufacturer, Model, Logo shown correctly | ✅ P0 |
| TC-B06 | OEM logo renders correctly | ENV-01, ENV-02, ENV-04 | 120×120 BMP logo visible, no distortion | ✅ P0 |
| TC-B07 | Desktop wallpaper applied | ENV-01, ENV-02, ENV-04 | Dark wallpaper active after restart | ✅ P0 |
| TC-B08 | Lock screen wallpaper applied | ENV-01, ENV-02, ENV-04 | ArizenOS lock screen on restart | ✅ P0 |
| TC-B09 | Dark theme applied | ENV-01, ENV-02, ENV-04 | System and apps in dark mode | ✅ P0 |
| TC-B10 | Transparency effects active | ENV-01, ENV-02, ENV-04 | Taskbar/Start acrylic visible | ⚠️ P1 |
| TC-B11 | Installation manifest written | ENV-01 | manifest.json readable, correct fields | ✅ P0 |
| TC-B12 | Rollback shortcut in Start Menu | ENV-01 | Shortcut visible and functional | ✅ P0 |

#### Group C — Rollback

| TC-ID | Test Case | Environment | Expected Result | Blocker |
|---|---|---|---|---|
| TC-C01 | Full rollback after full install | ENV-01, ENV-02 | All registry keys restored to pre-install state | ✅ P0 |
| TC-C02 | OEM info removed after rollback | ENV-01, ENV-02, ENV-04 | System Properties shows original OEM info | ✅ P0 |
| TC-C03 | Theme reverts to light after rollback | ENV-01 | System returns to light mode | ✅ P0 |
| TC-C04 | Rollback with missing backup file | ENV-01 | Error shown, user directed to Restore Point | ✅ P0 |
| TC-C05 | Double rollback (rollback when not installed) | ENV-01 | Graceful error, no crash | ⚠️ P1 |
| TC-C06 | Reinstall after rollback | ENV-01 | Clean reinstall succeeds | ✅ P0 |

#### Group D — Idempotency

| TC-ID | Test Case | Environment | Expected Result | Blocker |
|---|---|---|---|---|
| TC-D01 | Run playbook twice on same machine | ENV-01 | Second run succeeds, no duplicate entries | ✅ P0 |
| TC-D02 | Roll back, then install again | ENV-01 | Reinstall succeeds cleanly | ✅ P0 |

#### Group E — Visual QA

| TC-ID | Test Case | Environment | Expected Result | Blocker |
|---|---|---|---|---|
| TC-E01 | OEM logo at 100% DPI | ENV-04 | Logo sharp, correct proportions | ✅ P0 |
| TC-E02 | OEM logo at 125% DPI | ENV-04, ENV-05 | Logo sharp, not blurry | ⚠️ P1 |
| TC-E03 | OEM logo at 150% DPI | ENV-05 | Logo sharp, not blurry | ⚠️ P1 |
| TC-E04 | Wallpaper on 1080p display | ENV-04 | No visible JPEG artifacts | ✅ P0 |
| TC-E05 | Wallpaper on 4K display | ENV-05 | Crisp, fills screen correctly | ✅ P0 |
| TC-E06 | Transparency on Intel integrated GPU | ENV-04 | Effects apply without GPU error | ⚠️ P1 |
| TC-E07 | Dark theme on all Windows UI surfaces | ENV-04, ENV-05 | No light-mode remnants | ⚠️ P1 |

### 10.3 Acceptance Criteria for Release

| Criterion | Required |
|---|---|
| All P0 test cases pass on ENV-01 and ENV-02 | ✅ Required — hard gate |
| All P0 test cases pass on ENV-04 (physical) | ✅ Required — hard gate |
| All P0 test cases pass on ENV-03 (Win11 24H2) | ✅ Required — hard gate |
| No P0 test case fails on any test environment | ✅ Required — hard gate |
| All P1 test cases pass or have documented waivers | ⚠️ Required with exceptions |
| No unhandled exceptions in install log | ✅ Required |
| Rollback confirmed reversible on all ENV-0x | ✅ Required |

---

## 11. Release Checklist

### 11.1 Pre-Build

- [ ] All P0 assets verified (OEM BMP 120×120, wallpapers 4K JPEG)
- [ ] All registry values reviewed and validated against Win10 22H2 and Win11 23H2
- [ ] All scripts reviewed for idempotency
- [ ] `UserPreferencesMask` binary value validated on both OS versions
- [ ] Rollback script tested against fresh install
- [ ] Version number set to `0.1.0` in playbook manifest
- [ ] Playbook metadata complete (name, description, author, version, minOS, targetOS)

### 11.2 Build

- [ ] `.apbx` file built from finalized playbook source
- [ ] `.apbx` file integrity verified (SHA256 checksum generated)
- [ ] `.apbx` file tested in AME Wizard v1.0.0 (parse validation)
- [ ] `.apbx` file size < 50 MB

### 11.3 QA Gate

- [ ] All P0 test cases passed (see §10.2)
- [ ] All P0 test cases passed on physical hardware
- [ ] Rollback confirmed clean on all test environments
- [ ] Install log reviewed — zero unhandled exceptions
- [ ] Visual QA complete — OEM logo, wallpapers, dark theme, transparency

### 11.4 Release

- [ ] `CHANGELOG.md` entry for v0.1.0 written
- [ ] `releases/manifests/v0.1.0.json` created
- [ ] `releases/manifests/latest.json` updated to v0.1.0
- [ ] GitHub Release draft created with tag `v0.1.0`
- [ ] Release assets attached:
  - [ ] `ArizenOS-v0.1.0.apbx`
  - [ ] `ArizenOS-v0.1.0.apbx.sha256`
- [ ] Release notes written (user-facing language, not internal spec)
- [ ] GitHub Release published

### 11.5 Post-Release

- [ ] SHA256 checksum verified against published artifact
- [ ] Download and apply tested from the GitHub Release URL
- [ ] GitHub Discussions announcement posted
- [ ] `docs/roadmap/v0.1.0.md` marked complete
- [ ] v0.2.0 roadmap issue created

---

## Appendix A — Manifest Schema

The installation manifest written to `%ProgramData%\ArizenOS\manifest.json`:

```json
{
  "$schema": "https://arizenos.dev/schemas/manifest/v1.json",
  "product": "ArizenOS",
  "version": "0.1.0",
  "installed_at": "2026-06-02T00:00:00Z",
  "installed_by": "AME Wizard",
  "features_applied": [
    "oem-branding",
    "wallpaper-dark",
    "wallpaper-lockscreen",
    "theme-dark",
    "transparency",
    "performance-tweaks",
    "developer-setup"
  ],
  "backup_path": "%APPDATA%\\ArizenOS\\backup",
  "rollback_available": true,
  "rollback_version": "0.1.0"
}
```

---

## Appendix B — Open Issues for v0.1

| ID | Issue | Severity | Owner |
|---|---|---|---|
| OI-01 | OEM logo BMP not yet validated at 120×120px | P0 Blocker | Design team |
| OI-02 | `UserPreferencesMask` binary value not yet validated on Win10 22H2 | P0 Blocker | Engineering |
| OI-03 | Lock screen registry keys differ between Win10 and Win11 — dual-path needed | P0 Blocker | Engineering |
| OI-04 | DWM acrylic transparency behavior on Win10 is different from Win11 | P1 | Engineering |
| OI-05 | Physical hardware test environment not yet provisioned | P0 Blocker | QA |

---

*ArizenOS v0.1 Product Specification — Revision 1*  
*Approved by: Technical Council*  
*Next review: Before build handoff*
