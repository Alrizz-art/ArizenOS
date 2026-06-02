# ADR-0004: Kernel Research Separation Strategy

**Status**: Accepted
**Date**: 2026-06-02
**Deciders**: @Alrizz-art (Technical Council)

---

## Context

The ArizenOS repository contains two distinct domains:

1. **ArizenOS Platform** — An AI-first desktop experience layer for Windows 10/11. This is the primary product, actively developed and user-facing.
2. **ArizenOS Kernel** — An experimental bare-metal OS prototype (x86_64). Currently implements a bootloader, 64-bit kernel entry, C kernel main, and core headers. Scheduler, memory manager, drivers, filesystem, and userspace are not yet implemented.

These two domains share a single repository but have fundamentally different audiences, contribution workflows, build toolchains, and maturity levels. As the repository grows, contributors and tools must clearly understand which domain they are working in.

---

## Decision

**Relocate all kernel research code into `research/kernel/`.**

The kernel prototype moves from the repository root into a clearly namespaced subdirectory. All product code remains at its current locations. The repository remains a single monorepo.

### What moves

| Current Path | New Path |
|---|---|
| `arch/` | `research/kernel/arch/` |
| `drivers/` | `research/kernel/drivers/` |
| `fs/` | `research/kernel/fs/` |
| `kernel/` | `research/kernel/kernel/` |
| `lib/libc/`, `lib/libk/` | `research/kernel/lib/` |
| `userspace/` | `research/kernel/userspace/` |

### What does not move

Everything else — `apps/`, `branding/`, `docs/`, `packages/`, `playbook/`, `scripts/`, `registry/`, `releases/`, `tools/`, `.github/` — remains unchanged.

---

## Rationale

### Why the kernel code stays in this repository

- **History preservation**: The kernel prototype represents real architectural exploration. Its commit history has value and should not be erased.
- **Signal of intent**: Keeping the kernel research visible signals that ArizenOS has long-term ambitions beyond a Windows overlay. This is strategically important for community perception.
- **Consolidation**: Managing a separate repository for ~5 real source files creates unnecessary operational overhead.
- **Discoverability**: Contributors interested in the OS direction can find it naturally within the primary repo.

### Why the kernel code is moved to `research/kernel/`

- **Clear separation of concerns**: Contributors to the platform product should not encounter kernel C/Assembly files when browsing the repo root. Confusion between domains is the primary driver of incorrect contributions and wasted review cycles.
- **Toolchain isolation**: The kernel requires a cross-compiler (`x86_64-elf-gcc`), NASM, and QEMU. The platform requires Node.js and pnpm. These toolchains must not be conflated.
- **CI clarity**: CI pipelines for the platform (TypeScript build, ESLint, Playwright) must not accidentally attempt to lint or compile kernel C code.
- **Documentation clarity**: A `research/` prefix communicates maturity level immediately — this is experimental, not production.

### Why the repository remains single

Splitting into a separate repository (`ArizenOS-Kernel`) is premature. The kernel prototype does not yet demonstrate independent viability. It has no scheduler, no memory manager, no filesystem, and no runnable userspace. A separate repository for an incomplete prototype creates an abandoned-looking repo that hurts community perception. The split should happen when the kernel is meaningfully runnable as a standalone artifact.

---

## Consequences

### Easier
- New contributors understand the product domain immediately.
- CI pipelines can target `research/` independently.
- CODEOWNERS can assign separate maintainers to `research/kernel/`.
- The kernel research area can evolve its own Makefile, toolchain docs, and README without polluting root.

### Harder
- Any existing bookmarks or direct links to kernel files (e.g., `/blob/main/kernel/core/main.c`) will 404. GitHub will not automatically redirect.
- Contributors who had cloned and referenced these paths must update their local forks.

### Accepted trade-offs
- Path breakage is a one-time cost. The long-term clarity benefit outweighs it.
- No history is lost — `git log --follow` will trace the rename.

---

## Alternatives Considered

### A. Leave kernel code at root, add documentation only
**Rejected.** Documentation alone does not prevent contributors from submitting JavaScript PRs that accidentally touch kernel headers, or vice versa. Structural separation is the only reliable enforcement.

### B. Create a separate `ArizenOS-Kernel` repository now
**Rejected.** Premature. A separate repo for an incomplete prototype creates noise and splits maintainer attention before it is warranted. See "Future Split Criteria" below.

### C. Delete the kernel prototype entirely
**Rejected explicitly.** The kernel work represents intentional long-term research. Deleting it would misrepresent the project's scope.

---

## Future Split Criteria

A separate `ArizenOS-Kernel` repository will be created when **all** of the following are true:

| Criterion | Measurable Definition |
|---|---|
| Scheduler operational | Round-robin and/or CFS scheduler boots at least two concurrent kernel threads |
| PMM operational | Physical memory manager maps and allocates pages from a real memory map |
| VMM operational | Virtual memory manager enables paging, kernel and user address spaces separated |
| Filesystem operational | At least one filesystem (ext2 or tmpfs) can mount, read, and write files |
| Userspace bootable | `/sbin/init` (or equivalent PID 1) launches and runs in user mode |
| QEMU runnable | Kernel boots to a shell prompt in QEMU from a single `make run` command |
| CI passing | Dedicated kernel CI pipeline (build + QEMU smoke test) passes on main |

Until all seven criteria are met, the kernel remains in `research/kernel/` within this repository.

---

*ADR authored by the Technical Council — ArizenOS*
