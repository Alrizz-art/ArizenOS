<div align="center">

<img src=".github/assets/banner.svg" alt="ArizenOS" width="100%"/>

<br/>

[![Release](https://img.shields.io/github/v/release/Alrizz-art/ArizenOS?include_prereleases&style=flat-square&label=release&color=0ea5e9)](https://github.com/Alrizz-art/ArizenOS/releases)
[![License](https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-3b82f6?style=flat-square&logo=windows&logoColor=white)](https://github.com/Alrizz-art/ArizenOS)
[![AME Wizard](https://img.shields.io/badge/AME%20Wizard-compatible-22c55e?style=flat-square)](https://ameliorated.io)
[![Stars](https://img.shields.io/github/stars/Alrizz-art/ArizenOS?style=flat-square&color=f59e0b)](https://github.com/Alrizz-art/ArizenOS/stargazers)
[![Issues](https://img.shields.io/github/issues/Alrizz-art/ArizenOS?style=flat-square&color=ef4444)](https://github.com/Alrizz-art/ArizenOS/issues)
[![Downloads](https://img.shields.io/github/downloads/Alrizz-art/ArizenOS/total?style=flat-square&color=10b981)](https://github.com/Alrizz-art/ArizenOS/releases)

<br/>

**ArizenOS** transforms a stock Windows installation into a privacy-first, developer-ready desktop — clean, fast, and visually refined. Delivered as a single `.apbx` playbook for [AME Wizard](https://ameliorated.io).

<br/>

[**Download .apbx**](https://github.com/Alrizz-art/ArizenOS/releases/latest) &nbsp;·&nbsp; [Getting Started](#getting-started) &nbsp;·&nbsp; [What's Applied](#whats-applied) &nbsp;·&nbsp; [Contributing](CONTRIBUTING.md)

</div>

---

## Overview

ArizenOS is not a new operating system — it is the **experience layer Windows was never built to be.**

It applies a curated set of registry tweaks, branding assets, and performance optimizations to Windows 10/11 via AME Wizard — transforming the default desktop into a refined, minimal workspace. Every change is tracked and reversible.

---

## Getting Started

### Requirements

| | |
|---|---|
| **AME Wizard** | [Download latest beta](https://git.ameliorated.info/Styris/trusted-uninstaller-cli/releases) |
| **Windows** | 10 22H2 · 11 22H2 · 11 23H2 · 11 24H2 |
| **Updates** | Fully updated before applying |
| **Antivirus** | Disabled during install |
| **Power** | Plugged in |

### Installation

1. Download **AME Wizard** and **ArizenOS.apbx** from [Releases](https://github.com/Alrizz-art/ArizenOS/releases/latest)
2. Launch `AME Wizard Beta.exe`
3. Drag and drop `ArizenOS.apbx` into the Playbooks column
4. Follow all on-screen instructions and click **Next**

> **Backup first.** ArizenOS makes deep system changes. Back up your data before applying.

---

## What's Applied

| Feature | Description |
|---|---|
| **Privacy Hardening** | Disables telemetry, Cortana, activity feed, and advertising ID |
| **Debloat** | Removes pre-installed apps, Xbox services, and sponsored content |
| **Dark Theme** | System-wide dark mode with ArizenOS accent color |
| **Transparency** | Acrylic/mica effects enabled across the shell |
| **Performance** | Disables unnecessary scheduled tasks and background services |
| **OEM Branding** | ArizenOS identity in System Info and About page |
| **Wallpapers** | ArizenOS wallpapers deployed to desktop and lock screen |
| **Developer Mode** | Optional: WSL2, WinGet, Git, VS Code, Node.js *(opt-in)* |

---

## Rollback

ArizenOS ships a rollback configuration. In AME Wizard, load the playbook and select **Rollback** to revert applied changes.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit issues, feature requests, and pull requests.

---

## Security

See [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

---

## License

MIT — see [LICENSE](LICENSE) for full text.
