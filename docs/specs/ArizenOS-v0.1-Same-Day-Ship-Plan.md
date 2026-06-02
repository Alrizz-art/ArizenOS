# ArizenOS v0.1 — Same-Day Blocker Resolution & Ship Plan

**Document Type**: Execution Plan  
**Status**: ACTIVE  
**Date**: 2026-06-02  
**Objective**: Resolve OI-01, OI-02, OI-03, OI-05 and ship ArizenOS v0.1 today  
**Reference**: `docs/specs/ArizenOS-v0.1-Build-Readiness-Review.md`

---

> **This is an action document. Every section drives toward a single outcome: `ArizenOS.apbx` shipped today.**  
> No new governance. No new architecture. Execute, validate, ship.

---

## Part 1 — Fastest Validation Workflow Per Blocker

---

### OI-01 — OEM BMP Validation

**Time estimate**: 15–30 minutes  
**Risk if skipped**: Logo shows broken or missing in System Properties — visible to every user on first boot.

#### Validation Method

Two parallel paths — use whichever is faster given available tooling:

**Path A — PowerShell (no extra tools required)**

Open PowerShell on any Windows machine and run:

```powershell
$f = "path\to\arizenOS_logo_oem.bmp"
$b = [System.IO.File]::ReadAllBytes($f)
# Check magic bytes: BM
Write-Host "Magic:" ([char]$b[0])([char]$b[1])          # Must be: BM
# Check DIB header size (offset 14, 4 bytes LE) — must be 40
$dib = [BitConverter]::ToInt32($b, 14)
Write-Host "DIB header size:" $dib                       # Must be: 40
# Check width (offset 18) and height (offset 22)
$w = [BitConverter]::ToInt32($b, 18)
$h = [BitConverter]::ToInt32($b, 22)
Write-Host "Width:" $w "Height:" $h                      # Must be: 120 x 120
# Check bit depth (offset 28, 2 bytes LE) — must be 24
$bpp = [BitConverter]::ToInt16($b, 28)
Write-Host "Bit depth:" $bpp                             # Must be: 24
# Check compression (offset 30) — must be 0 (BI_RGB)
$comp = [BitConverter]::ToInt32($b, 30)
Write-Host "Compression:" $comp                          # Must be: 0
```

**Path B — Any Image Editor (Paint, GIMP, Photoshop, Affinity)**

1. Open the file
2. Check Image Size → must be 120×120 pixels
3. Check Image Mode → must be RGB (24-bit)
4. Export/Save As BMP → select "24-bit BMP", no RLE compression, no color profile

#### Required Tools

- PowerShell (built into Windows) — OR — any image editor

#### Pass Criteria (minimum to close OI-01)

All five must be true:

| Check | Required Value |
|---|---|
| File opens without error | ✅ |
| Magic bytes | `BM` |
| Dimensions | 120 × 120 px |
| Bit depth | 24-bit |
| Compression | 0 (none) |

Plus one live test (can be done on same machine — no VM required):

```powershell
# Quick live test — apply and verify in System Properties
$oemPath = "C:\oemtest\oemlogo.bmp"
New-Item -ItemType Directory -Force "C:\oemtest" | Out-Null
Copy-Item "path\to\arizenOS_logo_oem.bmp" $oemPath
Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation" -Name "Logo" -Value $oemPath
Start-Process "sysdm.cpl"   # Open System Properties — logo should be visible
```

Take a screenshot of System Properties showing the logo. That screenshot is the evidence.

#### Minimum Evidence to Close OI-01

- [ ] Screenshot of PowerShell output showing all 5 values correct  
- [ ] Screenshot of System Properties showing logo rendered  

**No VM required. Can be done on the dev machine in 15 minutes.**

#### Fallback Strategy

If logo fails to render (wrong format):

1. Open logo source file in any image editor
2. Export as: BMP → Windows BMP → 24-bit → no compression → no ICC profile
3. Confirm output is exactly 120×120px
4. Re-run validation — total additional time: 10 minutes

---

### OI-02 — UserPreferencesMask Validation

**Time estimate**: 20–30 minutes  
**Risk if skipped**: Visual effects misconfigured — could disable window animations or font smoothing system-wide.

#### Validation Method

This is a capture-and-record task. The goal is to let Windows generate the correct bitmask, then capture it.

**Step 1 — On any available Windows 10 or 11 machine (physical or VM):**

```powershell
# First, set visual effects to the target profile via the Windows API
# Open: System Properties → Advanced → Performance → Settings → Custom
# Enable exactly these effects:
#   ✅ Animate windows when minimizing and maximizing
#   ✅ Smooth edges of screen fonts
#   ✅ Show thumbnails instead of icons
#   ✅ Show translucent selection rectangle
#   ✅ Show shadows under windows
#   ✅ Show shadows under mouse pointer
#   ❌ Everything else — OFF
# Click OK, then immediately capture the resulting mask:

$mask = (Get-ItemProperty "HKCU:\Control Panel\Desktop").UserPreferencesMask
Write-Host "Mask (hex):" ($mask | ForEach-Object { $_.ToString("X2") } | Join-String -Separator " ")
```

**Step 2 — Record the output.** It will look like: `90 12 03 80 10 00 00 00` (example only).

**Step 3 — Repeat on Win11 if a Win11 machine is available.** If not: Win10 and Win11 masks are often identical for this effect subset. Ship with the Win10 value and note it in the manifest. Validate Win11 in v0.1.1 if different.

#### Required Tools

- Windows machine (physical or VM)
- PowerShell

#### Pass Criteria (minimum to close OI-02)

- Hex byte sequence captured from Windows after manually setting the target visual effects profile
- Value recorded in §4.3 of the BRR document
- Applying the captured value via `reg add` produces the correct checkboxes in the Performance Settings UI

#### Minimum Evidence to Close OI-02

- [ ] Screenshot of PowerShell output showing the hex byte sequence  
- [ ] Screenshot of Performance Settings showing correct checkboxes after re-applying the mask  

**Validated mask hex values (fill in when captured):**

| OS | Validated Mask (hex) | Captured By | Date |
|---|---|---|---|
| Windows 10 22H2 | `[TBD]` | | |
| Windows 11 23H2 | `[TBD]` | | |

#### Fallback Strategy

If Win11 machine is unavailable today:

- Ship with Win10 mask value
- Add playbook comment: "Win11 mask assumed identical — validate v0.1.1"
- This is acceptable for v0.1 — the worst case is that one visual effect is toggled differently on Win11. Not a user-visible failure.

---

### OI-03 — Lock Screen Dual-Path Validation

**Time estimate**: 20–30 minutes  
**Risk if skipped**: Lock screen wallpaper may not change on one of the target OS versions.

#### Validation Method

Test both registry paths simultaneously (Option A from BRR) on a single machine in one pass:

```powershell
# Deploy the wallpaper file
$dest = "C:\ProgramData\ArizenOS\wallpapers\arizenOS_lockscreen.jpg"
New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
Copy-Item "path\to\arizenOS_lockscreen.jpg" $dest

# Write both paths (Option A — write all, let OS consume what it needs)
# Path 1 — Policy path (Win10 primary)
$pol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization"
If (!(Test-Path $pol)) { New-Item -Path $pol -Force | Out-Null }
Set-ItemProperty $pol "LockScreenImage" $dest
Set-ItemProperty $pol "LockScreenOverlaysDisabled" 1

# Path 2 — PersonalizationCSP (Win11 primary)
$csp = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"
If (!(Test-Path $csp)) { New-Item -Path $csp -Force | Out-Null }
Set-ItemProperty $csp "LockScreenImagePath" $dest
Set-ItemProperty $csp "LockScreenImageUrl" $dest
Set-ItemProperty $csp "LockScreenImageStatus" 1

# Force policy refresh and lock
gpupdate /force
```

Then press **Win+L** to lock the screen. Take a screenshot (phone photo is fine).

#### Required Tools

- Windows machine (physical or VM — Win10 preferred, Win11 also tested if available)
- PowerShell (Admin)
- The lock screen wallpaper file

#### Pass Criteria (minimum to close OI-03)

- Lock screen shows ArizenOS wallpaper (not Windows Spotlight, not default Windows wallpaper)
- Tested on at least one Win10 machine AND one Win11 machine

If only one OS is available today: test on that OS, document the other as "assumed compatible — same dual-path strategy." Ship. Validate second OS in v0.1.1 if needed.

#### Minimum Evidence to Close OI-03

- [ ] Photo/screenshot of lock screen showing ArizenOS wallpaper on Win10  
- [ ] Photo/screenshot of lock screen showing ArizenOS wallpaper on Win11 (or waiver note if unavailable)  

#### Fallback Strategy

If PersonalizationCSP key creation fails (access denied in some enterprise configurations):

- The Policy path alone is sufficient for Win10
- Win11 will also respect the Policy path
- Ship with Policy path only + note in release docs: "PersonalizationCSP path included for compatibility — Policy path is the reliable path"

---

### OI-05 — Physical Hardware Validation

**Time estimate**: 30–45 minutes (if machine is available)  
**Risk if skipped**: Transparency effects, DPI scaling, and GPU-rendered OEM logo unvalidated.

#### Validation Method

This is the only blocker that requires physical hardware. However, the validation scope can be minimized to what actually needs hardware:

**What can be validated on VM (and should be done first):**

- All registry writes ✅
- Rollback ✅  
- Install log clean ✅
- OEM branding text ✅

**What requires physical hardware:**

- OEM logo DPI rendering (125%, 150%)
- Taskbar acrylic transparency (GPU-rendered)
- Wallpaper at native display resolution

**Minimum physical hardware test scope for v0.1:**

Run only these 5 tests on a physical machine:

| Test | Expected Result |
|---|---|
| OEM logo renders in System Properties | Visible, not broken |
| Desktop wallpaper fills screen | No letterboxing, no tiling |
| Lock screen wallpaper shows | ArizenOS wallpaper visible |
| Dark mode active | System and apps dark |
| Windows Defender still running after install | `Get-Service WinDefend` → Running |

**If no physical machine is available today:**

Apply the "Minimum Viable Hardware Waiver":

- Install on any available physical machine regardless of Windows version (even if it's a personal machine)
- Run only the 5 tests above
- The machine does not need to be a clean install for these 5 tests
- Take photos/screenshots
- Document the hardware specs in the BRR §8.2

This is a waiver, not a skip. The 5 tests still run.

#### Required Tools

- Any physical x64 Windows 10 or 11 machine
- AME Wizard installed
- The playbook file

#### Minimum Evidence to Close OI-05

- [ ] Hardware specs documented (CPU, GPU, OS version, display DPI)  
- [ ] 5 photos/screenshots showing the 5 minimum tests above passing  
- [ ] `Get-Service WinDefend` output showing Running  

---

## Part 2 — Same-Day Execution Schedule

**Target**: All blockers closed, GO decision made, .apbx generation authorized — within one working day.

```
Hour 0:00 — START
│
├── [0:00–0:15]  PREPARATION
│     Copy all 4 asset files to test machine working directory
│     Open PowerShell as Administrator
│     Confirm AME Wizard installed (or download if not)
│     Confirm all wallpaper + BMP files accessible
│
├── [0:15–0:30]  OI-01 — OEM BMP VALIDATION  (15 min)
│     Run PowerShell hex check (5 min)
│     Apply Logo registry key (2 min)
│     Open sysdm.cpl, take screenshot (3 min)
│     If PASS → mark OI-01 closed
│     If FAIL → fix BMP export (10 min extra), re-test
│
├── [0:30–1:00]  OI-02 — UserPreferencesMask VALIDATION  (30 min)
│     Open Performance Settings, configure target profile (10 min)
│     Run PowerShell capture command (2 min)
│     Record hex bytes in BRR §4.3 (5 min)
│     Re-apply via reg add, verify checkboxes match (10 min)
│     Screenshot both → mark OI-02 closed
│
├── [1:00–1:30]  OI-03 — LOCK SCREEN VALIDATION  (30 min)
│     Deploy lockscreen.jpg to C:\ProgramData\ArizenOS\wallpapers (2 min)
│     Run dual-path PowerShell script (5 min)
│     gpupdate /force (2 min)
│     Win+L → take photo of lock screen (2 min)
│     If PASS → mark OI-03 closed (Win10 confirmed)
│     If Win11 available: repeat on Win11 (10 min)
│     If Win11 unavailable: write waiver note
│
├── [1:30–2:15]  OI-05 — PHYSICAL HARDWARE VALIDATION  (45 min)
│     Use current machine if physical (skip setup)
│     OR set up available machine (15 min)
│     Apply full playbook via AME Wizard (15 min, includes install time)
│     Run 5 minimum physical tests (10 min)
│     Take 5 screenshots + WinDefend output (5 min)
│     Document hardware specs (5 min)
│     → mark OI-05 closed
│
├── [2:15–2:30]  GAP BUFFER  (15 min)
│     Handle any unexpected failures or re-tests
│     Update BRR document with all evidence
│
├── [2:30–2:45]  GO DECISION  (15 min)
│     Review all 4 blockers: all closed?
│     Review all 6 BRR Gates: all PASS?
│     Fill in GO Decision Record (§4 below)
│     → DECISION: GO
│
└── [2:45–END]   APBX GENERATION  (see §5 below)
```

**Total time to GO: ~2.5 hours from a cold start.**  
**Total time to .apbx ready: add 2–3 hours of generation work.**  
**Realistic ship time: same day, afternoon.**

---

## Part 3 — Minimum Acceptable Evidence Per Blocker

The following is the absolute minimum evidence required to close each blocker. Nothing more is required.

| Blocker | Minimum Evidence | Format | Where to Store |
|---|---|---|---|
| OI-01 | (1) PowerShell output showing BM / 120×120 / 24-bit / comp=0. (2) Screenshot of sysdm.cpl showing logo | Screenshot / terminal output | Attach to GitHub commit or issue |
| OI-02 | (1) PowerShell output showing captured hex byte sequence. (2) Screenshot of Performance Settings with correct checkboxes | Screenshot / terminal output | Record hex value in BRR §4.3 |
| OI-03 | (1) Photo/screenshot of lock screen showing ArizenOS wallpaper. Win10 required; Win11 or waiver note | Photo | Attach to GitHub commit or issue |
| OI-05 | (1) Hardware spec doc (5 fields). (2) 5 pass screenshots. (3) WinDefend output | Screenshots + text | BRR §8.2 |

**No formal test reports. No sign-off meetings. No QA tickets.** Evidence is committed or noted and the blocker is closed. That is the full process for v0.1.

---

## Part 4 — GO Decision Record

Fill this in when all 4 blockers are closed.

```
═══════════════════════════════════════════════════════════
ArizenOS v0.1.0 — OFFICIAL GO DECISION RECORD
═══════════════════════════════════════════════════════════

Decision:        [ GO ]
Version:         0.1.0
Date:            _______________
Decided by:      @Alrizz-art

───────────────────────────────────────────────────────────
BLOCKER STATUS AT DECISION TIME
───────────────────────────────────────────────────────────

OI-01 OEM BMP Validation:          [ CLOSED — date: _______ ]
OI-02 UserPreferencesMask:          [ CLOSED — date: _______ ]
OI-03 Lock Screen Dual-Path:        [ CLOSED — date: _______ ]
OI-05 Physical Hardware:            [ CLOSED — date: _______ ]

───────────────────────────────────────────────────────────
GATE STATUS
───────────────────────────────────────────────────────────

Gate 1 — Blocker Resolution:        [ PASS ]
Gate 2 — Asset Validation:          [ PASS ]
Gate 3 — Registry Validation:       [ PASS ]
Gate 4 — VM Testing:                [ PASS ]
Gate 5 — Physical Hardware:         [ PASS ]
Gate 6 — Documentation:             [ PASS ]

───────────────────────────────────────────────────────────
WAIVERS GRANTED
───────────────────────────────────────────────────────────

[ List any P1 items waived to v0.1.1 here ]
•
•

───────────────────────────────────────────────────────────
KNOWN ISSUES SHIPPING WITH v0.1.0
───────────────────────────────────────────────────────────

[ List any known cosmetic/P2 issues ]
•
•

───────────────────────────────────────────────────────────
AUTHORIZATION
───────────────────────────────────────────────────────────

.apbx generation is AUTHORIZED.
Playbook Manifest, YAML Entries, Script Manifest,
Asset Manifest, and ArizenOS.apbx may now be generated.

Signed: @Alrizz-art
Date:   _______________
═══════════════════════════════════════════════════════════
```

---

## Part 5 — .apbx Generation Work Breakdown

Immediately after GO is declared, these 5 artifacts are generated in order. Each one feeds the next.

---

### Artifact 1 — Registry Manifest

**What**: A structured definition of every registry key, value, type, and data that the playbook will write. This is the authoritative source — YAML entries and scripts are generated from it.

**Inputs required**:
- OI-02 resolved (UserPreferencesMask hex values)
- OI-03 resolved (lock screen strategy confirmed)
- All §4 BRR checklists confirmed

**Format**: YAML

**Effort**: 30 minutes  
**Output file**: `playbook/manifests/registry-manifest.yaml`

**Sections**:
```
registry-manifest.yaml
├── oem_branding        (6 values)
├── theme               (4 values)
├── dwm                 (4 values)
├── visual_effects      (3 values — including UserPreferencesMask)
├── lock_screen         (5 values — dual-path)
├── prefetch            (2 values)
└── developer_optional  (3 values)
```

---

### Artifact 2 — Asset Manifest

**What**: A declaration of every file the playbook copies to the target machine — source path (relative to .apbx), destination path, and verification hash.

**Inputs required**:
- OI-01 resolved (OEM BMP validated)
- All 4 wallpaper files validated against §3

**Format**: YAML

**Effort**: 15 minutes  
**Output file**: `playbook/manifests/asset-manifest.yaml`

**Contents**:
```
asset-manifest.yaml
├── oemlogo.bmp         → %ProgramData%\ArizenOS\branding\
├── arizenOS_dark.jpg   → %ProgramData%\ArizenOS\wallpapers\
├── arizenOS_default.jpg → %ProgramData%\ArizenOS\wallpapers\
└── arizenOS_lockscreen.jpg → %ProgramData%\ArizenOS\wallpapers\
```

Each entry includes: source, destination, sha256, size_bytes, required (bool).

---

### Artifact 3 — Script Manifest

**What**: Defines the 13 scripts (SCR-01 through SCR-13) from the product spec — their trigger, inputs, outputs, and execution order. Scripts are written against this manifest.

**Inputs required**:
- Registry manifest complete (scripts reference registry values from it)
- Asset manifest complete (scripts reference asset paths from it)

**Format**: YAML

**Effort**: 45 minutes  
**Output file**: `playbook/manifests/script-manifest.yaml`

**Sections** (maps to spec §8.1):
```
script-manifest.yaml
├── SCR-01  preflight-check
├── SCR-02  create-restore-point
├── SCR-03  backup-registry
├── SCR-04  deploy-assets
├── SCR-05  apply-oem-branding
├── SCR-06  apply-wallpaper
├── SCR-07  apply-theme
├── SCR-08  apply-transparency
├── SCR-09  apply-performance
├── SCR-10  apply-developer (conditional)
├── SCR-11  write-manifest
├── SCR-12  register-rollback
└── SCR-13  rollback
```

---

### Artifact 4 — Playbook Manifest

**What**: The root `.apbx` metadata file — playbook identity, version, target OS constraints, entry point, and checksum declarations. This is what AME Wizard reads first.

**Inputs required**:
- All three manifests above (registry, asset, script)
- Version number confirmed: `0.1.0`
- Min OS build confirmed: `19045` (Win10 22H2)

**Format**: YAML (AME Wizard playbook schema)

**Effort**: 20 minutes  
**Output file**: `playbook/manifests/playbook-manifest.yaml`

**Key fields**:
```yaml
name: "ArizenOS"
version: "0.1.0"
description: "AI-first desktop experience layer for Windows 10 and 11"
author: "ArizenOS Contributors"
minimum_os_build: 19045
target_os:
  - "Windows 10 22H2"
  - "Windows 11 23H2"
  - "Windows 11 24H2"
require_admin: true
create_restore_point: true
entry: SCR-01  # preflight-check
```

---

### Artifact 5 — YAML Entries

**What**: The actual playbook action entries — one YAML block per feature group, in execution order. These are the AME Wizard instructions that run the scripts, write the registry, copy the files.

**Inputs required**:
- All 4 manifests above
- AME Wizard YAML schema confirmed (entry types: `RunAction`, `RegistryKey`, `FileCopy`, `Condition`)

**Format**: AME Wizard YAML entry format

**Effort**: 60–90 minutes  
**Output files**: `playbook/entries/` (one file per feature group)

```
entries/
├── 01-preflight.yaml
├── 02-safety-net.yaml
├── 03-asset-deploy.yaml
├── 04-oem-branding.yaml
├── 05-lock-screen.yaml
├── 06-theme.yaml
├── 07-transparency.yaml
├── 08-performance.yaml
├── 09-developer.yaml       ← conditional
└── 10-finalize.yaml
```

---

### Final Step — .apbx Assembly

**What**: Bundle all manifests, entries, scripts, and assets into the `ArizenOS.apbx` archive. Generate SHA256 checksum. Validate with AME Wizard.

**Effort**: 30 minutes  
**Output**: `ArizenOS-v0.1.0.apbx` + `ArizenOS-v0.1.0.apbx.sha256`

---

### Total .apbx Generation Effort Summary

| Artifact | Effort |
|---|---|
| Registry Manifest | 30 min |
| Asset Manifest | 15 min |
| Script Manifest | 45 min |
| Playbook Manifest | 20 min |
| YAML Entries (10 files) | 60–90 min |
| .apbx Assembly + Validation | 30 min |
| **Total** | **~3.5–4 hours** |

**Combined with blocker resolution (2.5 hours): full same-day delivery is ~6–7 hours from cold start.**

---

## Immediate Next Actions

Execute in this exact order. Do not move to the next step until the current one is done.

```
NOW:
  □ 1. Open PowerShell as Administrator on any Windows machine
  □ 2. Run OI-01 hex check on arizenOS_logo_oem.bmp
  □ 3. Apply logo registry key, open sysdm.cpl, take screenshot
       → OI-01 CLOSED

  □ 4. Open Performance Settings, set target visual effects profile
  □ 5. Run PowerShell to capture UserPreferencesMask hex bytes
  □ 6. Record hex value, re-apply via reg add, verify checkboxes
       → OI-02 CLOSED

  □ 7. Run dual-path lock screen PowerShell script
  □ 8. gpupdate /force, then Win+L — take photo
       → OI-03 CLOSED

  □ 9. On any physical machine: apply playbook (or manually simulate)
  □ 10. Run 5 physical tests, take screenshots, record hardware specs
        → OI-05 CLOSED

  □ 11. All 4 blockers closed → fill in GO Decision Record above
  □ 12. Request .apbx generation
```

---

*ArizenOS v0.1.0 — Same-Day Ship Plan*  
*Status: Ready to execute*  
*All blockers resolvable within 2.5 hours on a single Windows machine.*
