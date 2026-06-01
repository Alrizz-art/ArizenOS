# Contributing to ArizenOS

Thank you for your interest in contributing to **ArizenOS** — an open-source operating system built from scratch.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Branch Naming](#branch-naming)
5. [Commit Message Convention](#commit-message-convention)
6. [Pull Request Process](#pull-request-process)
7. [Issue Guidelines](#issue-guidelines)
8. [Labels Reference](#labels-reference)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).
Be respectful, inclusive, and constructive. Harassment of any kind will not be tolerated.

---

## Getting Started

### Prerequisites

- `x86_64-elf` cross-compiler (GCC or Clang)
- `nasm` or `gas` assembler
- `QEMU` for testing
- `make` / `cmake`
- `git`

### Setup

```bash
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS
# Follow build instructions in README.md
make all
make run   # Launches in QEMU
```

---

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/Alrizz-art/ArizenOS/issues) first
2. Open a new issue with label `type: bug`
3. Include: OS version, steps to reproduce, expected vs actual behavior
4. Attach logs or screenshots if applicable

### Suggesting Features

1. Open an issue with label `type: feature`
2. Describe the problem it solves and proposed solution
3. A maintainer will triage and assign a milestone

### Submitting Code

1. Fork the repository
2. Create a branch from `develop` (see [Branch Naming](#branch-naming))
3. Make your changes
4. Ensure the build passes: `make all`
5. Open a Pull Request against `develop`

---

## Branch Naming

```
<type>/<short-description>
```

| Prefix      | Use for                                       |
|-------------|-----------------------------------------------|
| `feature/`  | New features (`feature/virtual-memory`)       |
| `fix/`      | Bug fixes (`fix/keyboard-irq-handler`)        |
| `hotfix/`   | Critical fixes on stable (`hotfix/cve-2027-x`)|
| `chore/`    | Tooling, CI, docs (`chore/update-makefile`)   |
| `docs/`     | Documentation only (`docs/syscall-reference`) |
| `refactor/` | Code restructuring (`refactor/vfs-layer`)     |
| `release/`  | Release prep (`release/v0.2.0`)               |

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

| Type       | When to use                                |
|------------|--------------------------------------------|
| `feat`     | New feature or capability                  |
| `fix`      | Bug fix                                    |
| `docs`     | Documentation changes only                 |
| `style`    | Code style (whitespace, formatting)        |
| `refactor` | Code restructuring, no behavior change     |
| `perf`     | Performance improvement                    |
| `test`     | Adding or fixing tests                     |
| `build`    | Build system or toolchain changes          |
| `ci`       | CI/CD pipeline changes                     |
| `chore`    | Other maintenance tasks                    |
| `revert`   | Reverting a previous commit                |
| `security` | Security fix or hardening                  |

### Scopes

| Scope         | Area                         |
|---------------|------------------------------|
| `kernel`      | Core kernel                  |
| `bootloader`  | Boot process                 |
| `drivers`     | Hardware drivers             |
| `fs`          | Filesystem                   |
| `mm`          | Memory management            |
| `net`         | Networking                   |
| `userspace`   | Userspace and applications   |
| `shell`       | Shell and CLI                |
| `ui`          | Display / UI layer           |
| `security`    | Security subsystem           |
| `build`       | Build system                 |
| `ci`          | CI/CD                        |

### Examples

```
feat(kernel): add round-robin process scheduler

fix(drivers): resolve PS/2 keyboard IRQ conflict with PIC

docs(fs): document VFS mount/unmount interface

security(mm): add stack-smashing protection to kernel heap

BREAKING CHANGE: syscall numbers renumbered for POSIX alignment
```

### Breaking Changes

Append `BREAKING CHANGE:` in the commit footer or add `!` after the type:

```
feat(kernel)!: renumber syscall table for POSIX alignment

BREAKING CHANGE: all syscall numbers have changed. Userspace binaries
must be recompiled against the new headers.
```

---

## Pull Request Process

1. **Target branch**: always `develop` (never `main` directly, except hotfixes)
2. **Title**: follow commit convention (`feat(kernel): add scheduler`)
3. **Description**: fill in the PR template — what, why, how tested
4. **Labels**: apply appropriate `type:`, `scope:`, and `size:` labels
5. **Milestone**: link to the appropriate milestone
6. **Review**: at least one maintainer approval required
7. **CI**: all checks must pass before merge
8. **Squash or rebase** preferred over merge commits

---

## Issue Guidelines

### Issue Title Format

```
[type] Short description of the problem or feature
```

Examples:
- `[bug] Kernel panics on APIC init with multiple CPUs`
- `[feature] Add ext4 filesystem read support`
- `[docs] Missing syscall reference for sys_read`

### Required Information

For bugs:
- ArizenOS version or commit hash
- Architecture (x86_64)
- Steps to reproduce
- Expected vs actual behavior
- QEMU command used (if applicable)
- Kernel log output

---

## Labels Reference

| Label                   | Meaning                                     |
|-------------------------|---------------------------------------------|
| `type: bug`             | Something isn't working                     |
| `type: feature`         | New feature or request                      |
| `type: security`        | Security issue                              |
| `priority: critical`    | Must fix immediately                        |
| `priority: high`        | Fix soon                                    |
| `status: in-progress`   | Being worked on                             |
| `status: needs-review`  | Waiting for review                          |
| `status: blocked`       | Blocked by dependency                       |
| `scope: kernel`         | Kernel component                            |
| `scope: drivers`        | Hardware drivers                            |
| `size: xs/s/m/l/xl`     | Estimated effort                            |

See all labels at: [github.com/Alrizz-art/ArizenOS/labels](https://github.com/Alrizz-art/ArizenOS/labels)
