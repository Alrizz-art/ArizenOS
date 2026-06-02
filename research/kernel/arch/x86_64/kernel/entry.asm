; ==============================================================================
; ArizenOS — Kernel Entry Point
; arch/x86_64/kernel/entry.asm
;
; This is the first kernel code that runs after the bootloader jumps to us.
; We are in 64-bit long mode. Set up the kernel stack, clear BSS, then
; call kernel_main().
;
; SPDX-License-Identifier: MIT
; Copyright (c) 2026 ArizenOS Contributors
; ==============================================================================

[BITS 64]

; ── External Symbols ──────────────────────────────────────────────────────────
extern kernel_main              ; C entry point
extern bss_start                ; Provided by linker script
extern bss_end                  ; Provided by linker script

; ── Exported Symbols ──────────────────────────────────────────────────────────
global kernel_entry

; ── Kernel Stack ──────────────────────────────────────────────────────────────
section .bss
align 16
kernel_stack_bottom:
    resb 65536                  ; 64 KiB kernel stack
kernel_stack_top:

; ── Entry Point ───────────────────────────────────────────────────────────────
section .text
kernel_entry:
    ; Set up kernel stack
    lea rsp, [rel kernel_stack_top]
    xor rbp, rbp                ; Clear frame pointer (marks stack bottom for GDB)

    ; Clear BSS segment
    lea rdi, [rel bss_start]
    lea rcx, [rel bss_end]
    sub rcx, rdi                ; rcx = BSS size in bytes
    xor eax, eax
    rep stosb                   ; Fill BSS with zeros

    ; Call the C kernel main
    ; rdi = multiboot2 magic (if passed from bootloader)
    ; rsi = multiboot2 info pointer (if passed from bootloader)
    call kernel_main

    ; kernel_main should never return
    ; If it does, halt the CPU
.hang:
    cli
    hlt
    jmp .hang
