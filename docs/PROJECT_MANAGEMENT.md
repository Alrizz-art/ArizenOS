# ArizenOS — Project Management Guide

## Overview

ArizenOS uses GitHub's native project management tooling:
- **Issues** — bug reports, feature requests, tasks
- **Pull Requests** — all code changes via PR (no direct push to `main`)
- **Milestones** — version-based grouping of issues and PRs
- **Labels** — 45-label classification system for triage and filtering
- **Project Board** — Kanban workflow (6 columns, see setup below)
- **Discussions** — community Q&A, RFC proposals, announcements

---

## Label System

### Type labels
| Label | Use for |
|-------|---------|
| `type: bug` | Something broken |
| `type: feature` | New functionality |
| `type: refactor` | Internal restructure, no behavior change |
| `type: documentation` | Docs only |
| `type: security` | Security fix or hardening |
| `type: performance` | Speed / resource optimization |
| `type: test` | Tests added or fixed |
| `type: chore` | Tooling, CI, dependencies |

### Priority labels
| Label | SLA |
|-------|-----|
| `priority: critical` | Fix within 24h — blocks release |
| `priority: high` | Fix this sprint |
| `priority: medium` | Standard backlog |
| `priority: low` | Nice-to-have |

### Status workflow
```
triage → confirmed → in-progress → needs-review → ready-to-merge → merged
                                                                  ↓
                                                     wontfix / duplicate / invalid
```

### Component labels
`component: debloat` · `component: theme` · `component: transparency`
`component: branding` · `component: developer-env` · `component: registry`
`component: scripts` · `component: playbook` · `component: security` · `component: ci-cd`

### Platform labels
`platform: windows-10` · `platform: windows-11` · `platform: both`

### Size labels (for effort estimation)
| Label | Effort |
|-------|--------|
| `size: XS` | < 1 hour |
| `size: S` | 1–4 hours |
| `size: M` | 1–2 days |
| `size: L` | 3–5 days |
| `size: XL` | 1+ weeks |

### Special labels
`good first issue` · `help wanted` · `breaking change` · `regression`
`needs: repro` · `needs: info`

---

## Milestones

| Milestone | Target | Focus |
|-----------|--------|-------|
| `v0.1.0 — Alpha` | Aug 2025 | Core playbook, scripts, assets |
| `v0.2.0 — Beta` | Sep 2025 | Full features + CI/CD |
| `v0.3.0 — RC` | Oct 2025 | Bug fixes + Win10/11 validation |
| `v1.0.0 — Stable` | Nov 2025 | First public stable release |
| `v1.1.0 — Post-Launch` | Dec 2025 | Community polish |
| `v2.0.0 — Major Upgrade` | Jun 2026 | GUI configurator + plugin system |

---

## Project Board Setup

The **ArizenOS Development Board** uses 6 columns with the following automation:

### Columns
```
Backlog → Ready → In Progress → Review → Validation → Done
```

| Column | Trigger In | Trigger Out |
|--------|-----------|-------------|
| **Backlog** | Issue opened | Label: `status: confirmed` |
| **Ready** | Label: `status: confirmed` | PR opened |
| **In Progress** | PR linked to issue | PR ready for review |
| **Review** | PR review requested | PR merged |
| **Validation** | PR merged | Issue closed |
| **Done** | Issue closed | — |

### Create the board
Go to: **https://github.com/Alrizz-art/ArizenOS/projects**
→ New Project → Board template → Name: `ArizenOS Development Board`

Then add these custom fields:
- **Priority** (Single select): Critical · High · Medium · Low
- **Phase** (Single select): Phase 0 · Phase 1 · Phase 2 · Phase 3 · Phase 4 · Phase 5 · Phase 6
- **Platform** (Single select): Windows 10 · Windows 11 · Both

> **Note:** GitHub Projects require the `project` OAuth scope.
> If creating via API, add `project` scope to your token at https://github.com/settings/tokens

---

## Commit Convention (Conventional Commits)

```
<type>(<scope>): <short description>

[optional body]

[optional footer: closes #N]
```

**Types:** `feat` · `fix` · `docs` · `style` · `refactor` · `perf` · `test` · `chore` · `ci` · `build`

**Scopes:** `debloat` · `theme` · `transparency` · `branding` · `wallpaper` · `devenv` · `registry` · `playbook` · `security` · `ci` · `release`

**Examples:**
```
feat(devenv): add Starship prompt to PS7 profile
fix(debloat): skip Xbox apps on Win10 where not present
docs(versioning): add branch strategy diagram
chore(ci): add .apbx artifact upload to release workflow
perf(registry): consolidate DWM keys into single import
```

**Breaking changes:**
```
feat(playbook)!: rename debloatLevel to DebloatLevel

BREAKING CHANGE: The key 'debloatLevel' renamed to 'DebloatLevel' to match
AME Wizard convention. Update any forks using the old key.
```

---

## Pull Request Workflow

1. Branch from `dev`: `git checkout -b feature/your-feature`
2. Fill the PR template (testing steps, changelog entry, platform tested)
3. Assign labels: type + component + platform + size
4. Link to milestone and issue
5. At least 1 maintainer approval required
6. Squash merge into `dev`

### PR Checklist
```
- [ ] CHANGELOG.md updated under [Unreleased]
- [ ] Tested on clean Windows install (specify build)
- [ ] No hardcoded paths or credentials
- [ ] Entry YAMLs valid (if modified)
- [ ] scripts/security-audit.ps1 passes (0 FAIL)
```

---

## Discussion Categories

| Category | For |
|----------|-----|
| 📣 Announcements | Release notes, project news (maintainers only) |
| 💬 General | General discussion |
| 🙋 Q&A | Help and support |
| 💡 Ideas | Feature brainstorming |
| 🗳️ RFC | Formal proposals for major changes (2-week comment period) |
| 🎉 Show and Tell | Share your ArizenOS setup / screenshots |
