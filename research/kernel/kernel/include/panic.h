/*
 * kernel/include/panic.h — Kernel Panic Interface
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */

#ifndef KERNEL_PANIC_H
#define KERNEL_PANIC_H

#include <kernel/kernel.h>

/**
 * panic - Halt the system with an error message.
 * @fmt: printf-style format string describing the fatal error
 *
 * Prints the error, a register dump, and a stack trace, then halts.
 * Never returns.
 */
__noreturn void panic(const char *fmt, ...);

/**
 * BUG_ON - Assert a condition is false, panic if true.
 */
#define BUG_ON(cond) \
    do { \
        if (unlikely(cond)) { \
            panic("BUG: %s:%d — condition '%s' is true", \
                  __FILE__, __LINE__, #cond); \
        } \
    } while (0)

/**
 * ASSERT - Assert a condition is true, panic if false.
 */
#define ASSERT(cond) \
    do { \
        if (unlikely(!(cond))) { \
            panic("ASSERT: %s:%d — '%s' failed", \
                  __FILE__, __LINE__, #cond); \
        } \
    } while (0)

/**
 * UNIMPLEMENTED - Mark a code path as not yet implemented.
 */
#define UNIMPLEMENTED() \
    panic("UNIMPLEMENTED: %s:%d in %s()", __FILE__, __LINE__, __func__)

#endif /* KERNEL_PANIC_H */
