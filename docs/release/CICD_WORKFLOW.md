# CI/CD Workflow

> **Platform:** GitHub Actions  
> **Runner Strategy:** GitHub-hosted Windows runners (unit/integration); Ubuntu runners (documentation, tooling)  
> **Workflows:** `ci.yml`, `release.yml`, `nightly.yml`, `security.yml`  
> **Owner:** Core Maintainers  
> **Philosophy:** Every gate is visible, deterministic, and fast enough that contributors don't circumvent it

---

## 1. Workflow Inventory

| Workflow File | Trigger | Runner | Purpose |
|-------------|---------|--------|---------|
| `ci.yml` | PR → `main`; PR → `release/*` | Windows | PR validation gate |
| `release.yml` | Tag push `v*` | Windows + Ubuntu | Build and publish releases |
| `nightly.yml` | Schedule 02:00 UTC + `workflow_dispatch` | Windows | Nightly build |
| `security.yml` | PR (security label); schedule (weekly) | Windows | Security audit |
| `branch-hygiene.yml` | Schedule (weekly) | Ubuntu | Stale branch cleanup |

---

## 2. CI Workflow (`ci.yml`)

The primary PR gate. Every PR to `main` or `release/*` must pass this workflow before merge.

### Trigger

```
on:
  pull_request:
    branches: [main, release/*]
  push:
    branches: [main]           ← Re-run on merge to confirm green state
```

### Jobs

```
Job: validate-metadata
───────────────────────
Runner:   ubuntu-latest
Timeout:  5 minutes
Purpose:  Fast pre-flight that doesn't need a Windows runner

  Steps:
    1. Checkout
    2. Verify CHANGELOG.md is updated (diff check)
       → If not: post comment "needs-changelog", set label, fail job
    3. Verify playbook.yaml syntax (YAML lint)
    4. Verify all entry YAML files referenced in playbook.yaml exist
    5. Verify no merge conflict markers in any file
    6. Verify commit messages follow conventional commit format
```

```
Job: unit-tests
───────────────
Runner:   windows-latest
Timeout:  15 minutes
Needs:    validate-metadata (runs after)

  Steps:
    1. Checkout
    2. Install Pester v5 (cached)
    3. Run test-registry-keys.ps1 → JUnit XML report
    4. Run test-oem-branding.ps1 → JUnit XML report
    5. Run test-debloat-safety.ps1 → JUnit XML report (CRITICAL)
    6. Run test-script-standards.ps1 → JUnit XML report
    7. Upload test reports as artifacts
    8. Publish test results to GitHub PR check
```

```
Job: build-validation
──────────────────────
Runner:   windows-latest
Timeout:  10 minutes
Needs:    unit-tests

  Steps:
    1. Checkout
    2. Run build-apbx.ps1 --dry-run (validate structure, don't produce .apbx)
    3. Validate all asset files exist at expected paths
    4. Validate playbook.yaml version field format matches SemVer
    5. Validate all entry YAML files pass schema check
    6. Post build validation summary to PR
```

```
Job: changelog-format
──────────────────────
Runner:   ubuntu-latest
Timeout:  2 minutes
Needs:    (none — runs in parallel with validate-metadata)

  Steps:
    1. Checkout
    2. Validate CHANGELOG.md structure (has [Unreleased] section)
    3. Validate new entries are in the correct sections
    4. Validate no entries reference PR numbers (content must be self-describing)
```

### Failure Behavior

| Job Fails | Effect |
|----------|--------|
| `validate-metadata` | `unit-tests` and `build-validation` are skipped (cascade) |
| `unit-tests` | `build-validation` is skipped |
| `build-validation` | PR is blocked — cannot merge |
| `changelog-format` | PR is labeled `needs-changelog-fix`, blocked from merge |

### CI Caching

| Cache | Key | TTL |
|-------|-----|-----|
| Pester module | `pester-v5-{hash}` | 7 days |
| PowerShell modules | `psmodules-{lock-hash}` | 7 days |

---

## 3. Release Workflow (`release.yml`)

Triggered on tag push. Handles both stable releases and pre-releases.

### Trigger

```
on:
  push:
    tags:
      - 'v*.*.*'           ← Stable: v1.2.3
      - 'v*.*.*-*'         ← Pre-release: v1.2.3-rc.1
```

### Jobs

```
Job: validate-release
──────────────────────
Runner:   ubuntu-latest
Timeout:  5 minutes

  Steps:
    1. Checkout at tag
    2. Extract version from tag name
    3. Verify playbook.yaml version field EXACTLY matches tag version
       → MISMATCH = fail immediately (blocking error)
    4. Verify release changelog file exists:
       playbook/releases/changelogs/v{version}.md
    5. Verify release manifest file exists:
       playbook/releases/manifests/v{version}.json
    6. Verify SHA256 placeholder in manifest is not empty
    7. Determine release type: stable vs. pre-release (by tag suffix)
```

```
Job: run-tests
───────────────
Runner:   windows-latest
Timeout:  20 minutes
Needs:    validate-release

  Steps:
    1. Checkout at tag
    2. Run full unit test suite (all 4 test files)
    3. Run security audit: scripts/security-audit.ps1
       → Record baseline results as artifact
    4. All tests must pass — any failure blocks release
```

```
Job: build
───────────
Runner:   windows-latest
Timeout:  15 minutes
Needs:    run-tests

  Steps:
    1. Checkout at tag
    2. Run scripts/build-apbx.ps1 (full build, not dry-run)
    3. Verify ArizenOS.apbx created
    4. Verify ArizenOS.apbx opens without schema error
       (AME Wizard CLI validation, if available; otherwise manifest check)
    5. Generate SHA256 checksum
    6. Write checksum to playbook/releases/checksums/v{version}.sha256
    7. Upload ArizenOS.apbx as workflow artifact
    8. Upload checksum as workflow artifact
```

```
Job: publish
─────────────
Runner:   ubuntu-latest
Timeout:  10 minutes
Needs:    build

  Steps:
    1. Download artifacts from build job
    2. Read release body from playbook/releases/changelogs/v{version}.md
    3. Determine GitHub Release flags:
       pre-release = true  if tag contains prerelease identifier
       pre-release = false if tag is clean vX.Y.Z
       latest     = true  only if pre-release = false
    4. Create GitHub Release via API:
       - tag: {pushed tag}
       - name: "ArizenOS v{version}" (or "ArizenOS v{version} [RC N]")
       - body: {changelog content}
       - pre-release: {determined above}
       - latest: {determined above}
    5. Upload ArizenOS.apbx to release
    6. Upload ArizenOS.apbx.sha256 to release
    7. If stable release: update playbook/releases/manifests/latest.json
       and commit to main via API (bot commit)
```

### Environment Secrets Required

| Secret | Used By | Purpose |
|--------|---------|---------|
| `GITHUB_TOKEN` | All jobs (provided by GitHub Actions) | Checkout, release creation |
| `RELEASE_SIGNING_KEY` | (Future) `publish` job | GPG sign the release assets |

The standard `GITHUB_TOKEN` (auto-provided by Actions) has sufficient permissions for release creation when `permissions: contents: write` is set in the workflow.

---

## 4. Nightly Workflow (`nightly.yml`)

See `NIGHTLY_RELEASES.md` for full process. CI detail:

### Jobs

```
Job: check-changes
───────────────────
Runner:   ubuntu-latest
Timeout:  2 minutes

  Steps:
    1. Compare HEAD of main to last nightly tag (nightly/*)
    2. If no new commits: set output skip=true
    3. Post to #ci-notifications: "No new commits — nightly skipped"

Job: build-nightly
───────────────────
Runner:   windows-latest
Timeout:  20 minutes
Needs:    check-changes (skipped if skip=true)

  Steps:
    1. Checkout main at HEAD
    2. Run unit tests
    3. Run build-apbx.ps1
    4. Rename artifact: ArizenOS-nightly-{date}-{sha}.apbx
    5. Generate checksum
    6. Create lightweight tag: nightly/{YYYYMMDD}
    7. Create GitHub Pre-Release (nightly spec)
    8. Expire old nightlies (keep 7 most recent)
    9. Post build summary to #ci-notifications
```

---

## 5. Security Workflow (`security.yml`)

### Trigger

```
on:
  pull_request:
    labels: [security]       ← Security-labeled PRs get extra scrutiny
  schedule:
    - cron: '0 6 * * 1'     ← Weekly Monday 06:00 UTC baseline scan
  workflow_dispatch:          ← Manual trigger for ad-hoc audit
```

### Jobs

```
Job: static-analysis
─────────────────────
Runner:   windows-latest
Timeout:  10 minutes

  Steps:
    1. Run test-script-standards.ps1 (extended mode)
    2. Scan for Invoke-Expression, IEX, DownloadString patterns
    3. Scan for hardcoded credentials or API keys (secret scanning)
    4. Verify no HTTP URLs in script bodies (HTTPS only)
    5. Verify all WinGet package IDs against known-good list

Job: protected-component-check
────────────────────────────────
Runner:   windows-latest
Timeout:  5 minutes

  Steps:
    1. Run test-registry-keys.ps1 (full protected key audit)
    2. Run test-debloat-safety.ps1 (protected apps guard verification)
    3. Scan all .reg files for protected key patterns
    4. Scan all .ps1 files for protected service names
    5. Fail if ANY protected component is referenced in a modifying context

Job: generate-security-report
──────────────────────────────
Runner:   ubuntu-latest
Timeout:  5 minutes
Needs:    static-analysis, protected-component-check

  Steps:
    1. Aggregate results from both jobs
    2. Generate Markdown security report
    3. Upload report as artifact
    4. If weekly scan: post report summary to #security-notifications
    5. If PR scan: post summary as PR comment
```

---

## 6. Branch Hygiene Workflow (`branch-hygiene.yml`)

### Schedule

Weekly, Monday 08:00 UTC.

### Jobs

```
Job: stale-branches
────────────────────
Runner:   ubuntu-latest

  Steps:
    1. List all branches except: main, release/*, hotfix/*, experiment/*
    2. For each branch with no commits in 30 days:
       a. If the branch has an open PR: skip (do not touch)
       b. If no open PR: post a comment to the branch author (via commit history)
          "This branch has been inactive for 30 days. It will be deleted in 7 days
           unless a PR is opened."
    3. For branches with no commits in 37 days AND no open PR:
       a. Delete the branch
       b. Post to #ci-notifications: "Deleted stale branch: {name}"
```

Protected branches (`main`, `release/*`) are never touched by this workflow.

---

## 7. CI Environment Standards

### Runner Selection

| Job Type | Runner | Justification |
|----------|--------|--------------|
| PowerShell script execution | `windows-latest` | Native Windows environment |
| Registry validation | `windows-latest` | Registry operations require Windows |
| YAML/JSON validation | `ubuntu-latest` | Faster, cheaper, no Windows needed |
| GitHub API operations | `ubuntu-latest` | Platform-agnostic |
| Release artifact upload | `ubuntu-latest` | Platform-agnostic |

### Timeouts

All jobs have explicit timeouts. Jobs that hang (e.g., AME Wizard waiting for user input) are terminated. Timeouts are conservative — 2× expected duration.

| Job | Timeout |
|-----|---------|
| Metadata validation | 5 min |
| Unit tests | 15 min |
| Build validation | 10 min |
| Full build | 15 min |
| Nightly build | 20 min |
| Security scan | 15 min |

### Concurrency Controls

Concurrent CI runs on the same branch are cancelled:

```
concurrency:
  group: ci-{github.ref}
  cancel-in-progress: true
```

This prevents queue pileup when multiple commits land in quick succession on `main`. Release and nightly workflows do not use concurrency cancellation — they always run to completion.

---

## 8. Notifications

| Event | Channel | Audience |
|-------|---------|---------|
| PR CI failure | GitHub PR check + comment | PR author + reviewers |
| Nightly build failure | #ci-notifications | Core Maintainers |
| 3 consecutive nightly failures | Core Maintainer mention in #ci-notifications | All Core Maintainers |
| Stable release published | GitHub Discussions + #releases | All |
| Security scan new finding | #security-notifications | Security Lead + Core Maintainers |
| Stale branch deleted | #ci-notifications | Committers of the deleted branch |

---

## 9. CI Permissions Model

The CI workflows operate under the principle of least privilege.

| Workflow | `contents` | `pull-requests` | `issues` | `packages` |
|----------|-----------|-----------------|---------|-----------|
| `ci.yml` | `read` | `write` (post comments) | `write` (labels) | `none` |
| `release.yml` | `write` (create releases, tags) | `none` | `none` | `none` |
| `nightly.yml` | `write` (create pre-releases, tags) | `none` | `none` | `none` |
| `security.yml` | `read` | `write` (post comments) | `none` | `none` |
| `branch-hygiene.yml` | `write` (delete branches) | `none` | `none` | `none` |

No CI workflow has admin permissions. Release creation uses the `GITHUB_TOKEN` with scoped permissions — never a personal access token from a maintainer account.

---

## 10. Extending the CI Pipeline

When adding a new CI job or step:

1. **Draft the job locally** — test the PowerShell commands on a local machine before adding to CI
2. **Add an explicit timeout** — every job and every long-running step gets a timeout
3. **Define failure behavior** — what happens to downstream jobs if this job fails?
4. **Add to the matrix if needed** — if the job should run on both Win 10 22H2 and Win 11 23H2, use a `strategy.matrix`
5. **Document here** — update this file with the new job's entry in the workflow inventory
6. **Test in a fork first** — GitHub Actions workflows can be tested in a fork without affecting the main repo
7. **PR with `ci` label** — CI changes get the `ci` label for automatic routing to Core Maintainers

New CI jobs that run on Windows runners have a higher cost impact. Core Maintainer approval is required before adding any new Windows-runner job.
