# ArizenOS Security Review Process

> **Version:** 1.0.0  
> **Required For:** Every stable release, every hotfix, every change to scripts/registry  
> **Script:** `scripts/security-audit.ps1`

---

## Security Philosophy

ArizenOS is a privileged playbook. It runs as SYSTEM, modifies registry hives that affect all users, and is distributed to people who trust it with their operating systems. This carries a higher security obligation than a typical application.

**Non-negotiable commitments:**
1. ArizenOS never weakens Windows security posture
2. ArizenOS never disables Defender, Update, Firewall, or UAC
3. ArizenOS never executes remote code at install time
4. ArizenOS never collects user data
5. Every script is readable, auditable, and documented

---

## Pre-Release Security Review Checklist

This checklist is completed by a Core Maintainer before every stable or hotfix release.

### 1. Script Audit

For every new or modified `.ps1` script:

- [ ] **No remote code execution**
  - No `Invoke-Expression` with external input
  - No `IEX (New-Object Net.WebClient).DownloadString(...)`
  - No `Start-Process` with URLs
  - No `curl | iex` or equivalent patterns

- [ ] **No credential handling**
  - Scripts do not request, store, or transmit passwords
  - Scripts do not create new user accounts
  - Scripts do not modify existing user passwords

- [ ] **Principle of least privilege respected**
  - Scripts only request Administrator where genuinely needed
  - `#Requires -RunAsAdministrator` is NOT present on scripts that don't need it
  - No `RunAs: System` in entry YAML unless strictly necessary

- [ ] **Input validation**
  - Script parameters are validated with `[ValidateSet]` or explicit guards
  - No `param([string]$Input)` used as a path without `Test-Path` validation
  - No user-provided strings interpolated into registry paths

- [ ] **Error handling**
  - Scripts use `try/catch` around all registry and service operations
  - Scripts fail gracefully — a caught exception writes a log entry and continues
  - Scripts do NOT silently swallow errors that affect security state

- [ ] **No persistence mechanisms**
  - Scripts do not create startup entries, scheduled tasks, or services for ArizenOS itself
  - Scripts do not install third-party kernel drivers
  - Scripts do not modify bootloader or BCD

### 2. Registry Audit

For every new or modified `.reg` file:

- [ ] **No protected key writes**
  - Does not write to `HKLM\SYSTEM\CurrentControlSet\Services\WinDefend`
  - Does not write to `HKLM\SYSTEM\CurrentControlSet\Services\wuauserv`
  - Does not write to `HKLM\SYSTEM\CurrentControlSet\Services\mpssvc`
  - Does not write to `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender`
  - Does not write to `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate`

- [ ] **No UAC bypass keys**
  - Does not set `ConsentPromptBehaviorAdmin` to 0
  - Does not set `EnableLUA` to 0
  - Does not set `PromptOnSecureDesktop` to 0

- [ ] **No firewall disable keys**
  - Does not set any `EnableFirewall` to 0
  - Does not add inbound firewall exception rules

- [ ] **No delete operations without rollback**
  - Any `[-HKEY_...]` delete line has a corresponding backup entry in rollback docs

- [ ] **Value type correctness**
  - REG_DWORD used for boolean/integer values
  - No REG_SZ "0" or "1" where REG_DWORD is expected by Windows

### 3. Debloat Safety Audit

For any change to `scripts/debloat.ps1` or the debloat entry:

- [ ] `$ProtectedApps` still contains all required entries:
  - `Microsoft.WindowsStore`
  - `Microsoft.StorePurchaseApp`
  - `Microsoft.DesktopAppInstaller`
  - `Microsoft.NET.*` (pattern)
  - `Microsoft.VCLibs.*` (pattern)
  - `Microsoft.UI.Xaml.*` (pattern)
  - `Microsoft.MicrosoftEdge`
  - `Microsoft.WindowsCalculator`
  - `Microsoft.WindowsNotepad`

- [ ] No new entries in `$SafeRemoval` or `$MinimalRemoval` overlap with `$ProtectedApps`

- [ ] No new `$TelemetryServices` entries include:
  - `WinDefend`
  - `WdNisSvc`
  - `SecurityHealthService`
  - `wscsvc` (Security Center)
  - `wuauserv` (Windows Update)
  - `bits` (Background Intelligent Transfer)
  - `CryptSvc` (Cryptographic Services)
  - `EventLog`

- [ ] No new `$TelemetryTasks` entries include Defender scan tasks

### 4. Asset Audit

- [ ] OEM BMP is a valid Windows-format bitmap (no embedded code)
- [ ] Wallpaper JPGs are clean image files (no steganographic payloads)
- [ ] No scripts embedded in image files (verify with `file` command or hex inspection)

### 5. Supply Chain Audit

- [ ] No new third-party scripts or code are `curl`-fetched at install time
- [ ] WinGet installs use only verified, official package IDs
- [ ] No PowerShell Gallery (`Install-Module`) calls without `-Repository PSGallery` and hash verification
- [ ] `developer-setup.ps1` WinGet package IDs verified against official WinGet manifest

**WinGet Package ID Verification:**
| Package | Expected ID | Verify At |
|---------|------------|-----------|
| Git | `Git.Git` | `winget search Git.Git` |
| VS Code | `Microsoft.VisualStudioCode` | `winget search Microsoft.VisualStudioCode` |
| Node.js LTS | `OpenJS.NodeJS.LTS` | `winget search OpenJS.NodeJS` |
| Python | `Python.Python.3.12` | `winget search Python.Python` |
| PowerShell | `Microsoft.PowerShell` | `winget search Microsoft.PowerShell` |
| Oh My Posh | `JanDeDobbeleer.OhMyPosh` | `winget search OhMyPosh` |

---

## Security Audit Script — Post-Install Gates

`scripts/security-audit.ps1` produces a pass/fail report. The following must ALL be PASS for a release to ship:

| Check | Required Result | ArizenOS Cause if FAIL |
|-------|----------------|------------------------|
| UAC Level ≥ 2 | PASS | UAC must not be lowered |
| Defender RealTime = True | PASS | Defender must not be disabled |
| Defender Antivirus = True | PASS | |
| Firewall (all profiles) = Enabled | PASS | Firewall must not be disabled |
| Remote Desktop = Disabled | PASS | RDP must not be enabled |
| SMBv1 = False | PASS | SMBv1 must remain disabled |
| Remote Registry = Disabled | PASS or WARN | Can be WARN if was pre-existing |

Any FAIL that was NOT present before install = **release blocked**.

---

## Responsible Disclosure

Security vulnerabilities in ArizenOS (scripts that could be weaponized, registry keys that weaken security) are reported via:

- GitHub Issues with label `security` (for low-severity)
- Private email to maintainer (for high-severity — see `SECURITY.md`)

Response SLA:
- Critical (active exploitation possible): 24 hours
- High (serious weakening of security posture): 72 hours
- Medium/Low: Next patch release cycle

---

## Security Review Sign-Off

Each release includes a security review sign-off comment on the release PR:

```
## Security Review — v0.1.0

Reviewed by: @{maintainer}
Date: YYYY-MM-DD

Script audit: ✅ Pass
Registry audit: ✅ Pass
Debloat safety audit: ✅ Pass
Asset audit: ✅ Pass
Supply chain audit: ✅ Pass
Post-install security-audit.ps1: ✅ Pass (0 FAIL, 2 WARN pre-existing)

APPROVED for release.
```
