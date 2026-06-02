# Changelog

All notable changes to **ArizenOS** will be documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial playbook release

---

## [0.1.0] — 2026-06-02

### Added
- `playbook.conf` — AME Wizard playbook manifest (supports Windows 10 22H2, 11 22H2/23H2/24H2)
- `Configuration/main.yml` — Main task orchestration with 8 modular stages
- `Configuration/Tasks/01-restore-point.yml` — System restore point creation before any changes
- `Configuration/Tasks/02-oem-branding.yml` — ArizenOS OEM identity (System Info, About page)
- `Configuration/Tasks/03-dark-theme.yml` — System-wide dark mode with ArizenOS accent
- `Configuration/Tasks/04-transparency.yml` — Acrylic transparency across the shell
- `Configuration/Tasks/05-debloat.yml` — Telemetry removal, bloatware uninstall, service hardening
- `Configuration/Tasks/06-wallpaper.yml` — ArizenOS wallpapers for desktop and lock screen
- `Configuration/Tasks/07-developer.yml` — Optional developer environment (WSL2, WinGet, Git, VS Code)
- `Configuration/Tasks/08-finalize.yml` — Cleanup and post-install finalization
- `Configuration/rollback.yml` — Full rollback to pre-ArizenOS system state
- `Executables/` — PowerShell scripts for branding, wallpaper, developer setup, and security audit
- Interactive debloat selection (Safe vs Minimal) via AME Wizard FeaturePage
- Optional restore point, OEM branding, wallpaper, and developer mode via user choice

---

[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Alrizz-art/ArizenOS/releases/tag/v0.1.0
