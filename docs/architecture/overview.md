# Architecture Overview — ArizenOS

**Document version:** 0.1  
**Last updated:** 2026-06-01  
**Status:** Living document — updated as design evolves

---

## Design Philosophy

ArizenOS is a **monolithic kernel** with a modular internal structure.

Key principles:
1. **Correctness first** — a kernel that crashes is worse than a slow one
2. **Explicit over implicit** — no magic, every behavior is documented
3. **Minimal surface area** — fewer lines of kernel code = fewer bugs
4. **POSIX-compatible** syscall interface where practical
5. **No unnecessary abstractions** — abstract when it pays off, not by default

---

## Target Architecture

| Property     | Value         |
|--------------|---------------|
| Architecture | x86_64        |
| Boot modes   | BIOS (stage 1→2), UEFI (future) |
| CPU mode     | 64-bit long mode |
| Paging       | 4-level (PML4 → PDPT → PD → PT) |
| Min RAM      | 32 MB         |

---

## System Architecture Diagram

```
 User Applications
 ┌──────────────────────────────────────────────────────────┐
 │  /bin/init    /bin/sh    /usr/bin/*    User Programs     │
 └──────────────────────────┬───────────────────────────────┘
                            │ System Calls (int 0x80 / syscall)
 ┌──────────────────────────▼───────────────────────────────┐
 │                  SYSCALL DISPATCHER                       │
 │              kernel/core/syscall.c                        │
 └───┬──────────┬──────────┬──────────┬──────────┬──────────┘
     │          │          │          │          │
 ┌───▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
 │SCHED │  │  MM  │  │  VFS │  │ NET  │  │SECUR │
 │      │  │      │  │      │  │      │  │      │
 │Round │  │Paging│  │mount/│  │TCP/IP│  │Caps/ │
 │Robin │  │Heap  │  │open/ │  │UDP   │  │Perms │
 │→ CFS │  │VMM   │  │read/ │  │DHCP  │  │      │
 └───┬──┘  └───┬──┘  │write │  └───┬──┘  └──────┘
     │         │     └───┬──┘      │
 ┌───▼─────────▼─────────▼─────────▼──────────────────────┐
 │                    KERNEL CORE                           │
 │  GDT  IDT  Interrupts  Timer (PIT/APIC)  Printk  Panic │
 │              kernel/core/                               │
 └──────────────────────────┬──────────────────────────────┘
                            │
 ┌──────────────────────────▼──────────────────────────────┐
 │                      DRIVERS                            │
 │  VGA/Framebuf  PS/2 Kbd  AHCI  NVMe  RTL8139  Serial  │
 │                    drivers/                             │
 └──────────────────────────┬──────────────────────────────┘
                            │
 ┌──────────────────────────▼──────────────────────────────┐
 │                     HARDWARE                            │
 │            x86_64 CPU   RAM   PCI   I/O Ports          │
 └─────────────────────────────────────────────────────────┘
```

---

## Boot Sequence

```
Power On
  │
  ▼
BIOS POST
  │
  ▼
Stage 1 Bootloader (512B, MBR)
  │  Loads Stage 2 from disk
  ▼
Stage 2 Bootloader (GRUB / custom)
  │  1. Enable A20 line
  │  2. Load GDT (32-bit protected mode)
  │  3. Enter protected mode
  │  4. Set up page tables
  │  5. Enter long mode (64-bit)
  │  6. Load kernel ELF into memory
  ▼
Kernel Entry Point  (arch/x86_64/kernel/entry.asm)
  │  Stack setup, BSS clear
  ▼
kernel_main()  (kernel/core/main.c)
  │  1. Initialize serial / VGA output
  │  2. Initialize GDT
  │  3. Initialize IDT + ISRs
  │  4. Initialize PIC / APIC
  │  5. Initialize PIT timer
  │  6. Initialize physical memory manager
  │  7. Initialize virtual memory (paging)
  │  8. Initialize heap allocator
  │  9. Initialize VFS
  │  10. Initialize scheduler
  │  11. Launch /sbin/init (PID 1)
  ▼
Userspace (/sbin/init → /bin/sh)
```

---

## Memory Layout (x86_64)

```
Virtual Address Space (48-bit canonical)
─────────────────────────────────────────

0xFFFF_FFFF_FFFF_FFFF ┐
                       │  Kernel space (higher half)
0xFFFF_8000_0000_0000 ─┤
                       │
  Kernel code/data     │  Mapped at link time
  Kernel heap          │  Dynamic allocation
  Physical memory map  │  1:1 mapped (HHDM)
                       │
0xFFFF_8000_0000_0000 ─┘

0x0000_7FFF_FFFF_FFFF ┐
                       │  User space (lower half)
  User stack           │  Grows downward
  User heap            │  mmap / brk
  User code/data       │  ELF segments
  NULL guard page      │  No mapping at 0x0
0x0000_0000_0000_0000 ─┘
```

---

## Key Subsystems

### Memory Management (`kernel/mm/`)

| Component | File | Purpose |
|-----------|------|---------|
| Physical MM | `pmm.c` | Page frame allocator (bitmap-based) |
| Virtual MM | `vmm.c` | Page table management |
| Heap | `heap.c` | `kmalloc` / `kfree` (slab-like) |
| Paging | `paging.c` | Map/unmap virtual pages |

### Scheduler (`kernel/sched/`)

- **v0.3.0:** Simple round-robin (fixed time quantum)
- **v0.4.0+:** Priority-based preemptive scheduler (CFS-inspired)

### Virtual Filesystem (`kernel/fs/` + `fs/`)

The VFS provides a unified interface over all filesystem implementations:

```
vfs_open() → looks up mount point → calls fs->open()
vfs_read() → dispatches to mounted fs implementation
```

Implementations: `tmpfs` (ram disk), `ext2` (persistent)

### Syscall Interface (`kernel/core/syscall.c`)

Linux-compatible syscall numbers where practical (eases porting tools).
Dispatched via the `syscall` instruction (MSR-based fast path).

---

## Inter-Subsystem Communication

- All subsystems communicate via **well-defined C interfaces** (header files in `kernel/include/`)
- No global mutable state outside designated subsystem-owned structures
- Subsystem init order is **explicit** in `kernel_main()` — no constructor magic

---

## Future Architecture Directions

| Feature | Target Version | Notes |
|---------|---------------|-------|
| SMP (multi-core) | v1.1.0+ | Per-CPU structures, spinlocks |
| UEFI boot | v0.4.0+ | Alongside BIOS support |
| ACPI | v0.4.0+ | Power management, device discovery |
| USB | v1.0.0+ | XHCI controller |
| GPU | Long-term | DRM/KMS-inspired |

---

*This document is maintained alongside the codebase. If you find it outdated, please open an issue or submit a PR.*
