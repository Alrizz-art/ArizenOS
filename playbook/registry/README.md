# playbook/registry/ — Feature-Scoped Registry Sources

> **Purpose:** Registry files organized by feature for playbook packaging  
> **Ownership:** Core Team  
> **Release Process:** Changes sync to root `registry/` on PR merge

---

## Purpose

`playbook/registry/` organizes the ArizenOS registry modifications by feature domain. This is distinct from the root `registry/` directory, which contains the flat, canonical `.reg` files consumed by scripts and the build process.

The relationship:
- `playbook/registry/{feature}/` = feature-grouped source and documentation
- `root registry/*.reg` = flat canonical files (synced from here; used by scripts and build)

---

## Directory Structure

```
playbook/registry/
├── README.md
├── dark-theme/
│   └── dark-theme.reg          ← System-wide dark mode, DWM accent
├── transparency/
│   └── transparency.reg        ← Acrylic, blur, Mica effects
├── performance/
│   └── performance.reg         ← Explorer, NTFS, network, visual FX tweaks
├── oem/
│   └── oem-branding.reg        ← OEM information, consumer feature suppression
└── debloat/
    └── telemetry-policies.reg  ← Telemetry, advertising, privacy policies
```

---

## Registry File Standards

All `.reg` files in this directory must:

1. Begin with `Windows Registry Editor Version 5.00`
2. Include a comment block:
   ```
   ; Feature: {feature name}
   ; Scope: {HKLM / HKCU / both}
   ; Target OS: Windows 10 22H2+ / Windows 11 23H2+
   ; Author: {GitHub handle}
   ; Tested: {date, OS versions}
   ; Rollback: {path to rollback .reg or procedure}
   ```
3. Group keys logically with section comments (`;  --- Section Name ---`)
4. Use `dword:` for integers and booleans (never string "0")
5. Never include `[-HKEY_...]` delete operations without documentation

---

## Feature Registry Map

### dark-theme/dark-theme.reg
Sets system-wide dark mode and ArizenOS accent color.

**Keys modified:**
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize` — system dark mode
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize` — user dark mode + transparency
- `HKCU\SOFTWARE\Microsoft\Windows\DWM` — accent color, Aero Peek, colorization
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent` — accent palette

**Protected keys — never touched:**
- No Defender policy keys
- No Windows Update policy keys
- No UAC keys

### transparency/transparency.reg
Enables Acrylic and glass effects.

**Keys modified:**
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\EnableTransparency`
- `HKCU\SOFTWARE\Microsoft\Windows\DWM` — Composition, GlassOpacity, ColorizationBlurBalance
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced` — OLED taskbar transparency
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ImmersiveShell` — Acrylic surface
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\EnableMicaEffect` (Win 11 only — no-op on Win 10)

### performance/performance.reg
Responsiveness and SSD optimizations.

**Keys modified:**
- `HKCU\Control Panel\Desktop` — MenuShowDelay, WaitToKillAppTimeout, AutoEndTasks
- `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem` — NtfsDisableLastAccessUpdate, LongPathsEnabled
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile` — NetworkThrottlingIndex
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` — GPU Priority, Scheduling

**Safety note:** Hibernation and Prefetch keys are commented out in `performance.reg` by default. Enable only after testing on target hardware.

### oem/oem-branding.reg
OEM identity and consumer feature suppression.

**Keys modified:**
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation` — Manufacturer, Model, SupportURL, Logo
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` — RegisteredOrganization, RegisteredOwner
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent` — suppress consumer features
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` — suppress suggestions

### debloat/telemetry-policies.reg
Privacy-first telemetry suppression via Group Policy keys.

**Keys modified:**
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection` — AllowTelemetry = 0
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection` — MaxTelemetryAllowed = 0
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo` — DisabledByGroupPolicy = 1
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy` — TailoredExperiencesWithDiagnosticDataEnabled = 0
- `HKCU\SOFTWARE\Microsoft\InputPersonalization` — restrict ink/text collection
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\WifiNetworkManager` — disable WiFi Sense

**These keys are policy-enforced (Group Policy level) — they survive user changes in Settings UI.**

---

## Adding a New Registry File

1. Create `playbook/registry/{feature}/{feature}.reg`
2. Follow the comment block standard above
3. Run `playbook/tests/unit/test-registry-keys.ps1` to validate
4. Sync to root `registry/{feature}.reg` on merge
5. Update the entry YAML that references it (`playbook/manifests/entries/`)
6. Document rollback procedure in `playbook/ROLLBACK_WORKFLOW.md`
