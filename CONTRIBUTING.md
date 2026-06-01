# Contributing to ArizenOS

Thank you for your interest in ArizenOS. We're building something sovereign, composable, and transparent — and we want contributions that share those values.

## Before You Start

1. Read the [Core Principles](docs/PRINCIPLES.md)
2. Check the [Roadmap](docs/ROADMAP.md) to see what's in scope
3. Open an issue before large PRs to discuss approach

## Development Setup

```powershell
# Requires: Windows 10 AME, PowerShell 7+, Git, Rust 1.79+, Python 3.12+, Node 20+
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS
.\scripts\dev-setup.ps1
```

## Code Standards

- **Rust:** `clippy` clean, `rustfmt` formatted
- **Python:** `ruff` linted, `black` formatted, type-annotated
- **TypeScript:** `eslint` clean, `prettier` formatted
- **Commits:** Follow the commit message convention in [NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md)

## Pull Request Process

1. Fork → create branch (`feat/your-feature`)
2. Write tests for new functionality
3. Ensure all checks pass locally
4. Open PR against `dev` branch
5. Fill out the PR template completely

## What We're Looking For

- Features aligned with the v0.x roadmap
- Performance improvements with benchmarks
- Agent implementations (follow agent manifest spec)
- Plugin SDK examples
- Documentation improvements

## What We Won't Merge

- Cloud dependencies in core components
- Telemetry or usage analytics of any kind
- Features that require Microsoft Account or Windows Store
- Breaking changes to the IPC protocol without an RFC
