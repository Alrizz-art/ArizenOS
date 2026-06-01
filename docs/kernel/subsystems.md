# Kernel Subsystems Reference — ArizenOS

This document describes each kernel subsystem — its purpose, current status,
design decisions, and key interfaces.

---

## 1. Kernel Core (`kernel/core/`)

### 1.1 Main (`main.c`)

The C entry point for the kernel. Responsible for:
- Initializing all subsystems in a defined order
- Launching the first userspace process (`/sbin/init`)
- Entering the idle loop

Init order is explicit — no constructor magic or registration systems.

### 1.2 Printk (`printk.c`)

Kernel-space printf equivalent. Outputs to:
- VGA text buffer (early boot)
- Serial port (debugging)
- Ring buffer (for dmesg equivalent — future)

Supports format specifiers: `%d`, `%u`, `%x`, `%X`, `%s`, `%p`, `%c`, `%lu`, `%lx`

```c
printk("[kernel] Initialized PMM: %lu pages available\n", free_pages);
```

### 1.3 Panic (`panic.c`)

```c
void panic(const char *fmt, ...);
```

Called on unrecoverable kernel errors. Prints the message, a stack trace,
register dump, and halts the CPU. Never returns.

### 1.4 Syscall Dispatcher (`syscall.c`)

Handles the `syscall` instruction (via MSR LSTAR). Dispatches to the
appropriate handler based on `rax` (syscall number). Linux-compatible
numbering where practical.

---

## 2. Memory Management (`kernel/mm/`)

### 2.1 Physical Memory Manager (PMM) — `pmm.c`

**Algorithm:** Bitmap allocator

- One bit per physical page frame (4 KiB pages)
- `pmm_alloc_frame()` → returns physical address of a free page
- `pmm_free_frame(addr)` → marks page as free
- O(n) worst case, O(1) amortized with next-fit pointer

**Initialization:** Reads the memory map provided by the bootloader (multiboot2)
and marks all non-usable regions as reserved.

### 2.2 Virtual Memory Manager (VMM) — `vmm.c`

Manages the 4-level page table hierarchy (PML4 → PDPT → PD → PT).

```c
int vmm_map(uintptr_t virt, uintptr_t phys, uint64_t flags);
int vmm_unmap(uintptr_t virt);
uintptr_t vmm_virt_to_phys(uintptr_t virt);
```

Flags: `VMM_PRESENT`, `VMM_WRITABLE`, `VMM_USER`, `VMM_NX`, `VMM_GLOBAL`

### 2.3 Heap Allocator — `heap.c`

Kernel heap for dynamic allocation. Implements `kmalloc` / `kfree`.

**Algorithm (planned):** Slab allocator for fixed-size objects,
free-list allocator for variable-size.

```c
void *kmalloc(size_t size);
void *kcalloc(size_t count, size_t size);
void *krealloc(void *ptr, size_t size);
void kfree(void *ptr);
```

---

## 3. Interrupt Handling (`arch/x86_64/kernel/`)

### 3.1 GDT (`gdt.c`)

Global Descriptor Table setup. Defines:
- Null descriptor (required)
- Kernel code segment (ring 0)
- Kernel data segment (ring 0)
- User code segment (ring 3)
- User data segment (ring 3)
- TSS descriptor (for privilege level switches)

### 3.2 IDT (`idt.c`)

Interrupt Descriptor Table. Registers handlers for:
- CPU exceptions (0–31): divide by zero, page fault, GPF, etc.
- IRQ lines (32–47): remapped from PIC
- Syscall vector (0x80): user → kernel transition

### 3.3 PIC / APIC (`pic.c`, `apic.c`)

- **PIC (8259A):** Remaps IRQs to 32–47, used in early boot
- **APIC:** Replaces PIC for multi-core and per-CPU interrupt routing (planned)

---

## 4. Scheduler (`kernel/sched/`)

**v0.3.0:** Preemptive round-robin scheduler
**v0.4.0+:** CFS-inspired priority scheduler

### Task Structure

```c
struct task {
    uint64_t    id;           // PID
    char        name[64];     // Process name
    task_state_t state;       // RUNNING, READY, BLOCKED, ZOMBIE
    uintptr_t   kernel_stack; // Kernel stack pointer
    uintptr_t   user_stack;   // User stack pointer
    uintptr_t   page_table;   // CR3 — physical address of PML4
    int         exit_code;
    struct task *parent;
    // ... signals, file descriptors, etc.
};
```

### Context Switch

Saves/restores: `rax`, `rbx`, `rcx`, `rdx`, `rsi`, `rdi`, `rbp`, `rsp`,
`r8`–`r15`, `rip`, `rflags`, `cr3` (page table switch).

---

## 5. Virtual Filesystem (`kernel/fs/` + `fs/`)

### VFS Interface

Every filesystem implementation provides:

```c
struct fs_ops {
    int (*open)(struct inode *node, struct file *file, int flags);
    int (*close)(struct file *file);
    ssize_t (*read)(struct file *file, void *buf, size_t count, off_t *pos);
    ssize_t (*write)(struct file *file, const void *buf, size_t count, off_t *pos);
    int (*readdir)(struct file *file, struct dirent *entry);
    struct inode *(*lookup)(struct inode *dir, const char *name);
    int (*mkdir)(struct inode *dir, const char *name, mode_t mode);
    int (*unlink)(struct inode *dir, const char *name);
    int (*stat)(struct inode *node, struct stat *statbuf);
};
```

### Mount Table

```c
int vfs_mount(const char *path, struct filesystem *fs);
int vfs_unmount(const char *path);
```

---

## 6. Drivers (`drivers/`)

### Driver Interface

All drivers register with a simple probe/remove pattern:

```c
struct driver {
    const char *name;
    int (*probe)(void);      // Returns 0 if hardware found, -ENODEV if not
    void (*remove)(void);
};
```

### Display Driver (`drivers/display/`)

- **vga.c:** Text-mode 80×25 VGA output (early boot, debug)
- **framebuffer.c:** Linear framebuffer (planned, requires bootloader support)

### Input Driver (`drivers/input/`)

- **ps2_keyboard.c:** PS/2 keyboard via I/O ports 0x60/0x64
- Translates scan codes to key events
- IRQ1 handler

### Storage Drivers (`drivers/storage/`)

- **ahci.c:** AHCI (SATA) — planned for v0.4.0
- **nvme.c:** NVMe over PCIe — planned for v0.4.0

---

## 7. Network Stack (`kernel/net/`)

Planned for v0.4.0. Will implement:

| Layer | Protocol | File |
|-------|---------|------|
| L2 | Ethernet | `net/ethernet.c` |
| L2 | ARP | `net/arp.c` |
| L3 | IPv4 | `net/ipv4.c` |
| L4 | TCP | `net/tcp.c` |
| L4 | UDP | `net/udp.c` |
| Application | DHCP client | `net/dhcp.c` |

---

*Subsystem documentation is added as each subsystem is implemented.*
*If a section is sparse, it means the subsystem is planned but not yet built.*
