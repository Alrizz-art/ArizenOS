# GitHub Releases

> **Platform:** GitHub Releases (github.com/Alrizz-art/ArizenOS/releases)  
> **Artifacts:** `ArizenOS.apbx` + `ArizenOS.apbx.sha256`  
> **Automation:** CI workflow `release.yml` handles all stable and pre-release publishing  
> **Owner:** Release Manager (stable); CI System (nightly/pre-release)

---

## 1. Release Types on GitHub

ArizenOS uses four distinct GitHub Release configurations:

| Type | `pre-release` flag | `latest` flag | Tag Format | Created By |
|------|--------------------|--------------|-----------|-----------|
| Stable | `false` | `true` | `v1.2.3` | CI (on tag push) |
| Pre-Release (alpha/beta/rc) | `true` | `false` | `v1.2.3-rc.1` | CI (on pre-release tag push) |
| Nightly | `true` | `false` | `nightly/20260601` | CI (scheduled) |
| Yanked | `true` (edited) | `false` | *(existing tag, unchanged)* | Release Manager (manual edit) |

**The `latest` flag controls what users and tooling see as the recommended download.** Only one release can hold `latest: true` at any time. When a new stable is published, GitHub automatically transitions `latest` to the new release.

---

## 2. Stable Release Page Specification

Every stable GitHub Release must contain the following, in order:

### Release Title

```
ArizenOS v{MAJOR}.{MINOR}.{PATCH}
```

No additional qualifiers. Titles are not truncated, stylized, or versioned with codenames in v0.x.

### Release Body Structure

The release body is populated from `playbook/releases/changelogs/v{version}.md` by the CI system. The structure is:

```markdown
## Overview

{One paragraph: what is ArizenOS, what this release introduces, who it is for.}

## What's New in v{version}

### Added
- {feature description} — {brief user impact}
- ...

### Changed
- {change description}

### Fixed
- {bug description} — {platforms affected}

### Security
- {CVE or description} — {severity} — {components affected}

### Deprecated
- {feature} — scheduled for removal in v{future-version}

### Removed
- {removed item} — see migration: {link}

---

## What Is Never Changed

ArizenOS never modifies:
- Windows Update
- Windows Defender / Microsoft Defender
- Microsoft Store
- Network stack or Windows Firewall
- UAC policy

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| Windows | 10 22H2 (Build 19045) or 11 23H2 (Build 22631) |
| AME Wizard | v0.7.3+ |
| Disk Space | 4 GB free |
| Account | Administrator |

---

## Download & Verify

1. Download `ArizenOS.apbx` from the assets below
2. Verify the SHA256 checksum:
   ```
   Get-FileHash .\ArizenOS.apbx -Algorithm SHA256
   # Expected: {hash from ArizenOS.apbx.sha256}
   ```
3. Open `ArizenOS.apbx` with AME Wizard

---

## Known Issues

{List any known issues or workarounds.}
{If none: "No known issues in this release."}

---

## Full Changelog

[CHANGELOG.md]({link-to-changelog-in-repo})

---

*SHA256: `{hash}`*
```

### Release Assets

Every stable release attaches exactly two assets:

| Asset | Description |
|-------|-------------|
| `ArizenOS.apbx` | The playbook archive for AME Wizard |
| `ArizenOS.apbx.sha256` | SHA256 checksum — one line: `{hash}  ArizenOS.apbx` |

No additional assets (source code ZIP, debug builds, partial builds) are attached to stable releases. GitHub's automatic "Source code (zip)" and "Source code (tar.gz)" assets are suppressed by the CI release workflow.

---

## 3. Pre-Release Page Specification

Pre-release GitHub Releases (alpha, beta, RC) follow the same body structure as stable releases with these differences:

**Title format:**
```
ArizenOS v{version}-{prerelease}  [BETA] / [ALPHA] / [RC]
```

**Additional header banner (inserted before Overview):**
```markdown
> **⚠ PRE-RELEASE — NOT FOR PRODUCTION USE**  
> This is a {alpha/beta/release candidate} build. It may contain bugs and incomplete features.  
> Report issues with label `{rc-feedback / beta-feedback / alpha-feedback}`.
```

**Differences from stable:**
- `pre-release: true` — does not appear as "Latest Release" on the releases page
- Does not update `latest.json`
- Does not carry a GPG-signed tag (pre-releases use lightweight annotated tags)
- Known issues section is always present (even if empty: "None identified so far")

---

## 4. Release Asset Integrity

### SHA256 Checksum File Format

```
{64-char-lowercase-hex}  ArizenOS.apbx
```

The two-space separator between hash and filename is the standard `sha256sum` format. Users can verify with:

```powershell
# PowerShell
$result = Get-FileHash .\ArizenOS.apbx -Algorithm SHA256
$expected = (Get-Content .\ArizenOS.apbx.sha256 -Raw).Trim().Split("  ")[0]
if ($result.Hash.ToLower() -eq $expected) { Write-Host "✓ Checksum valid" }
else { Write-Error "✗ CHECKSUM MISMATCH — do not install" }
```

```bash
# Linux/macOS (for contributors)
sha256sum -c ArizenOS.apbx.sha256
```

### Asset Signing (Future)

In v1.0.0, all release assets will be signed with a project PGP key. The public key will be published to:
- The repository root as `SIGNING_KEY.asc`
- keys.openpgp.org

Until signing is implemented, the SHA256 checksum is the primary integrity mechanism.

---

## 5. Release Tag Specification

### Stable Release Tags

```
Name:      v{MAJOR}.{MINOR}.{PATCH}
Type:      Annotated (git tag -a)
Signed:    Yes (GPG signed by Release Manager)
Message:   "ArizenOS v{version}\n\n{one-paragraph summary}"
Created:   On main at the release merge commit
```

### Pre-Release Tags

```
Name:      v{MAJOR}.{MINOR}.{PATCH}-{prerelease}.{N}
Type:      Annotated (git tag -a)
Signed:    No (lightweight annotated, not GPG signed)
Message:   "ArizenOS v{version}-{prerelease}.{N}"
Created:   On release/{version} branch
```

### Nightly Tags

```
Name:      nightly/{YYYYMMDD}
Type:      Lightweight
Signed:    No
Created:   By CI on main at build time
Lifetime:  Deleted when the nightly is expired (>7 nightlies exist)
```

### Tag Immutability

**Stable and pre-release tags are permanent and immutable.** They are never moved, deleted, or re-pushed. If a tag is pushed by mistake:
1. Do NOT delete and re-push the tag
2. Publish a new tag at the correct commit instead
3. Add a note to the GitHub Release explaining the skip

---

## 6. GitHub Release Automation

The `release.yml` CI workflow handles publication. It is triggered by:

| Event | Workflow Behavior |
|-------|-----------------|
| Tag push matching `v*.*.*` (no pre-release) | Build + publish stable release |
| Tag push matching `v*.*.*-*` | Build + publish pre-release |
| Schedule (02:00 UTC daily) | Build + publish nightly (if new commits) |
| `workflow_dispatch` | Manual nightly trigger (with reason parameter) |

The workflow does NOT trigger on:
- Branch pushes
- Pull request events
- Non-`v` prefixed tags (e.g., `nightly/*` tags are created by the workflow itself)

---

## 7. Release Visibility and Discovery

### GitHub "Latest Release" Link

`https://github.com/Alrizz-art/ArizenOS/releases/latest` always points to the most recent stable release. Pre-releases and nightlies never appear at this URL.

### Release Listing Order

GitHub lists releases in reverse chronological order. Nightlies appear between stable releases. To keep the releases page readable:
- Nightlies are auto-expired after 7 builds
- Pre-releases older than 60 days with no activity are archived (hidden from the main releases list, but not deleted)

### Repository README Badge

The repository README carries a dynamic badge that always reflects the latest stable version:

```
[![Latest Release](https://img.shields.io/github/v/release/Alrizz-art/ArizenOS?label=ArizenOS&color=1E293B)](https://github.com/Alrizz-art/ArizenOS/releases/latest)
```

---

## 8. Editing and Correcting a Published Release

### Allowed Post-Publish Edits

| Edit | Allowed | Process |
|------|---------|---------|
| Typo in release notes | ✅ Yes | Direct edit, no announcement |
| Add a "known issue" discovered after publish | ✅ Yes | Add to release body + post comment |
| Correct the SHA256 listed in release body | ✅ Yes (only description, not asset) | Verify asset is correct first |
| Replace the `.apbx` asset after publish | ❌ No | Issue a patch release instead |
| Delete a stable release | ❌ No | Yank procedure (see `STABLE_RELEASES.md §6`) |
| Move the stable tag to a different commit | ❌ No | Tags are immutable |

### Replacing a Broken Asset (Emergency Only)

If a published `.apbx` is discovered to be corrupt (wrong file, build error, missing content), the emergency procedure is:

1. Immediately yank the release (mark as pre-release)
2. Fix the build issue on a hotfix branch
3. Tag `v{MAJOR}.{MINOR}.{PATCH+1}`
4. Publish the corrected version as the new stable release
5. Post a notice on the original release page referencing the replacement

Never silently replace an asset — users who downloaded the original file will have a different checksum and may distrust future releases.

---

## 9. Release Permissions

| Action | GitHub Permission Required | ArizenOS Role Required |
|--------|--------------------------|----------------------|
| Create release | Write | Core Maintainer |
| Edit release body | Write | Core Maintainer |
| Upload release assets | Write | Core Maintainer or CI system |
| Delete release | Admin | Release Manager only |
| Delete release assets | Admin | Release Manager only |
| Push release tags | Write + bypass protection | Release Manager only |

CI uses a dedicated `RELEASE_BOT_TOKEN` (GitHub App token with scoped permissions) — not a personal access token. This token has:
- `contents: write` (create releases, upload assets)
- `packages: write` (if packages are introduced later)
- No admin permissions
- Restricted to the `Alrizz-art/ArizenOS` repository
