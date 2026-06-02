/*
 * kernel/include/kernel.h — Core Kernel Definitions
 *
 * Fundamental types, macros, and constants used throughout the kernel.
 * Every kernel source file should include this header.
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */

#ifndef KERNEL_KERNEL_H
#define KERNEL_KERNEL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ── Compiler Attributes ────────────────────────────────────────────────────── */
#define __noreturn      __attribute__((noreturn))
#define __packed        __attribute__((packed))
#define __aligned(n)    __attribute__((aligned(n)))
#define __unused        __attribute__((unused))
#define __used          __attribute__((used))
#define __weak          __attribute__((weak))
#define __section(s)    __attribute__((section(s)))
#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)

/* ── Integer Types ──────────────────────────────────────────────────────────── */
typedef uint8_t     u8;
typedef uint16_t    u16;
typedef uint32_t    u32;
typedef uint64_t    u64;
typedef int8_t      s8;
typedef int16_t     s16;
typedef int32_t     s32;
typedef int64_t     s64;
typedef uintptr_t   paddr_t;    /* Physical address */
typedef uintptr_t   vaddr_t;    /* Virtual address */

/* ── Common Constants ───────────────────────────────────────────────────────── */
#define NULL            ((void *)0)
#define PAGE_SIZE       4096UL
#define PAGE_SHIFT      12UL
#define PAGE_MASK       (~(PAGE_SIZE - 1))

/* Round up/down to page boundary */
#define PAGE_ALIGN_UP(addr)     (((addr) + PAGE_SIZE - 1) & PAGE_MASK)
#define PAGE_ALIGN_DOWN(addr)   ((addr) & PAGE_MASK)

/* Page frame number from physical address */
#define PFN(addr)               ((addr) >> PAGE_SHIFT)

/* ── Error Codes (POSIX-compatible) ─────────────────────────────────────────── */
#define EPERM       1       /* Operation not permitted */
#define ENOENT      2       /* No such file or directory */
#define ESRCH       3       /* No such process */
#define EINTR       4       /* Interrupted system call */
#define EIO         5       /* I/O error */
#define ENXIO       6       /* No such device or address */
#define ENOEXEC     8       /* Exec format error */
#define EBADF       9       /* Bad file number */
#define ENOMEM      12      /* Out of memory */
#define EACCES      13      /* Permission denied */
#define EFAULT      14      /* Bad address */
#define EBUSY       16      /* Device or resource busy */
#define EEXIST      17      /* File exists */
#define ENODEV      19      /* No such device */
#define ENOTDIR     20      /* Not a directory */
#define EISDIR      21      /* Is a directory */
#define EINVAL      22      /* Invalid argument */
#define EMFILE      24      /* Too many open files */
#define ENOSPC      28      /* No space left on device */
#define ENOSYS      38      /* Function not implemented */
#define ENOTSUP     95      /* Operation not supported */

/* ── Utility Macros ─────────────────────────────────────────────────────────── */
#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))
#define MIN(a, b)           ((a) < (b) ? (a) : (b))
#define MAX(a, b)           ((a) > (b) ? (a) : (b))
#define CLAMP(x, lo, hi)    (MIN(MAX(x, lo), hi))
#define IS_ALIGNED(x, a)    (((x) & ((a) - 1)) == 0)
#define ALIGN_UP(x, a)      (((x) + (a) - 1) & ~((a) - 1))
#define ALIGN_DOWN(x, a)    ((x) & ~((a) - 1))

/* Offset of a member within a struct */
#define OFFSET_OF(type, member)     __builtin_offsetof(type, member)

/* Get the containing struct from a pointer to a member */
#define CONTAINER_OF(ptr, type, member) \
    ((type *)((char *)(ptr) - OFFSET_OF(type, member)))

/* ── I/O Port Access (x86) ──────────────────────────────────────────────────── */
static inline void outb(u16 port, u8 value) {
    __asm__ volatile ("outb %0, %1" : : "a"(value), "Nd"(port) : "memory");
}

static inline u8 inb(u16 port) {
    u8 value;
    __asm__ volatile ("inb %1, %0" : "=a"(value) : "Nd"(port) : "memory");
    return value;
}

static inline void outw(u16 port, u16 value) {
    __asm__ volatile ("outw %0, %1" : : "a"(value), "Nd"(port) : "memory");
}

static inline u16 inw(u16 port) {
    u16 value;
    __asm__ volatile ("inw %1, %0" : "=a"(value) : "Nd"(port) : "memory");
    return value;
}

static inline void outl(u16 port, u32 value) {
    __asm__ volatile ("outl %0, %1" : : "a"(value), "Nd"(port) : "memory");
}

static inline u32 inl(u16 port) {
    u32 value;
    __asm__ volatile ("inl %1, %0" : "=a"(value) : "Nd"(port) : "memory");
    return value;
}

/* I/O delay — one I/O write to unused port */
static inline void io_wait(void) {
    outb(0x80, 0);
}

/* ── CPU Control ────────────────────────────────────────────────────────────── */
static inline void cpu_halt(void) {
    __asm__ volatile ("hlt");
}

static inline void cpu_cli(void) {
    __asm__ volatile ("cli" ::: "memory");
}

static inline void cpu_sti(void) {
    __asm__ volatile ("sti" ::: "memory");
}

static inline void cpu_hlt_forever(void) __noreturn;
static inline void cpu_hlt_forever(void) {
    for (;;) {
        cpu_cli();
        cpu_halt();
    }
}

#endif /* KERNEL_KERNEL_H */
