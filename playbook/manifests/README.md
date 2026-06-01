# playbook/manifests/ — AME Wizard Entry Manifests

> **Purpose:** Source and specification layer for all AME Wizard entry YAML files  
> **Ownership:** Core Team (structural); approved contributors (entry content)  
> **Release Process:** Entries compiled to `entries/` directory at build time

---

## Purpose

`playbook/manifests/` is where AME Wizard entry YAML files are designed, specified, and maintained. These files define every discrete operation that ArizenOS performs on a user's system.

### Relationship to `entries/`

AME Wizard requires entry files at `entries/` relative to `playbook.yaml` (which is at the repo root). The path is resolved by the `!include: entries/{name}.yaml` declarations in `playbook.yaml`.

```
playbook/manifests/entries/    ← SOURCE: designed and maintained here
        │
        │  (build step: scripts/build-apbx.ps1 packages from repo root)
        │
entries/                       ← AME RUNTIME PATH: where AME reads entries
```

For v0.1, entries are maintained in both locations until the build script is extended to handle the copy. The canonical source of truth is `playbook/manifests/entries/`.

---

## Directory Structure

```
playbook/manifests/
├── README.md                   ← This file
└── entries/
    ├── restore-point.yaml      ← Phase 0: Create system restore point
    ├── oem-branding.yaml       ← Phase 1: OEM registry + asset copy
    ├── dark-theme.yaml         ← Phase 1: Dark theme + DWM accent
    ├── transparency.yaml       ← Phase 1: Transparency / Acrylic / Mica
    ├── debloat.yaml            ← Phase 2: Telemetry, services, app removal
    ├── wallpaper.yaml          ← Phase 3: Desktop and lock screen wallpaper
    ├── developer-setup.yaml    ← Phase 4: WSL2, WinGet apps, dev tools
    └── final-cleanup.yaml      ← Phase 5: Policy flush, Explorer restart, log
```

---

## Entry Execution Order

Entries execute in the order declared in root `playbook.yaml`. The order is safety-critical — do not change it without review.

```
1. restore-point    Phase 0: Safety net FIRST — no exceptions
2. oem-branding     Phase 1: Registry (no service changes)
3. dark-theme       Phase 1: Registry (visual only)
4. transparency     Phase 1: Registry (visual only)
5. debloat          Phase 2: Service + app changes (reversible with restore point)
6. wallpaper        Phase 3: File copy + registry (fully reversible)
7. developer-setup  Phase 4: Optional, deferred (WSL2 restart required)
8. final-cleanup    Phase 5: Flush + log — ALWAYS runs regardless of prior state
```

---

## Entry Authoring Specification

### Required Fields

Every entry YAML must contain:

```yaml
name: "Human-readable name (shown in AME Wizard progress)"
description: "One sentence — what this entry does and why"
# Author: {GitHub handle}
# Tested on: Windows 10 22H2 (Build 19045), Windows 11 23H2 (Build 22631)
# Added: YYYY-MM-DD
# ErrorOnFail: [true/false] — see notes below
```

### Error Handling Policy

| Entry Type | `errorOnFail` | Reasoning |
|-----------|--------------|----------|
| `restore-point` | `false` | Restore creation failing should warn, not abort |
| Registry-only entries | `false` | Registry apply failure is non-critical |
| `debloat` | `false` | Individual app removal failures are acceptable |
| `wallpaper` | `false` | Visual — not system-critical |
| `developer-setup` | `false` | Optional feature — graceful skip acceptable |
| `final-cleanup` | `false` | Always runs; handles its own error logging |

No ArizenOS entry uses `errorOnFail: true` in v0.1. This is intentional — a failed optional feature must never block the rest of the playbook.

### Condition Blocks

All entries that depend on user configuration must declare a `condition`:

```yaml
# Only runs if user selected OEMBranding = ON
condition:
  - type: "HasConfigOption"
    option: "OEMBranding"
    value: true
```

Entries that always run (restore-point, final-cleanup) have no condition block.

### Action Types Used in ArizenOS

| AME Action Type | Used In | Notes |
|----------------|---------|-------|
| `ApplyRegistryFile` | oem-branding, dark-theme, transparency | Path relative to playbook.yaml |
| `RunPowerShellScript` | debloat, oem-branding, wallpaper, developer-setup | Path relative to playbook.yaml |
| `CopyFile` | oem-branding, wallpaper | Source relative to playbook.yaml |
| `CreateDirectory` | oem-branding, wallpaper, final-cleanup | Creates `C:\ArizenOS\*` paths |
| `CreateRestorePoint` | restore-point | Native AME action |

---

## Entry Descriptions

### restore-point.yaml
Creates a Windows System Restore Point named "ArizenOS Pre-Install — {timestamp}" before any changes are applied. This is the user's safety net. Runs unconditionally (not gated by a configuration option) unless the user explicitly unchecks `RollbackPoint`.

### oem-branding.yaml
Applies OEM identity to Windows System Properties. Writes manufacturer name, model, support URL, and OEM logo path to the Windows registry. Copies the OEM BMP asset to `C:\ArizenOS\OEM\`. Does not modify Defender, Update, or security settings.

### dark-theme.yaml
Sets the system-wide dark mode and applies the ArizenOS accent color (Deep Slate `#1E293B`). Modifies DWM colorization keys and theme personalization keys for both HKLM (system) and HKCU (user). Fully reversible via registry revert.

### transparency.yaml
Enables Windows transparency effects, DWM Acrylic composition, OLED taskbar transparency mode (Win 10/11), and Mica backend (Win 11 only, no-op on Win 10). All registry-only changes.

### debloat.yaml
The most sensitive entry. Disables telemetry services, disables scheduled telemetry tasks, applies privacy registry policies, and optionally removes AppX packages. The protected apps guard (`$ProtectedApps`) cannot be bypassed. Windows Update, Defender, Store, and WinGet are never touched.

### wallpaper.yaml
Copies ArizenOS wallpaper assets to `C:\ArizenOS\Wallpapers\` and sets them as the desktop and lock screen backgrounds. Uses `SystemParametersInfo` for desktop and registry for lockscreen. Fully reversible.

### developer-setup.yaml
Optional entry (gated by `DeveloperMode = ON`). Enables WSL2, enables Windows Developer Mode, verifies WinGet availability, and installs developer tools via WinGet. WSL2 installation requires a system restart — this is flagged in the completion summary. Gracefully skips WinGet steps if offline.

### final-cleanup.yaml
Always executes last. Flushes group policy (`gpupdate /force`), restarts Explorer shell, writes installation summary log, and signals AME Wizard that the playbook is complete. Handles its own error logging independently of other entries.
