<div align="center">

<br/>

```
    ___         _                    ___  _____
   / _ \  _ __ (_) ____ ___  _ __  / _ \/ ___|
  / /_\ \| '__|| ||_  // _ \| '_ \| | | \___ \
 / /   \ | |   | | / /|  __/| | | | |_| |___) |
/_/     \_|_|  |_|/_/  \___||_| |_|\___/|____/
```

**A Modern, Open-Source Operating System Built from Scratch**

<br/>

[![Build Status](https://github.com/Alrizz-art/ArizenOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Alrizz-art/ArizenOS/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Alrizz-art/ArizenOS?include_prereleases&color=blue)](https://github.com/Alrizz-art/ArizenOS/releases)
[![License](https://img.shields.io/github/license/Alrizz-art/ArizenOS?color=green)](LICENSE)
[![Issues](https://img.shields.io/github/issues/Alrizz-art/ArizenOS)](https://github.com/Alrizz-art/ArizenOS/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Milestone](https://img.shields.io/badge/milestone-v0.1.0_Foundation-orange)](https://github.com/Alrizz-art/ArizenOS/milestones)
[![Architecture](https://img.shields.io/badge/arch-x86__64-lightgrey)](docs/architecture/overview.md)
[![Conventional Commits](https://img.shields.io/badge/commits-conventional-fe5196)](https://www.conventionalcommits.org)

<br/>

[📖 Documentation](docs/) · [🐛 Report Bug](https://github.com/Alrizz-art/ArizenOS/issues/new?template=bug_report.md) · [✨ Request Feature](https://github.com/Alrizz-art/ArizenOS/issues/new?template=feature_request.md) · [🔒 Security Policy](SECURITY.md) · [💬 Discussions](https://github.com/Alrizz-art/ArizenOS/discussions)

</div>

---

## Overview

**ArizenOS** is an open-source, x86_64 operating system built entirely from scratch — designed for learning, research, and eventually real-world use. It is engineered with clarity, correctness, and international open-source standards at its core.

> *"An operating system built not just to run, but to be understood."*

### Goals

- **Correctness over speed** — every design decision is documented and justified
- **Minimal dependencies** — custom implementations over third-party code where practical
- **Open development** — all design decisions happen in the open via issues and discussions
- **POSIX-compatible** where it makes sense — familiar syscall interface from day one

---

## Current Status

> ⚠️ **ArizenOS is in early development (pre-alpha).** It does not yet boot a full userspace. See the [roadmap](#roadmap) for what's planned.

| Component       | Status         | Milestone       |
|-----------------|----------------|-----------------|
| Build System    | 🔨 In Progress | v0.1.0          |
| Bootloader      | 🔨 In Progress | v0.1.0          |
| Kernel Entry    | 🔨 In Progress | v0.1.0          |
| Memory Manager  | 📋 Planned     | v0.2.0          |
| Process Sched.  | 📋 Planned     | v0.3.0          |
| Syscall Layer   | 📋 Planned     | v0.3.0          |
| Network Stack   | 📋 Planned     | v0.4.0          |
| Shell           | 📋 Planned     | v0.3.0          |

---

## Architecture

ArizenOS targets **x86_64** (64-bit) and is designed as a **monolithic kernel** with modular subsystems.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERSPACE                               │
│   [ Shell ]  [ Init ]  [ Utilities ]  [ Future Applications ]  │
├─────────────────────────────────────────────────────────────────┤
│                    SYSCALL INTERFACE                             │
├──────────────┬──────────────┬───────────────┬───────────────────┤
│   SCHEDULER  │    MEMORY    │  FILESYSTEM   │    NETWORKING     │
│  (Round-Rob) │  (Paging +   │  (VFS + ext2/ │  (TCP/IP Stack)  │
│              │   Heap Alloc)│   tmpfs)      │                  │
├──────────────┴──────────────┴───────────────┴───────────────────┤
│                      KERNEL CORE                                 │
│     [ GDT/IDT ]  [ IRQ Routing ]  [ Timer ]  [ Syscall Disp ] │
├─────────────────────────────────────────────────────────────────┤
│                        DRIVERS                                   │
│    [ VGA/Framebuffer ]  [ PS/2 Keyboard ]  [ AHCI ]  [ NVMe ] │
├─────────────────────────────────────────────────────────────────┤
│                       BOOTLOADER                                 │
│          [ BIOS Stage 1 → Stage 2 → Long Mode → Kernel ]       │
└─────────────────────────────────────────────────────────────────┘
                         HARDWARE (x86_64)
```

See [Architecture Overview](docs/architecture/overview.md) for the full design document.

---

## Roadmap

| Milestone | Version | Target | Description |
|-----------|---------|--------|-------------|
| Foundation | `v0.1.0` | Jul 2026 | Build system, bootloader, kernel entry, VGA output |
| Core Systems | `v0.2.0` | Sep 2026 | Paging, heap allocator, IRQ handling, keyboard driver |
| Userspace Alpha | `v0.3.0` | Nov 2026 | Scheduler, syscalls, ELF loader, basic shell |
| Networking & Storage | `v0.4.0` | Jan 2027 | NVMe/AHCI, TCP/IP stack, persistent filesystem |
| Beta | `v0.5.0` | Mar 2027 | Feature freeze, security hardening, full CI |
| **Stable** | **`v1.0.0`** | **Jun 2027** | **First stable public release** |

→ [Full release schedule](RELEASE_SCHEDULE.md) · [All milestones](https://github.com/Alrizz-art/ArizenOS/milestones)

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| `x86_64-elf-gcc` | ≥ 13.0 | Cross-compiler |
| `nasm` | ≥ 2.15 | x86 assembler |
| `qemu-system-x86_64` | ≥ 8.0 | Emulator for testing |
| `make` | ≥ 4.3 | Build orchestration |
| `xorriso` | ≥ 1.5 | ISO image creation |
| `grub-pc-bin` | Any | Bootloader tools |

### Install Dependencies (Ubuntu / Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential nasm xorriso \
    grub-pc-bin grub-common mtools \
    qemu-system-x86
```

For the cross-compiler, see [Toolchain Setup](docs/contributing/development-setup.md#toolchain).

### Build & Run

```bash
# Clone the repository
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS

# Build the OS
make all

# Run in QEMU
make run

# Build an ISO image
make iso

# Run tests
make test
```

### QEMU Options

```bash
# Run with serial output to terminal
make run QEMU_EXTRA="-serial stdio"

# Run with 512MB RAM
make run QEMU_EXTRA="-m 512M"

# Run with KVM acceleration (Linux only)
make run QEMU_EXTRA="-enable-kvm"
```

---

## Repository Structure

```
ArizenOS/
├── arch/                    # Architecture-specific code
│   └── x86_64/
│       ├── boot/            # Bootloader (Stage 1, Stage 2, UEFI)
│       ├── kernel/          # Arch-specific kernel code (GDT, IDT, paging)
│       └── include/         # Arch-specific headers
├── kernel/                  # Architecture-independent kernel
│   ├── core/                # Core kernel (main, panic, printk)
│   ├── mm/                  # Memory management
│   ├── sched/               # Process scheduler
│   ├── fs/                  # VFS layer
│   ├── net/                 # Network stack
│   ├── security/            # Security subsystem
│   └── include/             # Kernel headers
├── drivers/                 # Hardware drivers
│   ├── display/             # VGA / framebuffer
│   ├── input/               # Keyboard, mouse
│   ├── storage/             # AHCI, NVMe
│   └── net/                 # Network interface drivers
├── fs/                      # Filesystem implementations
│   ├── vfs/                 # Virtual Filesystem core
│   ├── tmpfs/               # In-memory filesystem
│   └── ext2/                # ext2 read/write support
├── lib/                     # Shared libraries
│   ├── libk/                # Kernel-only runtime library
│   └── libc/                # Minimal C standard library (for userspace)
├── userspace/               # Userspace programs
│   ├── init/                # Init process (PID 1)
│   ├── shell/               # ArizenSH — the system shell
│   └── utils/               # Core utilities (ls, cat, echo, ps)
├── tests/                   # Test suite
│   ├── unit/                # Unit tests (per subsystem)
│   └── integration/         # Boot and integration tests
├── tools/                   # Developer tooling
│   ├── toolchain/           # Cross-compiler setup scripts
│   └── debug/               # GDB helpers, QEMU debug scripts
├── scripts/                 # Build and CI scripts
│   ├── build/               # Build helpers
│   └── ci/                  # CI-specific scripts
├── docs/                    # Documentation
│   ├── architecture/        # System design documents
│   ├── kernel/              # Kernel subsystem references
│   ├── contributing/        # Contributor guides
│   ├── playbooks/           # Operational playbooks
│   └── api/                 # Syscall and API reference
├── branding/                # Brand assets
│   ├── logo/                # Logo files (SVG, PNG)
│   └── assets/              # Screenshots, banners
├── .github/                 # GitHub configuration
│   ├── workflows/           # GitHub Actions
│   ├── ISSUE_TEMPLATE/      # Issue templates
│   └── assets/              # GitHub-specific images
├── Makefile                 # Top-level build system
├── README.md
├── CHANGELOG.md
├── VERSIONING.md
├── RELEASE_SCHEDULE.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── LICENSE                  # MIT License
```

---

## Contributing

We welcome contributions of all kinds — code, documentation, testing, design, and ideas.

1. Read the [Contributing Guide](CONTRIBUTING.md)
2. Check [open issues](https://github.com/Alrizz-art/ArizenOS/issues) or [discussions](https://github.com/Alrizz-art/ArizenOS/discussions)
3. Fork → Branch → Commit (following [Conventional Commits](https://www.conventionalcommits.org)) → PR

All commits must pass CI and receive at least one review before merging.

→ [Development Setup](docs/contributing/development-setup.md) · [Code Style Guide](docs/contributing/code-style.md)

---

## Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/Alrizz-art/ArizenOS/issues) | Bug reports, feature requests |
| [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions) | General questions, ideas, announcements |
| [Security Advisories](https://github.com/Alrizz-art/ArizenOS/security/advisories) | Private vulnerability reports |

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

---

## License

ArizenOS is released under the **MIT License**.
See [LICENSE](LICENSE) for the full text.

---

## Acknowledgments

ArizenOS is inspired by and learns from:

- [OSDev Wiki](https://wiki.osdev.org/) — the canonical open-source OS development reference
- [Linux Kernel](https://kernel.org/) — the gold standard for kernel engineering
- [SerenityOS](https://github.com/SerenityOS/serenity) — proving that ambitious OS projects can happen in the open
- [xv6](https://github.com/mit-pdos/xv6-riscv) — clarity and simplicity in kernel design
- [MINIX 3](https://www.minix3.org/) — microkernel design principles

---

<div align="center">

Built with dedication by [@Alrizz-art](https://github.com/Alrizz-art) and [contributors](https://github.com/Alrizz-art/ArizenOS/graphs/contributors)

**[⬆ Back to Top](#arizenos)**

</div>
