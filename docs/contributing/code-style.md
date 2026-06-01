# Code Style Guide — ArizenOS

ArizenOS follows a consistent, readable coding style inspired by the Linux kernel
but simplified for clarity.

---

## General Principles

1. **Readability over cleverness** — future maintainers will thank you
2. **Explicit over implicit** — no hidden control flow
3. **One thing per function** — functions should do exactly one thing
4. **Error paths are first-class** — handle errors explicitly, every time

---

## C Style

### Indentation

- **4 spaces** per indent level — no tabs
- Maximum line length: **100 characters**

```c
// ✅ Correct
void kernel_init(void) {
    gdt_init();
    idt_init();
    pic_init();
}

// ❌ Wrong — tabs, wrong brace style
void kernel_init(void)
{
	gdt_init();
}
```

### Naming Conventions

| Thing | Convention | Example |
|-------|-----------|---------|
| Functions | `snake_case` | `page_alloc()`, `vfs_open()` |
| Variables | `snake_case` | `page_count`, `current_task` |
| Constants / Macros | `UPPER_SNAKE_CASE` | `PAGE_SIZE`, `IRQ_TIMER` |
| Types (typedef) | `snake_case_t` | `page_t`, `task_t` |
| Structs (no typedef) | `snake_case` | `struct page`, `struct task` |
| Enum values | `UPPER_SNAKE_CASE` | `MM_ERR_OOM`, `VFS_ERR_NOENT` |
| File names | `snake_case.c/.h` | `page_alloc.c`, `vfs.h` |

### Braces

Always use braces, even for single-line bodies:

```c
// ✅ Correct
if (ptr == NULL) {
    return -EINVAL;
}

// ❌ Wrong
if (ptr == NULL)
    return -EINVAL;
```

### Function Layout

```c
/**
 * page_alloc - Allocate a physical page frame.
 * @flags: Allocation flags (PA_ZEROED, PA_DMA, etc.)
 *
 * Returns the physical address of the allocated page,
 * or 0 on failure (out of memory).
 */
uintptr_t page_alloc(uint32_t flags) {
    if (!pmm_initialized) {
        panic("page_alloc: PMM not initialized");
    }

    uintptr_t page = pmm_alloc_frame();
    if (page == 0) {
        return 0;
    }

    if (flags & PA_ZEROED) {
        memset((void *)page, 0, PAGE_SIZE);
    }

    return page;
}
```

### Error Handling

Return negative error codes (Linux-compatible):

```c
// ✅ Correct — negative errno style
int vfs_open(const char *path, int flags, struct file **out) {
    if (!path) {
        return -EINVAL;
    }

    struct inode *node = vfs_lookup(path);
    if (!node) {
        return -ENOENT;
    }

    *out = file_alloc(node, flags);
    if (!*out) {
        return -ENOMEM;
    }

    return 0;
}
```

### Comments

Use `//` for single-line, `/* */` for blocks, `/** */` for doc comments:

```c
// Single-line explanation

/*
 * Multi-line block comment
 * explaining complex logic.
 */

/**
 * function_name - One-line summary.
 * @param1: Description of param1.
 * @param2: Description of param2.
 *
 * Longer description if needed.
 * Returns 0 on success, negative errno on failure.
 */
```

Do **not** comment the obvious:

```c
// ❌ Useless comment
i++;  // increment i

// ✅ Useful comment
i++;  // advance past the null terminator
```

### Headers

Every `.h` file must have an include guard:

```c
#ifndef KERNEL_MM_PMM_H
#define KERNEL_MM_PMM_H

// ... declarations ...

#endif /* KERNEL_MM_PMM_H */
```

Group includes in this order, separated by blank lines:

```c
// 1. Standard/system headers
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// 2. Kernel headers
#include <kernel/types.h>
#include <kernel/panic.h>

// 3. Subsystem headers
#include <mm/pmm.h>
```

---

## Assembly Style (NASM)

```nasm
; File: arch/x86_64/kernel/entry.asm
; Comments use semicolons

section .text
global kernel_entry

; kernel_entry — ELF entry point from bootloader
; Expects: stack set up, multiboot2 info in RBX
kernel_entry:
    ; Disable interrupts during init
    cli

    ; Set up the kernel stack
    lea rsp, [kernel_stack_top]

    ; Zero BSS segment
    call zero_bss

    ; Enter C kernel
    call kernel_main

    ; Should never return — halt
.halt:
    hlt
    jmp .halt
```

Rules:
- Labels: `snake_case` for local, `UPPER_CASE` for constants
- Indent with 4 spaces
- Comment every non-obvious instruction block

---

## File Header

Every source file should start with:

```c
/*
 * kernel/mm/pmm.c — Physical Memory Manager
 *
 * Manages allocation and freeing of physical page frames.
 * Uses a bitmap to track free/used pages.
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */
```

---

## Git Commit Style

Follow [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<scope>): <short summary in present tense, lowercase, no period>

[optional body — wrap at 72 chars]

[optional footer(s)]
```

Examples:
```
feat(mm): add physical page frame allocator using bitmap
fix(drivers): resolve IRQ conflict between PS/2 and PIC
docs(kernel): document GDT entry format
refactor(sched): extract task_switch into its own function
```

---

## EditorConfig

The project includes `.editorconfig` — install the EditorConfig plugin for your editor
and it will apply these rules automatically.

```ini
[*.{c,h,asm}]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
max_line_length = 100
```
