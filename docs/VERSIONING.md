# ArizenOS — Versioning System

## Semantic Versioning 2.0.0

ArizenOS follows **SemVer 2.0.0** as defined at [semver.org](https://semver.org).

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

1.0.0            Stable release
1.1.0            Backward-compatible new feature
1.1.1            Bug fix
2.0.0-alpha.1    Alpha pre-release
2.0.0-beta.3     Beta pre-release
2.0.0-rc.1       Release candidate
1.0.0+build.20251101  Build metadata (does not affect precedence)
```

---

## When to Bump What

### MAJOR — Breaking change (X.0.0)
Increment when any of the following occur:
- `playbook.yaml` schema fields renamed or removed
- Entry YAML action types or required fields changed
- PowerShell script parameter signatures changed (breaking callers)
- Minimum Windows build requirement raised
- Registry key paths restructured (requires user re-apply)
- Asset paths or filenames changed (breaks existing installs)

### MINOR — New functionality (0.X.0)
Increment when adding backward-compatible features:
- New AME Wizard entry phase added
- New PowerShell script or registry file
- New wallpaper variant or logo
- New `playbook.yaml` configuration option
- New platform support (e.g., ARM64)
- New optional developer tool added

### PATCH — Bug fix (0.0.X)
Increment for backward-compatible corrections:
- Script error fix that doesn't change interface
- Registry key value correction
- Asset quality improvement (same filename)
- Documentation fix
- CI/CD workflow correction
- Typo or formatting fix in YAML/scripts

---

## Pre-release Identifiers

| Suffix | Stage | Who | Via |
|--------|-------|-----|-----|
| `alpha.N` | Unstable, breaking changes expected | Core contributors | Internal only |
| `beta.N` | Feature-complete, bugs expected | Community testers | GitHub Releases (pre-release) |
| `rc.N` | No new features, final validation | Public | GitHub Releases (pre-release) |
| _(none)_ | Stable | Everyone | GitHub Releases (latest) |

Version precedence (low → high):
```
1.0.0-alpha.1 < 1.0.0-alpha.2 < 1.0.0-beta.1 < 1.0.0-rc.1 < 1.0.0
```

---

## Git Tagging Convention

```bash
# Stable
git tag -a v1.0.0 -m "Release v1.0.0: Arizen"

# Pre-release
git tag -a v2.0.0-beta.1 -m "Pre-release v2.0.0-beta.1: Ascend beta"

# Push all tags
git push origin --tags
```

Tag format: **always prefix with `v`** (e.g., `v1.0.0` not `1.0.0`).

---

## Branch Strategy (Git Flow adapted)

```
main              Always stable — matches latest release tag
dev               Integration branch — all features merge here
feature/<name>    New feature (branch from dev)
fix/<name>        Bug fix (branch from dev)
release/vX.Y      Release prep (branch from dev, merges to main + dev)
hotfix/<name>     Critical patch (branch from main, merges to main + dev)
```

### Flow diagram
```
feature/X ──┐
fix/X     ──┼──► dev ──► release/vX.Y ──► main ──► tag vX.Y.Z
            │                                  │
            └──────────────────────────────────┘ (backport)

hotfix/X ──────────────────────────────────────► main ──► tag vX.Y.(Z+1)
                                                      └──► dev (backport)
```

---

## Version File Locations

The version is maintained in **one source of truth** only:

```yaml
# playbook.yaml — line 7
version: "2.0.0"
```

The `scripts/bump-version.ps1` script updates this automatically and keeps
`CHANGELOG.md` in sync. Never manually edit version strings in other files.

---

## Automated Version Bump

```powershell
# From repo root:
.\scripts\bump-version.ps1 -Type patch               # 1.0.0 → 1.0.1
.\scripts\bump-version.ps1 -Type minor               # 1.0.0 → 1.1.0
.\scripts\bump-version.ps1 -Type major               # 1.0.0 → 2.0.0
.\scripts\bump-version.ps1 -Type minor -Pre beta.1   # 1.0.0 → 1.1.0-beta.1
```

The script:
1. Reads current version from `playbook.yaml`
2. Calculates next version per SemVer rules
3. Updates `playbook.yaml → version:`
4. Adds `[X.Y.Z] - YYYY-MM-DD` header to `CHANGELOG.md`
5. Stages the two changed files (`git add`)
6. Prints the git tag command to run next

---

## Changelog Commitment

Every PR that changes behavior **must** include an entry under `[Unreleased]` in
`CHANGELOG.md`. PRs without a changelog entry will be blocked by the PR template checklist.
