# Contributing to ArizenOS

Thank you for contributing to ArizenOS. This guide covers both contribution domains in this repository.

---

## Two Domains — Two Workflows

This repository contains two distinct domains:

| Domain | Location | Language | Audience |
|---|---|---|---|
| **ArizenOS Platform** | `apps/`, `packages/`, `branding/`, `playbook/` | TypeScript, React | Platform developers |
| **Kernel Research** | `research/kernel/` | C, Assembly | Systems programmers |

**Read the relevant section below for your domain.** The toolchains, review processes, and maintainers are different.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).
Be respectful, inclusive, and constructive. Harassment of any kind will not be tolerated.

---

## Platform Contributions (TypeScript / Windows)

### Prerequisites

- Node.js 18+
- pnpm 8+
- Windows 10 (build 19041+) or Windows 11 (for app testing)

### Setup

```bash
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS
pnpm install
pnpm build
```

### How to Contribute

1. Check [existing issues](https://github.com/Alrizz-art/ArizenOS/issues) first
2. Fork the repository
3. Create a branch from `develop` (see [Branch Naming](#branch-naming))
4. Make your changes
5. Ensure the build passes: `pnpm build`
6. Open a Pull Request against `develop`

---

## Kernel Research Contributions (C / Assembly)

### Prerequisites

- `x86_64-elf-gcc` cross-compiler
- `nasm` assembler
- `QEMU` (x86_64)
- `make`

All kernel research code lives in `research/kernel/`. See [`research/kernel/README.md`](research/kernel/README.md) for the full setup guide.

### How to Contribute

1. All kernel PRs **must target** the `research/kernel/` subtree — do not modify platform code in a kernel PR
2. Kernel PRs require review from a **Kernel Research Maintainer** (see [GOVERNANCE.md](GOVERNANCE.md))
3. Use `kernel:` commit scope prefix (e.g., `feat(kernel/mm): add page frame allocator`)

---

## Branch Naming

```
<type>/<scope>/<short-description>
```

| Prefix | Use for |
|---|---|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `hotfix/` | Critical fixes on stable |
| `chore/` | Tooling, CI, maintenance |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring |
| `release/` | Release preparation |
| `research/` | Kernel research work |

Examples:
- `feature/launcher/spotlight-redesign`
- `fix/assistant/context-overflow`
- `research/kernel/mm-page-allocator`
- `docs/kernel/scheduler-design`

---

## Commit Message Convention

ArizenOS uses **Conventional Commits** ([conventionalcommits.org](https://www.conventionalcommits.org)).

### Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes only |
| `style` | Code style / formatting |
| `refactor` | Restructuring, no behavior change |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system changes |
| `ci` | CI/CD pipeline changes |
| `chore` | Maintenance tasks |
| `revert` | Reverting a previous commit |
| `security` | Security fix or hardening |

### Platform Scopes

`launcher`, `assistant`, `voice`, `hub`, `agent`, `glass`, `mind`, `shell`, `ui`, `skin`, `core`, `flow`, `sync`, `branding`, `playbook`, `ci`, `build`

### Kernel Research Scopes

`kernel`, `kernel/mm`, `kernel/sched`, `kernel/net`, `bootloader`, `drivers`, `fs`, `userspace`

### Examples

```
feat(launcher): add AI-powered spotlight search

fix(glass): resolve compositor flicker on multi-monitor

feat(kernel/mm): add physical page frame allocator

docs(kernel): document VFS mount interface design

BREAKING CHANGE: playbook schema v2 replaces v1 entry format
```

---

## Pull Request Process

1. **Target branch**: always `develop` (never `main` directly)
2. **Title**: follow Conventional Commits format
3. **Description**: fill in the PR template
4. **Labels**: apply `type:`, `scope:`, and `size:` labels
5. **Review**: at least one maintainer approval required
   - Platform PRs → Platform Maintainer
   - Kernel PRs → Kernel Research Maintainer
6. **CI**: all checks must pass before merge

---

## Issue Guidelines

### Title Format

```
[type][scope] Short description
```

Examples:
- `[bug][launcher] Crashes on Windows 10 with multiple displays`
- `[feature][assistant] Support multi-turn context in chat`
- `[research][kernel/mm] Design for physical memory manager`

---

## Labels Reference

| Label | Meaning |
|---|---|
| `type: bug` | Something isn't working |
| `type: feature` | New feature request |
| `type: research` | Kernel/OS research item |
| `domain: platform` | Platform (Windows) domain |
| `domain: kernel` | Kernel research domain |
| `priority: critical` | Must fix immediately |
| `priority: high` | Fix soon |
| `status: in-progress` | Being worked on |
| `size: xs/s/m/l/xl` | Estimated effort |
