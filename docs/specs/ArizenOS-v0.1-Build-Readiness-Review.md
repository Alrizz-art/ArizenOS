# ArizenOS v0.1 — Build Readiness Review (BRR)

**Document Type**: Build Readiness Review  
**Version**: v0.1.0  
**Status**: OPEN — Blockers Outstanding  
**Date**: 2026-06-02  
**Author**: Engineering · QA · Release Management  
**Reference Spec**: `docs/specs/ArizenOS-v0.1-Product-Specification.md`

---

> **Definition**: A Build Readiness Review is a formal gate assessment conducted before the first production build of a release artifact. The BRR confirms that every known blocker has been resolved, every asset has been validated, and every test environment is ready. No `.apbx` is generated until this document reaches **GO** status across all sections.

---

## Table of Contents

1. [BRR Status Dashboard](#1-brr-status-dashboard)
2. [Blocker Resolution Plan](#2-blocker-resolution-plan)
3. [Branding Asset Validation Checklist](#3-branding-asset-validation-checklist)
4. [Registry Validation Checklist](#4-registry-validation-checklist)
5. [Windows 10 Compatibility Matrix](#5-windows-10-compatibility-matrix)
6. [Windows 11 Compatibility Matrix](#6-windows-11-compatibility-matrix)
7. [VM Test Plan](#7-vm-test-plan)
8. [Physical Hardware Test Plan](#8-physical-hardware-test-plan)
9. [Release Gate Criteria](#9-release-gate-criteria)
10. [Go / No-Go Decision Framework](#10-go--no-go-decision-framework)
11. [Pre-Build Signoff Requirements](#11-pre-build-signoff-requirements)

---

## 1. BRR Status Dashboard

Current state at document creation. Updated by the responsible owner when each item is resolved.

| ID | Blocker / Gate | Owner | Status | Due |
|---|---|---|---|---|
| OI-01 | OEM BMP validated at 120×120px, 24-bit | Design | 🔴 OPEN | Pre-build |
| OI-02 | `UserPreferencesMask` validated on Win10 + Win11 | Engineering | 🔴 OPEN | Pre-build |
| OI-03 | Lock screen dual-path (Win10 vs Win11) resolved | Engineering | 🔴 OPEN | Pre-build |
| OI-05 | Physical hardware test environment provisioned | QA | 🔴 OPEN | Pre-QA gate |
| BRR-01 | All registry values validated in isolated VM | Engineering | 🔴 OPEN | Pre-build |
| BRR-02 | All assets validated against spec dimensions | Design | 🔴 OPEN | Pre-build |
| BRR-03 | VM test environments provisioned | QA | 🔴 OPEN | Pre-test |
| BRR-04 | Rollback script validated on all target OS versions | Engineering | 🔴 OPEN | Pre-QA gate |
| BRR-05 | Release gate criteria reviewed and signed off | Release Mgmt | 🔴 OPEN | Pre-release |

**Current BRR Decision: 🔴 NO-GO**  
Zero items resolved. Build must not proceed until §10 reaches GO.

---

## 2. Blocker Resolution Plan

### OI-01 — OEM BMP Validation

**Problem**: The OEM manufacturer logo (`arizenOS_logo_oem.bmp`) has not been confirmed to meet Windows OEM branding requirements. An incorrectly formatted BMP causes the logo to appear broken, distorted, or missing in System Properties on some DPI configurations.

**Root Cause**: Windows OEM logo rendering uses a legacy code path from the Win32 `SystemPropertiesPage` that expects a very specific BMP format. Common failures include wrong bit depth, incorrect header, or dimensions outside the expected 120×120px boundary.

**Resolution Steps**:

| Step | Action | Owner | Done? |
|---|---|---|---|
| R01-1 | Open `arizenOS_logo_oem.bmp` in a hex editor or image inspector and confirm: file header `BM` (bytes 0-1), DIB header size 40 bytes (BITMAPINFOHEADER), bit depth = 24 (0x18) | Design | ⬜ |
| R01-2 | Confirm image dimensions: width = 120px (offset 18, little-endian DWORD), height = 120px (offset 22) | Design | ⬜ |
| R01-3 | Confirm no ICC color profile is embedded (Windows OEM logo renderer does not support embedded profiles) | Design | ⬜ |
| R01-4 | Deploy to test VM, place at `C:\ProgramData\ArizenOS\branding\oemlogo.bmp`, write registry key `HKLM\...\OEMInformation\Logo` pointing to that path | Engineering | ⬜ |
| R01-5 | Open `sysdm.cpl` (System Properties → Computer Name tab area, or via `About` page) and visually confirm logo renders | QA | ⬜ |
| R01-6 | Repeat R01-4 and R01-5 on: Win10 22H2 VM, Win11 23H2 VM, Win10 physical machine at 100% DPI, Win10 at 125% DPI, Win11 at 150% DPI | QA | ⬜ |
| R01-7 | If logo fails at any DPI: export a new 120×120 BMP with white or transparent background matching `#1E1E1E` (dark system background), re-test | Design | ⬜ |
| R01-8 | Mark OI-01 resolved, update dashboard | Design Lead | ⬜ |

**Acceptance Criteria**: Logo renders without distortion or missing pixels on Win10 22H2 and Win11 23H2 at 100%, 125%, and 150% DPI in System Properties.

---

### OI-02 — UserPreferencesMask Binary Validation

**Problem**: The `UserPreferencesMask` registry value at `HKCU\Control Panel\Desktop` is a binary (REG_BINARY) bitmask that controls all Windows visual effects simultaneously. The exact byte sequence varies between Windows 10 and Windows 11 and must be validated before being hardcoded in the playbook.

**Root Cause**: The bitmask is an 8-byte (64-bit) value where each bit controls one visual effect. Microsoft has never fully documented all bit positions. Incorrect values can disable critical UI effects (window animations, font smoothing) or enable unintended ones.

**Target Effect Profile** (from spec §9.4):

| Effect | Target State |
|---|---|
| Animate windows when minimizing/maximizing | ✅ ON |
| Smooth edges of screen fonts | ✅ ON |
| Show thumbnails instead of icons | ✅ ON |
| Show translucent selection rectangle | ✅ ON |
| Animate controls inside windows | ❌ OFF |
| Fade/slide menus into view | ❌ OFF |
| Fade out menu items after clicking | ❌ OFF |
| Show shadows under windows | ✅ ON |
| Show shadows under mouse pointer | ✅ ON |

**Resolution Steps**:

| Step | Action | Owner | Done? |
|---|---|---|---|
| R02-1 | On a clean Win10 22H2 VM: open System Properties → Advanced → Performance Settings → Custom. Apply the exact target effect profile above. Click OK. | Engineering | ⬜ |
| R02-2 | Export the resulting `UserPreferencesMask` value: `reg export "HKCU\Control Panel\Desktop" C:\mask_win10.reg`. Record the exact hex bytes. | Engineering | ⬜ |
| R02-3 | Repeat R02-1 and R02-2 on a clean Win11 23H2 VM. Record as mask_win11. | Engineering | ⬜ |
| R02-4 | Repeat R02-1 and R02-2 on a clean Win11 24H2 VM. Record as mask_win11_24h2. | Engineering | ⬜ |
| R02-5 | Compare all three values. If identical: one value works for all. If different: the playbook script must detect OS version and apply the correct mask (see OI-03 pattern for dual-path logic). | Engineering | ⬜ |
| R02-6 | Write the validated hex values to this document (§4.3) before marking resolved. | Engineering | ⬜ |
| R02-7 | Validate by re-applying the mask via registry write on a fresh VM and confirming the Performance Settings UI shows the correct checkboxes | QA | ⬜ |
| R02-8 | Mark OI-02 resolved, update dashboard | Engineering Lead | ⬜ |

**Acceptance Criteria**: Exact byte sequence recorded for Win10 22H2, Win11 23H2, and Win11 24H2. Applying the byte sequence via `reg add` produces the correct visual effects profile confirmed in the Performance Settings UI.

---

### OI-03 — Lock Screen Dual-Path (Win10 vs Win11)

**Problem**: The registry path for setting a custom lock screen wallpaper is different on Windows 10 and Windows 11. Using only the Win11 path on Win10 (or vice versa) results in the lock screen not being changed.

**Root Cause**: Windows 10 uses `HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization` with `LockScreenImage`. Windows 11 introduced `PersonalizationCSP` (`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP`) as the primary path. Both may need to be set depending on OS version.

**Resolution Steps**:

| Step | Action | Owner | Done? |
|---|---|---|---|
| R03-1 | On clean Win10 22H2 VM: deploy wallpaper file to `C:\ProgramData\ArizenOS\wallpapers\arizenOS_lockscreen.jpg` | Engineering | ⬜ |
| R03-2 | Write ONLY the Win10 policy path (`HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization\LockScreenImage`). Lock the workstation (Win+L). Confirm lock screen changes. | Engineering | ⬜ |
| R03-3 | Revert, then write ONLY the PersonalizationCSP path. Confirm result (expected: may not work on Win10). | Engineering | ⬜ |
| R03-4 | Document which paths work on Win10 22H2. | Engineering | ⬜ |
| R03-5 | Repeat R03-1 through R03-4 on Win11 23H2 VM. Document which paths work. | Engineering | ⬜ |
| R03-6 | Repeat R03-1 through R03-4 on Win11 24H2 VM. | Engineering | ⬜ |
| R03-7 | Based on results, define the dual-path strategy: | Engineering | ⬜ |
|   | **Option A**: Write both paths on all OS versions (safe, both are harmless if not consumed) | | |
|   | **Option B**: Script detects OS build number and writes only the correct path | | |
|   | **Recommended**: Option A — write both paths. It is non-destructive and avoids version detection logic. | | |
| R03-8 | Validate Option A on all three OS versions. Confirm lock screen applies in all cases. | QA | ⬜ |
| R03-9 | Write final registry table (both paths, all OS) to §4.4 before marking resolved. | Engineering | ⬜ |
| R03-10 | Mark OI-03 resolved, update dashboard | Engineering Lead | ⬜ |

**Acceptance Criteria**: Lock screen wallpaper applies correctly on Win10 22H2, Win11 23H2, and Win11 24H2 using a single strategy (no version branching required unless Option B is selected with full justification).

---

### OI-05 — Physical Hardware Test Environment

**Problem**: All current testing is VM-only. Physical hardware is required because: (1) DPI scaling behavior on real displays differs from VM, (2) GPU driver paths for DWM transparency/acrylic differ from virtualized graphics, (3) OEM logo rendering in System Properties uses GDI which can behave differently on real hardware.

**Resolution Steps**:

| Step | Action | Owner | Done? |
|---|---|---|---|
| R05-1 | Provision at least one physical x64 machine running Windows 10 22H2 (clean install, no customization) | QA | ⬜ |
| R05-2 | Provision at least one physical x64 machine running Windows 11 23H2 or 24H2 (clean install) | QA | ⬜ |
| R05-3 | Document hardware specs for both machines: CPU, GPU, RAM, display resolution and DPI, Windows build | QA | ⬜ |
| R05-4 | Confirm AME Wizard can be installed and run on both machines | QA | ⬜ |
| R05-5 | Confirm machines are NOT domain-joined | QA | ⬜ |
| R05-6 | Confirm Secure Boot and TPM status documented (not required off, just documented) | QA | ⬜ |
| R05-7 | Mark physical machines as available in §8 (Physical Hardware Test Plan) | QA Lead | ⬜ |
| R05-8 | Mark OI-05 resolved, update dashboard | QA Lead | ⬜ |

**Acceptance Criteria**: At least two physical machines (one Win10, one Win11) provisioned, clean, documented, and confirmed capable of running AME Wizard.

---

## 3. Branding Asset Validation Checklist

All assets must pass 100% of checks before build. Failures block the release.

### 3.1 OEM Logo — `arizenOS_logo_oem.bmp`

| Check | Requirement | Method | Status |
|---|---|---|---|
| File exists | `assets/logos/arizenOS_logo_oem.bmp` present in repo | Directory listing | ⬜ |
| File format | BMP (magic bytes: `42 4D` at offset 0) | Hex editor / `file` command | ⬜ |
| DIB header type | BITMAPINFOHEADER (size = 40 at offset 14) | Hex editor | ⬜ |
| Width | 120 pixels (little-endian DWORD at offset 18: `78 00 00 00`) | Hex editor / image inspector | ⬜ |
| Height | 120 pixels (little-endian DWORD at offset 22: `78 00 00 00`) | Hex editor / image inspector | ⬜ |
| Bit depth | 24-bit (value at offset 28: `18 00`) | Hex editor / image inspector | ⬜ |
| Compression | None (BI_RGB = 0 at offset 30) | Hex editor | ⬜ |
| No embedded ICC profile | Profile data offset (offset 50) = 0 | Hex editor | ⬜ |
| File size | ≤ 256 KB | File properties | ⬜ |
| Visual render — Win10 VM | Logo visible, correct proportions in `sysdm.cpl` | Manual QA | ⬜ |
| Visual render — Win11 VM | Logo visible, correct proportions in Settings → About | Manual QA | ⬜ |
| Visual render — 100% DPI | No distortion | Physical machine | ⬜ |
| Visual render — 125% DPI | No blurring or clipping | Physical machine | ⬜ |
| Visual render — 150% DPI | No blurring or clipping | Physical machine | ⬜ |

### 3.2 Desktop Wallpaper Dark — `arizenOS_dark.jpg`

| Check | Requirement | Method | Status |
|---|---|---|---|
| File exists | `assets/wallpapers/arizenOS_dark.jpg` present | Directory listing | ⬜ |
| Format | JPEG (magic bytes: `FF D8 FF`) | Hex editor / `file` command | ⬜ |
| Width | 3840 pixels | Image inspector (exiftool / Photoshop) | ⬜ |
| Height | 2160 pixels | Image inspector | ⬜ |
| Aspect ratio | 16:9 (3840/2160 = 1.777…) | Calculated | ⬜ |
| Color space | sRGB | Image inspector (EXIF/ICC) | ⬜ |
| JPEG quality | ≥ Q90 (visual artifact check) | Image inspector / eye test | ⬜ |
| File size | ≤ 8 MB | File properties | ⬜ |
| Visual render — 1080p | No visible compression artifacts | Physical display | ⬜ |
| Visual render — 4K | Crisp, fills screen | Physical display | ⬜ |
| Content appropriateness | No text that will conflict with desktop icons | Visual review | ⬜ |
| Brand consistency | Uses ArizenOS color palette and identity | Design review | ⬜ |

### 3.3 Desktop Wallpaper Default — `arizenOS_default.jpg`

| Check | Requirement | Method | Status |
|---|---|---|---|
| File exists | `assets/wallpapers/arizenOS_default.jpg` present | Directory listing | ⬜ |
| Format | JPEG | `file` command | ⬜ |
| Dimensions | 3840 × 2160 | Image inspector | ⬜ |
| Aspect ratio | 16:9 | Calculated | ⬜ |
| Color space | sRGB | Image inspector | ⬜ |
| JPEG quality | ≥ Q90 | Image inspector | ⬜ |
| File size | ≤ 8 MB | File properties | ⬜ |
| Visually distinct from dark variant | Not identical, serves as light mode alternative | Visual review | ⬜ |
| Brand consistency | Consistent with dark variant | Design review | ⬜ |

### 3.4 Lock Screen Wallpaper — `arizenOS_lockscreen.jpg`

| Check | Requirement | Method | Status |
|---|---|---|---|
| File exists | `assets/wallpapers/arizenOS_lockscreen.jpg` present | Directory listing | ⬜ |
| Format | JPEG | `file` command | ⬜ |
| Dimensions | 3840 × 2160 | Image inspector | ⬜ |
| Aspect ratio | 16:9 | Calculated | ⬜ |
| Color space | sRGB | Image inspector | ⬜ |
| JPEG quality | ≥ Q90 | Image inspector | ⬜ |
| File size | ≤ 8 MB | File properties | ⬜ |
| Lock screen composition check | No important visual elements in bottom-left corner (clock overlays this area) | Visual review | ⬜ |
| Lock screen composition check | No important visual elements in top-right corner (network/battery status overlays) | Visual review | ⬜ |
| Visual render — Win10 lock screen | Image fills screen correctly, no letterboxing | VM test | ⬜ |
| Visual render — Win11 lock screen | Image fills screen correctly, no letterboxing | VM test | ⬜ |
| Brand consistency | More minimal than desktop wallpaper — appropriate for first-boot impression | Design review | ⬜ |

---

## 4. Registry Validation Checklist

All registry values must be validated by manually applying them to an isolated VM and confirming the intended behavior. Validation is not complete until the "Confirmed on" column shows both Win10 and Win11.

### 4.1 OEM Branding Keys

**Hive**: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation`

| Value | Type | Expected Data | Confirmed Win10 | Confirmed Win11 |
|---|---|---|---|---|
| `Manufacturer` | REG_SZ | `ArizenOS` | ⬜ | ⬜ |
| `Model` | REG_SZ | `ArizenOS Experience Layer v0.1` | ⬜ | ⬜ |
| `SupportURL` | REG_SZ | `https://github.com/Alrizz-art/ArizenOS` | ⬜ | ⬜ |
| `Logo` | REG_SZ | Full expanded path to oemlogo.bmp | ⬜ | ⬜ |

**Verification method**: After writing keys, open `sysdm.cpl` (Win10) or Settings → System → About (Win11). Confirm Manufacturer, Model, Support Link, and logo are all visible and correct.

### 4.2 Theme Keys

**Hive**: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize`

| Value | Type | Data | Effect | Confirmed Win10 | Confirmed Win11 |
|---|---|---|---|---|---|
| `AppsUseLightTheme` | REG_DWORD | `0` | Apps in dark mode | ⬜ | ⬜ |
| `SystemUsesLightTheme` | REG_DWORD | `0` | Taskbar/Start dark | ⬜ | ⬜ |
| `EnableTransparency` | REG_DWORD | `1` | Transparency on | ⬜ | ⬜ |
| `ColorPrevalence` | REG_DWORD | `0` | No accent on taskbar | ⬜ | ⬜ |

**Verification method**: After writing, check Settings → Personalization → Colors. Confirm "Dark" is selected for both Windows mode and App mode. Confirm transparency toggle is on. Confirm taskbar color does not show accent.

### 4.3 UserPreferencesMask — PENDING VALIDATION

> **⚠️ BLOCKER (OI-02)**: The exact byte values below are PLACEHOLDERS. They must not be used in the playbook until R02-6 is completed and real values are substituted.

| OS Version | Placeholder Value | Validated Value | Confirmed |
|---|---|---|---|
| Windows 10 22H2 | `[TBD — see R02-2]` | | ⬜ |
| Windows 11 23H2 | `[TBD — see R02-3]` | | ⬜ |
| Windows 11 24H2 | `[TBD — see R02-4]` | | ⬜ |

> This table must be completed by Engineering (OI-02 resolution) before the playbook can be written. The responsible engineer must edit this document and replace `[TBD]` with the real hex byte sequences.

### 4.4 Lock Screen Keys — PENDING VALIDATION

> **⚠️ BLOCKER (OI-03)**: The effective path combination below is UNCONFIRMED. Must be validated per R03-8.

**Proposed strategy**: Write both paths on all OS versions (Option A from OI-03 resolution plan).

**Path 1** — `HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization`

| Value | Type | Data | Works Win10 | Works Win11 |
|---|---|---|---|---|
| `LockScreenImage` | REG_SZ | Full path to lockscreen.jpg | ⬜ | ⬜ |
| `LockScreenOverlaysDisabled` | REG_DWORD | `1` | ⬜ | ⬜ |

**Path 2** — `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP`

| Value | Type | Data | Works Win10 | Works Win11 |
|---|---|---|---|---|
| `LockScreenImagePath` | REG_SZ | Full path to lockscreen.jpg | ⬜ | ⬜ |
| `LockScreenImageUrl` | REG_SZ | Full path to lockscreen.jpg | ⬜ | ⬜ |
| `LockScreenImageStatus` | REG_DWORD | `1` | ⬜ | ⬜ |

**Verification method**: After writing both path sets, run `gpupdate /force`, then lock the workstation (Win+L). Confirm lock screen shows ArizenOS wallpaper.

### 4.5 DWM / Transparency Keys

**Hive**: `HKCU\SOFTWARE\Microsoft\Windows\DWM`

| Value | Type | Data | Confirmed Win10 | Confirmed Win11 |
|---|---|---|---|---|
| `EnableAeroPeek` | REG_DWORD | `1` | ⬜ | ⬜ |
| `AlwaysHibernateThumbnails` | REG_DWORD | `0` | ⬜ | ⬜ |
| `Composition` | REG_DWORD | `1` | ⬜ | ⬜ |
| `ColorPrevalence` | REG_DWORD | `0` | ⬜ | ⬜ |

**Verification method**: After writing, hover over taskbar items to confirm Aero Peek thumbnails appear. Confirm title bars do not show accent color.

### 4.6 Developer Setup Keys (Optional — validate even though optional)

**Hive**: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock`

| Value | Type | Data | Confirmed Win10 | Confirmed Win11 |
|---|---|---|---|---|
| `AllowDevelopmentWithoutDevLicense` | REG_DWORD | `1` | ⬜ | ⬜ |
| `AllowAllTrustedApps` | REG_DWORD | `1` | ⬜ | ⬜ |

**Hive**: `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`

| Value | Type | Data | Confirmed Win10 | Confirmed Win11 |
|---|---|---|---|---|
| `LongPathsEnabled` | REG_DWORD | `1` | ⬜ | ⬜ |

**Verification method**: After Developer Mode keys: confirm Settings → Privacy & Security → For Developers shows Developer Mode as ON. After LongPathsEnabled: confirm via `(Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem").LongPathsEnabled` = 1.

---

## 5. Windows 10 Compatibility Matrix

Reference OS: **Windows 10 22H2, Build 19045**

### 5.1 Feature Compatibility

| Feature | Win10 22H2 | Win10 21H2 | Notes |
|---|---|---|---|
| OEM Branding (sysdm.cpl) | ✅ Confirmed | ✅ Confirmed | Legacy path, unchanged since Win7 |
| OEM Logo rendering | ⬜ Pending | ⬜ Pending | Pending OI-01 resolution |
| Desktop wallpaper registry | ✅ Expected | ✅ Expected | Standard since Win7 |
| Dark theme (apps) | ✅ Expected | ✅ Expected | Available since Win10 1809 |
| Dark theme (system/taskbar) | ✅ Expected | ✅ Expected | Available since Win10 1903 |
| Taskbar transparency (acrylic) | ⬜ Pending validation | ⬜ Pending | Behavior differs from Win11 |
| Start menu transparency | ⬜ Pending validation | ⬜ Pending | Win10 Start is different from Win11 |
| Lock screen (Policies path) | ⬜ Pending OI-03 | ⬜ Pending | Primary path for Win10 |
| Lock screen (PersonalizationCSP) | ⬜ Pending OI-03 | ⬜ Pending | May not apply on Win10 |
| UserPreferencesMask | ⬜ Pending OI-02 | ⬜ Pending | Requires validated byte sequence |
| Prefetch registry keys | ✅ Expected | ✅ Expected | Standard since Win7 |
| Developer Mode registry | ✅ Expected | ✅ Expected | Available since Win10 1607 |
| LongPathsEnabled | ✅ Expected | ✅ Expected | Available since Win10 1607 |
| Rollback (registry restore) | ✅ Expected | ✅ Expected | Standard `reg import` |
| Rollback (restore point) | ✅ Expected | ✅ Expected | Standard System Restore |

### 5.2 Win10-Specific Known Behaviors

| Behavior | Impact | Mitigation |
|---|---|---|
| Start menu uses older acrylic renderer | Transparency may appear slightly different | Cosmetic only — no mitigation needed |
| Settings app "About" page layout differs | OEM info shows in different location than Win11 | Document in release notes |
| `PersonalizationCSP` key may not exist by default | Key creation required, not just value write | Script must create key if absent |
| Taskbar acrylic requires specific DWM + Themes combo | Transparency may not apply without restart | Post-install restart required |
| Windows 10 S Mode blocks all registry writes | Playbook aborts in preflight | Covered by SCR-01 |

### 5.3 Win10 Build Compatibility Notes

| Build | Version | Status | Notes |
|---|---|---|---|
| 19045 | 22H2 | ✅ Primary target | All features expected |
| 19044 | 21H2 | ⚠️ Best-effort | OEM branding and wallpaper expected; transparency not guaranteed |
| 19043 | 21H1 | ❌ Below minimum | Playbook aborts in preflight |
| 17763 | 1809 | ❌ Unsupported | Dark mode not available system-wide |

---

## 6. Windows 11 Compatibility Matrix

Reference OS: **Windows 11 23H2, Build 22631**

### 6.1 Feature Compatibility

| Feature | Win11 23H2 | Win11 24H2 | Notes |
|---|---|---|---|
| OEM Branding (Settings → About) | ✅ Confirmed | ✅ Expected | Path moved from sysdm.cpl to Settings |
| OEM Logo rendering | ⬜ Pending | ⬜ Pending | Must verify in Settings → System → About |
| Desktop wallpaper registry | ✅ Expected | ✅ Expected | Same path as Win10 |
| Dark theme (apps) | ✅ Expected | ✅ Expected | Same path as Win10 |
| Dark theme (system) | ✅ Expected | ✅ Expected | Same path as Win10 |
| Taskbar transparency (acrylic) | ✅ Expected | ✅ Expected | Enhanced in Win11 |
| Start menu transparency | ✅ Expected | ✅ Expected | Win11 Start natively supports acrylic |
| Lock screen (PersonalizationCSP) | ⬜ Pending OI-03 | ⬜ Pending | Primary path for Win11 |
| Lock screen (Policies path) | ⬜ Pending OI-03 | ⬜ Pending | Secondary/fallback |
| UserPreferencesMask | ⬜ Pending OI-02 | ⬜ Pending | Requires validated byte sequence |
| Rounded corners (Win11) | ✅ Unaffected | ✅ Unaffected | ArizenOS does not modify corner radius |
| Snap layouts | ✅ Unaffected | ✅ Unaffected | Not modified |
| Prefetch registry keys | ✅ Expected | ✅ Expected | Same as Win10 |
| Developer Mode registry | ✅ Expected | ✅ Expected | Same path |
| LongPathsEnabled | ✅ Expected | ✅ Expected | Same path |

### 6.2 Win11-Specific Known Behaviors

| Behavior | Impact | Mitigation |
|---|---|---|
| OEM info shows in Settings → System → About (not sysdm.cpl) | Different visual from Win10 — but registry path is identical | No mitigation needed; document in release notes |
| Win11 24H2 Copilot+ changes taskbar behavior | Transparency behavior may differ on Copilot+ devices | Test on standard non-Copilot+ hardware first |
| Win11 Start menu is different from Win10 | Transparency applies differently | May require different DWM tweaks — pending testing |
| Win11 requires TPM 2.0 (clean install) | Our playbook does not touch TPM | No impact |
| Mica/Acrylic/Blur materials are natively supported in Win11 | ArizenOS transparency settings align with native Win11 design language | Positive compatibility |

### 6.3 Win11 Build Compatibility Notes

| Build | Version | Status | Notes |
|---|---|---|---|
| 26100 | 24H2 | ✅ Full support | All features expected |
| 22631 | 23H2 | ✅ Primary target | All features expected |
| 22621 | 22H2 | ⚠️ Best-effort | Expected to work, not in test matrix |
| 22000 | 21H2 (initial) | ❌ Below preferred minimum | Dark mode and transparency may behave differently |

---

## 7. VM Test Plan

### 7.1 VM Environment Specifications

All VMs must be **clean installs** with no additional software beyond AME Wizard and a snapshot taken before each test run.

| ENV-ID | OS | Build | VM Platform | RAM | Storage | GPU | Snapshot |
|---|---|---|---|---|---|---|---|
| ENV-01 | Windows 10 22H2 | 19045 | Hyper-V or VMware | 4 GB | 60 GB | Software/Virtual | ⬜ Pending |
| ENV-02 | Windows 11 23H2 | 22631 | Hyper-V or VMware | 4 GB | 60 GB | Software/Virtual | ⬜ Pending |
| ENV-03 | Windows 11 24H2 | 26100 | Hyper-V or VMware | 4 GB | 60 GB | Software/Virtual | ⬜ Pending |
| ENV-06 | Windows 10 S Mode | Any | Hyper-V | 4 GB | 60 GB | Software/Virtual | ⬜ Pending |

### 7.2 VM Provisioning Steps

For each VM listed above:

| Step | Action | Done? |
|---|---|---|
| VP-1 | Install Windows (clean) from official ISO | ⬜ |
| VP-2 | Apply all Windows Updates to latest patch level | ⬜ |
| VP-3 | Install AME Wizard (latest version) | ⬜ |
| VP-4 | Create snapshot: `"Clean — Pre-ArizenOS"` | ⬜ |
| VP-5 | Disable automatic updates during testing (to prevent mid-test changes) | ⬜ |
| VP-6 | Set display resolution to 1920×1080 (for consistent screenshot comparison) | ⬜ |
| VP-7 | Set DPI to 100% for baseline tests | ⬜ |
| VP-8 | Confirm no prior ArizenOS installation or registry keys present | ⬜ |
| VP-9 | Document VM host specs (CPU, RAM, storage) | ⬜ |

### 7.3 VM Test Execution Protocol

For each test run:

1. **Restore** to the `"Clean — Pre-ArizenOS"` snapshot
2. **Copy** the `ArizenOS.apbx` and all asset files to the VM
3. **Launch** AME Wizard as Administrator
4. **Load** the playbook and proceed through the UX flow
5. **Record** each test case result (PASS / FAIL / BLOCKED)
6. **Capture** screenshots for visual test cases
7. **Export** install log (`%APPDATA%\ArizenOS\logs\install.log`)
8. **Attach** log and screenshots to the test run report

### 7.4 VM Test Case Assignment

| Test Group | ENV-01 (Win10) | ENV-02 (Win11 23H2) | ENV-03 (Win11 24H2) | ENV-06 (S Mode) |
|---|---|---|---|---|
| Group A — Preflight | ✅ Required | ✅ Required | ✅ Required | ✅ Required |
| Group B — Installation | ✅ Required | ✅ Required | ✅ Required | N/A (aborts) |
| Group C — Rollback | ✅ Required | ✅ Required | ⚠️ Best-effort | N/A |
| Group D — Idempotency | ✅ Required | ✅ Required | ⚠️ Best-effort | N/A |
| Group E — Visual QA | ✅ Screenshots only | ✅ Screenshots only | ✅ Screenshots only | N/A |

---

## 8. Physical Hardware Test Plan

### 8.1 Hardware Requirements

> **OI-05 must be resolved before this section can be executed.**

| ENV-ID | OS | Type | Required Specs | Purpose |
|---|---|---|---|---|
| ENV-04 | Windows 10 22H2 | Physical desktop or laptop | x64 CPU, real GPU, 1080p+ display | DPI/transparency validation |
| ENV-05 | Windows 11 23H2 or 24H2 | Physical desktop or laptop | x64 CPU, real GPU, 1080p+ display | DPI/transparency validation |

### 8.2 Hardware Machine Documentation Template

For each physical machine, record before testing:

```
Machine ID: ENV-04 / ENV-05
OS: 
OS Build: 
CPU: 
GPU: 
GPU Driver version: 
RAM: 
Display resolution: 
Display DPI setting: 
Windows activation status: 
Domain-joined: Yes / No
TPM version: 
Secure Boot: Enabled / Disabled
AME Wizard version installed: 
Snapshot/backup method: (Macrium, Acronis, WIM image, etc.)
Pre-test image taken: Yes / No
```

### 8.3 Physical Hardware Test Cases

These tests supplement VM tests and focus specifically on behaviors that require real hardware.

| TC-ID | Test Case | ENV | Priority |
|---|---|---|---|
| PHY-01 | OEM logo renders correctly at 100% DPI in System Properties | ENV-04 | ✅ P0 |
| PHY-02 | OEM logo renders correctly at 125% DPI | ENV-04, ENV-05 | ⚠️ P1 |
| PHY-03 | OEM logo renders correctly at 150% DPI | ENV-05 | ⚠️ P1 |
| PHY-04 | Taskbar acrylic transparency visible (not just flat dark) | ENV-04, ENV-05 | ⚠️ P1 |
| PHY-05 | Wallpaper renders at full resolution — no upscaling artifacts | ENV-04, ENV-05 | ✅ P0 |
| PHY-06 | Lock screen displays ArizenOS wallpaper (not Windows Spotlight) | ENV-04, ENV-05 | ✅ P0 |
| PHY-07 | Full installation completes without GPU-related errors in install log | ENV-04, ENV-05 | ✅ P0 |
| PHY-08 | Rollback completes cleanly on physical hardware | ENV-04 | ✅ P0 |
| PHY-09 | No system instability (BSODs, crashes) after 30-minute normal use post-install | ENV-04, ENV-05 | ✅ P0 |
| PHY-10 | Windows Update still functional after install | ENV-04 | ✅ P0 |
| PHY-11 | Windows Defender still active after install | ENV-04 | ✅ P0 |

### 8.4 Physical Test Pass/Fail Criteria

| Criterion | Required |
|---|---|
| PHY-01 through PHY-09 all PASS on ENV-04 | ✅ P0 gate — blocks release if any fail |
| PHY-01, PHY-05, PHY-06 PASS on ENV-05 | ✅ P0 gate |
| PHY-10 and PHY-11 PASS on ENV-04 | ✅ P0 gate — confirms non-destructive claim |

---

## 9. Release Gate Criteria

These are the objective, binary criteria evaluated at the Go/No-Go meeting. Each item is PASS or FAIL — no partial credit.

### Gate 1 — Blocker Resolution Gate

| Criterion | Status |
|---|---|
| OI-01 OEM BMP validated and confirmed | ⬜ OPEN |
| OI-02 UserPreferencesMask values recorded for all target OS versions | ⬜ OPEN |
| OI-03 Lock screen dual-path resolved and validated | ⬜ OPEN |
| OI-05 Physical hardware environments provisioned and documented | ⬜ OPEN |
| Zero additional P0 blockers open | ⬜ OPEN |

**Gate 1 passes when**: All five rows above are checked GREEN.

### Gate 2 — Asset Validation Gate

| Criterion | Status |
|---|---|
| OEM logo: 120×120px, 24-bit BMP, confirmed renders on Win10 and Win11 | ⬜ OPEN |
| Desktop wallpaper (dark): 3840×2160, sRGB, ≤ 8 MB | ⬜ OPEN |
| Desktop wallpaper (default): 3840×2160, sRGB, ≤ 8 MB | ⬜ OPEN |
| Lock screen: 3840×2160, sRGB, ≤ 8 MB, composition validated | ⬜ OPEN |
| All asset validation checklists (§3) fully checked | ⬜ OPEN |

**Gate 2 passes when**: All five rows above are checked GREEN.

### Gate 3 — Registry Validation Gate

| Criterion | Status |
|---|---|
| All OEM branding keys confirmed on Win10 and Win11 | ⬜ OPEN |
| All theme keys confirmed on Win10 and Win11 | ⬜ OPEN |
| UserPreferencesMask byte sequences recorded (OI-02) | ⬜ OPEN |
| Lock screen registry paths confirmed (OI-03) | ⬜ OPEN |
| All DWM keys confirmed on Win10 and Win11 | ⬜ OPEN |
| All developer setup keys confirmed on Win10 and Win11 | ⬜ OPEN |

**Gate 3 passes when**: All six rows above are checked GREEN.

### Gate 4 — VM Testing Gate

| Criterion | Status |
|---|---|
| All 4 VM environments provisioned with clean snapshots | ⬜ OPEN |
| All P0 test cases PASS on ENV-01 (Win10 22H2) | ⬜ OPEN |
| All P0 test cases PASS on ENV-02 (Win11 23H2) | ⬜ OPEN |
| All P0 test cases PASS on ENV-03 (Win11 24H2) | ⬜ OPEN |
| S Mode abort test PASS on ENV-06 | ⬜ OPEN |
| Zero unhandled exceptions in install logs across all VM runs | ⬜ OPEN |
| Rollback confirmed clean on ENV-01 and ENV-02 | ⬜ OPEN |

**Gate 4 passes when**: All seven rows above are checked GREEN.

### Gate 5 — Physical Hardware Testing Gate

| Criterion | Status |
|---|---|
| OI-05 resolved (physical machines provisioned) | ⬜ OPEN |
| All P0 physical test cases PASS on ENV-04 | ⬜ OPEN |
| P0 physical test cases PASS on ENV-05 | ⬜ OPEN |
| Windows Defender active post-install (PHY-11) | ⬜ OPEN |
| Windows Update functional post-install (PHY-10) | ⬜ OPEN |

**Gate 5 passes when**: All five rows above are checked GREEN.

### Gate 6 — Release Documentation Gate

| Criterion | Status |
|---|---|
| CHANGELOG.md v0.1.0 entry written | ⬜ OPEN |
| `releases/manifests/v0.1.0.json` created | ⬜ OPEN |
| `releases/manifests/latest.json` updated | ⬜ OPEN |
| User-facing release notes written | ⬜ OPEN |
| All BRR sections updated to reflect resolved blockers | ⬜ OPEN |

**Gate 6 passes when**: All five rows above are checked GREEN.

---

## 10. Go / No-Go Decision Framework

### 10.1 Decision Participants

| Role | Name | Vote Authority |
|---|---|---|
| Release Manager | @Alrizz-art | ✅ Required |
| Engineering Lead | @Alrizz-art | ✅ Required |
| QA Lead | @Alrizz-art | ✅ Required |
| Design Lead | @Alrizz-art | ✅ Required |

*(For a solo maintainer, all roles are held by @Alrizz-art. The decision framework still applies — each domain is reviewed independently against its gate criteria.)*

### 10.2 Decision Logic

```
                    ┌─────────────────────────────┐
                    │   BRR Go/No-Go Evaluation   │
                    └──────────────┬──────────────┘
                                   │
             ┌─────────────────────▼─────────────────────┐
             │        Are ALL 6 Gates PASSED?            │
             └──────────┬────────────────────┬───────────┘
                        │ YES                │ NO
                        ▼                    ▼
             ┌──────────────────┐  ┌─────────────────────────┐
             │  Are any P0 TCs  │  │  Identify failing gate  │
             │  still FAILING?  │  │  Assign owner + due date│
             └─────┬──────┬─────┘  │  Re-schedule evaluation │
                   │ YES  │ NO     └─────────────────────────┘
                   ▼      ▼
             ┌─────────┐ ┌──────────────────────────────┐
             │ NO-GO   │ │  CONDITIONAL GO               │
             │ Blocked │ │  P1/P2 failures only          │
             └─────────┘ │  Document waivers, proceed   │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │       GO       │
                               │  Authorize     │
                               │  .apbx build   │
                               └────────────────┘
```

### 10.3 No-Go Conditions (Absolute)

The following conditions produce an **unconditional NO-GO** — no exceptions:

| Condition | Reason |
|---|---|
| Any P0 test case fails on any target OS | P0 failures are user-facing defects that damage first impressions |
| OEM logo fails to render on Win10 or Win11 | This is the primary branding element |
| Rollback fails on any target OS | Non-reversibility violates the spec's core design philosophy |
| Windows Defender is disabled after install | Violates the "non-destructive" guarantee |
| Windows Update is broken after install | Violates the "non-destructive" guarantee |
| Any unhandled exception causes playbook crash | Instability in the installer undermines trust |
| OI-02 UserPreferencesMask not validated | Unknown byte value could corrupt visual settings |

### 10.4 Conditional Go Conditions (Waivable P1 Failures)

These failures can be waived for v0.1 with documented justification:

| Condition | Waiver Process |
|---|---|
| Transparency at 150% DPI not perfect | Document known issue, fix in v0.1.1 |
| OEM logo slightly blurry at 125% DPI | Document, fix in v0.1.1 |
| Lock screen composition not ideal on 16:10 displays | Document, fix in v0.1.1 |
| Win10 21H2 behavior different from 22H2 | Document as "best-effort" in release notes |

### 10.5 Go Decision Record Template

When all gates pass, the Go decision is recorded as follows:

```markdown
## ArizenOS v0.1.0 — Go/No-Go Decision Record

**Decision**: [ GO | NO-GO | CONDITIONAL GO ]
**Date**: 
**Decided by**: @Alrizz-art

**Gates status at decision time**:
- Gate 1 — Blocker Resolution: [ PASS | FAIL ]
- Gate 2 — Asset Validation:   [ PASS | FAIL ]
- Gate 3 — Registry Validation: [ PASS | FAIL ]
- Gate 4 — VM Testing:         [ PASS | FAIL ]
- Gate 5 — Physical Hardware:  [ PASS | FAIL ]
- Gate 6 — Documentation:      [ PASS | FAIL ]

**Waivers granted** (if CONDITIONAL GO):
- 

**Known issues shipping with v0.1.0**:
- 

**Next action**: Proceed to §11 (Pre-Build Signoff) and generate .apbx
```

---

## 11. Pre-Build Signoff Requirements

**This section defines the exact requirements that must be met before any of the following are generated:**
- Playbook Manifest
- YAML Entries
- Asset Manifest
- Script Manifest
- `ArizenOS.apbx`

### 11.1 Mandatory Pre-Build Requirements

All items below must be TRUE before build authorization is granted.

#### Documentation Complete

- [ ] This BRR document has been fully updated — all `⬜ OPEN` items resolved and confirmed
- [ ] §4.3 UserPreferencesMask table filled with real validated hex values
- [ ] §4.4 Lock screen registry table confirmed with real test results
- [ ] §8.2 physical machine specs documented for ENV-04 and ENV-05
- [ ] Go/No-Go Decision Record (§10.5) filled and signed

#### Assets Ready

- [ ] `arizenOS_logo_oem.bmp` — 120×120px, 24-bit BMP, validated against §3.1
- [ ] `arizenOS_dark.jpg` — 3840×2160, sRGB, ≤ 8 MB, validated against §3.2
- [ ] `arizenOS_default.jpg` — 3840×2160, sRGB, ≤ 8 MB, validated against §3.3
- [ ] `arizenOS_lockscreen.jpg` — 3840×2160, sRGB, ≤ 8 MB, validated against §3.4
- [ ] All 4 assets committed to `main` branch at their specified paths

#### Registry Values Finalized

- [ ] UserPreferencesMask byte values recorded and committed to this document (§4.3)
- [ ] Lock screen strategy confirmed (Option A or B) and documented (§4.4)
- [ ] All other registry values in §4.1, §4.2, §4.5, §4.6 confirmed on both OS versions

#### Testing Complete

- [ ] All P0 test cases PASS on ENV-01 (Win10 22H2 VM)
- [ ] All P0 test cases PASS on ENV-02 (Win11 23H2 VM)
- [ ] All P0 test cases PASS on ENV-03 (Win11 24H2 VM)
- [ ] S Mode abort test PASS on ENV-06
- [ ] All P0 physical tests PASS on ENV-04
- [ ] All P0 physical tests PASS on ENV-05
- [ ] Zero unhandled exceptions in any install log
- [ ] Rollback confirmed clean on Win10 and Win11

#### Release Documentation Ready

- [ ] `CHANGELOG.md` entry for v0.1.0 written and committed
- [ ] `releases/manifests/v0.1.0.json` created and committed
- [ ] `releases/manifests/latest.json` updated and committed
- [ ] User-facing release notes drafted

### 11.2 Build Authorization Statement

When all items in §11.1 are checked, the following statement may be issued:

> **ArizenOS v0.1.0 Build Authorization**
>
> All pre-build requirements have been verified. Assets are validated. Registry values are confirmed. Testing is complete on all target platforms. No P0 test cases are failing.
>
> **The following artifacts may now be generated:**
> - Playbook Manifest
> - YAML Entry files
> - Script Manifest
> - Asset Manifest
> - `ArizenOS.apbx`
>
> Issued by: @Alrizz-art  
> Date:

---

*ArizenOS v0.1.0 Build Readiness Review — Revision 1*  
*Status: OPEN — 9 blockers outstanding*  
*Owner: @Alrizz-art*  
*Next BRR evaluation: When all Gate 1 items are resolved*
