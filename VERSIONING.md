# Versioning System — ArizenOS

ArizenOS follows **Semantic Versioning 2.0.0** ([semver.org](https://semver.org)).

---

## Version Format

```
vMAJOR.MINOR.PATCH[-PRE_RELEASE][+BUILD_METADATA]
```

| Part            | Example    | Meaning                                               |
|-----------------|------------|-------------------------------------------------------|
| `MAJOR`         | `1`        | Breaking changes — incompatible ABI/API               |
| `MINOR`         | `2`        | New features, backward-compatible                     |
| `PATCH`         | `3`        | Bug fixes, backward-compatible                        |
| `PRE_RELEASE`   | `-alpha.1` | Unstable pre-release identifier                       |
| `BUILD_METADATA`| `+20260701`| Build info (ignored in precedence)                    |

---

## Pre-release Identifiers

| Tag          | Example         | Stage                              |
|--------------|-----------------|------------------------------------|
| `dev`        | `v0.1.0-dev.1`  | Active development, unstable       |
| `alpha`      | `v0.1.0-alpha.1`| Early testing, major features may be missing |
| `beta`       | `v0.5.0-beta.1` | Feature-complete, testing phase    |
| `rc`         | `v1.0.0-rc.1`   | Release Candidate — near-final     |
| *(none)*     | `v1.0.0`        | Stable release                     |

---

## Semantic Versioning Rules

### MAJOR version (`X.0.0`)
Increment MAJOR when:
- Kernel ABI breaks (syscall numbers changed, removed, or reordered)
- Boot protocol changes incompatibly
- Driver interface requires rewrite
- Filesystem format changes without migration path

### MINOR version (`0.X.0`)
Increment MINOR when:
- New subsystem added (e.g., new driver class, new syscall added)
- New kernel feature added (backward-compatible)
- New userspace API added
- Existing feature significantly extended

### PATCH version (`0.0.X`)
Increment PATCH when:
- Bug fix that doesn't break existing behavior
- Security patch
- Performance improvement with no API change
- Documentation correction with no code change

---

## Pre-1.0 Rules

During pre-1.0 development (`v0.x.x`), the following relaxed rules apply:
- **MINOR** may include breaking changes (public API not yet stable)
- **PATCH** is for backward-compatible bug fixes only
- Everything is considered unstable until `v1.0.0`

---

## Git Tags

All releases are tagged in Git using the format `vMAJOR.MINOR.PATCH`.

```bash
# Create a release tag
git tag -a v0.1.0 -m "Release v0.1.0 — Foundation"
git push origin v0.1.0

# List all release tags
git tag --list "v*" --sort=-version:refname
```

---

## Branch Strategy

| Branch              | Purpose                                        |
|---------------------|------------------------------------------------|
| `main`              | Latest stable release                          |
| `develop`           | Integration branch — next release in progress  |
| `feature/<name>`    | New features branched from `develop`           |
| `fix/<name>`        | Bug fixes branched from `main` or `develop`    |
| `hotfix/<name>`     | Critical fixes for the current stable release  |
| `release/<version>` | Release preparation (freeze, final testing)    |
| `chore/<name>`      | Maintenance, CI, tooling                       |

---

## Release Types

| Type       | Trigger                        | Branch         |
|------------|--------------------------------|----------------|
| Stable     | Planned milestone reached      | `release/vX.Y` |
| Hotfix     | Critical security/crash bug    | `hotfix/<name>`|
| Pre-release| Milestone reached (pre-stable) | `develop`      |
