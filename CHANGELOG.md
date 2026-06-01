# Changelog

All notable changes to ArizenOS will be documented in this file.

This file follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- ============================================================
CHANGELOG STANDARDS FOR CONTRIBUTORS

Sections per release (use only what applies):
  ### Added       — New features, scripts, entries, assets
  ### Changed     — Changes to existing functionality
  ### Deprecated  — Features to be removed in a future release
  ### Removed     — Features removed in this release
  ### Fixed       — Bug fixes
  ### Security    — Security fixes or hardening improvements

Rules:
  1. Add entries under [Unreleased] as you work
  2. On release: rename [Unreleased] → [X.Y.Z] - YYYY-MM-DD
  3. Each entry: imperative mood ("Add X" not "Added X")
  4. Reference issues/PRs: "(#123)", "(closes #456)"
  5. Note breaking changes: "**BREAKING:** ..."
  6. Keep entries short — one line per change
  7. Most impactful changes first within each section
============================================================ -->

## [Unreleased]

### Added
- `entries.yaml` index manifest with error handling, rollback hooks, and Win10/Win11 compatibility matrix
- `entries/` directory with 8 AME Wizard phase entry files
- `scripts/build-apbx.ps1` — automated .apbx packaging script
- `assets/logos/` — OEM BMP logo (120×120), white and dark PNG variants
- `assets/wallpapers/` — 4K default wallpaper, lockscreen, dark variant
- `docs/SPECIFICATION.md` — enterprise-grade playbook specification
- `scripts/security-audit.ps1` — pre/post security validation script
- `scripts/rollback.ps1` — three-tier rollback (RestorePoint / Registry / AppX)

---

## [0.1.0-alpha.1] - 2025-06-01

### Added
- Initial ArizenOS AME Wizard playbook (`playbook.yaml`)
- `scripts/debloat.ps1` — safe debloat for Win10/Win11 (40+ apps, telemetry, services)
- `scripts/oem-branding.ps1` — OEM identity (System Info, About page)
- `scripts/apply-theme.ps1` — system-wide dark mode + DWM acrylic/Mica
- `scripts/wallpaper.ps1` — desktop and lock screen wallpaper deployment
- `scripts/developer-setup.ps1` — WSL2, WinGet, 10 dev packages, PS7 profile
- `registry/dark-theme.reg` — ArizenOS deep slate accent (#0F172A / #1E293B)
- `registry/transparency.reg` — Acrylic/Mica transparency tweaks
- `registry/oem-branding.reg` — OEM information and CDM content policies
- `registry/performance.reg` — NTFS, network throttling, and visual FX tweaks
- `README.md` with full installation guide and asset requirements
- `LICENSE` (MIT)

---

<!-- Older releases will appear here as project progresses -->

[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/v0.1.0-alpha.1...HEAD
[0.1.0-alpha.1]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.1.0-alpha.1
