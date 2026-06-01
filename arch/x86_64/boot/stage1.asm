; ==============================================================================
; ArizenOS — Stage 1 Bootloader
; arch/x86_64/boot/stage1.asm
;
; 512-byte MBR bootloader. Loaded by BIOS at 0x7C00.
; Responsibility: load Stage 2 from disk, jump to it.
;
; SPDX-License-Identifier: MIT
; Copyright (c) 2026 ArizenOS Contributors
; ==============================================================================

[BITS 16]
[ORG 0x7C00]

; ── Entry Point ───────────────────────────────────────────────────────────────
start:
    cli                         ; Disable interrupts
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00              ; Stack grows downward from our load address
    sti                         ; Re-enable interrupts

    ; Save boot drive number (BIOS passes it in DL)
    mov [boot_drive], dl

    ; TODO: Load Stage 2 from disk using INT 13h
    ; For now, print a placeholder message and halt

    mov si, msg_boot
.print_loop:
    lodsb
    test al, al
    jz .halt
    mov ah, 0x0E
    int 0x10
    jmp .print_loop

.halt:
    cli
    hlt
    jmp .halt

; ── Data ──────────────────────────────────────────────────────────────────────
msg_boot    db "ArizenOS Stage 1 Bootloader", 0x0D, 0x0A, 0
boot_drive  db 0

; ── MBR Padding & Signature ───────────────────────────────────────────────────
times 510 - ($ - $$) db 0      ; Pad to 510 bytes
dw 0xAA55                       ; MBR boot signature
