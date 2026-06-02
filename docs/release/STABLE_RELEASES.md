# Stable Releases

> **Output:** `ArizenOS.apbx` published as a GitHub Release  
> **Cadence:** Milestone-driven, not calendar-driven  
> **Audience:** All end users on Windows 10 22H2+ or Windows 11 23H2+  
> **Owner:** Release Manager + Core Maintainers

---

## 1. Release Cadence

ArizenOS does not follow a fixed calendar release schedule. Releases are **milestone-driven**: a release ships when it is ready, not because a date arrived.

**Guiding principle:** Ship quality, not dates.

Typical cadence (aspirational, not contractual):

| Release Type | Expected Frequency |
|-------------|-------------------|
| PATCH (hotfix) | As needed — within 48h of critical bug identification |
| MINOR | Every 6–12 weeks (when milestone features are complete) |
| MAJOR | Annually or when a platform-breaking change is necessary |

---

## 2. Release Classifications

| Class | Version Example | Definition |
|-------|----------------|-----------|
| **Initial Stable** | `0.1.0` | First public stable release |
| **Feature Release** | `0.2.0`, `0.3.0` | New features, backwards compatible |
| **Major Release** | `1.0.0` | Stability commitment, possible breaking changes |
| **Patch Release** | `0.1.1`, `1.0.2` | Bug fixes and security patches only |
| **Security Release** | `0.1.2` (labeled) | Security-only — fast-tracked patch |

---

## 3. Stable Release Prerequisites

A version is eligible for stable release only when all of the following are satisfied. This list is enforced by the Release Manager and verified via CI where automated.

### 3.1 Code Completeness

- [ ] All issues and PRs assigned to the milestone are closed
- [ ] No open pull requests with the milestone's labels against `main` or the release branch
- [ ] `playbook.yaml` version field matches the release version
- [ ] Feature freeze has been declared and respected

### 3.2 Test Gates

- [ ] Unit tests: 100% pass on Windows 10 22H2
- [ ] Unit tests: 100% pass on Windows 11 23H2
- [ ] Integration tests: 100% pass on clean Windows 10 22H2 VM snapshot
- [ ] Integration tests: 100% pass on clean Windows 11 23H2 VM snapshot
- [ ] Smoke tests: manually verified on physical hardware (at least one Core Maintainer)
- [ ] Rollback tests: Tier 1 and Tier 2 verified on both platforms
- [ ] Offline installation test: all non-internet phases complete without errors

### 3.3 Security

- [ ] Security review completed (see `SECURITY_PATCH_PROCESS.md`)
- [ ] `scripts/security-audit.ps1` produces zero new FAIL results post-install on both platforms
- [ ] Debloat safety audit: `test-debloat-safety.ps1` passes 100%
- [ ] All WinGet package IDs verified against official WinGet manifest
- [ ] No scripts contain remote code execution patterns (static analysis)
- [ ] Security review sign-off comment present on release PR

### 3.4 Documentation

- [ ] `CHANGELOG.md` updated with `## [{version}] — YYYY-MM-DD` section
- [ ] `playbook/releases/changelogs/v{version}.md` written
- [ ] `playbook/releases/manifests/v{version}.json` complete
- [ ] `playbook/releases/manifests/latest.json` updated
- [ ] All architecture docs (`ARCHITECTURE.md`, etc.) reflect new version accurately
- [ ] Known issues documented in release notes

### 3.5 Build Verification

- [ ] `scripts/build-apbx.ps1` runs cleanly with zero warnings
- [ ] `ArizenOS.apbx` opens in AME Wizard without schema errors
- [ ] All eight entry YAMLs present inside the archive
- [ ] All referenced scripts present inside the archive
- [ ] All referenced assets present inside the archive
- [ ] File size within expected range (< 50MB for v0.x)
- [ ] SHA256 checksum generated and saved to `playbook/releases/checksums/v{version}.sha256`

---

## 4. The Release Process — Step by Step

### Step 1 — Declare Feature Freeze

**Who:** Release Manager  
**When:** All milestone features merged, beta testing period complete

```
Action: Create GitHub Milestone for vX.Y.Z (if not exists)
Action: Close or defer all non-critical open issues on the milestone
Action: Post announcement: "Feature freeze for vX.Y.Z — entering RC phase"
Action: Create release/X.Y.Z branch from main
```

### Step 2 — RC Tagging

**Who:** Release Manager

```
Action: Tag release/X.Y.Z at HEAD with vX.Y.Z-rc.1
Action: CI automatically builds ArizenOS.apbx from the tag
Action: CI publishes GitHub Pre-Release with the .apbx and pre-release flag
Action: Post community announcement inviting RC testing
```

### Step 3 — RC Stabilization

**Who:** Core Team + Community Testers  
**Duration:** Minimum 7 days

During this period:
- Testers report issues via GitHub Issues with label `rc-feedback`
- Release Manager triages all issues: blocker vs. non-blocker
- Blockers are fixed on the release branch and tagged as `rc.{N+1}`
- Non-blockers are filed for a future release milestone
- All fixes are cherry-picked to `main`

### Step 4 — Pre-Release Checklist Completion

**Who:** Release Manager  
**Action:** Walk through the full checklist in Section 3 of this document. Check each item.

Any unchecked item is a **release blocker** and must be resolved before Step 5.

### Step 5 — Security Review Sign-Off

**Who:** Security-designated Core Maintainer  
**Action:** Complete `SECURITY_PATCH_PROCESS.md` pre-release checklist. Post sign-off comment on release PR.

### Step 6 — Merge Release Branch

**Who:** Release Manager

```
Action: Open PR: release/X.Y.Z → main
Action: PR title: "release: vX.Y.Z"
Action: Require 2 Core Maintainer approvals
Action: Merge via merge commit (not squash)
```

### Step 7 — Tag Stable Release

**Who:** Release Manager  
**Location:** On `main`, at the merge commit

```
Tag: vX.Y.Z
Message: "ArizenOS vX.Y.Z\n\n{one-paragraph summary}"
Signed: Yes (GPG signed by Release Manager)
```

**This tag is immutable and permanent. It is never moved or deleted.**

### Step 8 — CI Automated Publish

Triggered automatically by the `vX.Y.Z` tag push (no pre-release in tag name):

```
CI workflow: release.yml
  1. Build ArizenOS.apbx from tag
  2. Generate SHA256 checksum
  3. Create GitHub Release:
     - Title: "ArizenOS vX.Y.Z"
     - Body: contents of playbook/releases/changelogs/vX.Y.Z.md
     - Assets: ArizenOS.apbx + ArizenOS.apbx.sha256
     - pre-release: false
     - latest: true
  4. Update playbook/releases/manifests/latest.json (via commit on main)
```

### Step 9 — Post-Release

```
Action: Announce on GitHub Discussions (pinned post)
Action: Archive release/X.Y.Z branch (keep 90 days, then delete)
Action: Update project README download badge/link
Action: Open new milestone for next release
Action: Begin 14-day monitoring period (watch Issues for regression reports)
```

---

## 5. Stable Release Artifact Specification

Every stable release produces exactly these artifacts:

| Artifact | Description | Published To |
|----------|-------------|-------------|
| `ArizenOS.apbx` | The playbook archive — user downloads this | GitHub Release |
| `ArizenOS.apbx.sha256` | SHA256 checksum for verification | GitHub Release |
| `v{version}.json` | Machine-readable release manifest | Repository (`playbook/releases/manifests/`) |
| `v{version}.md` | Human-readable changelog | Repository (`playbook/releases/changelogs/`) |
| GitHub Release Page | Release notes, assets, links | GitHub |

Artifacts NOT produced for stable releases (only for nightly):
- Debug builds
- Unsigned variants
- Platform-specific partial builds

---

## 6. Rollback and Yanking

If a stable release is found to contain a critical defect after publish:

**Option A — Hotfix (preferred):** Issue a `vX.Y.{Z+1}` patch release with the fix. The original release remains published.

**Option B — Yank (severe only):** If the release causes data loss, security compromise, or is fundamentally broken, the Release Manager may "yank" the release:

1. Edit the GitHub Release to add a prominent warning banner
2. Mark the GitHub Release as `pre-release: true` (removes "latest" designation)
3. Publish the hotfix as the new "latest" immediately
4. Update `playbook/releases/manifests/latest.json` to point to the hotfix
5. Never delete the yanked release or its assets — the download must remain available for rollback investigation

**A yanked release is never re-promoted to stable. A new version always replaces it.**

---

## 7. End-of-Life for Stable Releases

A stable MINOR version reaches EOL when the next MINOR version has been stable for 90 days.

EOL announcement appears:
- In the GitHub Release for the EOL version (edit description)
- In the next release's changelog under `[EOL Notices]`
- As a GitHub Discussion post

After EOL, the version receives no further patches. Its artifacts remain permanently available for download.
