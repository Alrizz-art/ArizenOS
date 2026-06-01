# Development Setup — ArizenOS

This guide walks you through setting up a complete ArizenOS development environment
on Linux, macOS, and Windows (WSL2).

---

## Prerequisites Overview

| Tool | Version | Required | Notes |
|------|---------|----------|-------|
| `x86_64-elf-gcc` | ≥ 13.0 | ✅ | Cross-compiler — see [Toolchain](#toolchain) |
| `nasm` | ≥ 2.15 | ✅ | x86 assembler |
| `qemu-system-x86_64` | ≥ 8.0 | ✅ | Emulator |
| `make` | ≥ 4.3 | ✅ | Build system |
| `xorriso` | ≥ 1.5 | ✅ | ISO creation |
| `grub-pc-bin` | Any | ✅ | Bootloader tools |
| `gdb` | ≥ 12.0 | Recommended | Kernel debugging |
| `git` | ≥ 2.40 | ✅ | Version control |

---

## Platform Setup

### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    nasm \
    qemu-system-x86 \
    xorriso \
    grub-pc-bin \
    grub-common \
    mtools \
    gdb
```

### Arch Linux / Manjaro

```bash
sudo pacman -S --needed \
    base-devel \
    git \
    nasm \
    qemu \
    xorriso \
    grub \
    mtools \
    gdb
```

### macOS (Homebrew)

```bash
brew install \
    nasm \
    qemu \
    xorriso \
    gdb \
    make

# GRUB tools (needed for ISO creation)
brew install --cask grub
```

### Windows (WSL2)

1. Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) with Ubuntu 24.04
2. Follow the Ubuntu instructions above inside WSL2
3. For QEMU GUI: install [QEMU for Windows](https://www.qemu.org/download/#windows) natively or use X11 forwarding

---

## Toolchain

ArizenOS requires a **bare-metal cross-compiler** targeting `x86_64-elf`.
This is different from your host's `gcc` — it produces code for a system with no OS.

### Option A — Build from Source (Recommended)

```bash
# Download the toolchain build script
curl -fsSL https://raw.githubusercontent.com/Alrizz-art/ArizenOS/main/tools/toolchain/build-toolchain.sh | bash

# This will build and install to ~/opt/cross/
export PATH="$HOME/opt/cross/bin:$PATH"
echo 'export PATH="$HOME/opt/cross/bin:$PATH"' >> ~/.bashrc
```

See [`tools/toolchain/README.md`](../../tools/toolchain/README.md) for manual build instructions.

### Option B — Pre-built Binaries (Ubuntu)

```bash
# Install the cross-compiler from apt (may not be latest)
sudo apt-get install -y gcc-x86-64-linux-gnu
# Note: this may not be bare-metal — check with:
x86_64-linux-gnu-gcc --version
```

### Verify Toolchain

```bash
x86_64-elf-gcc --version
# Expected: x86_64-elf-gcc (GCC) 13.x.x

x86_64-elf-ld --version
# Expected: GNU ld (GNU Binutils) 2.x.x

nasm --version
# Expected: NASM version 2.15.x

qemu-system-x86_64 --version
# Expected: QEMU emulator version 8.x.x
```

---

## Clone and Build

```bash
# Clone the repository
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS

# Checkout the develop branch for latest work
git checkout develop

# Verify build configuration
make info

# Build the kernel
make all

# Run in QEMU
make run
```

---

## Development Workflow

### Branch Strategy

Always branch from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org):

```bash
git commit -m "feat(mm): add physical page frame allocator"
git commit -m "fix(drivers): resolve PS/2 keyboard IRQ conflict"
git commit -m "docs(kernel): document VFS mount interface"
```

### Before Submitting a PR

```bash
# Ensure the build succeeds
make clean && make all

# Run tests
make test

# Check your commit messages follow convention
git log --oneline origin/develop..HEAD
```

---

## Debugging

### GDB + QEMU

```bash
# Terminal 1: Start QEMU with GDB server
make run-debug

# Terminal 2: Connect GDB
gdb build/arizenos.elf
(gdb) target remote :1234
(gdb) break kernel_main
(gdb) continue
```

### Useful GDB Commands for Kernel Debugging

```gdb
# Set breakpoint at kernel entry
break kernel_main

# Step through instructions
stepi

# Print registers
info registers

# Examine memory
x/10xg 0xffffffff80000000

# Backtrace
bt

# Print a variable
print *page_table

# Load symbols
symbol-file build/arizenos.elf
```

### QEMU Monitor

Press `Ctrl+Alt+2` in QEMU to enter the monitor:

```
(qemu) info registers     # dump CPU registers
(qemu) info mem           # show memory mappings
(qemu) x /10i $eip        # disassemble at current IP
(qemu) stop               # pause execution
(qemu) cont               # resume
```

### Serial Output

```bash
# Redirect kernel serial output to host terminal
make run QEMU_EXTRA="-serial stdio"
```

---

## Editor Setup

### VS Code

Install the recommended extensions:

```bash
# Install from the .vscode/extensions.json recommendations
code --install-extension ms-vscode.cpptools
code --install-extension ms-vscode.makefile-tools
code --install-extension EditorConfig.EditorConfig
```

The project includes `.vscode/c_cpp_properties.json` with correct include paths.

### Vim / Neovim

```vim
" Add to your .vimrc / init.vim
set expandtab
set tabstop=4
set shiftwidth=4
set textwidth=80
```

Or use the included `.editorconfig` — most editors support it with a plugin.

---

## Common Issues

### `x86_64-elf-gcc: command not found`

Your cross-compiler isn't in PATH. Run:
```bash
export PATH="$HOME/opt/cross/bin:$PATH"
```
Or rebuild the toolchain using `tools/toolchain/build-toolchain.sh`.

### QEMU shows blank screen

This is expected during early development — the kernel may not be initializing VGA output yet. Check for output on the serial port:
```bash
make run QEMU_EXTRA="-serial stdio -display none"
```

### `grub-mkrescue: command not found`

```bash
sudo apt-get install grub-pc-bin grub-common xorriso
```

### Build fails with linker errors

Ensure you're using the cross-compiler, not the host `gcc`:
```bash
make info  # check which CC is being used
```

---

## Getting Help

- 📖 [Architecture Overview](../architecture/overview.md)
- 💬 [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions)
- 🐛 [Open an Issue](https://github.com/Alrizz-art/ArizenOS/issues/new?template=bug_report.md)
- 📚 [OSDev Wiki](https://wiki.osdev.org/) — essential reference for OS development
