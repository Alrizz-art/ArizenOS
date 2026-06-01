# ArizenOS Release Strategy

> **Version:** 1.0.0  
> **CI:** `.github/workflows/release.yml`  
> **Artifact:** `ArizenOS.apbx` attached to GitHub Release

---

## Release Types

| Type | Trigger | Version Bump | Review Required | Test Gate |
|------|---------|--------------|----------------|----------|
| **Alpha** | Manual — early builds | `v0.x.0-alpha.N` | 1 Core Maintainer | Smoke only |
| **Beta** | Manual — feature complete | `v0.x.0-beta.N` | 2 Core Maintainers | Full suite |
| **Release Candidate** | Manual — pre-release | `v0.x.0-rc.N` | 2 Core Maintainers | Full suite × 2 OS |
| **Stable** | Manual + tag push | `v0.x.0` | 2 Core Maintainers + security review | Full suite × 2 OS |
| **Hotfix** | Issue: severity=critical | `v0.x.{N+1}` | 1 Core Maintainer | Smoke + targeted |

---

## Release Checklist

### Pre-Release Gate (all must be ✅ before tagging)

**Code Quality**
- [ ] All PR checks pass (CI green)
- [ ] No open issues tagged `blocker` on the milestone
- [ ] `CHANGELOG.md` updated with this version's changes
- [ ] `playbook.yaml` version field updated

**Testing**
- [ ] Unit tests: all pass on Win 10 22H2 and Win 11 23H2
- [ ] Integration tests: all pass on Win 10 22H2 and Win 11 23H2
- [ ] Smoke tests: manual checklist completed on both OS versions
- [ ] Security audit: `scripts/security-audit.ps1` shows no regressions
- [ ] Rollback test: Tier 2 registry revert verified

**Build**
- [ ] `scripts/build-apbx.ps1` runs without errors
- [ ] `ArizenOS.apbx` opens correctly in AME Wizard
- [ ] `playbook.yaml` found inside archive
- [ ] All referenced entry files present in archive
- [ ] File size is reasonable (< 50MB for v0.1)

**Documentation**
- [ ] `playbook/releases/changelogs/v{version}.md` written
- [ ] `playbook/releases/manifests/v{version}.json` updated
- [ ] `playbook/releases/manifests/latest.json` updated
- [ ] `README.md` download badge/link updated (if applicable)

**Security**
- [ ] Security review completed (see `SECURITY_REVIEW.md`)
- [ ] No new scripts introduce remote code execution paths
- [ ] No new registry keys touch protected components
- [ ] Debloat protected list reviewed — no regressions

---

## Release Process

### Step 1 — Prepare Release Branch

```
Branch: release/v0.1.0
From: main (after all features merged)
```

On the release branch:
1. Bump version in `playbook.yaml` → `version: "0.1.0"`
2. Update `CHANGELOG.md`
3. Update `playbook/releases/manifests/v0.1.0.json`
4. Update `playbook/releases/manifests/latest.json`
5. Run full test suite

### Step 2 — Build .apbx

```powershell
# Run on Windows with PowerShell
.\scripts\build-apbx.ps1
# Output: ArizenOS.apbx at repo root
```

### Step 3 — Verify the .apbx

```powershell
# Open in AME Wizard and verify:
# 1. Configuration UI loads correctly
# 2. All entry options show
# 3. Do NOT run the full playbook — AME Wizard shows validation warnings
```

### Step 4 — Generate Checksums

```powershell
$hash = Get-FileHash ArizenOS.apbx -Algorithm SHA256
"$($hash.Hash)  ArizenOS.apbx" | Out-File playbook/releases/checksums/v0.1.0.sha256
```

### Step 5 — Merge and Tag

```
PR: release/v0.1.0 → main
Require: 2 Core Maintainer approvals

After merge, tag main:
    Tag: v0.1.0
    Message: "ArizenOS v0.1.0 — {one-line description}"
```

### Step 6 — CI Automated Release

`.github/workflows/release.yml` triggers on tag push `v*`:
1. Runs `scripts/build-apbx.ps1` on Windows runner
2. Generates SHA256 checksum
3. Creates GitHub Release with:
   - Tag `v0.1.0`
   - Release title: "ArizenOS v0.1.0"
   - Release body from `playbook/releases/changelogs/v0.1.0.md`
   - Attached assets: `ArizenOS.apbx`, `ArizenOS.apbx.sha256`

### Step 7 — Post-Release

1. Announce on GitHub Discussions (pinned post)
2. Update `releases/manifests/latest.json` pointer
3. Monitor Issues for 14 days (see `LIFECYCLE.md §5.1`)

---

## Release Manifest Format

`playbook/releases/manifests/v{version}.json`:

```json
{
  "version": "0.1.0",
  "channel": "stable",
  "releaseDate": "2026-MM-DD",
  "minWindowsBuild": 19045,
  "targetBuilds": [
    { "name": "Windows 10 22H2", "build": 19045 },
    { "name": "Windows 11 23H2", "build": 22631 }
  ],
  "features": [
    "oem-branding",
    "dark-theme",
    "transparency",
    "debloat",
    "wallpaper",
    "developer-setup"
  ],
  "checksumSHA256": "{hash}",
  "downloadURL": "https://github.com/Alrizz-art/ArizenOS/releases/download/v0.1.0/ArizenOS.apbx",
  "releaseNotesURL": "https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.1.0",
  "breakingChanges": false,
  "rollbackSupported": true
}
```

`playbook/releases/manifests/latest.json`:
```json
{
  "latest": "0.1.0",
  "latestURL": "https://github.com/Alrizz-art/ArizenOS/releases/latest/download/ArizenOS.apbx"
}
```

---

## Changelog Format

`playbook/releases/changelogs/v0.1.0.md`:

```markdown
# ArizenOS v0.1.0

**Release Date:** YYYY-MM-DD  
**Minimum Windows Build:** 19045  

## What's New
- Initial release of ArizenOS playbook
- Safe OEM branding via registry and BMP asset
- Dark theme with Arizen Deep Slate accent (#1E293B)
- Transparency and Acrylic effects
- Safe debloat (telemetry, advertising, optional apps)
- ArizenOS wallpaper set (default, dark, lockscreen)
- Optional developer environment (WSL2, WinGet apps)

## What Is NOT Changed
- Windows Update — fully intact
- Windows Defender — fully intact
- Microsoft Store — fully intact
- Networking — fully intact

## Known Issues
- WSL2 requires system restart to complete installation
- Wallpaper may revert on theme switch (user must reapply)

## Download
`ArizenOS.apbx` — SHA256: {hash}
```
