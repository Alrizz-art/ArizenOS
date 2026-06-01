# ArizenOS Playbook Architecture

> **Product:** ArizenOS v0.1  
> **Output:** `ArizenOS.apbx` — AME Wizard Playbook  
> **Targets:** Windows 10 22H2 (Build 19045) · Windows 11 23H2+ (Build 22631+)  
> **Status:** Architecture v1.0 — Asset Production Phase

---

## What Is This

`playbook/` is the architectural staging zone and documentation layer for the ArizenOS AME Wizard playbook. It defines what goes into `ArizenOS.apbx`, how it is built, tested, rolled back, and released.

The `.apbx` is a ZIP archive that AME Wizard consumes. It contains:
- `playbook.yaml` — root manifest (lives at repo root, compiled at build time)
- `entries/*.yaml` — individual operation manifests
- `scripts/*.ps1` — PowerShell scripts executed by entries
- `registry/*.reg` — registry files applied by entries
- `assets/` — OEM logos, wallpapers, branding files

**AME Wizard never breaks:** all operations in this playbook are explicitly scoped to avoid touching Windows Update, Defender, Microsoft Store, Networking, and Security Components.

---

## Directory Index

```
playbook/
├── README.md                 ← You are here
├── ARCHITECTURE.md           ← Full structural spec + entry map
├── LIFECYCLE.md              ← Playbook lifecycle (design → ship → maintain)
├── INSTALLATION_WORKFLOW.md  ← Step-by-step installation flow
├── ROLLBACK_WORKFLOW.md      ← Rollback procedures and triggers
├── TESTING_STRATEGY.md       ← Testing pyramid and gate criteria
├── RELEASE_STRATEGY.md       ← Release process end-to-end
├── VERSIONING_STRATEGY.md    ← SemVer application for playbooks
├── SECURITY_REVIEW.md        ← Security checklist and review process
│
├── assets/                   ← Binary assets bundled into .apbx
├── manifests/                ← AME entry YAML specs and source
├── registry/                 ← Registry file sources organized by feature
├── releases/                 ← Release artifacts, manifests, checksums
├── rollback/                 ← Rollback configuration and backup specs
├── scripts/                  ← Playbook-scoped PowerShell scripts
└── tests/                    ← Test suites, fixtures, reports
```

---

## Relationship to Root Directories

| Root Path | `playbook/` Counterpart | Relationship |
|-----------|------------------------|-------------|
| `scripts/*.ps1` | `playbook/scripts/` | Root = build/maintenance utilities. `playbook/scripts/` = AME entry scripts |
| `registry/*.reg` | `playbook/registry/` | Root = standalone .reg files. `playbook/registry/` = entry-scoped, organized by feature |
| `entries/*.yaml` | `playbook/manifests/entries/` | `entries/` is the AME-required path. `playbook/manifests/` is the source/spec layer |
| `assets/` | `playbook/assets/` | Root `assets/` = raw branding. `playbook/assets/` = packaged-and-ready copies |
| `branding/` | `playbook/assets/branding/` | Branding architecture sources; exports land in playbook assets |

---

## What This Playbook Does

| Feature | Entry File | Safe? | Rollback? |
|---------|-----------|-------|----------|
| System Restore Point | `restore-point.yaml` | ✅ Yes | N/A — creates safety net |
| OEM Branding | `oem-branding.yaml` | ✅ Yes | ✅ Registry revert |
| Dark Theme | `dark-theme.yaml` | ✅ Yes | ✅ Registry revert |
| Transparency Tweaks | `transparency.yaml` | ✅ Yes | ✅ Registry revert |
| Safe Debloat | `debloat.yaml` | ✅ Yes (protected list) | ✅ App re-provision |
| Wallpaper | `wallpaper.yaml` | ✅ Yes | ✅ Revert to default |
| Developer Setup | `developer-setup.yaml` | ✅ Yes | ✅ Manual uninstall |
| Final Cleanup | `final-cleanup.yaml` | ✅ Yes | ✅ Re-enable steps |

### What Is NEVER Touched

- Windows Update (service, policies, registry keys)
- Windows Defender / Microsoft Defender Antivirus
- Microsoft Store (`Microsoft.WindowsStore`, `Microsoft.StorePurchaseApp`)
- Network stack, DNS, Firewall
- UAC policy
- BitLocker / TPM
- Windows Recovery Environment (WinRE)
- .NET Runtime and Visual C++ Redistributables

---

## Quick Start

```
Build:    scripts/build-apbx.ps1
Test:     playbook/tests/smoke/run-smoke.ps1
Release:  See playbook/RELEASE_STRATEGY.md
```
