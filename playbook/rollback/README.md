# playbook/rollback/ — Rollback Configuration and Backup Specifications

> **Purpose:** Rollback infrastructure: backup specs, snapshot metadata, recovery scripts  
> **Ownership:** Core Team + `scripts/rollback.ps1` (existing)  
> **Release Process:** Updated when new rollback-affecting entries are added

---

## Purpose

`playbook/rollback/` defines the rollback system for ArizenOS. The actual rollback execution happens via `scripts/rollback.ps1` (existing script at repo root). This directory contains:

1. **Snapshot metadata specs** — what data is captured pre-install for recovery
2. **Registry backup specs** — which keys are backed up, in what format
3. **Recovery runbook** — step-by-step guide for each rollback scenario

The runtime backup files themselves live on the user's machine at `C:\ArizenOS\Backups\`, NOT in this repository. This directory contains specs and guides, not runtime data.

---

## Directory Structure

```
playbook/rollback/
├── README.md                  ← This file
├── snapshots/
│   └── .gitkeep               ← Runtime: restore point metadata (on user machine)
├── registry-backups/
│   └── .gitkeep               ← Runtime: pre-install registry exports (on user machine)
└── scripts/
    └── rollback-guide.md      ← Human rollback runbook (all three tiers)
```

---

## What Gets Backed Up During Installation

The restore point entry (`restore-point.yaml`) and individual entries create these backups on the user's machine:

### Windows System Restore Point
- **Location:** Windows System Restore (managed by Windows, not by ArizenOS)
- **Name:** `ArizenOS Pre-Install — YYYYMMDD_HHMMSS`
- **Created by:** `restore-point.yaml` → `scripts/rollback.ps1` or native AME action
- **What it captures:** Full system state snapshot (registry + service states + file state)

### Registry Backups
Created at `C:\ArizenOS\Backups\registry\` during installation:

| Backup File | Keys Captured | Created By |
|------------|--------------|-----------|
| `oem-pre-install.reg` | `HKLM\...\OEMInformation`, `HKLM\...\NT\CurrentVersion` | oem-branding entry |
| `theme-pre-install.reg` | `HKCU\...\Themes\Personalize`, `HKCU\...\DWM` | dark-theme entry |
| `transparency-pre-install.reg` | DWM Composition, ImmersiveShell | transparency entry |
| `services-pre-install.reg` | Disabled service startup types | debloat entry |
| `tasks-pre-install.txt` | List of disabled scheduled tasks | debloat entry |

### Installation Log
- **Location:** `C:\ArizenOS\Logs\install_{timestamp}.log`
- Contains the complete installation record with timestamps and results

---

## Rollback Scripts Reference

The existing `scripts/rollback.ps1` supports three modes:

| Flag | Action | Tier |
|------|--------|------|
| `-UseRestorePoint` | Interactive restore point selector | Tier 1 |
| `-RestoreRegistry` | Import all registry backups | Tier 2 |
| `-RestoreApps` | Re-provision removed AppX packages | Tier 3 |
| `-Full` | Tier 2 + Tier 3 combined | Tier 2+3 |

See `playbook/ROLLBACK_WORKFLOW.md` for the full decision tree and procedures.

---

## Rollback Coverage by Feature

| Feature | Rollback Method | Completeness |
|---------|----------------|-------------|
| OEM Branding | Registry backup restore + delete OEM keys | ✅ Full |
| Dark Theme | Registry backup restore | ✅ Full |
| Transparency | Registry backup restore | ✅ Full |
| Telemetry policies | Registry backup restore + re-enable services | ✅ Full |
| App removal (debloat) | Tier 1 (restore point) or Tier 3 (re-provision) | ⚠ Partial (Store re-download) |
| Wallpaper | Reset to Windows default via SystemParametersInfo | ✅ Full |
| Developer setup | `winget uninstall {id}` per tool; disable features | ✅ Full (manual) |
| Performance tweaks | Registry backup restore | ✅ Full |

---

## Backup Retention Policy

Runtime backups at `C:\ArizenOS\Backups\` are:
- **Never deleted by ArizenOS automatically**
- The user may delete them after confirming the installation is satisfactory
- Logs at `C:\ArizenOS\Logs\` are retained indefinitely (small file sizes)
- Windows Restore Points are subject to Windows' own storage management (default: 10% of disk)

---

## Adding Rollback Support for a New Entry

When adding a new entry that modifies system state, document its rollback in `rollback-guide.md`:

1. **What did the entry change?** (registry keys, services, files)
2. **How to back it up pre-install?** (add export to entry YAML or oem-branding script)
3. **How to restore it?** (registry import, service re-enable, file delete)
4. **Which rollback tier handles it?** (1, 2, or 3)
5. **Is it covered by the system restore point?** (almost always yes)
