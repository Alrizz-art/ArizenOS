# Hotfix Playbook — ArizenOS

Use this playbook for **critical bug fixes** that must go directly to the
stable `main` branch without waiting for the next planned release.

Hotfixes are appropriate for:
- Kernel panics on common hardware
- Security vulnerabilities (see [SECURITY.md](../../SECURITY.md))
- Data corruption bugs
- Boot failures on a recently released version

---

## Step 1 — Assess the Severity

Before starting a hotfix, confirm it qualifies:

| Criteria | Hotfix? |
|----------|---------|
| Crash / panic on boot | ✅ Yes |
| Security vulnerability | ✅ Yes |
| Data corruption | ✅ Yes |
| Performance regression | ❌ No — next release |
| Minor bug with workaround | ❌ No — next release |
| Documentation error | ❌ No — next release |

---

## Step 2 — Create the Hotfix Branch

Branch from `main` (not `develop`):

```bash
git checkout main
git pull origin main

git checkout -b hotfix/<short-description>
# e.g.: hotfix/fix-apic-init-panic
```

---

## Step 3 — Fix and Test

Apply the minimal fix — do not bundle unrelated changes.

```bash
# Make your fix
vim kernel/core/...

# Build and verify
make clean && make all
make run   # Confirm the fix works in QEMU
make test  # All tests must pass
```

---

## Step 4 — Bump the Patch Version

Increment only the PATCH number (`Z` in `X.Y.Z`):

```bash
# e.g., v0.1.0 → v0.1.1
# Update kernel/include/version.h
```

Update `CHANGELOG.md`:
```markdown
## [X.Y.Z+1] — YYYY-MM-DD

### Fixed
- kernel: fix APIC initialization panic on Q35 machines (#42)

### Security
- (if applicable)
```

Commit:
```bash
git add -A
git commit -m "fix(<scope>): <description of the fix>

Fixes #<issue number>"

git commit -m "chore(release): bump version to vX.Y.Z+1"
```

---

## Step 5 — PR to `main`

Open a PR: `hotfix/<name> → main`

- Title: `fix(<scope>): <description>`
- Label: `type: bug`, `priority: critical`, `status: needs-review`
- Link to the issue: `Fixes #N`
- Require at least one review approval
- CI must pass

---

## Step 6 — Tag and Release

```bash
git checkout main
git pull origin main

git tag -a vX.Y.Z+1 -m "Hotfix release vX.Y.Z+1

Critical fix: <one-line description>"

git push origin vX.Y.Z+1
```

The release workflow will automatically build and publish the GitHub Release.

---

## Step 7 — Back-Merge to `develop`

```bash
git checkout develop
git merge main
git push origin develop
```

This is **required** — do not skip. Otherwise `develop` will diverge and
the bug will reappear in the next release.

---

## Step 8 — If It's a Security Fix

1. Create a [GitHub Security Advisory](https://github.com/Alrizz-art/ArizenOS/security/advisories/new) **before** the tag is public
2. Request a CVE if the vulnerability qualifies
3. Publish the advisory simultaneously with the release tag
4. See [SECURITY.md](../../SECURITY.md) for the full disclosure process

---

## Hotfix Checklist

```
[ ] Severity confirmed — qualifies for hotfix
[ ] hotfix/<name> branch created from main
[ ] Fix is minimal and targeted
[ ] Build succeeds (make clean && make all)
[ ] Boot verified in QEMU
[ ] Tests pass
[ ] PATCH version bumped
[ ] CHANGELOG.md updated
[ ] PR to main approved and CI green
[ ] Tag vX.Y.Z+1 pushed
[ ] GitHub Release published
[ ] develop back-merged from main
[ ] Security advisory published (if security fix)
```
