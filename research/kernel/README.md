# ArizenOS Kernel Research

> **Status: Experimental — Not the primary product**
> This directory contains an OS kernel prototype. See [ADR-0004](../../docs/architecture/ADR-0004-kernel-research-strategy.md) for context.

---

## What This Is

An experimental bare-metal operating system kernel for `x86_64`, built to explore whether ArizenOS can eventually ship its own kernel alongside the Windows platform product.

This is **research code**, not a shipping product.

---

## Current State

| Component | Status |
|---|---|
| Stage 1 Bootloader (MBR) | ✅ Implemented |
| 64-bit Kernel Entry (ASM) | ✅ Implemented |
| Kernel Main (C) | ✅ Implemented |
| Core Headers (types, I/O ports, macros) | ✅ Implemented |
| GDT / IDT | 🔲 Stubbed |
| Physical Memory Manager | 🔲 Not started |
| Virtual Memory Manager | 🔲 Not started |
| Process Scheduler | 🔲 Not started |
| VFS / Filesystem | 🔲 Not started |
| Userspace / Init | 🔲 Not started |
| Device Drivers | 🔲 Not started |

---

## Directory Structure

```
research/kernel/
├── arch/
│   └── x86_64/
│       ├── boot/
│       │   └── stage1.asm      # 512-byte MBR bootloader
│       ├── kernel/
│       │   └── entry.asm       # 64-bit long mode kernel entry
│       └── include/            # arch-specific headers
├── drivers/
│   ├── display/                # VGA / framebuffer (not started)
│   ├── input/                  # PS/2 keyboard/mouse (not started)
│   ├── net/                    # Network drivers (not started)
│   └── storage/                # ATA / NVMe (not started)
├── fs/
│   ├── ext2/                   # ext2 filesystem (not started)
│   ├── tmpfs/                  # In-memory filesystem (not started)
│   └── vfs/                    # Virtual filesystem layer (not started)
├── kernel/
│   ├── core/
│   │   └── main.c              # C kernel entry point
│   ├── include/
│   │   ├── kernel.h            # Core types, macros, I/O port access
│   │   ├── panic.h             # Kernel panic interface
│   │   ├── printk.h            # Early console output
│   │   └── version.h           # Version definitions
│   ├── mm/                     # Memory manager (not started)
│   ├── sched/                  # Scheduler (not started)
│   ├── net/                    # Network stack (not started)
│   └── security/               # Security subsystem (not started)
├── lib/
│   ├── libc/                   # Freestanding C standard library (not started)
│   └── libk/                   # Kernel utility library (not started)
└── userspace/
    ├── init/                   # PID 1 / init system (not started)
    ├── shell/                  # Minimal shell (not started)
    └── utils/                  # Core userspace utilities (not started)
```

---

## Build Requirements

| Tool | Purpose |
|---|---|
| `x86_64-elf-gcc` | Cross-compiler (no host OS headers) |
| `nasm` | Assembler for `.asm` files |
| `ld` (cross) | Linker |
| `QEMU` | x86_64 emulator for testing |
| `make` | Build system |

> A Makefile and build guide will be added when the kernel reaches a bootable state.

---

## Contributing to Kernel Research

Kernel contributions are handled separately from platform contributions.

- Read [CONTRIBUTING.md](../../CONTRIBUTING.md) for general repository rules.
- For kernel-specific changes, prefix commit scopes with `kernel:`, `bootloader:`, `mm:`, `sched:`, etc.
- All kernel PRs require review from a **Kernel Research Maintainer** (see [GOVERNANCE.md](../../GOVERNANCE.md)).
- Kernel CI (QEMU boot test) will be added when the kernel reaches a runnable state.

---

## Relationship to ArizenOS Platform

The kernel research is **independent** from the Windows platform product:

| | ArizenOS Platform | ArizenOS Kernel Research |
|---|---|---|
| Target OS | Windows 10 / 11 | Bare metal x86_64 |
| Language | TypeScript, React | C, Assembly |
| Build tool | pnpm / Turbo | make / cross-gcc |
| Status | Active development | Early research |
| Audience | End users | Systems programmers |

---

## Future Split

When this kernel reaches the criteria defined in [ADR-0004](../../docs/architecture/ADR-0004-kernel-research-strategy.md#future-split-criteria), it will be extracted into a dedicated `ArizenOS-Kernel` repository.

---

*Part of the [ArizenOS](https://github.com/Alrizz-art/ArizenOS) monorepo — Kernel Research Domain*
