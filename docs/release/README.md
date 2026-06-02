# ArizenOS Release Engineering

> **Scope:** Complete release engineering process for the ArizenOS project  
> **Audience:** Core Maintainers, Release Managers, Contributors, Security Lead  
> **Effective From:** v0.1.0  
> **Maintained By:** Release Engineering Team

---

## What This Is

This directory is the authoritative reference for how ArizenOS is designed, built, tested, versioned, and shipped. Every decision that affects the quality and reliability of a release — from how a commit message is formatted to how a zero-day vulnerability is disclosed — is documented here.

These documents are living references. They evolve with the project. When a process changes, this documentation changes first.

---

## Documents

### Versioning and Branching

| Document | What It Answers |
|----------|----------------|
| [SEMANTIC_VERSIONING.md](SEMANTIC_VERSIONING.md) | When to bump MAJOR, MINOR, or PATCH; pre-release identifiers; version precedence; compatibility commitments |
| [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) | Trunk-based development model; branch taxonomy; naming conventions; protection rules; merge strategy |
| [RELEASE_BRANCHES.md](RELEASE_BRANCHES.md) | When release branches are created; RC stabilization period; hotfix branch lifecycle; cherry-pick policy; concurrent release support |

### Release Types

| Document | What It Answers |
|----------|----------------|
| [STABLE_RELEASES.md](STABLE_RELEASES.md) | Prerequisites to ship; step-by-step release process; artifact specification; rollback and yanking; end-of-life policy |
| [NIGHTLY_RELEASES.md](NIGHTLY_RELEASES.md) | Nightly build trigger; artifact naming; auto-generated notes; expiry policy; failure protocol |
| [GITHUB_RELEASES.md](GITHUB_RELEASES.md) | GitHub Release page specification; asset integrity; tag specification; automation; permissions |

### Process

| Document | What It Answers |
|----------|----------------|
| [CHANGELOG_PROCESS.md](CHANGELOG_PROCESS.md) | Two-layer changelog system; contributor responsibility; release changelog production; security section format |
| [SECURITY_PATCH_PROCESS.md](SECURITY_PATCH_PROCESS.md) | Severity classification; reporting channels; coordinated disclosure; remediation workflow; advisory publication; protected component violations |
| [CONTRIBUTOR_WORKFLOW.md](CONTRIBUTOR_WORKFLOW.md) | Contributor roles; PR process; review expectations; issue triage; code ownership; recognition |
| [CICD_WORKFLOW.md](CICD_WORKFLOW.md) | All GitHub Actions workflows; job specifications; failure behavior; permissions model; notification routing |

---

## Process at a Glance

```
CONTRIBUTING A CHANGE
──────────────────────
Fork → Branch (feat/{slug}) → Develop → Run unit tests locally
→ Update CHANGELOG.md [Unreleased] → Open PR → CI gate (ci.yml)
→ 2 Core Maintainer approvals → Squash merge to main
→ Feature branch auto-deleted

RELEASING A NEW VERSION
────────────────────────
Feature freeze → Create release/{version} branch → Tag rc.1
→ 7-day RC stabilization → Fix blockers (cherry-pick to main)
→ Pass full test matrix (Win 10 + Win 11) → Security review sign-off
→ Merge release branch to main → Tag v{version} (GPG signed)
→ CI builds .apbx + publishes GitHub Release + updates latest.json
→ 14-day post-release monitoring

SHIPPING A HOTFIX
──────────────────
Identify critical issue → Create hotfix/{version} from stable tag
→ Fix + unit tests + smoke tests → 1 Core Maintainer approval
→ Tag v{patch} → CI publishes hotfix release
→ Cherry-pick fix to main + any open release/* branches

RESPONDING TO A SECURITY ISSUE
────────────────────────────────
Private report received → Acknowledge within SLA → Reproduce + classify
→ Notify Core Maintainers privately → Fix on private branch
→ Coordinate disclosure date → Publish fix + advisory simultaneously
→ Post-mortem if protected component was violated
```

---

## Role Quick Reference

| Task | Who |
|------|-----|
| Review and merge PRs | Core Maintainer (2 required) |
| Declare feature freeze | Release Manager |
| Create release branch | Release Manager |
| Tag releases | Release Manager (GPG signed) |
| Run security review | Security Lead |
| Manage hotfixes | Core Maintainer (1 required) |
| Triage issues | Trusted Contributor or Core Maintainer |
| Handle security reports | Security Lead |
| Expire nightly releases | CI System (automated) |

---

## Key Invariants

These rules are non-negotiable across all release types, roles, and circumstances:

1. **`main` is always shippable.** No commit lands on `main` that does not pass CI.
2. **Tags are immutable.** A published tag is never moved, deleted, or re-pushed.
3. **Protected components are never touched.** Windows Update, Defender, Store, Firewall, UAC — in any release, under any configuration.
4. **Security disclosures are coordinated.** No public disclosure before the fix is published.
5. **Yanked releases are never deleted.** Users must always be able to download the exact version they installed.
6. **The changelog is human-written.** No automated changelog generators produce user-facing release notes.
7. **Nightlies never become `latest`.** Only stable releases update the `latest` pointer.
8. **Two Core Maintainer approvals for every stable merge.** No exceptions, no self-approvals.

---

## Getting Help

| Need | Where to Look |
|------|--------------|
| First contribution | `CONTRIBUTING.md` (repo root) → [CONTRIBUTOR_WORKFLOW.md](CONTRIBUTOR_WORKFLOW.md) |
| How to run tests | `playbook/tests/README.md` |
| How to build the .apbx | `scripts/build-apbx.ps1 --help` |
| Reporting a bug | GitHub Issues → Bug Report template |
| Reporting a security issue | `SECURITY.md` (repo root) — private channel |
| Current release status | GitHub Milestones |
| Latest stable download | [Releases](https://github.com/Alrizz-art/ArizenOS/releases/latest) |
