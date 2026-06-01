# ArizenOS — Release Schedule

## Release Philosophy

ArizenOS follows a **milestone-driven release cadence** — releases happen when
quality gates are met, not on a rigid calendar. Dates below are targets, not promises.

---

## Release Roadmap

| Version | Codename | Target Date | Status | Focus |
|---------|----------|-------------|--------|-------|
| `0.1.0-alpha.1` | **Genesis** | Jun 2025 | ✅ Released | Initial playbook, scripts, assets |
| `0.2.0-beta.1` | **Blueprint** | Sep 2025 | 🔄 In Progress | Full feature set + CI/CD + community test |
| `0.3.0-rc.1` | **Horizon** | Oct 2025 | 📅 Planned | Bug fixes, Win10/11 validation, docs |
| `1.0.0` | **Arizen** | Nov 2025 | 📅 Planned | First stable public release |
| `1.1.0` | **Refine** | Dec 2025 | 📅 Planned | Community feedback, polish |
| `2.0.0` | **Ascend** | Jun 2026 | 🔮 Future | GUI configurator, plugin system |

---

## Release Types

### Alpha (`0.x.0-alpha.N`)
- **Audience:** Core contributors only
- **Stability:** Expect breakage — schema and script APIs may change
- **Distribution:** Internal only, no GitHub Release asset
- **Gate:** Basic smoke test passes on clean Win11 22H2 VM

### Beta (`0.x.0-beta.N`)
- **Audience:** Community testers, early adopters
- **Stability:** Feature-complete, bugs expected
- **Distribution:** GitHub Releases (marked pre-release), no auto-update
- **Gate:**
  - [ ] All 8 entry phases execute without abort on Win11 22H2
  - [ ] All 8 entry phases execute without abort on Win10 22H2
  - [ ] Security audit (`security-audit.ps1`) passes with 0 FAIL
  - [ ] `build-apbx.ps1` produces a loadable `.apbx` in AME Wizard
  - [ ] Rollback fully restores pre-install state (tested in VM)

### Release Candidate (`0.x.0-rc.N`)
- **Audience:** Wider public, power users
- **Stability:** No new features — bug fixes only
- **Distribution:** GitHub Releases (pre-release)
- **Gate:** All beta gates + 72-hour community soak with no critical issues

### Stable (`X.Y.Z`)
- **Audience:** Everyone
- **Stability:** Production-ready
- **Distribution:** GitHub Releases (latest), README install link updated
- **Gate:** All RC gates + maintainer sign-off

---

## Release Process (Step by Step)

```
1. PREPARE
   ├── Create release/vX.Y branch from dev
   ├── Bump version in playbook.yaml
   ├── Update CHANGELOG.md (rename [Unreleased] → [X.Y.Z] - date)
   ├── Run scripts/build-apbx.ps1 locally
   └── Test .apbx on clean Win10 22H2 VM + Win11 22H2 VM

2. VALIDATE
   ├── Run scripts/security-audit.ps1 → 0 FAIL required
   ├── Verify rollback works: scripts/rollback.ps1 -Full
   ├── Check all required assets present in .apbx
   └── Review release notes draft

3. TAG & RELEASE
   ├── Merge release/vX.Y → main (PR required)
   ├── git tag -a vX.Y.Z -m "Release vX.Y.Z: <codename>"
   ├── git push origin --tags
   └── GitHub Actions auto-builds .apbx and attaches to release

4. COMMUNICATE
   ├── Publish GitHub Release with full changelog excerpt
   ├── Update README.md download link
   └── Post in Discussions: "Release: vX.Y.Z — <codename>"
```

---

## Hotfix Process

For critical security or data-loss bugs on stable releases:

```
1. Branch: hotfix/vX.Y.(Z+1) from main (NOT dev)
2. Fix, test, bump PATCH version
3. Merge → main (tag immediately) AND backport to dev
4. Release within 48 hours of confirmed critical issue
```

---

## Support Policy

| Branch | Support Level |
|--------|---------------|
| Latest stable (`1.x`) | Full support — bugs + security |
| Previous stable (`0.x`) | Security fixes only for 90 days post-1.0 |
| Alpha/Beta | Best-effort only |
| End-of-life | No support |

---

## Dependency on Windows Builds

ArizenOS tracks Windows release cadence:

| Windows Release | Expected Support | Notes |
|-----------------|-----------------|-------|
| Win10 22H2 (19045) | Until Oct 2025 MS EOL | Maintained until MS drops |
| Win11 22H2 (22621) | Active | Fully tested |
| Win11 23H2 (22631) | Active | Fully tested |
| Win11 24H2 (26100) | v1.1.0+ | Deep support in v2.0.0 |
| Win11 25H2+ | v2.0.0 | Future milestone |
