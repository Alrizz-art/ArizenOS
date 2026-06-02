/*
 * kernel/include/printk.h — Kernel Printf Interface
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */

#ifndef KERNEL_PRINTK_H
#define KERNEL_PRINTK_H

#include <stdarg.h>

/**
 * printk - Print a formatted string to kernel log outputs.
 * @fmt: printf-style format string
 *
 * Outputs to VGA text buffer and serial port.
 * Safe to call from interrupt context (uses spinlock internally).
 */
void printk(const char *fmt, ...);

/**
 * vprintk - va_list variant of printk.
 */
void vprintk(const char *fmt, va_list args);

#endif /* KERNEL_PRINTK_H */
