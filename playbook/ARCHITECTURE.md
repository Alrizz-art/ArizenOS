# ArizenOS Playbook Architecture

> **Version:** 1.0.0  
> **AME Wizard Compatibility:** v0.7.3+  
> **Windows Targets:** 10 22H2 (Build 19045) · 11 23H2 (Build 22631)

---

## 1. Package Structure

When packaged, `ArizenOS.apbx` is a ZIP archive with this internal layout:

```
ArizenOS.apbx (ZIP)
│
├── playbook.yaml                    ← Root AME manifest (from repo root)
│
├── entries/                         ← AME entry definitions
│   ├── restore-point.yaml
│   ├── oem-branding.yaml
│   ├── dark-theme.yaml
│   ├── transparency.yaml
│   ├── debloat.yaml
│   ├── wallpaper.yaml
│   ├── developer-setup.yaml
│   └── final-cleanup.yaml
│
├── scripts/                         ← PowerShell scripts (from root scripts/)
│   ├── oem-branding.ps1
│   ├── apply-theme.ps1
│   ├── transparency.ps1
│   ├── debloat.ps1
│   ├── wallpaper.ps1
│   ├── developer-setup.ps1
│   └── rollback.ps1
│
├── registry/                        ← Registry files (from root registry/)
│   ├── dark-theme.reg
│   ├── transparency.reg
│   ├── oem-branding.reg
│   └── performance.reg
│
└── assets/                          ← Binary assets
    ├── logos/
    │   ├── arizenOS_logo_oem.bmp    ← 120×120, 24-bit BMP (Windows spec)
    │   ├── arizenOS_w10.png         ← Edition selector image
    │   └── arizenOS_w11.png         ← Edition selector image
    └── wallpapers/
        ├── arizenOS_default.jpg
        ├── arizenOS_dark.jpg
        └── arizenOS_lockscreen.jpg
```

---

## 2. Repository Staging Structure

```
playbook/
│
├── assets/                          ← Assets staged for .apbx packaging
│   ├── oem/
│   │   ├── arizenOS_logo_oem.bmp   ← Windows OEM logo (120×120, 24-bit BMP)
│   │   └── arizenOS_logo_sm.bmp    ← Small OEM logo (96×96)
│   ├── wallpapers/
│   │   ├── arizenOS_default.jpg
│   │   ├── arizenOS_dark.jpg
│   │   └── arizenOS_lockscreen.jpg
│   └── branding/
│       ├── arizenOS_w10.png         ← Edition config selector
│       └── arizenOS_w11.png         ← Edition config selector
│
├── manifests/
│   ├── README.md                    ← Entry spec and authoring guide
│   └── entries/
│       ├── restore-point.yaml       ← Entry source (compiled to entries/ at build)
│       ├── oem-branding.yaml
│       ├── dark-theme.yaml
│       ├── transparency.yaml
│       ├── debloat.yaml
│       ├── wallpaper.yaml
│       ├── developer-setup.yaml
│       └── final-cleanup.yaml
│
├── registry/
│   ├── README.md
│   ├── dark-theme/
│   │   └── dark-theme.reg           ← Source for root registry/dark-theme.reg
│   ├── transparency/
│   │   └── transparency.reg
│   ├── performance/
│   │   └── performance.reg
│   ├── oem/
│   │   └── oem-branding.reg
│   └── debloat/
│       └── telemetry-policies.reg
│
├── releases/
│   ├── README.md
│   ├── manifests/
│   │   ├── v0.1.0.json             ← Release metadata
│   │   └── latest.json             ← Pointer to current release
│   ├── changelogs/
│   │   └── v0.1.0.md
│   └── checksums/
│       └── v0.1.0.sha256
│
├── rollback/
│   ├── README.md
│   ├── snapshots/
│   │   └── .gitkeep                ← Runtime: restore point metadata
│   ├── registry-backups/
│   │   └── .gitkeep                ← Runtime: pre-install registry exports
│   └── scripts/
│       └── rollback-guide.md       ← Rollback runbook
│
├── scripts/
│   ├── README.md
│   ├── setup/
│   │   ├── oem-branding.ps1        ← Entry-specific version
│   │   ├── wallpaper.ps1
│   │   ├── apply-theme.ps1
│   │   └── developer-setup.ps1
│   ├── branding/
│   │   └── apply-oem-assets.ps1
│   ├── cleanup/
│   │   └── final-cleanup.ps1
│   └── utilities/
│       └── common.ps1              ← Shared logging, error handling
│
└── tests/
    ├── README.md
    ├── unit/
    │   ├── test-registry-keys.ps1
    │   ├── test-oem-branding.ps1
    │   └── test-debloat-safety.ps1
    ├── integration/
    │   ├── test-full-install.ps1
    │   └── test-rollback.ps1
    ├── smoke/
    │   ├── run-smoke.ps1
    │   └── smoke-checklist.md
    └── reports/
        └── .gitkeep
```

---

## 3. Entry Execution Order

AME Wizard executes entries in the order defined in `playbook.yaml`. The order is safety-critical:

```
Phase 0 — Safety Net
└── [1] restore-point.yaml         Creates Windows Restore Point FIRST

Phase 1 — Registry Layer (no user-visible changes yet)
├── [2] oem-branding.yaml          Apply OEM registry + copy assets
├── [3] dark-theme.yaml            Apply dark theme registry
└── [4] transparency.yaml          Apply transparency/acrylic registry

Phase 2 — System Cleanup (irreversible without rollback)
└── [5] debloat.yaml               Remove telemetry, optional: remove apps

Phase 3 — Visual Layer (user-visible, safe)
└── [6] wallpaper.yaml             Set desktop and lockscreen wallpaper

Phase 4 — Environment (developer-optional)
└── [7] developer-setup.yaml       WSL2, WinGet, Git, VS Code, Node.js

Phase 5 — Finalize
└── [8] final-cleanup.yaml         Flush policies, restart shell, log summary
```

**Rule:** If Phase 0 fails (restore point creation fails and user has not explicitly skipped), the playbook halts. No further entries execute.

---

## 4. Entry YAML Schema

Each entry file follows the AME Wizard entry schema:

```yaml
# entries/example.yaml

name: "Feature Name"
description: "What this entry does"

# Conditional execution based on playbook.yaml configuration
condition:
  - type: "RegistryValueExists"     # or: FileExists, HasFeature, etc.
    path: "HKLM:\\..."
    key: "ValueName"

actions:
  # Registry application
  - name: "Apply registry tweaks"
    type: "ApplyRegistryFile"
    file: "registry/feature.reg"

  # PowerShell execution
  - name: "Run setup script"
    type: "RunPowerShellScript"
    script: "scripts/feature.ps1"
    arguments: ["-Level", "Safe"]
    runAs: "System"                  # or: User
    wait: true
    errorOnFail: true

  # File copy
  - name: "Copy OEM asset"
    type: "CopyFile"
    source: "assets/oem/arizenOS_logo_oem.bmp"
    destination: "C:\\ArizenOS\\OEM\\arizenOS_logo.bmp"

  # Service management
  - name: "Disable service"
    type: "SetServiceState"
    service: "ServiceName"
    state: "Disabled"
```

---

## 5. Safety Constraints

### Protected Components (NEVER modified)

The following are explicitly excluded from all entries. Any PR that touches these is blocked:

| Component | Protection Reason |
|-----------|------------------|
| `wuauserv` (Windows Update) | Core security patching |
| `WdNisSvc`, `WinDefend` (Defender) | Active malware protection |
| `Microsoft.WindowsStore` | App ecosystem integrity |
| `mpssvc` (Windows Firewall) | Network boundary protection |
| `lsass` dependencies | Authentication subsystem |
| `WinRE` partition | System recovery capability |
| `SgrmBroker` (System Guard) | Secure boot attestation |
| `EventLog` | Audit trail integrity |

### Safe Debloat Guard

`scripts/debloat.ps1` contains `$ProtectedApps` — a hardcoded allowlist of packages that can **never** be removed regardless of debloat level:

```
Microsoft.WindowsStore
Microsoft.StorePurchaseApp
Microsoft.DesktopAppInstaller    (WinGet)
Microsoft.NET.*
Microsoft.VCLibs.*
Microsoft.UI.Xaml.*
Microsoft.MicrosoftEdge
```

This guard is enforced at script level, entry level (explicit excludes), and test level (smoke test verifies).

---

## 6. Build Pipeline

```
Source (repo root)
        │
        ▼
[scripts/build-apbx.ps1]
        │
        ├── 1. Validate required files exist
        ├── 2. Check assets (OEM BMP, wallpapers)
        ├── 3. Compress-Archive (exclude: .git, *.apbx, node_modules)
        ├── 4. Rename .zip → .apbx
        └── 5. Verify playbook.yaml inside archive
        │
        ▼
ArizenOS.apbx (repo root)
```

CI (`.github/workflows/release.yml`) runs the build on tag push and attaches the `.apbx` to the GitHub Release.

---

## 7. Platform Compatibility Matrix

| Feature | Win 10 22H2 | Win 11 23H2 | Win 11 24H2 | Notes |
|---------|------------|------------|------------|-------|
| OEM Branding | ✅ | ✅ | ✅ | Registry path identical |
| Dark Theme | ✅ | ✅ | ✅ | DWM keys differ slightly |
| Transparency | ✅ | ✅ | ✅ | Mica only on Win 11 |
| Debloat (Safe) | ✅ | ✅ | ✅ | Package names verified |
| Wallpaper | ✅ | ✅ | ✅ | |
| Developer Setup | ✅ | ✅ | ✅ | WSL2 requires Build 19041+ |
| Performance Tweaks | ✅ | ✅ | ✅ | |

**Minimum build:** 19045 (enforced in `playbook.yaml` via `minWindowsBuild: 19045`)
