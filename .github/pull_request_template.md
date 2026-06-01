## Summary
<!-- What does this PR do? Link to the related issue(s). -->

Closes #<!-- issue number -->

## Type of Change
- [ ] `feat` — New feature
- [ ] `fix` — Bug fix
- [ ] `security` — Security fix
- [ ] `perf` — Performance improvement
- [ ] `refactor` — Code restructuring (no behavior change)
- [ ] `docs` — Documentation only
- [ ] `test` — Tests only
- [ ] `build` / `ci` — Build system or CI changes
- [ ] `chore` — Maintenance

## Scope
- [ ] Kernel
- [ ] Bootloader
- [ ] Drivers
- [ ] Filesystem
- [ ] Memory Management
- [ ] Networking
- [ ] Userspace / Shell
- [ ] Build System / CI
- [ ] Documentation

## Breaking Change?
- [ ] No
- [ ] Yes — describe the breaking change below

<!-- If yes, describe what breaks and how users should migrate -->

## How Was This Tested?
- [ ] Booted in QEMU (x86_64)
- [ ] Unit tested (if applicable)
- [ ] Tested on real hardware
- [ ] Only documentation / build change — no runtime testing needed

```
# QEMU command used:
qemu-system-x86_64 ...
```

## Checklist
- [ ] Code follows the project's coding style
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org)
- [ ] Documentation updated (if applicable)
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] No unrelated changes included
- [ ] All CI checks pass
