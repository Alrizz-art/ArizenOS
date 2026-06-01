# ArizenOS Testing Strategy

> **Version:** 1.0.0  
> **Test Runner:** PowerShell (Pester v5+ for unit tests)  
> **Environments:** Windows 10 22H2 VM · Windows 11 23H2 VM

---

## Testing Philosophy

Every change to the playbook must be tested before merge. ArizenOS runs with Administrator privileges on a user's production machine — there is no tolerance for scripts that silently fail, half-apply, or break protected components.

**The three questions every test answers:**
1. Did the intended change happen?
2. Did anything unintended happen?
3. Can the change be reversed?

---

## Test Pyramid

```
          ┌─────────────────────┐
          │    SMOKE TESTS      │  Fast: ~5 min
          │  (post-install)     │  Run on: physical/VM after install
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │  INTEGRATION TESTS  │  Medium: ~30 min
          │  (full install flow)│  Run on: clean VM snapshot
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │     UNIT TESTS      │  Fast: ~2 min
          │  (script logic)     │  Run on: any Windows machine
          └─────────────────────┘
```

---

## Unit Tests (`playbook/tests/unit/`)

Unit tests validate individual script behaviors and registry keys in isolation. They do NOT install the playbook — they test logic and state.

### test-registry-keys.ps1

Verifies that registry operations in each `.reg` file target valid key paths and valid value types.

| Test | Assertion |
|------|-----------|
| `dark-theme.reg` key paths | All `HKLM\` and `HKCU\` paths exist after application |
| `transparency.reg` values | `EnableTransparency` = DWORD 1 |
| `oem-branding.reg` values | OEM keys populated with correct strings |
| `performance.reg` values | All DWORD types, no string coercion |
| No protected keys touched | Registry files do not reference `Services\` for protected services |
| No delete operations | No `[-HKEY_...]` lines in any .reg without explicit approval |

### test-oem-branding.ps1

Verifies OEM asset handling:

| Test | Assertion |
|------|-----------|
| OEM BMP dimensions | Exactly 120×120 pixels |
| OEM BMP bit depth | 24-bit (no alpha) |
| OEM path set correctly | Registry `Logo` value points to valid file |
| Small OEM BMP dimensions | Exactly 96×96 pixels |

### test-debloat-safety.ps1

The most critical unit test. Verifies the protected apps guard:

| Test | Assertion |
|------|-----------|
| `$ProtectedApps` contains WindowsStore | ✅ Pass |
| `$ProtectedApps` contains WinGet | ✅ Pass |
| `$ProtectedApps` contains Edge | ✅ Pass |
| `$ProtectedApps` contains .NET packages | ✅ Pass |
| All packages in `$SafeRemoval` NOT in `$ProtectedApps` | ✅ No overlap |
| Dry-run: none of `$ProtectedApps` would be removed | ✅ Pass |
| `Remove-AppxSafely` skips protected package | ✅ Returns WARN, no removal |

### test-script-standards.ps1

Static analysis of all PS1 scripts:

| Test | Assertion |
|------|-----------|
| No `Invoke-Expression` | ✅ None found |
| No hardcoded `C:\` absolute paths | ✅ Uses `$env:SystemDrive` |
| No remote URL execution | ✅ No `(New-Object Net.WebClient).Download` patterns |
| All scripts have `.SYNOPSIS` | ✅ |
| All scripts have `.VERSION` | ✅ |
| All scripts use `Write-Log` or equivalent | ✅ |
| Log path uses `$env:SystemDrive\ArizenOS\Logs\` | ✅ |

---

## Integration Tests (`playbook/tests/integration/`)

Integration tests run the full install or rollback flow on a clean Windows snapshot. These require a VM with snapshot support (Hyper-V or VMware).

### Prerequisites

```
- Windows 10 22H2 clean snapshot (no prior ArizenOS install)
- Windows 11 23H2 clean snapshot
- AME Wizard installed
- Snapshots reverted before each test run
```

### test-full-install.ps1

Runs the full playbook install (all features enabled) and validates post-install state.

| Phase | Test | Assertion |
|-------|------|-----------|
| Phase 0 | Restore point created | `Get-ComputerRestorePoint` has "ArizenOS Pre-Install" |
| Phase 1 | OEM registry set | `HKLM\...\OEMInformation\Manufacturer` = "ArizenOS Project" |
| Phase 1 | OEM logo copied | `C:\ArizenOS\OEM\arizenOS_logo.bmp` exists |
| Phase 1 | Dark mode active | `HKCU\...\AppsUseLightTheme` = 0 |
| Phase 1 | Transparency enabled | `HKCU\...\EnableTransparency` = 1 |
| Phase 2 | Telemetry services disabled | `DiagTrack` StartType = Disabled |
| Phase 2 | Store NOT removed | `Microsoft.WindowsStore` still installed |
| Phase 2 | WinGet NOT removed | `Microsoft.DesktopAppInstaller` still installed |
| Phase 2 | Edge NOT removed | `Microsoft.MicrosoftEdge` still present |
| Phase 3 | Wallpaper applied | Current wallpaper path points to ArizenOS asset |
| Phase 4 | Log file created | `C:\ArizenOS\Logs\install_*.log` exists |
| Phase 4 | No critical errors | Log contains no `[FAIL]` entries |

### test-rollback.ps1

Tests all three rollback tiers after a full install.

| Tier | Test | Assertion |
|------|------|-----------|
| Tier 2 | Registry revert | OEM keys removed after `-RestoreRegistry` |
| Tier 2 | Theme revert | `AppsUseLightTheme` restored to 1 |
| Tier 2 | Services re-enabled | DiagTrack StartType = Automatic after re-enable |
| Tier 3 | Wallpaper revert | Desktop returns to Windows default |

### test-offline-install.ps1

Tests install behavior with no internet connection (Developer Setup step).

| Test | Assertion |
|------|-----------|
| WSL2 feature enables (offline) | ✅ Registry-only, no download |
| WinGet skipped gracefully | ✅ Log WARN, no error exit |
| All other phases complete | ✅ No other phase requires internet |

---

## Smoke Tests (`playbook/tests/smoke/`)

Smoke tests are lightweight post-install checks that run in ~5 minutes on any installed system. They do not require a clean VM.

### run-smoke.ps1

Runs automatically as part of `final-cleanup.yaml` (the last entry). Results written to install log.

| Check | Method | Pass Condition |
|-------|--------|---------------|
| ArizenOS log exists | `Test-Path` | `C:\ArizenOS\Logs\install_*.log` |
| Dark mode active | Registry read | `AppsUseLightTheme = 0` |
| OEM manufacturer set | Registry read | Value = "ArizenOS Project" |
| Windows Store present | `Get-AppxPackage` | Package found |
| Windows Defender active | `Get-MpComputerStatus` | `RealTimeProtectionEnabled = True` |
| UAC not disabled | Registry read | `ConsentPromptBehaviorAdmin >= 2` |
| Firewall enabled | `Get-NetFirewallProfile` | All profiles Enabled |
| WinGet available | `Get-Command winget` | Command found |
| No `[FAIL]` in install log | Log scan | 0 FAIL entries |

### smoke-checklist.md

Manual smoke checklist for human verification (used by QA before any release):

- [ ] System Properties dialog shows ArizenOS branding
- [ ] Desktop shows ArizenOS wallpaper
- [ ] Taskbar is dark
- [ ] Taskbar transparency effect visible
- [ ] Windows Update opens and functions normally
- [ ] Microsoft Store opens and can install an app
- [ ] Windows Defender Security Center shows green/protected
- [ ] Task Manager shows DiagTrack as Disabled
- [ ] Settings → Personalization shows current wallpaper
- [ ] Internet connectivity works
- [ ] Can install an app via WinGet (if online)

---

## Security Audit Test

Run `scripts/security-audit.ps1` pre and post installation.

**Pre-install:** Establishes baseline. All checks expected to PASS.  
**Post-install:** Must not introduce any new FAIL or WARN conditions not present pre-install.

Critical gate: If `scripts/security-audit.ps1` reports any new FAIL after install that was not present before install, the release is **blocked**.

Specific post-install assertions:
- `UAC Level`: PASS (ArizenOS never touches UAC)
- `Defender RealTime`: PASS
- `Firewall [all profiles]`: PASS
- `Remote Desktop`: PASS (unchanged)
- `SMBv1`: PASS (unchanged)
- `Telemetry Level`: PASS (AllowTelemetry = 0 — this is an improvement)

---

## Test Matrix — Windows Versions

| Test Suite | Win 10 22H2 | Win 11 23H2 | Win 11 24H2 |
|-----------|------------|------------|------------|
| Unit tests | ✅ Required | ✅ Required | Optional |
| Integration (full install) | ✅ Required | ✅ Required | Optional |
| Integration (rollback) | ✅ Required | ✅ Required | Optional |
| Smoke tests | ✅ Required | ✅ Required | Optional |
| Security audit | ✅ Required | ✅ Required | Optional |

A release **cannot ship** if any Required test fails on Win 10 22H2 or Win 11 23H2.

---

## CI Integration

`.github/workflows/ci.yml` runs unit tests on every PR:
- `test-registry-keys.ps1`
- `test-debloat-safety.ps1`
- `test-script-standards.ps1`

Integration and smoke tests require a Windows runner and are triggered manually or on release branch pushes.

---

## Test Reports

Test reports are saved to `playbook/tests/reports/` and attached to GitHub Release notes. Each report includes:
- Test run timestamp
- Windows version tested on
- Pass/Fail/Skip counts per suite
- Full log of any FAIL or WARN
