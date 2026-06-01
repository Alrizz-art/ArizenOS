# Release Schedule — ArizenOS

This document outlines the planned release roadmap for ArizenOS.
All dates are targets, not guarantees — open-source timelines may shift.

---

## Roadmap Overview

```
2026-07  ──── v0.1.0 Foundation
2026-09  ──── v0.2.0 Core Systems
2026-11  ──── v0.3.0 Userspace Alpha
2027-01  ──── v0.4.0 Networking & Storage
2027-03  ──── v0.5.0 Beta (Feature Freeze)
2027-06  ──── v1.0.0 Stable Release 🎉
```

---

## Detailed Schedule

### v0.1.0 — Foundation
**Target:** 2026-07-31 | **Status:** 🚧 In Progress

**Goals:**
- Repository structure and build system (Makefile, cross-compiler toolchain)
- Bootloader: BIOS/UEFI support, long mode entry (x86_64)
- Kernel entry point, GDT/IDT setup
- VGA text-mode output (basic `kprintf`)
- CI/CD: build pipeline, automated artifact generation
- GitHub project management: labels, milestones, project boards

**Definition of Done:**
- OS boots to a blank terminal screen
- CI passes on every push to `main`
- Build reproducible from clean environment

---

### v0.2.0 — Core Systems
**Target:** 2026-09-30 | **Status:** 📋 Planned

**Goals:**
- Physical and virtual memory management (paging, page frame allocator)
- Kernel heap allocator (`kmalloc` / `kfree`)
- Interrupt handling (PIC/APIC, IRQ routing)
- Basic keyboard driver (PS/2)
- Basic display driver (VGA/framebuffer)
- Virtual Filesystem (VFS) skeleton

**Definition of Done:**
- Kernel manages its own memory
- Keyboard input echoes to screen
- VFS API defined and tested

---

### v0.3.0 — Userspace Alpha
**Target:** 2026-11-30 | **Status:** 📋 Planned

**Goals:**
- Process scheduler (round-robin, then priority)
- Syscall interface (Linux-compatible subset where practical)
- ELF binary loader
- Basic shell (command parsing, process exec)
- Initial filesystem: tmpfs + ext2 read support

**Definition of Done:**
- First userspace program runs (`/bin/init`, `/bin/sh`)
- `ls`, `echo`, `cat` work
- System call table documented

---

### v0.4.0 — Networking & Storage
**Target:** 2027-01-31 | **Status:** 📋 Planned

**Goals:**
- NVMe / AHCI storage drivers
- Persistent filesystem (ext2 read/write or custom)
- Network stack: Ethernet, ARP, IP, TCP/UDP
- DHCP client
- Package management foundation (package format defined)

**Definition of Done:**
- File persistence across reboots
- `ping` works
- `wget` or basic HTTP GET works

---

### v0.5.0 — Beta
**Target:** 2027-03-31 | **Status:** 📋 Planned

**Goals:**
- **Feature freeze** — no new subsystems after this milestone
- Security audit pass (privilege separation, kernel hardening)
- Comprehensive documentation (kernel API, syscall reference, contributor guide)
- Full CI/CD with integration tests
- ISO image build pipeline
- Performance profiling and bottleneck fixes

**Definition of Done:**
- Zero known critical or high-priority bugs
- All documentation complete
- ISO boots on QEMU + real hardware (x86_64)

---

### v1.0.0 — Stable Release
**Target:** 2027-06-30 | **Status:** 📋 Planned

**Goals:**
- First publicly announced stable release
- Stable ABI guarantee (MAJOR version locked until breaking change)
- Official announcement + release notes
- Signed ISO image with checksums
- Long-term support (LTS) policy defined

**Definition of Done:**
- `v1.0.0` tag pushed and GitHub Release created
- ISO published to GitHub Releases
- Announcement posted

---

## Release Process

1. **Feature Freeze** — open `release/vX.Y.Z` branch from `develop`
2. **Testing Phase** — run full CI, manual boot tests on QEMU and hardware
3. **Release Candidate** — tag `vX.Y.Z-rc.N`, announce for community testing
4. **Stable Tag** — merge to `main`, tag `vX.Y.Z`, publish GitHub Release
5. **Changelog** — update `CHANGELOG.md` with all notable changes
6. **Announce** — post release notes to GitHub Discussions / project channels

---

## Hotfix Process

For critical security or crash bugs in stable releases:

1. Branch `hotfix/<description>` from `main`
2. Fix, test, and review
3. Merge to `main` AND back-merge to `develop`
4. Increment PATCH version and tag
5. Publish GitHub Release with security advisory if applicable
