# Release Branches

> **Scope:** Lifecycle of `release/*` and `hotfix/*` branches  
> **Owner:** Release Manager (designated Core Maintainer for a given release)  
> **Trigger:** Release enters RC phase

---

## 1. Purpose of Release Branches

Release branches exist to **stabilize a version for shipping** without blocking ongoing development on `main`. Once a release branch is created, `main` continues to receive new features for the next release while the release branch receives only critical bug fixes and RC-gate corrections.

Release branches are **not** created for every version — only for MINOR and MAJOR releases. PATCH releases (hotfixes) use the separate `hotfix/*` flow.

---

## 2. When a Release Branch Is Created

A release branch is created at the moment a release transitions from **beta** to **RC**. Prior to this point, all beta development happens directly on feature branches merging to `main`.

```
Timeline:

main ──▶ [feat/A merged] ──▶ [feat/B merged] ──▶ [0.2.0-beta.1 tag on main]
              ↓                                             ↓
         more features                          release/0.2.0 branched HERE
         continue on main                       (RC stabilization begins)
```

**Trigger conditions for release branch creation:**

1. Feature freeze declared by Release Manager
2. All planned features for the milestone are merged into `main`
3. Beta testing has occurred with no outstanding blocker-class issues
4. Release Manager announces: "Entering RC phase for v{X}.{Y}.0"

---

## 3. Release Branch Lifecycle

```
Phase 1: CREATION
─────────────────
Create: release/{version} from main at the feature-freeze commit
Tag:    v{version}-rc.1 on release branch
Notify: Core team + community testers

Phase 2: RC STABILIZATION
──────────────────────────
Only these are merged into release/{version}:
  - Critical bug fixes (severity: critical or high)
  - RC-specific test failures
  - Documentation corrections for this version

All fixes ALSO cherry-picked to main.

No new features. No MINOR changes.

Phase 3: RC PROMOTION
─────────────────────
If no blockers after RC stabilization period (minimum 7 days):
  → Promote rc.N to stable

If blockers found:
  → Fix on release branch
  → Tag rc.{N+1}
  → Restart stabilization period

Phase 4: STABLE RELEASE
────────────────────────
Merge release/{version} → main (merge commit)
Tag: v{version} on main (not on release branch)
Build .apbx from the tag
Publish GitHub Release
Archive release branch (do not delete immediately — keep 90 days)

Phase 5: ARCHIVAL
──────────────────
After 90 days, release branch is deleted.
The tag remains permanent.
```

---

## 4. What Is Allowed on a Release Branch

| Change Type | Allowed | PR Required | Approvals |
|------------|---------|------------|----------|
| Critical bug fix | ✅ Yes | Yes | 2 Core Maintainers |
| High-severity bug fix | ✅ Yes | Yes | 2 Core Maintainers |
| Medium/low bug fix | ⚠ Case-by-case | Yes | Release Manager decision |
| Documentation correction | ✅ Yes | Yes | 1 Core Maintainer |
| Security patch (critical) | ✅ Yes | Expedited | 1 Core Maintainer |
| New feature | ❌ No | — | — |
| Dependency addition | ❌ No | — | — |
| Refactoring | ❌ No | — | — |
| Version bump | ✅ Yes (automatic) | CI handles | N/A |

---

## 5. RC Stabilization Period

| RC Number | Minimum Stabilization Period | Testing Requirement |
|-----------|----------------------------|-------------------|
| rc.1 | 7 days | Full test suite on Win 10 22H2 + Win 11 23H2 |
| rc.2 | 5 days | Full test suite on both targets |
| rc.3+ | 3 days | Full test suite — if rc.4 needed, Release Manager review required |
| rc.5+ | Release Manager must escalate to Core Maintainers | May trigger milestone scope reduction |

If a release requires more than 3 RC iterations, a post-mortem is mandatory before `1.0.0`.

---

## 6. Cherry-Pick Policy

Every fix merged into a release branch **must** be cherry-picked to `main` within 48 hours. This is the Release Manager's responsibility.

Cherry-pick checklist:
- [ ] Fix is merged to `release/{version}`
- [ ] Cherry-pick commit created on `main` (via PR, not direct push)
- [ ] Cherry-pick PR references the original fix PR
- [ ] CI passes on `main` after cherry-pick

Untracked cherry-picks are a release-blocking defect. CI checks that the diff between `release/{version}` and `main` is only forward-compatible changes.

---

## 7. Hotfix Branches (`hotfix/{version}`)

Hotfix branches address **critical issues in already-published stable releases**. They do not go through the RC phase.

### When to Create a Hotfix Branch

A hotfix is triggered by any of:

| Trigger | Severity |
|---------|---------|
| A shipped entry accidentally touches a protected component | Critical |
| A script vulnerability is identified (remote code execution risk) | Critical |
| A registry change breaks a system component | Critical |
| A released entry causes data loss | Critical |
| A shipped entry fails on a significant percentage of systems | High |
| A security advisory affects a bundled package ID | High |

### Hotfix Branch Lifecycle

```
Stable tag (e.g. v0.1.0)
  │
  └─▶ hotfix/0.1.1 (branched FROM the v0.1.0 tag, not from main)
        │
        │  (Fix applied, unit tests, smoke tests)
        │
        ├─▶ PR → hotfix/0.1.1 (1 Core Maintainer approval)
        │
        ├─▶ Tag v0.1.1 on hotfix/0.1.1
        │
        ├─▶ Build .apbx from tag
        │
        ├─▶ Publish GitHub Release (marked as "patch" release)
        │
        ├─▶ Cherry-pick fix to main (PR)
        │
        └─▶ Cherry-pick fix to any active release/* branch
```

### Hotfix Merge Sequence

The order of operations is strict:

1. Fix is reviewed and merged to `hotfix/{version}`
2. Tag `v{version}` pushed on `hotfix/{version}`
3. CI builds `.apbx` from the tag
4. GitHub Release published
5. Fix cherry-picked to `main` via PR
6. Fix cherry-picked to any open `release/*` branch
7. `hotfix/{version}` branch deleted

**Never merge hotfix branch to `main` directly** — only cherry-pick the fix commit.

---

## 8. Concurrent Release Support

ArizenOS supports at most **two concurrent stable release lines** at any time: the latest stable release and the immediately prior stable release (LTS candidate for future consideration).

```
Current:   0.2.x  ← receives all hotfixes
Prior:     0.1.x  ← receives only critical security hotfixes (90 days after 0.2.0)
EOL:       0.0.x  ← no support
```

When `0.3.0` ships:
- `0.2.x` becomes the prior-supported line (security-only hotfixes)
- `0.1.x` reaches EOL
- EOL is announced in the release notes and GitHub notice at least 30 days before

---

## 9. Release Branch Naming Reference

| Scenario | Branch Name | Example |
|----------|------------|---------|
| New MINOR release | `release/0.{N}.0` | `release/0.2.0` |
| New MAJOR release | `release/{N}.0.0` | `release/1.0.0` |
| Critical patch on stable | `hotfix/0.{N}.{P}` | `hotfix/0.1.1` |

PATCH-only releases do not get release branches — they are always hotfixes from a prior release tag.
