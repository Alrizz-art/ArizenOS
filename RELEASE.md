# ArizenOS Release Standards

> Arizen Technologies — Release Process v1.0

---

## Table of Contents

1. [Release Philosophy](#1-release-philosophy)
2. [Release Types](#2-release-types)
3. [Version Numbering](#3-version-numbering)
4. [Release Cycle](#4-release-cycle)
5. [Release Process](#5-release-process)
6. [Changelog Standards](#6-changelog-standards)
7. [Rollback Policy](#7-rollback-policy)
8. [Long-Term Support](#8-long-term-support)

---

## 1. Release Philosophy

**Ship working software. Ship it often. Never ship a broken update.**

ArizenOS runs on users' primary desktops. A bad release is not just a bad user experience — it can disrupt someone's workday, break their development environment, or corrupt their configuration. We take release quality seriously.

Core commitments:
- Every stable release is tested on a clean Windows 10 and Windows 11 installation
- Every stable release has a documented rollback path
- No release ships without an updated changelog
- Security patches are released independently of the feature release cycle

---

## 2. Release Types

| Type | Tag Format | Description |
|---|---|---|
| **Nightly** | `nightly-YYYYMMDD` | Automated, unreviewed, latest `main` build |
| **Alpha** | `v0.X.0-alpha.N` | Early feature preview. Known issues expected. |
| **Beta** | `v0.X.0-beta.N` | Feature-complete. Bug fixes only. Public testing. |
| **Release Candidate** | `v0.X.0-rc.N` | Stable candidate. Critical fixes only. |
| **Stable** | `vMAJOR.MINOR.PATCH` | Production release. Full support. |
| **Patch** | `vMAJOR.MINOR.PATCH` | Bug and security fixes for stable. |
| **Security** | `vMAJOR.MINOR.PATCH` | Out-of-cycle. Security patches only. |
| **LTS** | `vMAJOR.0.0-lts` | Designated stable with extended support window. |

### Nightly Builds

- Built automatically by CI on every successful merge to `main`
- Tagged `nightly-YYYYMMDD`, overwriting the previous nightly tag
- Not recommended for production use
- Distributed via the `nightly` release channel

### Pre-releases (Alpha / Beta / RC)

- Alpha: Feature work is ongoing. May have broken modules.
- Beta: All planned features for this release are merged. Focus is bug fixing.
- RC: We believe this is ready to ship. Final community testing window.
- All pre-releases are opted into explicitly — never pushed to stable users

---

## 3. Version Numbering

ArizenOS follows [Semantic Versioning 2.0.0](https://semver.org).

```
MAJOR.MINOR.PATCH[-prerelease][+build]

0.1.0-alpha.1   — First public alpha
0.4.0-beta.2    — Second beta of the 0.4.0 release
0.4.0-rc.1      — First release candidate
0.4.0           — Stable release
0.4.1           — Patch release
1.0.0           — First stable general availability release
1.0.0-lts       — LTS designation (applied retroactively after 30 days)
```

### Versioning Rules

- `MAJOR` increments when the Plugin API or Skin SDK introduces breaking changes that require extension authors to update their packages. Technical Council vote required.
- `MINOR` increments when new modules, commands, or user-visible capabilities are added. No breaking changes.
- `PATCH` increments for bug fixes, security patches, and performance improvements with no new functionality.
- `0.x.y` is pre-1.0: minor versions may include breaking changes with documented migration paths. After `1.0.0`, strict SemVer applies.

---

## 4. Release Cycle

### Target Cadence

| Release Type | Target Frequency |
|---|---|
| Nightly | Daily (automated) |
| Minor (feature) | Every 6–8 weeks |
| Patch | As needed (typically 1–2 per minor cycle) |
| Security | Within 7 days of confirmed vulnerability |
| LTS | Annually |

### Release Calendar

The Technical Council maintains a public release calendar in the GitHub Project board. Dates are targets, not commitments. A release slips before it ships broken.

**Freeze Dates:**
- **Feature Freeze**: 3 weeks before planned stable date. Only bug fixes merged after this point.
- **String Freeze**: 2 weeks before planned stable date. No new UI strings. Translation window opens.
- **Code Freeze**: 1 week before planned stable date. Only critical bug fixes and security patches.

---

## 5. Release Process

### Who Releases

Releases are performed by **Module Owners** and **Core Team members** with release permissions. A minimum of two people must be involved in any stable release (one prepares, one reviews).

### Pre-Release Checklist

```
□ All milestone issues are closed or explicitly deferred to next milestone
□ CHANGELOG.md is updated with this release's section
□ All module owners have confirmed their modules are ready
□ Full test suite passes on CI (zero failures, zero skips without justification)
□ Visual regression tests pass
□ Manual smoke test completed on:
  □ Windows 10 22H2 (clean install)
  □ Windows 11 23H2 (clean install)
  □ Windows 11 23H2 (upgrade from previous stable)
□ Accessibility audit completed (automated + manual)
□ Documentation updated (all new features have docs)
□ Migration guide written (if breaking changes exist)
□ Release notes drafted and reviewed by at least 1 TC member
□ GitHub Release draft created and reviewed
□ Rollback procedure documented for this release
```

### Release Steps

```bash
# 1. Create release branch from main
git checkout -b release/v0.5.0

# 2. Bump versions across all packages
pnpm version:bump 0.5.0

# 3. Update CHANGELOG.md (finalize Unreleased section)
# Edit CHANGELOG.md manually

# 4. Commit version bump
git add .
git commit -m "chore(release): bump to v0.5.0"

# 5. Open PR: release/v0.5.0 → main
# Requires 2 Core Team approvals

# 6. After merge, tag from main
git tag -s v0.5.0 -m "ArizenOS v0.5.0"
git push origin v0.5.0

# 7. CI builds and publishes release artifacts

# 8. Publish GitHub Release (draft → publish)

# 9. Announce in GitHub Discussions + social channels
```

### Post-Release

Within 48 hours of a stable release:
- [ ] Announcement posted in GitHub Discussions (`announcements` category)
- [ ] Social media posts scheduled (Twitter/X, Reddit r/windows, r/unixporn)
- [ ] Nightly channel updated to build from post-release `main`
- [ ] Next milestone created in GitHub with target date

---

## 6. Changelog Standards

ArizenOS follows [Keep a Changelog](https://keepachangelog.com) v1.1.0.

### Format

```markdown
# Changelog

All notable changes to ArizenOS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Short description of new feature (#PR or #issue)

---

## [0.5.0] — 2025-09-15

### Added
- ArizenMind streaming inference for llama-3 and phi-3 models (#142)
- ArizenGlass depth shadow system with per-window elevation (#178)
- Widget pinning: widgets can now be anchored to monitor edges (#203)

### Changed
- Default blur radius reduced from 48px to 32px for performance on integrated GPUs (#215)
- ArizenMind.query() now returns ReadableStream instead of Promise<string> (#142)

### Deprecated
- `ArizenMind.ask()` — use `ArizenMind.query()` instead. Removed in v0.6.0.
- `LegacyWidgetBridge` — use ArizenWidgets SDK. Removed in v0.6.0.

### Removed
- Built-in Rainmeter bridge (deprecated in v0.3.0) (#201)

### Fixed
- Taskbar flicker on secondary monitor hotplug (#284)
- Glass rendering corruption on DPI change (#267)
- ArizenMind context window overflow causing silent truncation (#299)

### Security
- Fixed local inference endpoint bound to 0.0.0.0 by default (#291) — CVE-2025-XXXX

---

## [0.4.1] — 2025-08-02

### Fixed
- ...
```

### Changelog Rules

- Every merged PR that affects user-visible behavior must have a changelog entry
- Entries are written in past tense, third person, active voice: "Added X", "Fixed Y"
- Always link to the relevant PR or issue number
- Security entries must reference the CVE if assigned
- Internal-only changes (CI, tooling, test infrastructure) go in `Added` under `[Unreleased]` but are collapsed in GitHub Release notes

---

## 7. Rollback Policy

### When to Rollback

A release is rolled back if:
- A crash-level bug is reported by more than 5 unique users within 48 hours
- A data loss or data corruption issue is confirmed at any scale
- A security vulnerability of CVSS 7.0+ is discovered post-release
- Core functionality (window management, taskbar, launcher) is non-functional

### Rollback Process

1. Core Team member opens emergency GitHub Discussion (`rollback/vX.Y.Z`)
2. TC vote: simple majority, 4-hour window (emergency speed)
3. If approved: GitHub Release is marked `pre-release`, download links updated
4. Patch release process begins immediately — no feature freeze, critical fix only
5. Post-mortem published within 7 days in GitHub Discussions

### Patch Timeline Targets

| Severity | Patch Target |
|---|---|
| Critical (crash, data loss, security CVSS 9+) | 24–48 hours |
| High (major feature broken, security CVSS 7–9) | 72 hours |
| Medium (degraded experience, workaround exists) | Next scheduled patch |
| Low (minor visual glitch, edge case) | Next minor release |

---

## 8. Long-Term Support

### LTS Policy

ArizenOS designates one release per year as **Long-Term Support (LTS)**. LTS releases receive:
- Security patches for **24 months** from designation date
- Critical bug fixes for **18 months**
- No new features

LTS designation is applied 30 days after a stable release that passes a stability threshold (fewer than 10 community-confirmed bugs in the first 30 days).

### LTS Branch Management

LTS releases are maintained on `lts/vMAJOR.MINOR` branches. Fixes are backported from `main` by Module Owners. Backport PRs require 2 Core Team approvals.

### Supported Versions

| Version | Type | Status | End of Support |
|---|---|---|---|
| `main` | Nightly | Active | — |
| `0.5.x` | Stable | Current | 6 weeks after 0.6.0 |
| `0.4.x` | Stable | Maintenance | 2 weeks after 0.5.0 |
| `<0.4` | Pre-stable | Unsupported | — |

---

*ArizenOS Release Standards v1.0 — June 2025*
*Maintained by the Technical Council*
