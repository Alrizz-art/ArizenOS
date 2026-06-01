#!/usr/bin/env bash
# ==============================================================================
# ArizenOS — Cross-Compiler Toolchain Build Script
# tools/toolchain/build-toolchain.sh
#
# Builds a bare-metal x86_64-elf cross-compiler (GCC + Binutils).
# Installs to ~/opt/cross/ by default.
#
# Usage:
#   ./tools/toolchain/build-toolchain.sh
#   PREFIX=/usr/local ./tools/toolchain/build-toolchain.sh
#
# Reference: https://wiki.osdev.org/GCC_Cross-Compiler
# ==============================================================================

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
TARGET="${TARGET:-x86_64-elf}"
PREFIX="${PREFIX:-$HOME/opt/cross}"
JOBS="${JOBS:-$(nproc)}"
BUILD_DIR="${BUILD_DIR:-/tmp/arizenos-toolchain-build}"

BINUTILS_VERSION="2.42"
GCC_VERSION="13.3.0"

BINUTILS_URL="https://ftp.gnu.org/gnu/binutils/binutils-${BINUTILS_VERSION}.tar.xz"
GCC_URL="https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.xz"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# ── Preflight Checks ──────────────────────────────────────────────────────────
check_deps() {
    info "Checking build dependencies..."
    local missing=()
    for dep in gcc g++ make curl tar; do
        if ! command -v "$dep" &>/dev/null; then
            missing+=("$dep")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        error "Install them with: sudo apt-get install -y build-essential curl"
        exit 1
    fi
    success "All dependencies present"
}

# ── Download ──────────────────────────────────────────────────────────────────
download() {
    local url="$1"
    local filename=$(basename "$url")
    if [ ! -f "$BUILD_DIR/src/$filename" ]; then
        info "Downloading $filename..."
        curl -fL --progress-bar -o "$BUILD_DIR/src/$filename" "$url"
    else
        info "$filename already downloaded, skipping"
    fi
}

# ── Build ─────────────────────────────────────────────────────────────────────
main() {
    info "ArizenOS Cross-Compiler Toolchain Builder"
    info "  Target:   $TARGET"
    info "  Prefix:   $PREFIX"
    info "  GCC:      $GCC_VERSION"
    info "  Binutils: $BINUTILS_VERSION"
    info "  Jobs:     $JOBS"
    echo ""

    check_deps

    mkdir -p "$BUILD_DIR/src" "$BUILD_DIR/build-binutils" "$BUILD_DIR/build-gcc"
    mkdir -p "$PREFIX"

    export PATH="$PREFIX/bin:$PATH"

    # ── Binutils ──────────────────────────────────────────────────────────────
    download "$BINUTILS_URL"
    info "Extracting Binutils..."
    tar -xf "$BUILD_DIR/src/binutils-${BINUTILS_VERSION}.tar.xz" -C "$BUILD_DIR/src"

    info "Building Binutils..."
    cd "$BUILD_DIR/build-binutils"
    "$BUILD_DIR/src/binutils-${BINUTILS_VERSION}/configure" \
        --target="$TARGET" \
        --prefix="$PREFIX" \
        --with-sysroot \
        --disable-nls \
        --disable-werror \
        --quiet

    make -j"$JOBS" --quiet
    make install --quiet
    success "Binutils installed"

    # ── GCC ───────────────────────────────────────────────────────────────────
    download "$GCC_URL"
    info "Extracting GCC..."
    tar -xf "$BUILD_DIR/src/gcc-${GCC_VERSION}.tar.xz" -C "$BUILD_DIR/src"

    info "Downloading GCC prerequisites..."
    cd "$BUILD_DIR/src/gcc-${GCC_VERSION}"
    ./contrib/download_prerequisites --quiet

    info "Building GCC (this takes 10-30 minutes)..."
    cd "$BUILD_DIR/build-gcc"
    "$BUILD_DIR/src/gcc-${GCC_VERSION}/configure" \
        --target="$TARGET" \
        --prefix="$PREFIX" \
        --disable-nls \
        --enable-languages=c,c++ \
        --without-headers \
        --disable-hosted-libstdcxx \
        --quiet

    make -j"$JOBS" all-gcc --quiet
    make -j"$JOBS" all-target-libgcc --quiet
    make install-gcc --quiet
    make install-target-libgcc --quiet
    success "GCC installed"

    # ── Verify ────────────────────────────────────────────────────────────────
    echo ""
    info "Verifying installation..."
    "$PREFIX/bin/$TARGET-gcc" --version
    "$PREFIX/bin/$TARGET-ld" --version | head -1
    success "Toolchain ready at $PREFIX/bin/"

    echo ""
    echo "Add to your shell profile:"
    echo "  export PATH=\"$PREFIX/bin:\$PATH\""
    echo ""
    echo "Verify with:"
    echo "  $TARGET-gcc --version"
    echo "  make info  (from ArizenOS root)"
}

main "$@"
