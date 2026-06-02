# Changelog Process

> **File:** `CHANGELOG.md` (repo root) + `playbook/releases/changelogs/v{version}.md`  
> **Standard:** Keep a Changelog (keepachangelog.com) — adapted for playbook releases  
> **Ownership:** Every contributor adds to the changelog when they contribute  
> **Enforcement:** PR template requires changelog entry; CI blocks merges without it

---

## 1. Two-Layer Changelog System

ArizenOS maintains changelogs at two levels:

| Level | File | Audience | Updated By |
|-------|------|----------|-----------|
| **Root Changelog** | `CHANGELOG.md` | All — developers, users, maintainers | Every PR that changes behavior |
| **Release Changelog** | `playbook/releases/changelogs/v{x}.md` | Users reading release notes | Release Manager before tagging |

The root `CHANGELOG.md` is the cumulative record. Release changelogs are curated summaries derived from the root changelog for a specific version.

---

## 2. Root Changelog Format

`CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com) specification with ArizenOS-specific extensions.

### File Structure

```markdown
# Changelog

All notable changes to ArizenOS are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Added
### Changed
### Fixed
### Deprecated
### Removed
### Security

---

## [0.2.0] — 2026-MM-DD

### Added
- ...

### Fixed
- ...

---

## [0.1.0] — 2026-06-01

### Added
- Initial public release of ArizenOS playbook
- ...

[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/v0.1.0...HEAD
[0.2.0]: https://github.com/Alrizz-art/ArizenOS/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.1.0
```

### Section Definitions

| Section | What Belongs Here |
|---------|------------------|
| `[Unreleased]` | All merged changes not yet in a tagged release |
| `Added` | New features, new entries, new scripts, new assets, new config options |
| `Changed` | Changes to existing behavior, updated scripts, rewritten logic, updated assets |
| `Fixed` | Bug fixes — broken behavior that now works correctly |
| `Deprecated` | Features that will be removed in a future version |
| `Removed` | Features removed in this version |
| `Security` | Any change that addresses a security concern — always present, even for "no change" |

### Security Section Convention

The `Security` section in every release must be explicit:

```markdown
### Security
- No security changes in this release
```

OR, if there are changes:

```markdown
### Security
- **[MEDIUM]** Restricted `developer-setup.ps1` from accepting unchecked WinGet package IDs —
  previously, a malformed `playbook.yaml` could cause an unvalidated package install
```

This section is never omitted. An explicit "no security changes" statement is a deliberate signal, not laziness.

---

## 3. Contributor Changelog Responsibility

Every PR that changes behavior **must** include a changelog entry in the `[Unreleased]` section of `CHANGELOG.md`. This is enforced by:

1. The PR template (`PULL_REQUEST_TEMPLATE.md`) requires a checked box confirming the changelog is updated
2. CI runs a changelog-presence check: if `CHANGELOG.md` is not in the diff, the PR is labeled `needs-changelog` and a warning comment is posted
3. A PR in `needs-changelog` state cannot be merged (branch protection)

### What Requires a Changelog Entry

| Change Type | Requires Entry | Section |
|------------|---------------|---------|
| New playbook entry | ✅ Yes | Added |
| New script or registry file | ✅ Yes | Added |
| Script behavior change | ✅ Yes | Changed |
| Bug fix | ✅ Yes | Fixed |
| Security fix | ✅ Yes | Security |
| Asset update (logos, wallpapers) | ✅ Yes | Changed |
| Documentation-only change | ⚠ Optional | Changed (if user-facing doc) |
| CI/CD pipeline change | ⚠ Optional | Changed (only if user-visible) |
| Test addition/update | ❌ Not required | — |
| Code comment update | ❌ Not required | — |

### How to Write a Good Changelog Entry

**Format:**
```
- {What changed} — {Why it matters or what broke before} [{platforms affected if not all}]
```

**Good examples:**
```markdown
- Added `privacy-hardening` entry to disable advertising ID and activity history — users now have stronger out-of-box privacy defaults
- Fixed `wallpaper.ps1` null reference when `C:\ArizenOS\Wallpapers` did not exist on first run — affected clean installs on Windows 10 only
- Changed `debloat.ps1` `$SafeRemoval` to exclude `Microsoft.WindowsCamera` — camera app is utility, not telemetry
```

**Bad examples (do not write):**
```markdown
- Updated script                          ← No context
- Fixed bug                               ← What bug?
- Changed some registry values            ← What? Why?
- Added feature per #42                   ← Issue numbers expire; describe the feature
```

---

## 4. Release Changelog Production

When the Release Manager prepares a new version for release, they produce the version-specific changelog at `playbook/releases/changelogs/v{version}.md`.

### Production Process

**Step 1 — Extract from `[Unreleased]`**

Copy all entries from `CHANGELOG.md [Unreleased]` that belong to this release (feature-freeze determines the cut-off).

**Step 2 — Curate and Rewrite for User Audience**

The root changelog is contributor-oriented. The release changelog is user-oriented. Rewrite entries to:
- Remove implementation jargon
- Group related entries
- Add context for why changes matter to the end user
- Remove internal/CI-only changes

**Step 3 — Add Release Metadata**

```markdown
# ArizenOS v{version}

**Released:** {YYYY-MM-DD}  
**Minimum Windows Build:** {build number}  
**AME Wizard Compatibility:** v{version}+  
**SHA256:** `{hash of ArizenOS.apbx}`

---
```

**Step 4 — Verify "What Is Never Changed" Section**

Every release changelog includes this invariant section. It must match `ARCHITECTURE.md §5`. If a release candidate touches something on this list, it is a blocker.

**Step 5 — Sign Off**

Release changelog is reviewed by one additional Core Maintainer before the tag is pushed. It must accurately represent what is in the release.

### Moving `[Unreleased]` to a Version

When the stable tag is pushed, the Release Manager:
1. Creates `## [{version}] — {date}` in `CHANGELOG.md`
2. Moves all `[Unreleased]` content into the new versioned section
3. Creates a new empty `[Unreleased]` section at the top
4. Updates the comparison URLs at the bottom of `CHANGELOG.md`
5. This change is committed directly to `main` as the merge of the release branch

---

## 5. Changelog for Hotfixes

Hotfixes follow the same process but with expedited timelines:

1. The fix author adds an entry to `[Unreleased]` in the PR
2. The Release Manager creates `## [{patch-version}] — {date}` immediately at tag time
3. The release changelog at `playbook/releases/changelogs/v{patch-version}.md` focuses on:
   - What was broken (user-friendly description)
   - What is fixed
   - Who is affected (which Windows versions, which install configurations)
   - Whether reinstallation is required or if the fix is registry-only

---

## 6. Automated Changelog Tools

ArizenOS does NOT use automated changelog generators (e.g., `git log --oneline`, conventional-commits parsers). Changelogs are human-written.

**Rationale:** Automated changelogs surface commit messages, which are developer-internal. User-facing changelogs require curation and context that a commit message parser cannot provide. The extra time cost of human curation is worth the quality difference for a user-trust product like a Windows customization playbook.

---

## 7. Changelog Accessibility

The changelog is available at:

| Location | Audience | Format |
|---------|---------|--------|
| `CHANGELOG.md` (repo root) | Developers, contributors | Markdown |
| `playbook/releases/changelogs/v{x}.md` | Testers, maintainers | Markdown |
| GitHub Release body | All users | Rendered Markdown |
| `playbook/releases/manifests/v{x}.json` → `releaseNotesURL` | Tooling | URL pointer |

The `CHANGELOG.md` root file is the permanent historical record. It is never trimmed, truncated, or replaced — only appended to.

---

## 8. Changelog for Security Releases

Security-focused releases (even if patch-only) must include:

```markdown
### Security

- **[SEVERITY]** {Component}: {What was wrong}  
  **Affected versions:** v{X.Y.Z} through v{X.Y.Z-1}  
  **Fixed in:** v{this-version}  
  **Action required:** {None (automatic on reinstall) / Reinstall recommended / Manual step required}  
  **Credit:** {Researcher handle or "Internal discovery"}
```

If a CVE is assigned: include the CVE identifier. If disclosure is coordinated, the changelog entry is published simultaneously with the public disclosure date — never before.
