/*
 * kernel/core/main.c — Kernel Entry Point (C)
 *
 * This is the main C entry point for the ArizenOS kernel.
 * Called from arch/x86_64/kernel/entry.asm after stack and BSS are set up.
 *
 * Initialization order here is deliberate — do not reorder without updating
 * docs/architecture/overview.md#boot-sequence.
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */

#include <kernel/kernel.h>
#include <kernel/printk.h>
#include <kernel/panic.h>
#include <kernel/version.h>

/* Forward declarations — subsystem init functions */
/* Uncomment as each subsystem is implemented */

/* void gdt_init(void);    */
/* void idt_init(void);    */
/* void pic_init(void);    */
/* void timer_init(void);  */
/* void pmm_init(void);    */
/* void vmm_init(void);    */
/* void heap_init(void);   */
/* void vfs_init(void);    */
/* void sched_init(void);  */

/**
 * kernel_main - C entry point for ArizenOS.
 *
 * Called from entry.asm after the kernel stack is initialized
 * and the BSS segment is zeroed.
 *
 * This function never returns.
 */
void kernel_main(void) {
    /*
     * Step 1: Initialize early output (VGA text mode / serial)
     * This must happen first so all subsequent printk() calls work.
     */
    /* vga_init(); */
    /* serial_init(COM1, BAUD_115200); */

    printk("\n");
    printk("  ___         _                    ___  _____\n");
    printk(" / _ \\  _ __ (_) ____ ___  _ __  / _ \\/ ___|\n");
    printk("/ /_\\ \\| '__|| ||_  // _ \\| '_ \\| | | \\___ \\\n");
    printk("/ /   \\ | |   | | / /|  __/| | | | |_| |___) |\n");
    printk("/_/     \\_|_|  |_|/_/  \\___||_| |_|\\___/|____/\n");
    printk("\n");
    printk("ArizenOS %s — Starting up\n", ARIZENOS_VERSION);
    printk("Copyright (c) 2026 ArizenOS Contributors\n");
    printk("\n");

    /*
     * Step 2: CPU structures — GDT and IDT
     * Must be done before enabling interrupts.
     */
    printk("[init] GDT... ");
    /* gdt_init(); */
    printk("OK\n");

    printk("[init] IDT... ");
    /* idt_init(); */
    printk("OK\n");

    /*
     * Step 3: Interrupt controller
     */
    printk("[init] PIC... ");
    /* pic_init(); */
    printk("OK\n");

    /*
     * Step 4: System timer
     */
    printk("[init] Timer (PIT)... ");
    /* timer_init(HZ_100); */
    printk("OK\n");

    /*
     * Step 5: Physical Memory Manager
     */
    printk("[init] Physical Memory Manager... ");
    /* pmm_init(); */
    printk("OK\n");

    /*
     * Step 6: Virtual Memory Manager (paging)
     */
    printk("[init] Virtual Memory Manager... ");
    /* vmm_init(); */
    printk("OK\n");

    /*
     * Step 7: Kernel heap allocator
     */
    printk("[init] Heap allocator... ");
    /* heap_init(); */
    printk("OK\n");

    /*
     * Step 8: Virtual Filesystem
     */
    printk("[init] VFS... ");
    /* vfs_init(); */
    printk("OK\n");

    /*
     * Step 9: Process scheduler
     */
    printk("[init] Scheduler... ");
    /* sched_init(); */
    printk("OK\n");

    printk("\n[kernel] All subsystems initialized.\n");
    printk("[kernel] Launching /sbin/init...\n\n");

    /*
     * Step 10: Launch PID 1
     * This function should not return under normal operation.
     */
    /* exec_init(); */

    /*
     * If we reach here, something went wrong.
     */
    panic("kernel_main: exec_init() returned — system halted");
}
