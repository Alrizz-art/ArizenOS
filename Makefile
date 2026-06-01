# ==============================================================================
# ArizenOS — Top-Level Makefile
# ==============================================================================
# Usage:
#   make all      — Build the entire OS
#   make run      — Build and launch in QEMU
#   make iso      — Build a bootable ISO image
#   make clean    — Remove build artifacts
#   make test     — Run the test suite
#   make help     — Show this help message
# ==============================================================================

# ── Toolchain ─────────────────────────────────────────────────────────────────
ARCH           := x86_64
TARGET         := $(ARCH)-elf
CC             := $(TARGET)-gcc
AS             := nasm
LD             := $(TARGET)-ld
AR             := $(TARGET)-ar
OBJCOPY        := $(TARGET)-objcopy

# ── Directories ───────────────────────────────────────────────────────────────
BUILD_DIR      := build
ISO_DIR        := $(BUILD_DIR)/iso
KERNEL_BIN     := $(BUILD_DIR)/arizenos.elf
ISO_IMAGE      := $(BUILD_DIR)/arizenos.iso

# ── Compiler Flags ────────────────────────────────────────────────────────────
CFLAGS         := \
    -std=gnu11 \
    -ffreestanding \
    -fno-stack-protector \
    -fno-stack-check \
    -fno-pic \
    -fno-pie \
    -mno-red-zone \
    -mno-mmx \
    -mno-sse \
    -mno-sse2 \
    -Wall \
    -Wextra \
    -Wpedantic \
    -Werror \
    -O2 \
    -g \
    -Ikernel/include \
    -Iarch/$(ARCH)/include

ASFLAGS        := -f elf64

LDFLAGS        := \
    -nostdlib \
    -static \
    -z max-page-size=0x1000 \
    -T arch/$(ARCH)/kernel/linker.ld

# ── QEMU ──────────────────────────────────────────────────────────────────────
QEMU           := qemu-system-x86_64
QEMU_FLAGS     := \
    -m 256M \
    -cpu qemu64 \
    -machine q35 \
    -no-reboot \
    -no-shutdown \
    $(QEMU_EXTRA)

# ── Source Discovery ──────────────────────────────────────────────────────────
KERNEL_C_SRCS  := $(shell find kernel/ arch/$(ARCH)/kernel/ drivers/ fs/ lib/libk/ -name '*.c' 2>/dev/null)
KERNEL_ASM_SRCS:= $(shell find arch/$(ARCH)/ -name '*.asm' 2>/dev/null)

KERNEL_OBJS    := \
    $(patsubst %.c,$(BUILD_DIR)/%.o,$(KERNEL_C_SRCS)) \
    $(patsubst %.asm,$(BUILD_DIR)/%.o,$(KERNEL_ASM_SRCS))

# ── Default Target ────────────────────────────────────────────────────────────
.PHONY: all
all: $(KERNEL_BIN)
	@echo "  BUILD   ArizenOS kernel: $(KERNEL_BIN)"

# ── Kernel Link ───────────────────────────────────────────────────────────────
$(KERNEL_BIN): $(KERNEL_OBJS)
	@mkdir -p $(dir $@)
	@echo "  LD      $@"
	$(LD) $(LDFLAGS) -o $@ $^

# ── Compile C ─────────────────────────────────────────────────────────────────
$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	@echo "  CC      $<"
	$(CC) $(CFLAGS) -c $< -o $@

# ── Assemble ──────────────────────────────────────────────────────────────────
$(BUILD_DIR)/%.o: %.asm
	@mkdir -p $(dir $@)
	@echo "  AS      $<"
	$(AS) $(ASFLAGS) $< -o $@

# ── ISO Image ─────────────────────────────────────────────────────────────────
.PHONY: iso
iso: $(KERNEL_BIN)
	@mkdir -p $(ISO_DIR)/boot/grub
	cp $(KERNEL_BIN) $(ISO_DIR)/boot/arizenos.elf
	@echo 'set timeout=0'                                > $(ISO_DIR)/boot/grub/grub.cfg
	@echo 'set default=0'                               >> $(ISO_DIR)/boot/grub/grub.cfg
	@echo 'menuentry "ArizenOS" {'                      >> $(ISO_DIR)/boot/grub/grub.cfg
	@echo '    multiboot2 /boot/arizenos.elf'           >> $(ISO_DIR)/boot/grub/grub.cfg
	@echo '    boot'                                    >> $(ISO_DIR)/boot/grub/grub.cfg
	@echo '}'                                           >> $(ISO_DIR)/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO_IMAGE) $(ISO_DIR) 2>/dev/null
	@echo "  ISO     $(ISO_IMAGE)"

# ── Run in QEMU ───────────────────────────────────────────────────────────────
.PHONY: run
run: $(KERNEL_BIN)
	$(QEMU) $(QEMU_FLAGS) -kernel $(KERNEL_BIN)

.PHONY: run-iso
run-iso: iso
	$(QEMU) $(QEMU_FLAGS) -cdrom $(ISO_IMAGE)

.PHONY: run-debug
run-debug: $(KERNEL_BIN)
	$(QEMU) $(QEMU_FLAGS) -kernel $(KERNEL_BIN) \
	    -s -S -serial stdio &
	@echo "  GDB     Connect with: gdb $(KERNEL_BIN) -ex 'target remote :1234'"

# ── Tests ─────────────────────────────────────────────────────────────────────
.PHONY: test
test:
	@echo "  TEST    Running test suite..."
	@$(MAKE) -C tests/ all

# ── Clean ─────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	@echo "  CLEAN   Build artifacts removed"

.PHONY: distclean
distclean: clean
	find . -name '*.o' -delete
	find . -name '*.a' -delete

# ── Info ──────────────────────────────────────────────────────────────────────
.PHONY: info
info:
	@echo "ArizenOS Build Configuration"
	@echo "  Architecture : $(ARCH)"
	@echo "  Target       : $(TARGET)"
	@echo "  CC           : $(shell which $(CC) 2>/dev/null || echo 'NOT FOUND')"
	@echo "  AS           : $(shell which $(AS) 2>/dev/null || echo 'NOT FOUND')"
	@echo "  QEMU         : $(shell which $(QEMU) 2>/dev/null || echo 'NOT FOUND')"
	@echo "  Build Dir    : $(BUILD_DIR)"

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "ArizenOS — Build System"
	@echo "========================"
	@echo ""
	@echo "  make all          Build the kernel ELF binary"
	@echo "  make iso          Build a bootable ISO image"
	@echo "  make run          Run in QEMU (kernel direct boot)"
	@echo "  make run-iso      Run in QEMU (ISO boot)"
	@echo "  make run-debug    Run in QEMU with GDB server on :1234"
	@echo "  make test         Run the test suite"
	@echo "  make clean        Remove build artifacts"
	@echo "  make distclean    Remove all generated files"
	@echo "  make info         Show toolchain configuration"
	@echo "  make help         Show this message"
	@echo ""
	@echo "  QEMU_EXTRA=...    Pass extra flags to QEMU"
	@echo ""
	@echo "  Example: make run QEMU_EXTRA='-serial stdio -m 512M'"
	@echo ""
