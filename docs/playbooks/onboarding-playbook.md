# Contributor Onboarding Playbook — ArizenOS

Welcome to ArizenOS! This playbook gets you from zero to your first merged PR.

---

## Day 1 — Orientation

### 1. Read the Core Docs

In order:
1. [README.md](../../README.md) — project overview and goals
2. [Architecture Overview](../architecture/overview.md) — system design
3. [CONTRIBUTING.md](../../CONTRIBUTING.md) — workflow and standards
4. [Code Style Guide](../contributing/code-style.md) — coding conventions
5. [Development Setup](../contributing/development-setup.md) — toolchain setup

### 2. Set Up Your Environment

Follow [Development Setup](../contributing/development-setup.md) completely.

Verify with:
```bash
make info   # All tools should show versions, not "NOT FOUND"
make all    # Should succeed (or fail with expected "WIP" messages)
make run    # QEMU should launch
```

### 3. Join the Community

- ⭐ Star the repository
- 👀 Watch the repository (All Activity) for notifications
- 💬 Introduce yourself in [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions)

---

## Day 2 — First Contribution

### Find a Good First Issue

Look for issues labeled:
- [`good first issue`](https://github.com/Alrizz-art/ArizenOS/labels/good%20first%20issue)
- [`size: xs`](https://github.com/Alrizz-art/ArizenOS/labels/size%3A%20xs) or [`size: s`](https://github.com/Alrizz-art/ArizenOS/labels/size%3A%20s)
- [`type: documentation`](https://github.com/Alrizz-art/ArizenOS/labels/type%3A%20documentation)

If you have an idea not covered by existing issues, open one first and discuss
before starting work — this avoids duplicate effort.

### Claim the Issue

Comment on the issue: "I'd like to work on this" — a maintainer will assign it to you.

### Branch Naming

```bash
git checkout develop
git pull origin develop
git checkout -b <type>/<short-description>

# Examples:
git checkout -b docs/add-gdt-comments
git checkout -b fix/serial-init-null-check
git checkout -b feat/vga-scroll-support
```

### Commit Your Work

Follow [Conventional Commits](https://www.conventionalcommits.org):

```bash
git add -p   # Stage changes interactively (preferred over git add .)
git commit -m "docs(kernel): add inline comments to GDT setup

GDT segment descriptor fields were not documented, making the
boot sequence hard to follow for new contributors.

Closes #42"
```

### Open the PR

```bash
git push origin <your-branch>
```

Then open a PR on GitHub:
- **Base branch:** `develop`
- **Title:** follow commit convention
- **Description:** fill in the PR template
- **Labels:** apply `type:`, `scope:`, `size:` labels
- **Milestone:** assign to the relevant milestone

---

## Understanding the Codebase

### Where to Start Reading

| You want to understand... | Start here |
|--------------------------|-----------|
| How the OS boots | `arch/x86_64/boot/` + [Architecture Overview](../architecture/overview.md) |
| Kernel entry point | `arch/x86_64/kernel/entry.asm` → `kernel/core/main.c` |
| Memory management | `kernel/mm/` + `kernel/include/mm.h` |
| Interrupt handling | `arch/x86_64/kernel/idt.c` + `kernel/core/irq.c` |
| Filesystem | `fs/vfs/` + `kernel/fs/` |
| How to add a driver | `drivers/` — pick a simple one like `drivers/display/` |

### Key Header Files

| Header | Purpose |
|--------|---------|
| `kernel/include/kernel.h` | Core kernel types and macros |
| `kernel/include/mm.h` | Memory management interface |
| `kernel/include/vfs.h` | Virtual filesystem interface |
| `kernel/include/sched.h` | Scheduler interface |
| `arch/x86_64/include/arch.h` | x86_64-specific types |

---

## Review Process

What to expect after opening a PR:

| Timeframe | What happens |
|-----------|-------------|
| 0–48h | Maintainer acknowledges the PR |
| 48–96h | Initial review with comments |
| After changes | Re-review within 48h |
| Approved | Merge by maintainer |

**Tips for a smooth review:**
- Keep PRs small and focused — one logical change per PR
- Respond to all review comments (even if just "Done" or "I disagree because...")
- Update the PR description if the scope changes
- Don't force-push after review starts — add new commits instead

---

## Common Pitfalls

| Mistake | How to Avoid |
|---------|-------------|
| Opening a PR to `main` | Always target `develop` |
| Giant PRs | Split into smaller logical units |
| Missing commit convention | Use `feat/fix/docs/etc.` prefix |
| Not linking the issue | Add `Closes #N` in the PR description |
| Breaking the build | Run `make clean && make all` before pushing |
| Skipping labels | Apply `type:`, `scope:`, `size:` labels |

---

## Getting Help

Stuck? Here's where to ask:

1. **GitHub Discussions** — general questions, design discussions
2. **Issue comments** — questions specific to an issue you're working on
3. **PR comments** — questions about your in-progress code

We're a small team and response times may vary, but we read everything.
