# Branch Strategy

> **Model:** Scaled Trunk-Based Development with release stabilization branches  
> **Primary Branch:** `main`  
> **Protected Branches:** `main`, `release/*`, `hotfix/*`  
> **Owner:** Release Engineering Team

---

## 1. Philosophy

ArizenOS uses a **scaled trunk-based development** model. All feature work merges into `main` through short-lived feature branches. Release stabilization happens on dedicated release branches, which are created only when a release enters the RC phase. This model keeps `main` shippable at all times and avoids the complexity of long-lived development branches.

```
main ──────────────────────────────────────────────────────▶  (always releasable)
       │        │        │         │          │
     feat/A   feat/B   fix/C   release/0.2  hotfix/0.1.1
       │        │        │         │          │
       └────────┴────────┴─────────┴──────────┘ (merged back to main)
```

---

## 2. Branch Taxonomy

| Branch Type | Pattern | Created By | Lifetime | Merges Into |
|------------|---------|-----------|---------|-------------|
| **Trunk** | `main` | Permanent | Permanent | N/A |
| **Feature** | `feat/{slug}` | Any contributor | Days to weeks | `main` |
| **Bugfix** | `fix/{slug}` | Any contributor | Hours to days | `main` |
| **Release** | `release/{version}` | Release Manager | Days (RC phase only) | `main` |
| **Hotfix** | `hotfix/{version}` | Core Maintainer | Hours to days | `main` + `release/*` |
| **Documentation** | `docs/{slug}` | Any contributor | Days | `main` |
| **Chore** | `chore/{slug}` | Any contributor | Days | `chore` → `main` |
| **Experiment** | `experiment/{slug}` | Any contributor | Open-ended | Never (or `main` with RFC) |

---

## 3. Main Branch (`main`)

`main` is the single source of truth. It is:

- **Always in a shippable state** — every commit to `main` must pass all CI checks
- **Never committed to directly** — all changes arrive via Pull Request
- **Protected by branch rules** — force-push disabled, deletion disabled, required status checks enforced
- **Signed** — all commits on `main` are GPG-signed (enforced via `git config commit.gpgSign true` for Core Maintainers)

### What "Shippable" Means for `main`

A commit on `main` is shippable if:
- All unit tests pass
- Script static analysis passes
- `scripts/build-apbx.ps1` succeeds (dry-run validation)
- No known critical security issues in any merged PR
- Debloat safety tests pass

`main` is not required to have passed integration tests on a clean VM — that gate applies only to release branches.

---

## 4. Feature Branches (`feat/{slug}`)

**Naming:** `feat/{2-5-word-slug-in-kebab-case}`

```
feat/privacy-hardening
feat/fonts-support
feat/windows11-mica-effect
feat/oem-support-url
```

**Lifecycle:**

```
main (latest)
  │
  └─▶ feat/privacy-hardening
            │
            │  (develop, commit, push)
            │
            └─▶ Pull Request → main
                  (code review + CI gate)
```

**Rules:**
- Branch from the latest `main` commit — never from another feature branch
- One feature per branch — no bundling of unrelated changes
- Maximum lifetime: 30 days. Branches older than 30 days require a rebase onto `main` and a comment explaining the delay
- Feature branches are deleted immediately after merge

---

## 5. Bugfix Branches (`fix/{slug}`)

**Naming:** `fix/{2-5-word-slug}`

```
fix/oem-bmp-bit-depth
fix/debloat-missing-guard
fix/wallpaper-null-path
```

Same rules as feature branches. Bugfixes targeting the current `release/*` branch (not yet stable) are branched from and merged into that release branch, then cherry-picked to `main`.

Hotfixes for **stable releases** follow the separate `hotfix/` flow (see Section 8 of `RELEASE_BRANCHES.md`).

---

## 6. Release Branches (`release/{version}`)

**Naming:** `release/{MAJOR}.{MINOR}.{PATCH}` — no pre-release suffix in branch name

```
release/0.2.0
release/1.0.0
```

Release branches are created when a MINOR or MAJOR release enters the RC phase. See `RELEASE_BRANCHES.md` for the complete lifecycle.

---

## 7. Hotfix Branches (`hotfix/{version}`)

**Naming:** `hotfix/{MAJOR}.{MINOR}.{PATCH}` — the patch version being produced

```
hotfix/0.1.1
hotfix/1.0.2
```

Hotfix branches branch from the release tag of the version being patched, not from `main`. This is the only scenario where a branch is not created from `main`.

---

## 8. Branch Protection Rules

### `main`

| Rule | Setting |
|------|---------|
| Require pull request before merging | ✅ Enabled |
| Required approving reviews | 2 (Core Maintainer) |
| Dismiss stale pull request approvals on new commits | ✅ Enabled |
| Require review from Code Owners | ✅ Enabled |
| Require status checks to pass | ✅ All CI jobs |
| Require branches to be up to date before merging | ✅ Enabled |
| Require conversation resolution before merging | ✅ Enabled |
| Require signed commits | ✅ Enabled |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled |

### `release/*`

| Rule | Setting |
|------|---------|
| Require pull request before merging | ✅ Enabled |
| Required approving reviews | 2 (Core Maintainer) |
| Require status checks to pass | ✅ All CI jobs |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled (automatic after release tag is pushed) |

### `hotfix/*`

| Rule | Setting |
|------|---------|
| Require pull request before merging | ✅ Enabled |
| Required approving reviews | 1 (Core Maintainer) |
| Require status checks to pass | ✅ CI unit + smoke |
| Allow force pushes | ❌ Disabled |

---

## 9. Merge Strategy

| Scenario | Strategy | Rationale |
|----------|---------|-----------|
| Feature/fix → `main` | Squash merge | Clean linear history, atomic commits |
| Release branch → `main` | Merge commit | Preserves release history in graph |
| Hotfix → `main` | Squash merge | Single atomic commit |
| Hotfix → `release/*` | Cherry-pick | Targeted fix, no history noise |

**Squash merge commit message format:**

```
{type}({scope}): {description} (#PR_NUMBER)

{optional body}
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `perf`, `security`, `ci`, `test`

---

## 10. Repository-Level Settings

| Setting | Value |
|---------|-------|
| Default branch | `main` |
| Delete head branches after merge | ✅ Enabled (auto-cleanup) |
| Allow merge commits | ❌ Disabled (release merges only, handled by Release Manager) |
| Allow squash merging | ✅ Enabled |
| Allow rebase merging | ❌ Disabled (prevents non-linear history) |
| Automatically delete head branches | ✅ Enabled |
