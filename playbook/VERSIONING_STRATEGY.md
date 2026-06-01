# ArizenOS Playbook Versioning Strategy

> **Version:** 1.0.0  
> **Format:** Semantic Versioning (SemVer 2.0.0)

---

## Version Format

```
MAJOR.MINOR.PATCH[-prerelease[.N]]

Examples:
  0.1.0          — First public alpha/beta
  0.1.1          — Hotfix
  0.2.0          — New features added
  1.0.0          — First stable, full-featured release
  1.0.0-alpha.1  — Pre-release
  1.0.0-beta.2   — Beta
  1.0.0-rc.1     — Release candidate
```

---

## Version Semantics for a Playbook

ArizenOS is a playbook, not a software library. SemVer is applied with AME Wizard compatibility and Windows version compatibility as the primary axes.

### MAJOR version bump when:

- The `playbook.yaml` schema changes in a way that breaks AME Wizard compatibility
- The minimum Windows build requirement changes (`minWindowsBuild`)
- A previously-supported Windows version is dropped
- A fundamental change to the entry execution order that could cause conflicts on upgrade
- The Plugin API (if introduced) has breaking changes

**Example:** Dropping Windows 10 support would be `1.0.0 → 2.0.0`

### MINOR version bump when:

- A new playbook entry is added (new feature)
- A new configuration option is added to `playbook.yaml`
- An existing script is substantially rewritten (same behavior, new implementation)
- New apps are added to the debloat list
- New branding assets are added
- A deprecated entry is removed (after one minor version deprecation period)

**Example:** Adding a new "Privacy Hardening" entry would be `0.1.0 → 0.2.0`

### PATCH version bump when:

- A registry key value is corrected
- A script bug is fixed without behavior change
- An app name in the debloat list is corrected (e.g. package renamed by Microsoft)
- Documentation changes with no functional impact
- Asset file update (new wallpaper, updated OEM logo) without structural change

**Example:** Fixing a wrong registry path → `0.1.0 → 0.1.1`

---

## Pre-Release Identifiers

| Identifier | Meaning | Stability | Use |
|-----------|---------|-----------|-----|
| `alpha.N` | Early development, not feature-complete | Low | Internal testing only |
| `beta.N` | Feature-complete, public testing | Medium | Community testing |
| `rc.N` | Release candidate — no new features | High | Final validation |

Pre-release versions are NOT recommended for production use. AME Wizard shows the version string to users — alpha/beta/rc labels are visible.

---

## Where Version Is Declared

| File | Field | Notes |
|------|-------|-------|
| `playbook.yaml` | `version: "0.1.0"` | **Source of truth** for the .apbx |
| `playbook/releases/manifests/v{x}.json` | `"version": "0.1.0"` | Release metadata |
| `playbook/releases/manifests/latest.json` | `"latest": "0.1.0"` | Latest pointer |
| `CHANGELOG.md` | Section heading `## [0.1.0] — YYYY-MM-DD` | Changelog |
| GitHub Release tag | `v0.1.0` | Git tag — must match playbook.yaml |

**Rule:** All four must agree. If they disagree at release time, the release is blocked.

---

## Version Bump Process

### Using the existing bump script:

```powershell
# Bump patch: 0.1.0 → 0.1.1
.\scripts\bump-version.ps1 -Type patch

# Bump minor: 0.1.0 → 0.2.0
.\scripts\bump-version.ps1 -Type minor

# Bump major: 0.1.0 → 1.0.0
.\scripts\bump-version.ps1 -Type major
```

The `scripts/bump-version.ps1` script (existing) updates:
- `playbook.yaml` version field
- Any version references in documentation

After bumping:
1. Update `playbook/releases/manifests/v{new}.json`
2. Update `playbook/releases/manifests/latest.json`
3. Add `## [{new-version}] — {date}` section to `CHANGELOG.md`

---

## Compatibility Matrix Versioning

Each release documents its Windows compatibility explicitly in `releases/manifests/v{x}.json`. When a new Windows version is tested and confirmed, it is added to `targetBuilds` without a version bump (documentation update only).

---

## Upgrade Path

ArizenOS does not have an in-place upgrade mechanism in v0.x. Users who want to upgrade to a newer version:
1. Run `scripts/rollback.ps1 -Full` (or use Restore Point)
2. Apply new `ArizenOS.apbx` from scratch

**v1.0.0 goal:** Introduce an upgrade mode that only re-applies changed entries.

---

## Version History Commitment

Once a version is tagged and released:
- The tag is immutable
- The release and its `.apbx` are retained permanently
- The GitHub Release is not deleted
- Previous versions remain downloadable at their original URLs

This ensures users can always roll back to a known-good playbook version.
