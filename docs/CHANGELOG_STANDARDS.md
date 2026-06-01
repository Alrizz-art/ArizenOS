# ArizenOS — Changelog Standards

## Format: Keep a Changelog 1.1.0

ArizenOS uses the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
All entries live in `CHANGELOG.md` at the repo root.

---

## Structure

```markdown
## [Unreleased]
### Added
- Description of new thing (#PR)

## [1.1.0] - 2025-12-15
### Added
- ...
### Fixed
- ...

## [1.0.0] - 2025-11-01
### Added
- ...

[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Alrizz-art/ArizenOS/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v1.0.0
```

---

## Sections (use only what applies)

| Section | When to use |
|---------|-------------|
| `### Added` | New scripts, entries, assets, features, docs |
| `### Changed` | Changes to existing behavior, defaults, or interfaces |
| `### Deprecated` | Features that will be removed in a future version |
| `### Removed` | Anything deleted (scripts, apps from debloat list, etc.) |
| `### Fixed` | Bug fixes |
| `### Security` | Security vulnerability fixes or new hardening |

---

## Writing Good Entries

### Rules

1. **Imperative mood** — "Add support for…" not "Added support for…"
2. **One line per change** — keep it scannable
3. **Reference issues/PRs** — `(#123)` or `(closes #456)`
4. **Mark breaking changes** — prefix with `**BREAKING:**`
5. **Most impactful first** within each section
6. **No internal jargon** — write for a user reading the changelog, not the codebase

### Examples

```markdown
### Added
- Add Windows 11 24H2 (build 26100) support to debloat entry (#45)
- Add `arizenOS_alt.jpg` wallpaper variant (deep navy colorway)
- Add `scripts/bump-version.ps1` for automated SemVer version bumping

### Changed
- **BREAKING:** Rename `playbook.yaml` field `debloatLevel` to `DebloatLevel` to match
  AME Wizard capitalization convention — update any forks using the old name (#52)
- Increase developer-setup entry timeout from 900s to 1800s for slow connections (#48)
- Move OEM logo from `assets/oem/` to `assets/logos/` for cleaner structure

### Fixed
- Fix `oem-branding.ps1` crash when `C:\ArizenOS\OEM` directory pre-exists (#41)
- Fix transparency entry applying OLED taskbar key on non-OLED systems (#39)
- Fix `build-apbx.ps1` including `.git` directory in output archive (#44)

### Security
- Disable `RemoteRegistry` service in debloat phase (closes #37)
- Add SMBv1 disabled check to security audit script
```

---

## The `[Unreleased]` Section

- **Always exists** at the top of `CHANGELOG.md`
- Contributors add entries here during development
- On release: `[Unreleased]` is renamed to `[X.Y.Z] - YYYY-MM-DD`
- A fresh empty `[Unreleased]` is created above it

The `scripts/bump-version.ps1` handles this rename automatically.

---

## What NOT to Put in the Changelog

| Don't include | Reason |
|---------------|--------|
| Internal refactors with no user impact | Users don't care about code structure |
| CI/CD pipeline changes | Infrastructure, not product |
| Typo fixes in code (not docs) | Too granular |
| Dependency version bumps | Unless it changes behavior |
| `Merge branch X into Y` | Git noise |
| Individual commit messages | Too granular |

Exception: security-relevant dependency upgrades should appear under `### Security`.

---

## Diff Links (bottom of CHANGELOG.md)

Every version must have a diff link at the bottom:

```markdown
[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v1.0.0
[0.2.0-beta.1]: https://github.com/Alrizz-art/ArizenOS/compare/v0.1.0-alpha.1...v0.2.0-beta.1
[0.1.0-alpha.1]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.1.0-alpha.1
```

---

## PR Checklist Requirement

Every pull request must include a changelog entry. The PR template enforces this:

```
- [ ] CHANGELOG.md updated under [Unreleased]
```

PRs that skip this will receive a review comment requesting the entry before merge.
