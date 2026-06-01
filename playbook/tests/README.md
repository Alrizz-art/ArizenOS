# playbook/tests/ — Test Suites

> **Purpose:** Unit, integration, and smoke test suites for the ArizenOS playbook  
> **Framework:** Pester v5+ (unit), VMware/Hyper-V snapshots (integration), inline PS (smoke)  
> **CI:** `.github/workflows/ci.yml` runs unit tests on every PR

---

## Directory Structure

```
playbook/tests/
├── README.md
├── unit/
│   ├── test-registry-keys.ps1      ← Validate .reg files
│   ├── test-oem-branding.ps1       ← Validate OEM asset dimensions
│   ├── test-debloat-safety.ps1     ← Critical: verify protected apps guard
│   └── test-script-standards.ps1  ← Static analysis of all PS1 scripts
├── integration/
│   ├── test-full-install.ps1       ← Full install on clean VM snapshot
│   └── test-rollback.ps1           ← All rollback tiers after full install
├── smoke/
│   ├── run-smoke.ps1               ← Quick post-install verification
│   └── smoke-checklist.md          ← Manual QA checklist
└── reports/
    └── .gitkeep                    ← Runtime: test reports saved here
```

---

## Running Tests

### Unit Tests (any machine, ~2 min)

```powershell
# Install Pester if not present
Install-Module Pester -Force -SkipPublisherCheck

# Run all unit tests
Invoke-Pester playbook/tests/unit/ -Output Detailed

# Run specific test
Invoke-Pester playbook/tests/unit/test-debloat-safety.ps1 -Output Detailed
```

### Integration Tests (clean VM snapshot required, ~30 min)

```powershell
# On a clean Windows 10 22H2 VM:
.\playbook\tests\integration\test-full-install.ps1

# After full-install test completes:
.\playbook\tests\integration\test-rollback.ps1
```

### Smoke Tests (any ArizenOS installation, ~5 min)

```powershell
.\playbook\tests\smoke\run-smoke.ps1
```

---

## Test File Specifications

### unit/test-registry-keys.ps1

Tests all `.reg` files for correctness without applying them.

| Test ID | Description | Pass Criteria |
|---------|-------------|--------------|
| REG-001 | dark-theme.reg valid key paths | All paths exist after mock apply |
| REG-002 | transparency.reg value types | All values are DWORD |
| REG-003 | oem-branding.reg no delete ops | No `[-HKEY_...]` lines |
| REG-004 | performance.reg no protected services | No writes to `Services\WinDefend` |
| REG-005 | No .reg file writes to Defender policy | `Policies\Microsoft\Windows Defender` not touched |
| REG-006 | No .reg file writes to Update policy | `WindowsUpdate` keys not touched |
| REG-007 | No .reg file disables UAC | `EnableLUA` and `ConsentPromptBehaviorAdmin` not lowered |

### unit/test-oem-branding.ps1

| Test ID | Description | Pass Criteria |
|---------|-------------|--------------|
| OEM-001 | OEM logo exists | `playbook/assets/oem/arizenOS_logo_oem.bmp` present |
| OEM-002 | OEM logo dimensions | Exactly 120×120 pixels |
| OEM-003 | OEM logo format | 24-bit BMP, no alpha channel |
| OEM-004 | Small OEM logo exists | `arizenOS_logo_sm.bmp` present |
| OEM-005 | Small OEM logo dimensions | Exactly 96×96 pixels |
| OEM-006 | Registry logo path matches | `oem-branding.reg` Logo value matches copy destination |

### unit/test-debloat-safety.ps1 ← CRITICAL TEST

This test must pass on every PR that touches `debloat.ps1` or any debloat list.

| Test ID | Description | Pass Criteria |
|---------|-------------|--------------|
| DEB-001 | $ProtectedApps contains WindowsStore | True |
| DEB-002 | $ProtectedApps contains WinGet | True |
| DEB-003 | $ProtectedApps contains Edge | True |
| DEB-004 | $ProtectedApps contains .NET pattern | True |
| DEB-005 | $ProtectedApps contains VCLibs | True |
| DEB-006 | $ProtectedApps contains UI.Xaml | True |
| DEB-007 | No overlap: $SafeRemoval ∩ $ProtectedApps | Empty set |
| DEB-008 | No overlap: $MinimalRemoval ∩ $ProtectedApps | Empty set |
| DEB-009 | Remove-AppxSafely skips protected package | Returns WARN, no removal |
| DEB-010 | $TelemetryServices excludes WinDefend | True |
| DEB-011 | $TelemetryServices excludes wuauserv | True |
| DEB-012 | $TelemetryServices excludes wscsvc | True |
| DEB-013 | $TelemetryServices excludes EventLog | True |

### unit/test-script-standards.ps1

Static analysis — does not execute scripts.

| Test ID | Description | Pass Criteria |
|---------|-------------|--------------|
| STD-001 | No Invoke-Expression | 0 occurrences across all .ps1 |
| STD-002 | No IEX | 0 occurrences |
| STD-003 | No hardcoded C:\ paths | 0 hardcoded drive paths |
| STD-004 | No remote download patterns | 0 `DownloadString`, `DownloadFile` with http |
| STD-005 | All scripts have .SYNOPSIS | 100% |
| STD-006 | All scripts have .VERSION | 100% |
| STD-007 | Log path uses $env:SystemDrive | 100% |

### integration/test-full-install.ps1

Run on a clean VM snapshot after running the full playbook.

Validates the complete post-install state per `INSTALLATION_WORKFLOW.md`.

| Phase | Test Count |
|-------|-----------|
| Phase 0 (restore point) | 2 |
| Phase 1 (OEM, theme, transparency) | 8 |
| Phase 2 (debloat) | 6 |
| Phase 3 (wallpaper) | 3 |
| Phase 4 (developer setup) | 4 |
| Phase 5 (logs, summary) | 3 |
| **Total** | **26** |

### integration/test-rollback.ps1

Run after `test-full-install.ps1` on the same VM.

| Tier | Test Count |
|------|-----------|
| Tier 2 registry revert | 5 |
| Tier 3 wallpaper revert | 2 |
| Tier 3 service re-enable | 3 |
| **Total** | **10** |

### smoke/run-smoke.ps1

Post-install verification. Runs in ~5 minutes on any ArizenOS-installed machine.

| Check | Method |
|-------|--------|
| ArizenOS log exists | Test-Path |
| Dark mode active | Registry read |
| OEM branding set | Registry read |
| Windows Store present | Get-AppxPackage |
| Defender RealTime | Get-MpComputerStatus |
| UAC not disabled | Registry read |
| Firewall enabled (all profiles) | Get-NetFirewallProfile |
| WinGet available | Get-Command |
| No [FAIL] in install log | Log parse |

---

## CI Integration

`.github/workflows/ci.yml` runs on every PR:

```yaml
- name: Run unit tests
  shell: pwsh
  run: Invoke-Pester playbook/tests/unit/ -Output Detailed -PassThru | Export-NunitReport
```

Integration and smoke tests run on the `release.yml` workflow (Windows runner, manual trigger).

Test reports are saved to `playbook/tests/reports/` and attached to GitHub Releases.
