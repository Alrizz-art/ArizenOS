# Release Playbook — ArizenOS

This playbook describes the exact steps to cut a new ArizenOS release.
Follow it in order — do not skip steps.

---

## Prerequisites

Before starting, ensure:
- [ ] All issues linked to the milestone are closed or explicitly deferred
- [ ] All PRs targeting this milestone are merged into `develop`
- [ ] CI is green on `develop`
- [ ] You have push access to the repository

---

## Step 1 — Create the Release Branch

```bash
git checkout develop
git pull origin develop

# Create release branch (e.g., release/v0.2.0)
git checkout -b release/vX.Y.Z

# Push to GitHub
git push origin release/vX.Y.Z
```

---

## Step 2 — Bump the Version

Update version references throughout the codebase:

```bash
# Search for version strings
grep -r "0\.1\.0" --include="*.c" --include="*.h" --include="*.md" .

# Update version in kernel header
# kernel/include/version.h:
#   #define ARIZENOS_VERSION_MAJOR X
#   #define ARIZENOS_VERSION_MINOR Y
#   #define ARIZENOS_VERSION_PATCH Z
#   #define ARIZENOS_VERSION "vX.Y.Z"
```

Commit the version bump:
```bash
git add -A
git commit -m "chore(release): bump version to vX.Y.Z"
```

---

## Step 3 — Update CHANGELOG.md

Move all entries from `[Unreleased]` to the new version section:

```markdown
## [X.Y.Z] — YYYY-MM-DD

### Added
- ...

### Fixed
- ...

### Changed
- ...
```

Update the comparison links at the bottom:
```markdown
[Unreleased]: https://github.com/Alrizz-art/ArizenOS/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/Alrizz-art/ArizenOS/compare/vA.B.C...vX.Y.Z
```

Commit:
```bash
git add CHANGELOG.md
git commit -m "docs(changelog): update for vX.Y.Z release"
```

---

## Step 4 — Test the Release Build

```bash
# Clean build
make distclean
make all

# Verify it boots in QEMU
make run

# Build ISO and verify it boots
make iso
make run-iso

# Run test suite
make test
```

All tests must pass before continuing.

---

## Step 5 — Merge to `main`

Open a PR: `release/vX.Y.Z → main`

PR title: `chore(release): vX.Y.Z`

- Wait for CI to pass
- Get at least one review approval
- Merge using **Merge Commit** (not squash — preserves release history)

```bash
git checkout main
git pull origin main
```

---

## Step 6 — Tag the Release

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z — <Milestone Name>

$(cat CHANGELOG.md | awk '/## \[X.Y.Z\]/,/## \[/' | head -50)"

git push origin vX.Y.Z
```

This triggers the GitHub Actions release workflow automatically.

---

## Step 7 — Verify the GitHub Release

1. Go to [Releases](https://github.com/Alrizz-art/ArizenOS/releases)
2. Verify the release was created by the workflow
3. Check that the ISO artifact is attached (once build system is ready)
4. Edit the release notes if needed
5. Publish the release (unmark as draft if needed)

---

## Step 8 — Back-Merge to `develop`

```bash
git checkout develop
git merge main
git push origin develop
```

This keeps `develop` up to date with hotfixes applied to `main`.

---

## Step 9 — Close the Milestone

1. Go to [Milestones](https://github.com/Alrizz-art/ArizenOS/milestones)
2. Open the `vX.Y.Z` milestone
3. Click **Close milestone**

---

## Step 10 — Post-Release

- [ ] Post announcement in [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions)
- [ ] Update the [project board](https://github.com/users/Alrizz-art/projects/2) — move closed items to Done
- [ ] Open the next milestone if not already created
- [ ] Draft initial entries for the next `[Unreleased]` section in CHANGELOG.md

---

## Pre-release Checklist Summary

```
[ ] All milestone issues closed / deferred
[ ] CI green on develop
[ ] release/vX.Y.Z branch created
[ ] Version bumped in kernel/include/version.h
[ ] CHANGELOG.md updated
[ ] Clean build succeeds
[ ] QEMU boot verified
[ ] ISO boot verified
[ ] Tests pass
[ ] PR to main approved and merged
[ ] Tag vX.Y.Z pushed
[ ] GitHub Release created and verified
[ ] develop back-merged from main
[ ] Milestone closed
[ ] Announcement posted
```
