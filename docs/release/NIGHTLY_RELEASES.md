# Nightly Releases

> **Output:** `ArizenOS-nightly-{date}-{sha}.apbx`  
> **Cadence:** Daily at 02:00 UTC from `main`  
> **Audience:** Developers, contributors, advanced community testers  
> **Stability:** Experimental — not for production use  
> **Owner:** CI/CD System (automated)

---

## 1. Purpose

Nightly releases serve two audiences:

1. **Contributors** who need a runnable `.apbx` to test their in-progress work against real AME Wizard behavior without triggering a formal pre-release
2. **Advanced community testers** who want to track development and surface issues before they reach beta

Nightlies are not user releases. They carry no stability guarantee, no changelog, and no support commitment. Every nightly is automatically deprecated the moment the next nightly is published.

---

## 2. Build Trigger

Nightlies are built by the CI workflow `nightly.yml` on a schedule.

**Schedule:** Daily at 02:00 UTC, IF `main` has received at least one new commit since the last successful nightly build.

**Skip condition:** If `main` has not changed (no new commits) since the last nightly, the build is skipped and no new release is created. A skipped build posts a log entry but does not create a GitHub Pre-Release.

**Manual trigger:** Core Maintainers may trigger a nightly build on demand via `workflow_dispatch` with an optional `reason` parameter logged to the build record.

---

## 3. Artifact Naming

```
ArizenOS-nightly-{YYYYMMDD}-{short-sha}.apbx

Examples:
  ArizenOS-nightly-20260601-bac5c48.apbx
  ArizenOS-nightly-20260602-a1b2c3d.apbx
```

The nightly artifact is **never** named `ArizenOS.apbx`. This prevents accidental confusion with stable releases.

The accompanying checksum file follows the same pattern:
```
ArizenOS-nightly-{YYYYMMDD}-{short-sha}.apbx.sha256
```

---

## 4. Nightly Build Process

```
02:00 UTC — nightly.yml triggered by schedule
        │
        ▼
Check: has main changed since last nightly?
  NO  → Skip build, log "no new commits", exit
  YES ↓
        │
        ▼
Checkout main at HEAD
        │
        ▼
Run CI validation gates:
  - Unit tests (test-registry-keys, test-debloat-safety, test-script-standards)
  - Build validation (dry-run of build-apbx.ps1)
        │
        ▼
Gates passed? 
  NO  → Mark build FAILED, post to #ci-notifications, exit (no release created)
  YES ↓
        │
        ▼
Build ArizenOS-nightly-{date}-{sha}.apbx
Generate SHA256 checksum
        │
        ▼
Create GitHub Pre-Release:
  - Tag:       nightly/{YYYYMMDD}   (lightweight, not GPG-signed)
  - Title:     "ArizenOS Nightly — {YYYY-MM-DD} ({short-sha})"
  - Body:      auto-generated (see Section 5)
  - Assets:    .apbx + .sha256
  - pre-release: true
  - latest:    false
        │
        ▼
Expire previous nightly (see Section 6)
        │
        ▼
Post build summary to #ci-notifications
```

---

## 5. Nightly Release Notes (Auto-Generated)

Nightly release notes are generated automatically by the CI system. They contain:

```markdown
## ArizenOS Nightly — {YYYY-MM-DD}

> **⚠ EXPERIMENTAL BUILD — NOT FOR PRODUCTION USE**  
> This is an automated nightly build from the `main` branch.  
> It may contain incomplete features, known bugs, and untested changes.  
> Use only for development and testing purposes.

**Build Information**
- Commit: {full SHA} ([view](https://github.com/Alrizz-art/ArizenOS/commit/{sha}))
- Branch: main
- Build Time: {ISO 8601 timestamp}
- Windows Targets: 10 22H2 (Build 19045+), 11 23H2+

**Commits Since Last Nightly**
{auto-generated list of commits since previous nightly tag}

**CI Status**
- Unit Tests: ✅ Passed / ❌ Failed
- Build Validation: ✅ Passed / ❌ Failed
- Integration Tests: Not run (nightly only runs unit tests)

**How to Report Issues**
File a GitHub Issue with label `nightly-bug` and include:
- Your Windows version and build number
- The nightly build date and commit SHA (shown above)
- `C:\ArizenOS\Logs\install_*.log`
```

---

## 6. Nightly Expiry Policy

At most **7 nightly releases** are retained at any time. When a new nightly is published:

1. The CI system queries all existing nightly releases tagged `nightly/*`
2. Releases beyond the 7 most recent are deleted from GitHub Releases
3. Their `.apbx` and `.sha256` assets are deleted from GitHub
4. Their lightweight tags are deleted from the repository

**Exception:** A nightly is never deleted if it is actively referenced by an open bug report (checked via Issue search for the commit SHA). Such nightlies are retained until the referenced issue is closed.

---

## 7. What Nightlies Do NOT Include

| Item | Nightlies | Stable |
|------|-----------|--------|
| Human-written changelog | ❌ Auto-generated only | ✅ |
| Security review | ❌ | ✅ Required |
| Integration test pass | ❌ Not run | ✅ Required |
| Smoke test sign-off | ❌ | ✅ Required |
| GPG-signed tag | ❌ Lightweight tag only | ✅ Annotated, signed |
| `latest.json` pointer | ❌ Never updated | ✅ Updated on release |
| Support commitment | ❌ None | ✅ Per lifecycle policy |
| AME Wizard "update available" notification | ❌ | ✅ |

---

## 8. Nightly vs. Pre-Release Comparison

| Attribute | Nightly | Alpha | Beta | RC |
|-----------|---------|-------|------|----|
| Source | `main` HEAD | `main` milestone | `main` milestone | `release/*` |
| Trigger | Schedule | Manual | Manual | Manual |
| Changelog | Auto-generated | Manual | Manual | Manual |
| Security review | No | No | No | Yes |
| Integration tests | No | Optional | Yes | Yes |
| Retention | 7 builds | Permanent | Permanent | Permanent |
| Audience | Developers | Internal | Community | All |

---

## 9. Disabling Nightlies

The nightly build can be disabled without code changes:

- In GitHub Actions, disable the `nightly.yml` workflow schedule
- Or: add a repository variable `NIGHTLY_DISABLED=true` — the workflow checks this at start and exits cleanly

Disabling is appropriate during:
- Extended feature freezes (no commits expected)
- CI runner maintenance windows
- Periods when `main` is intentionally unstable (e.g. mid-migration)

---

## 10. Nightly Build Failure Protocol

If a nightly build fails (unit tests fail or build validation fails):

1. CI posts a failure notice to `#ci-notifications` with the error summary and commit SHA
2. No release is published (broken builds are never published, even as nightlies)
3. The commit author (from the most recent commit on `main`) is mentioned in the notice
4. If the same failure persists for **3 consecutive nightly builds**, it is escalated to all Core Maintainers
5. A persistent failure that blocks main for more than 72 hours is treated as a critical defect — a hotfix or revert is mandatory

A nightly build failure does not block development on `main`. It is a signal that the failing change needs attention, not a hard stop.
