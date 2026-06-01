# ArizenOS Playbook Lifecycle

> **Version:** 1.0.0  
> **Scope:** Full lifecycle from feature design through maintenance and deprecation

---

## Overview

The ArizenOS playbook lifecycle has five stages. Every change — whether a new feature, a registry tweak, or a script update — moves through all five stages before it ships in a `.apbx` release.

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   DESIGN    │──▶│   BUILD     │──▶│   TEST      │──▶│   RELEASE   │──▶│  MAINTAIN   │
│             │   │             │   │             │   │             │   │             │
│ RFC → Spec  │   │ Entry YAML  │   │ Unit        │   │ Build .apbx │   │ Monitor     │
│ Risk assess │   │ Scripts     │   │ Integration │   │ Sign off    │   │ Hotfix      │
│ Compat check│   │ Registry    │   │ Smoke test  │   │ Publish     │   │ Deprecate   │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

---

## Stage 1 — Design

**Gate in:** GitHub Issue with label `playbook` or `playbook-feature`  
**Gate out:** Issue approved by Core Maintainer + RFC merged (for significant changes)

### 1.1 Feature Classification

Before any work starts, every proposed change is classified:

| Class | Definition | Examples | RFC Required |
|-------|-----------|---------|--------------|
| **Cosmetic** | Visual-only, fully reversible, no service changes | Wallpaper, theme color | No |
| **Registry** | Registry-only changes, no service or app impact | Transparency toggle, DWM tweak | No |
| **Service** | Modifies service state or startup type | Disable telemetry service | Yes |
| **App Removal** | Removes AppX packages | Debloat additions | Yes |
| **Structural** | New entry, new script, new playbook config | New entry YAML | Yes |
| **Critical** | Touches security, UAC, Defender, Store | N/A — prohibited | Blocked |

### 1.2 Safety Pre-Check

Before design proceeds, answer these questions:

1. Does this change touch any protected component? (See `ARCHITECTURE.md §5`) → **Stop if yes**
2. Is this change reversible via registry revert? → Document rollback path
3. Does this work on both Windows 10 22H2 AND Windows 11 23H2+? → Test on both
4. Does this require internet access? → Mark as optional; handle offline gracefully
5. Does this require admin rights? → Document privilege requirement in entry YAML

### 1.3 Compatibility Research

Every registry key and script behavior must be verified against:
- Windows 10 22H2 (Build 19045)
- Windows 11 23H2 (Build 22631)
- Windows 11 24H2 (Build 26100) — secondary target

Source verification hierarchy (highest to lowest authority):
1. Microsoft official documentation / Windows Dev Docs
2. Verified community sources (NTLite forums, Win-Debloat-Tools, Atlas OS)
3. Personal testing on clean VM
4. Community testing reports on GitHub Issues

---

## Stage 2 — Build

**Gate in:** Design approval  
**Gate out:** All files created, PR opened, builds without errors

### 2.1 Entry Development Order

1. Write the entry YAML in `playbook/manifests/entries/`
2. Write or update the PowerShell script in `playbook/scripts/` or root `scripts/`
3. Write or update the registry file in `playbook/registry/` or root `registry/`
4. Copy/update assets to `playbook/assets/` if needed
5. Update `playbook.yaml` configuration if a new user-facing option is introduced
6. Update rollback documentation if the change has irreversible components

### 2.2 Entry Authoring Standards

Every entry YAML must:
- Have a human-readable `name` and `description`
- Declare explicit `condition` blocks (do not run blindly)
- Handle `ErrorOnFail` correctly — cosmetic entries: `false`; system entries: `true`
- Reference scripts with relative paths only (no absolute paths)
- Carry a comment header with author, date, Windows version tested on

### 2.3 Script Authoring Standards

Every PS1 script must:
- Use `#Requires -RunAsAdministrator` where admin is needed
- Have a `.SYNOPSIS`, `.DESCRIPTION`, `.VERSION` block
- Set `$ErrorActionPreference = "Stop"` at top
- Write all output through a `Write-Log` function to `$env:SystemDrive\ArizenOS\Logs\`
- Test with `SilentlyContinue` on operations that may not apply to all Windows versions
- Never hardcode paths — use `$PSScriptRoot`, `$env:SystemDrive`, `$env:USERPROFILE`
- Never execute remote code (no `Invoke-Expression`, no `IEX`, no remote URLs in scripts)

### 2.4 Registry File Standards

Every .reg file must:
- Begin with `Windows Registry Editor Version 5.00`
- Include a comment block identifying the feature, target OS, and author
- Use `dword:` for boolean/integer values (not string "0" or "1")
- Never include `[-HKEY_...]` delete operations without a corresponding rollback .reg
- Never touch `HKLM:\SYSTEM\CurrentControlSet\Services\` for protected services

---

## Stage 3 — Test

**Gate in:** PR opened with all files  
**Gate out:** All tests pass, PR approved by two reviewers

Test requirements by change class:

| Class | Unit | Integration | Smoke | Security Audit |
|-------|------|-------------|-------|----------------|
| Cosmetic | Optional | — | ✅ Required | — |
| Registry | ✅ Required | Optional | ✅ Required | — |
| Service | ✅ Required | ✅ Required | ✅ Required | ✅ Required |
| App Removal | ✅ Required | ✅ Required | ✅ Required | ✅ Required |
| Structural | ✅ Required | ✅ Required | ✅ Required | ✅ Required |

See `TESTING_STRATEGY.md` for test specifications.

---

## Stage 4 — Release

**Gate in:** All tests pass, two Core Maintainer approvals  
**Gate out:** `ArizenOS.apbx` published to GitHub Releases

See `RELEASE_STRATEGY.md` for the full release process.

---

## Stage 5 — Maintain

### 5.1 Post-Release Monitoring

After every release, monitor for 14 days:
- GitHub Issues tagged `bug` and `playbook`
- Community Discord/Reddit reports
- Security advisories for any affected Windows component

### 5.2 Hotfix Policy

A hotfix is triggered if any of these occur:
- A shipped entry breaks a system component (any severity)
- A shipped entry accidentally touches a protected component
- A security vulnerability is identified in a script

Hotfix release: patch version bump (e.g. v0.1.0 → v0.1.1), expedited review (1 reviewer), no new features.

### 5.3 Deprecation

An entry is deprecated when:
- The underlying Windows feature is removed in newer builds
- A better approach exists and the old entry would conflict
- The entry was conditional on a Windows version that is EOL

Deprecation process:
1. Mark entry with `deprecated: true` comment
2. Add deprecation notice to `playbook/manifests/entries/{entry}.yaml`
3. Keep deprecated entry for one full minor version before removal
4. Document in `CHANGELOG.md` under `[Deprecated]`

---

## Lifecycle Decision Tree

```
New Change Proposed
        │
        ▼
  Touches protected component?
  YES → BLOCKED
  NO  ↓
        ▼
  Class: Critical/Service/App Removal?
  YES → RFC required
  NO  ↓
        ▼
  Works on Win 10 22H2 AND Win 11 23H2+?
  NO  → Fix compatibility first
  YES ↓
        ▼
  Rollback path documented?
  NO  → Document before proceeding
  YES ↓
        ▼
  Build → Test → Release
```
