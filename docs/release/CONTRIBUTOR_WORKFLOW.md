# Contributor Workflow

> **Scope:** All contributors — first-time, recurring, and Core Maintainers  
> **Governance:** `CONTRIBUTING.md` (repo root) is the entry point; this document is the engineering detail  
> **Code of Conduct:** `CODE_OF_CONDUCT.md` (repo root)

---

## 1. Contributor Roles

| Role | Access Level | Who | Responsibilities |
|------|-------------|-----|-----------------|
| **Community Contributor** | Fork + PR only | Anyone | Submit PRs, file issues, community testing |
| **Trusted Contributor** | Write access (non-protected branches) | Invited after 3+ merged PRs | Review PRs, triage issues, moderate discussions |
| **Core Maintainer** | Write + bypass protection (scoped) | Appointed by existing Core Maintainers | Review/merge PRs, release process, project direction |
| **Release Manager** | Core Maintainer + release authority | Rotated per-release cycle | Drive release process, manage release branches |
| **Security Lead** | Core Maintainer + security channels | Designated per rotation | Security review, advisory management |

---

## 2. Getting Started

### Fork and Clone

All community contributions start from a fork. Direct pushes to `Alrizz-art/ArizenOS` are not available to community contributors.

```
1. Fork: github.com/Alrizz-art/ArizenOS → your-username/ArizenOS
2. Clone your fork locally
3. Add upstream remote: git remote add upstream https://github.com/Alrizz-art/ArizenOS.git
4. Keep your fork current: git fetch upstream && git merge upstream/main
```

### Development Environment

ArizenOS is a Windows-native project. Development on Linux/macOS is possible for documentation and registry file changes, but script and integration testing requires Windows.

**Minimum development setup:**
- Windows 10 22H2 or Windows 11 23H2 (physical or VM)
- PowerShell 7+ (for running test scripts)
- AME Wizard v0.7.3+ (for manual testing of the .apbx)
- Git with GPG signing configured
- Pester v5+ (`Install-Module Pester`)
- A Hyper-V or VMware snapshot for clean integration tests (optional for first contributions)

---

## 3. Contribution Types and Paths

### Bug Report

```
File a GitHub Issue with template: Bug Report
Required fields:
  - ArizenOS version (from C:\ArizenOS\Logs\ or GitHub Release)
  - Windows version and build number (winver)
  - AME Wizard version
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - C:\ArizenOS\Logs\install_*.log (attach)
  - scripts/security-audit.ps1 output (if relevant)
```

### Feature Request

```
File a GitHub Issue with template: Feature Request
Required fields:
  - What should ArizenOS do?
  - Why does this matter to users?
  - Windows versions affected
  - Is this reversible? (if not, explain)
  - Does it touch any protected component? (if yes, the request is declined)
```

### Documentation Contribution

Documentation-only PRs (`docs/{slug}` branches) require:
- Correct Markdown formatting
- Accurate technical content (tested where applicable)
- One Core Maintainer approval (not two)
- No changelog entry required (unless the doc is user-facing and describes changed behavior)

### Script or Registry Contribution

All script and registry contributions require the full review process (Section 4).

---

## 4. Pull Request Process

### Step 1 — Claim the Work

Before starting significant work, comment on the relevant Issue: "I'll work on this." This prevents duplicate effort.

For first-time contributors, look for Issues labeled `good-first-issue`:
- Documentation corrections
- Clarifying comments in scripts
- New entries to the debloat list (following established pattern)
- Test additions

### Step 2 — Branch

```
From: upstream/main (always the latest main)
Name: {type}/{slug}
  feat/privacy-hardening
  fix/oem-bmp-dimensions
  docs/architecture-update
  chore/ci-timeout-increase
```

### Step 3 — Develop

Follow the authoring standards in `LIFECYCLE.md §2`. Every change type has specific requirements.

**During development, run locally before pushing:**

```powershell
# Unit tests (required before every push)
Invoke-Pester playbook/tests/unit/ -Output Detailed

# Script static analysis
Invoke-Pester playbook/tests/unit/test-script-standards.ps1 -Output Detailed

# Debloat safety (if touching debloat.ps1 or debloat lists)
Invoke-Pester playbook/tests/unit/test-debloat-safety.ps1 -Output Detailed
```

### Step 4 — Commit

```
Commit message format:
  {type}({scope}): {description}

  {optional body — what changed and why}

  Refs: #{issue-number}

Types: feat, fix, docs, chore, refactor, perf, security, ci, test
Scopes: playbook, entries, scripts, registry, assets, docs, ci, tests

Examples:
  feat(entries): add transparency.yaml for Acrylic and Mica effects
  fix(scripts): correct null path in wallpaper.ps1 on first run (#42)
  docs(release): update VERSIONING_STRATEGY with MAJOR bump triggers
  security(scripts): remove Invoke-Expression from developer-setup.ps1
```

All commits must be GPG-signed for security-sensitive changes (scripts, registry files). Documentation commits do not require signing.

### Step 5 — Update Changelog

Add an entry to `[Unreleased]` in `CHANGELOG.md`. See `CHANGELOG_PROCESS.md §3`.

### Step 6 — Open Pull Request

Use the PR template. Fill in all sections:

```markdown
## Summary
{What does this PR change and why?}

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change (MAJOR version bump required)
- [ ] Documentation only
- [ ] Security fix

## Testing
- [ ] Unit tests pass locally
- [ ] Smoke test completed (if script change)
- [ ] Tested on Windows 10 22H2
- [ ] Tested on Windows 11 23H2

## Checklist
- [ ] Changelog updated (CHANGELOG.md [Unreleased])
- [ ] No protected components are modified
- [ ] No hardcoded paths or credentials
- [ ] Follows authoring standards in LIFECYCLE.md
- [ ] Debloat safety test passes (if applicable)

## Related Issues
Closes #{issue-number}
```

### Step 7 — Review

**For community contributors:**
- 2 Core Maintainer approvals required to merge to `main`
- The PR author must not approve their own PR (enforced by GitHub)
- Reviewers are assigned automatically from `CODEOWNERS`
- Average review turnaround: 3–7 days
- If no review in 14 days, the author may post a comment requesting attention

**Review focus areas:**

| Area | Reviewers Check |
|------|----------------|
| Safety | Does this touch protected components? |
| Reversibility | Is there a documented rollback path? |
| Compatibility | Works on Win 10 22H2 AND Win 11 23H2? |
| Standards | Follows `LIFECYCLE.md §2` authoring standards? |
| Tests | Appropriate test coverage present or updated? |
| Security | Script static analysis passes? No remote code execution? |

### Step 8 — Address Feedback

All review comments must be resolved before merge. Reviewer comments fall into three categories:

| Category | Required Action |
|---------|----------------|
| `MUST` / `BLOCKER` | Fix required — PR cannot merge without it |
| `SHOULD` | Strong recommendation — fix or explain why not |
| `NIT` / `SUGGEST` | Optional — contributor's discretion |

### Step 9 — Merge

Once approved, the PR is squash-merged by a Core Maintainer. The squash merge commit message follows the commit format in Step 4. The feature branch is automatically deleted after merge.

---

## 5. Review Expectations for Core Maintainers

Core Maintainers commit to:

- **First response within 72 hours** on any PR (not necessarily full review — acknowledgement is enough)
- **Full review within 7 days** for standard PRs
- **Expedited review within 24 hours** for security-labeled PRs
- **Constructive feedback** — every blocking comment explains why and suggests how to resolve it
- **No approving then requesting changes** — approve only when the PR is ready
- **No merging your own PRs** — always requires a second Core Maintainer

---

## 6. Issue Triage

Issues are triaged within 72 hours by a Core Maintainer or Trusted Contributor. Triage assigns:

| Label | Meaning |
|-------|---------|
| `bug` | Confirmed defect in current behavior |
| `feature-request` | New capability requested |
| `security` | Security-related issue |
| `question` | User question — not a bug or feature |
| `good-first-issue` | Suitable for a first contribution |
| `needs-repro` | Cannot confirm without more information |
| `wont-fix` | Intentional behavior or out of scope |
| `duplicate` | Linked to existing issue |
| `playbook` | Related to playbook content (entries, scripts, registry) |
| `ci` | Related to CI/CD pipeline |
| `blocker` | Blocks a release milestone |

---

## 7. Code Ownership (`CODEOWNERS`)

ArizenOS uses GitHub `CODEOWNERS` to automatically assign reviewers.

```
# Default — all Core Maintainers review everything
*                              @Alrizz-art

# Playbook entries — require at least one Core Maintainer familiar with AME
entries/                       @Alrizz-art
playbook/manifests/entries/    @Alrizz-art

# Scripts — extra scrutiny for any PS1 change
scripts/                       @Alrizz-art
playbook/scripts/              @Alrizz-art

# Registry files — careful review required
registry/                      @Alrizz-art
playbook/registry/             @Alrizz-art

# Security-sensitive
scripts/security-audit.ps1     @Alrizz-art
playbook/SECURITY_REVIEW.md    @Alrizz-art

# CI/CD
.github/                       @Alrizz-art
```

As the team grows, `CODEOWNERS` is updated to route specific subsystems to the most knowledgeable maintainers.

---

## 8. Contributor Recognition

All contributors are recognized in:

- `CONTRIBUTORS.md` (repo root) — all contributors who have merged at least one PR
- GitHub Release Notes — significant contributors for each release are called out
- GitHub Discussions pinned post for major releases

The project does not have a monetary reward system. Recognition is the primary mechanism for acknowledging contributions.
