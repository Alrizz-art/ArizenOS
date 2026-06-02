# Semantic Versioning Strategy

> **Standard:** Semantic Versioning 2.0.0 (semver.org)  
> **Scope:** All ArizenOS release artifacts — `.apbx` playbooks, tooling, documentation schemas  
> **Effective:** From v0.1.0 onward  
> **Owner:** Release Engineering Team

---

## 1. Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE[.N]][+BUILD]

Examples:
  0.1.0
  0.2.0-alpha.1
  0.2.0-beta.3
  0.2.0-rc.1
  1.0.0
  1.0.1
  1.1.0+20260601
```

All version strings are lowercase. No leading zeros. Build metadata (`+BUILD`) is stripped from the distributed artifact name but included in release manifests.

---

## 2. Version Component Definitions

### MAJOR

Incremented when a release introduces changes that are **incompatible with prior versions** in a way that requires user action or breaks existing deployments.

**Triggers a MAJOR bump:**

| Scenario | Example |
|----------|---------|
| AME Wizard schema version compatibility break | New playbook.yaml spec that older AME cannot parse |
| Minimum Windows build requirement raised | Dropping Windows 10 support |
| An entry is removed that was previously stable | Removing `developer-setup` from the playbook |
| Rollback compatibility is broken | New install cannot be reverted by old rollback script |
| Signing certificate rotated (user trust change) | New signing identity requires re-trust |

**Does NOT trigger MAJOR:**

- Adding new optional entries
- New configuration options with safe defaults
- Script rewrites with identical behavior

**MAJOR = 0 (Pre-Release Era):**  
While `MAJOR` is `0`, the project is in pre-release. Breaking changes may occur at any MINOR version. The guarantee of stability and backwards compatibility begins at `1.0.0`.

---

### MINOR

Incremented when a release adds **new functionality in a backwards-compatible manner**.

**Triggers a MINOR bump:**

| Scenario | Example |
|----------|---------|
| New playbook entry added | Adding a `privacy-hardening` entry |
| New user-facing configuration option | Adding `PerformanceMode` toggle |
| New script added to the playbook | Adding `fonts.ps1` |
| Existing entry substantially rewritten (same behavior) | Rewriting `debloat.ps1` with new logic |
| New app added to the debloat list | Adding `Microsoft.BingNews` to `$SafeRemoval` |
| New asset type added | Adding lockscreen slideshow support |
| New Windows target version added to compatibility matrix | Certifying Windows 11 24H2 |

**Resets PATCH to 0.**

---

### PATCH

Incremented when a release delivers **backwards-compatible bug fixes**.

**Triggers a PATCH bump:**

| Scenario | Example |
|----------|---------|
| Registry key value corrected | Wrong DWORD value for DWM accent |
| Script bug fixed without behavior change | Fixing a null reference in `wallpaper.ps1` |
| Package name corrected in debloat list | Microsoft renamed an AppX identifier |
| Asset corrected | OEM BMP had wrong bit depth |
| Documentation-only correction (if shipped in .apbx) | Entry YAML comment corrected |
| Compatibility fix for a new Windows Update build | New cumulative update broke a registry path |

**Does NOT reset MINOR or MAJOR.**

---

## 3. Pre-Release Identifiers

Pre-release versions denote instability and are not recommended for production use. AME Wizard displays the version string — users see these labels.

### Identifier Hierarchy

```
alpha  →  beta  →  rc  →  [stable, no identifier]
```

Each stage implies higher stability than the previous.

| Identifier | Meaning | Audience | Stability Guarantee |
|-----------|---------|----------|-------------------|
| `alpha.N` | Feature-incomplete, expect breakage | Internal team, early contributors | None |
| `beta.N` | Feature-complete, may have bugs | Community testers | Best-effort |
| `rc.N` | Release candidate — no new features | All community members | High — only critical bugs addressed |
| *(none)* | Stable release | All users | Full SemVer guarantee |

### Pre-Release Numbering

`N` starts at `1` and increments within the same MAJOR.MINOR.PATCH cycle. It resets to `1` when the identifier type advances.

```
0.2.0-alpha.1  →  0.2.0-alpha.2  →  0.2.0-beta.1  →  0.2.0-rc.1  →  0.2.0
```

A pre-release version ALWAYS has lower precedence than its stable counterpart:  
`0.2.0-rc.1 < 0.2.0`

---

## 4. Build Metadata

Build metadata is appended with `+` and does not affect version precedence.

```
1.0.0+20260601        ← build date
1.0.0+sha.bac5c48     ← commit SHA
1.0.0+20260601.sha.bac5c48
```

Build metadata appears in:
- `playbook/releases/manifests/v{version}.json` — `buildMetadata` field
- CI artifacts for traceability
- Never in the user-facing download filename

---

## 5. Version Precedence

When comparing two versions for upgrade decisions:

```
1. Compare MAJOR numerically
2. If equal, compare MINOR numerically
3. If equal, compare PATCH numerically
4. If equal, compare pre-release:
   - A version WITHOUT pre-release has higher precedence
   - alpha < beta < rc (lexicographic on identifier, numeric on N)
5. Build metadata is ignored for precedence

Examples (ascending):
  0.1.0-alpha.1
  0.1.0-alpha.2
  0.1.0-beta.1
  0.1.0-rc.1
  0.1.0           ← stable
  0.1.1
  0.2.0-alpha.1
  0.2.0
  1.0.0
```

---

## 6. Where the Version Lives

The version is declared once and propagated:

| File | Field | Authority |
|------|-------|-----------|
| `playbook.yaml` | `version:` | **Source of truth** |
| `playbook/releases/manifests/v{x}.json` | `"version"` | Release record |
| `playbook/releases/manifests/latest.json` | `"latest"` | Update pointer |
| `CHANGELOG.md` | `## [x.y.z] — YYYY-MM-DD` | Human changelog |
| Git tag | `v{x.y.z}` | Immutable release anchor |
| GitHub Release title | `ArizenOS v{x.y.z}` | Distribution label |

**Rule:** All six must agree exactly at the moment a release tag is pushed. A mismatch at tag time is a blocking error — the CI release workflow validates this before building the `.apbx`.

---

## 7. Version Lifecycle States

| State | Description | Version Example | .apbx Distributed |
|-------|-------------|----------------|------------------|
| **Development** | In-progress work on a branch | `0.2.0-dev` (not tagged) | No |
| **Alpha** | Early testing, incomplete | `0.2.0-alpha.1` | Yes — GitHub pre-release |
| **Beta** | Feature-complete testing | `0.2.0-beta.1` | Yes — GitHub pre-release |
| **RC** | Release candidate | `0.2.0-rc.1` | Yes — GitHub pre-release |
| **Stable** | Supported production release | `0.2.0` | Yes — GitHub stable release |
| **Hotfix** | Critical patch on stable | `0.2.1` | Yes — GitHub stable release |
| **EOL** | No longer maintained | `0.1.x` after `0.2.0` ships | Available, not supported |

---

## 8. Compatibility Commitments by Version Range

| Range | Commitment |
|-------|-----------|
| `0.x.y` (pre-stable) | No breaking change guarantees. Best effort. |
| `1.x.y` → `1.x.y+1` (patch) | Zero breaking changes. Pure bug fixes. |
| `1.x.y` → `1.x+1.0` (minor) | No breaking changes. New features, safe defaults. |
| `1.x.y` → `2.0.0` (major) | Breaking changes documented and migration guide provided. |

---

## 9. Deprecation Policy

Before anything is removed (triggering a MAJOR bump), it must be deprecated for at least one full MINOR release cycle:

```
0.3.0   → Feature marked [DEPRECATED] in CHANGELOG and docs
0.4.0   → Feature removed (triggers MAJOR if breaking)
```

Deprecated features produce a visible deprecation warning in the AME Wizard log during install. Removal is never silent.

---

## 10. Version Bump Authority

| Bump Type | Authority | Requires RFC |
|-----------|-----------|-------------|
| PATCH | Any Core Maintainer | No |
| MINOR | Any Core Maintainer | No (for backwards-compatible additions) |
| MAJOR | Unanimous Core Maintainer vote | Yes — RFC must be merged |
| Pre-release promotion | Release Manager | No |

The `scripts/bump-version.ps1` tool (existing) is the only authorized method for bumping the version. Manual edits to version fields in any file are not accepted.
