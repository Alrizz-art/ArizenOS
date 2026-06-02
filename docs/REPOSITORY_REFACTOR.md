# ArizenOS — Repository Refactor Implementation Plan

> **Status:** Ready to execute  
> **Author:** Release Engineering Team  
> **Based On:** Architecture decisions from branding architecture (commit `ed03083`),
> playbook architecture (commit `bac5c48`), and release engineering documentation
> (commit `e89c784`)  
> **Constraint:** Preserve full git history. Preserve all working code.
> Use `git mv` wherever possible. Do not break AME Wizard paths.
> Do not rewrite existing script logic.

---

## 0. Pre-Conditions

Before executing any step, confirm these invariants.

```
git status                     # must be clean — no uncommitted changes
git log --oneline -3           # confirm you are on main at e89c784 or later
git remote -v                  # confirm origin = Alrizz-art/ArizenOS
```

**Protected paths — never moved, never renamed:**

| Path | Why |
|------|-----|
| `playbook.yaml` | AME Wizard reads from repo root — cannot move |
| `entries.yaml` | Included by `playbook.yaml` via `!include entries.yaml` |
| `entries/*.yaml` | AME entry paths hard-referenced as `path: entries/{name}.yaml` |
| `scripts/*.ps1` | Referenced by entry YAMLs as `scripts/{name}.ps1` |
| `registry/*.reg` | Referenced by entry YAMLs as `registry/{name}.reg` |
| `assets/logos/arizenOS_logo_oem.bmp` | Referenced in `playbook.yaml` config options |
| `assets/logos/arizenOS_w10.png` | Referenced in `playbook.yaml` config options |
| `assets/logos/arizenOS_w11.png` | Referenced in `playbook.yaml` config options |
| `assets/wallpapers/*.jpg` | Referenced by `scripts/wallpaper.ps1` |

If any of the above are moved, AME Wizard will fail to load the playbook. Do not move them.

---

## Current Repository State (Verified at Commit e89c784)

```
ArizenOS/
│
├── playbook.yaml                   ← AME root manifest v2.0.0 — STAYS AT ROOT
├── entries.yaml                    ← AME entry index v2.0.0 — STAYS AT ROOT
│
├── entries/                        ← AME entry YAMLs — STAYS AT ROOT
│   ├── restore-point.yaml
│   ├── oem-branding.yaml
│   ├── dark-theme.yaml
│   ├── transparency.yaml
│   ├── debloat.yaml
│   ├── wallpaper.yaml
│   ├── developer-setup.yaml
│   └── final-cleanup.yaml
│
├── scripts/                        ← PS1 scripts — STAYS
│   ├── apply-theme.ps1
│   ├── build-apbx.ps1
│   ├── bump-version.ps1
│   ├── debloat.ps1
│   ├── developer-setup.ps1
│   ├── oem-branding.ps1
│   ├── rollback.ps1
│   ├── security-audit.ps1
│   ├── wallpaper.ps1
│   ├── build/                      ← EMPTY (.gitkeep only)
│   └── ci/                         ← EMPTY (.gitkeep only)
│
├── registry/                       ← Flat .reg files — STAYS
│   ├── dark-theme.reg
│   ├── oem-branding.reg
│   ├── performance.reg
│   └── transparency.reg
│
├── assets/                         ← Binary assets — STAYS
│   ├── logos/
│   │   ├── arizenOS_logo_oem.bmp
│   │   ├── arizenOS_logo_dark.png
│   │   ├── arizenOS_logo_white.png
│   │   └── README.md
│   └── wallpapers/
│       ├── arizenOS_dark.jpg
│       ├── arizenOS_default.jpg
│       ├── arizenOS_lockscreen.jpg
│       └── README.md
│
├── releases/                       ← ROOT-LEVEL: MIGRATE into playbook/releases/
│   ├── manifests/
│   │   └── latest.json             ← Conflicts with playbook/releases/manifests/latest.json
│   └── README.md                   ← Superseded by playbook/releases/README.md
│
├── branding/                       ← Architecture complete (ed03083) — UNCHANGED
├── playbook/                       ← Architecture complete (bac5c48) — source layers EMPTY
│   ├── manifests/entries/          ← EMPTY: needs population from entries/
│   ├── registry/{feature}/         ← EMPTY: needs population from registry/
│   └── assets/                     ← EMPTY: needs population from assets/
│
├── docs/
│   ├── release/                    ← Release engineering complete (e89c784)
│   ├── architecture/               ← Existing ADRs and overview
│   ├── playbooks/                  ← Existing operational playbooks
│   ├── VERSIONING.md               ← CONFLICT: duplicates docs/release/SEMANTIC_VERSIONING.md
│   └── RELEASE_SCHEDULE.md         ← CONFLICT: duplicates docs/release/STABLE_RELEASES.md
│
├── ARCHITECTURE.md                 ← Root: needs update to navigation document
├── VERSIONING.md                   ← Root: needs update to navigation document
├── RELEASE.md                      ← Root: needs update → docs/release/
├── RELEASE_SCHEDULE.md             ← Root: MIGRATE content → docs/release/
├── BRAND_GUIDELINES.md             ← Root: MIGRATE → branding/BRAND_GUIDELINES.md
│
├── .github/workflows/
│   ├── ci.yml, release.yml,        ← Exist — verify against CICD_WORKFLOW.md spec
│   ├── nightly.yml, security.yml
│   ├── labeler.yml
│   └── stale.yml                   ← RENAME → branch-hygiene.yml per CICD_WORKFLOW.md
│
└── kernel/, apps/, arch/,          ← OS-layer code — DO NOT TOUCH
    drivers/, fs/, lib/,
    packages/, tools/, userspace/
```

---

## Target Repository State (Post-Refactor)

```
ArizenOS/
│
├── playbook.yaml                   ← UNCHANGED
├── entries.yaml                    ← UNCHANGED
├── entries/                        ← UNCHANGED (8 AME entry files)
├── scripts/                        ← UNCHANGED (9 PS1 files + subdirs)
├── registry/                       ← UNCHANGED (4 .reg files)
├── assets/                         ← UNCHANGED (logos/ + wallpapers/)
│
├── playbook/manifests/entries/     ← POPULATED: mirrors of entries/*.yaml
├── playbook/registry/{feature}/    ← POPULATED: mirrors of registry/*.reg
├── playbook/assets/oem/            ← POPULATED: OEM BMP from assets/logos/
├── playbook/assets/wallpapers/     ← POPULATED: wallpapers from assets/wallpapers/
│
├── releases/                       ← REMOVED: content merged into playbook/releases/
│
├── BRAND_GUIDELINES.md             ← BECOMES: forwarding stub (content → branding/)
├── RELEASE_SCHEDULE.md             ← BECOMES: forwarding stub (content → docs/release/)
├── ARCHITECTURE.md                 ← BECOMES: multi-system navigation document
├── VERSIONING.md                   ← BECOMES: navigation document → docs/release/
├── RELEASE.md                      ← BECOMES: navigation document → docs/release/
│
├── branding/BRAND_GUIDELINES.md    ← NEW: moved from root
│
├── docs/VERSIONING.md              ← BECOMES: redirect stub
├── docs/RELEASE_SCHEDULE.md        ← BECOMES: redirect stub
├── docs/release/VERSIONING_LEGACY.md      ← NEW: original docs/VERSIONING.md preserved
├── docs/release/RELEASE_SCHEDULE_LEGACY.md ← NEW: original docs/RELEASE_SCHEDULE.md
├── docs/release/RELEASE_SCHEDULE_HISTORY.md ← NEW: original root RELEASE_SCHEDULE.md
│
├── scripts/README.md               ← NEW: maps scripts to entries and purposes
│
├── .github/workflows/branch-hygiene.yml ← RENAMED from stale.yml
│
└── [kernel, apps, arch, ...]       ← UNTOUCHED in every phase
```

---

## Phase 1 — Releases Directory Consolidation

**Problem:** `releases/` at root is superseded by `playbook/releases/` (bac5c48).
The root `releases/manifests/latest.json` conflicts with `playbook/releases/manifests/latest.json`.

**Risk:** Low — no scripts, entry YAMLs, or AME manifests reference `releases/`.

### Pre-flight verification

```
grep -r "releases/" entries/ scripts/ registry/ playbook.yaml entries.yaml
```

Expected result: zero matches. If any matches are found, resolve those references before proceeding.

### Step 1.1 — Reconcile latest.json

Both files claim to be the version pointer. Verify content:

```
cat releases/manifests/latest.json
cat playbook/releases/manifests/latest.json
```

The `playbook/releases/manifests/latest.json` file (established in bac5c48) is authoritative.
If `releases/manifests/latest.json` contains a higher version number or additional
fields not present in the `playbook/` version, manually merge those fields into
`playbook/releases/manifests/latest.json` before the next step.

### Step 1.2 — Remove the root releases/ directory

```
git rm -r releases/
```

Files being removed and their disposition:

| File | Disposition |
|------|------------|
| `releases/manifests/latest.json` | Content verified in `playbook/releases/manifests/latest.json` |
| `releases/README.md` | Superseded by `playbook/releases/README.md` (bac5c48) |

**Commit message:**
```
chore(releases): remove root releases/ — consolidated into playbook/releases/

releases/manifests/latest.json content merged into playbook/releases/manifests/latest.json.
releases/README.md superseded by playbook/releases/README.md (bac5c48).

No AME Wizard paths affected.
No script references to releases/ exist (verified via grep).
```

---

## Phase 2 — Root Documentation Migrations

**Problem:** Several root-level files are superseded by architecture subdirectories.
None of these files are referenced by code paths — risk is zero.

### Step 2.1 — Move BRAND_GUIDELINES.md into branding/

`branding/` (est. ed03083) is now the authoritative home for all brand documentation.
Root `BRAND_GUIDELINES.md` belongs inside `branding/`.

```
git mv BRAND_GUIDELINES.md branding/BRAND_GUIDELINES.md
```

After the `git mv`, create a **new** forwarding stub at the original root path.
This stub keeps external links working (GitHub renders root markdown files):

File to create: `BRAND_GUIDELINES.md` (root, new file replacing the moved one)

```markdown
# Brand Guidelines

> This document has moved.
>
> The complete ArizenOS brand guidelines are in [`branding/`](branding/).
>
> | Document | Contents |
> |----------|---------|
> | [`branding/README.md`](branding/README.md) | System overview |
> | [`branding/NAMING_CONVENTIONS.md`](branding/NAMING_CONVENTIONS.md) | File naming rules |
> | [`branding/CONTRIBUTOR_GUIDE.md`](branding/CONTRIBUTOR_GUIDE.md) | How to contribute |
> | [`branding/MIGRATION.md`](branding/MIGRATION.md) | Asset migration guide |
> | [`branding/VERSIONING.md`](branding/VERSIONING.md) | Asset versioning |
> | [`branding/BRAND_GUIDELINES.md`](branding/BRAND_GUIDELINES.md) | Full guidelines |
```

```
git add BRAND_GUIDELINES.md branding/BRAND_GUIDELINES.md
```

**Commit message:**
```
docs(branding): move BRAND_GUIDELINES.md into branding/

branding/ is the authoritative home for brand documentation (est. ed03083).
Root BRAND_GUIDELINES.md becomes a forwarding stub to maintain external links.
Full content preserved at branding/BRAND_GUIDELINES.md with git history intact.
```

### Step 2.2 — Move RELEASE_SCHEDULE.md into docs/release/

Root `RELEASE_SCHEDULE.md` is superseded by `docs/release/STABLE_RELEASES.md` (e89c784)
which defines release cadence in full. Preserve the original content as historical reference.

```
git mv RELEASE_SCHEDULE.md docs/release/RELEASE_SCHEDULE_HISTORY.md
```

Create a forwarding stub at the original root path:

File to create: `RELEASE_SCHEDULE.md` (root, new file)

```markdown
# Release Schedule

> This document has moved.
>
> Release scheduling and cadence are documented in [`docs/release/`](docs/release/).
>
> | Document | Contents |
> |----------|---------|
> | [`docs/release/STABLE_RELEASES.md`](docs/release/STABLE_RELEASES.md) | Stable release cadence |
> | [`docs/release/NIGHTLY_RELEASES.md`](docs/release/NIGHTLY_RELEASES.md) | Nightly build schedule |
> | [`docs/release/README.md`](docs/release/README.md) | Release engineering index |
>
> Historical schedule reference: [`docs/release/RELEASE_SCHEDULE_HISTORY.md`](docs/release/RELEASE_SCHEDULE_HISTORY.md)
```

```
git add RELEASE_SCHEDULE.md docs/release/RELEASE_SCHEDULE_HISTORY.md
```

**Commit message:**
```
docs(release): move root RELEASE_SCHEDULE.md into docs/release/

docs/release/STABLE_RELEASES.md (e89c784) is the authoritative cadence document.
Root RELEASE_SCHEDULE.md becomes a forwarding stub.
Original content preserved at docs/release/RELEASE_SCHEDULE_HISTORY.md.
```

### Step 2.3 — Resolve docs/VERSIONING.md conflict

`docs/VERSIONING.md` conflicts with `docs/release/SEMANTIC_VERSIONING.md` (e89c784).
The new document is authoritative and supersedes the old one.

```
git mv docs/VERSIONING.md docs/release/VERSIONING_LEGACY.md
```

Create redirect stub at the original path:

File to create: `docs/VERSIONING.md` (new file)

```markdown
# Versioning

> This document has moved.
>
> The authoritative versioning strategy is in [`docs/release/`](release/).
>
> | Document | Contents |
> |----------|---------|
> | [`docs/release/SEMANTIC_VERSIONING.md`](release/SEMANTIC_VERSIONING.md) | Full SemVer strategy — **authoritative** |
> | [`playbook/VERSIONING_STRATEGY.md`](../playbook/VERSIONING_STRATEGY.md) | Playbook-specific versioning |
> | [`branding/VERSIONING.md`](../branding/VERSIONING.md) | Brand asset versioning |
>
> Original content preserved at [`docs/release/VERSIONING_LEGACY.md`](release/VERSIONING_LEGACY.md).
```

```
git add docs/VERSIONING.md docs/release/VERSIONING_LEGACY.md
```

**Commit message:**
```
docs(versioning): resolve docs/VERSIONING.md conflict with docs/release/

docs/release/SEMANTIC_VERSIONING.md (e89c784) is authoritative.
docs/VERSIONING.md becomes a redirect stub.
Original content preserved as docs/release/VERSIONING_LEGACY.md.
```

### Step 2.4 — Resolve docs/RELEASE_SCHEDULE.md conflict

`docs/RELEASE_SCHEDULE.md` conflicts with `docs/release/STABLE_RELEASES.md` (e89c784).

```
git mv docs/RELEASE_SCHEDULE.md docs/release/RELEASE_SCHEDULE_LEGACY.md
```

Create redirect stub:

File to create: `docs/RELEASE_SCHEDULE.md` (new file)

```markdown
# Release Schedule

> This document has moved.
>
> See [`docs/release/STABLE_RELEASES.md`](release/STABLE_RELEASES.md) for the
> current release cadence policy.
>
> Original content preserved at [`docs/release/RELEASE_SCHEDULE_LEGACY.md`](release/RELEASE_SCHEDULE_LEGACY.md).
```

```
git add docs/RELEASE_SCHEDULE.md docs/release/RELEASE_SCHEDULE_LEGACY.md
```

**Commit message:**
```
docs(release): resolve docs/RELEASE_SCHEDULE.md conflict

docs/release/STABLE_RELEASES.md (e89c784) is authoritative.
docs/RELEASE_SCHEDULE.md becomes a redirect stub.
Original content preserved as docs/release/RELEASE_SCHEDULE_LEGACY.md.
```

---

## Phase 3 — Root Navigation Document Updates

**Problem:** `ARCHITECTURE.md`, `VERSIONING.md`, and `RELEASE.md` at root are
stale and do not reference the architecture subdirectories. These files stay
at root — they are expected there by GitHub and by users. Their content is
updated in-place (no moves).

### Step 3.1 — Update root ARCHITECTURE.md

Replace the body with a multi-system navigation document:

```markdown
# ArizenOS Architecture

ArizenOS is a multi-layer system. Each layer maintains its own
architecture documentation. Start with the index for your layer:

| Layer | Document | Description |
|-------|----------|-------------|
| **AME Playbook** | [`playbook/ARCHITECTURE.md`](playbook/ARCHITECTURE.md) | `.apbx` package spec, entry execution order, safety model |
| **Branding System** | [`branding/ARCHITECTURE.md`](branding/ARCHITECTURE.md) | Design token system, asset pipeline, export hierarchy |
| **OS System** | [`docs/architecture/overview.md`](docs/architecture/overview.md) | Kernel, userspace, driver, and filesystem architecture |
| **Release Engineering** | [`docs/release/README.md`](docs/release/README.md) | Versioning, branching, CI/CD, security |
| **API Surface** | [`docs/api/`](docs/api/) | Public API reference |

## Architecture Decision Records

Significant architectural decisions are recorded as ADRs in [`docs/architecture/`](docs/architecture/):

- [ADR-0001: Monorepo Structure](docs/architecture/ADR-0001-monorepo.md)
- [ADR-0002: Glass Rendering](docs/architecture/ADR-0002-glass-rendering.md)
- [ADR-0003: Local AI](docs/architecture/ADR-0003-local-ai.md)

## Dependency Graph

[`docs/architecture/dependency-graph.md`](docs/architecture/dependency-graph.md)
```

```
git add ARCHITECTURE.md
```

**Commit message:**
```
docs(architecture): update root ARCHITECTURE.md as multi-system navigation index

Maps all architecture layers to their authoritative documentation:
- playbook/ARCHITECTURE.md (bac5c48)
- branding/ARCHITECTURE.md (ed03083)
- docs/architecture/ (existing ADRs)
- docs/release/README.md (e89c784)
```

### Step 3.2 — Update root VERSIONING.md

Replace the body with a navigation document:

```markdown
# ArizenOS Versioning

ArizenOS uses Semantic Versioning 2.0.0 across all components.
Each component maintains its own versioning specification:

| Component | Document |
|-----------|---------|
| **Playbook releases** (`.apbx`) | [`docs/release/SEMANTIC_VERSIONING.md`](docs/release/SEMANTIC_VERSIONING.md) — **authoritative** |
| **Playbook internal** | [`playbook/VERSIONING_STRATEGY.md`](playbook/VERSIONING_STRATEGY.md) |
| **Brand assets** | [`branding/VERSIONING.md`](branding/VERSIONING.md) |
| **Changelog standards** | [`docs/release/CHANGELOG_PROCESS.md`](docs/release/CHANGELOG_PROCESS.md) |

## Format at a Glance

```
MAJOR — Breaking: AME schema change, Windows target dropped
MINOR — Feature: new entry, new config option, new script
PATCH — Fix: registry correction, script bug, asset correction

Pre-release:  alpha.N → beta.N → rc.N → (stable)
```

Full specification: [`docs/release/SEMANTIC_VERSIONING.md`](docs/release/SEMANTIC_VERSIONING.md)
```

```
git add VERSIONING.md
```

**Commit message:**
```
docs(versioning): update root VERSIONING.md as navigation document

Full specification in docs/release/SEMANTIC_VERSIONING.md (e89c784).
Root file provides format summary and routes to authoritative sources.
```

### Step 3.3 — Update root RELEASE.md

Replace the body with a navigation document:

```markdown
# ArizenOS Release Process

The complete release engineering documentation is in [`docs/release/`](docs/release/).

## Document Index

| Document | Purpose |
|----------|---------|
| [`docs/release/README.md`](docs/release/README.md) | Master index — start here |
| [`docs/release/STABLE_RELEASES.md`](docs/release/STABLE_RELEASES.md) | How stable releases are prepared and shipped |
| [`docs/release/NIGHTLY_RELEASES.md`](docs/release/NIGHTLY_RELEASES.md) | Automated nightly build process |
| [`docs/release/GITHUB_RELEASES.md`](docs/release/GITHUB_RELEASES.md) | GitHub Release page specification |
| [`docs/release/CHANGELOG_PROCESS.md`](docs/release/CHANGELOG_PROCESS.md) | How the changelog is maintained |
| [`docs/release/SECURITY_PATCH_PROCESS.md`](docs/release/SECURITY_PATCH_PROCESS.md) | Vulnerability response and disclosure |
| [`docs/release/BRANCH_STRATEGY.md`](docs/release/BRANCH_STRATEGY.md) | Branching model |
| [`docs/release/CONTRIBUTOR_WORKFLOW.md`](docs/release/CONTRIBUTOR_WORKFLOW.md) | PR process and review |
| [`docs/release/CICD_WORKFLOW.md`](docs/release/CICD_WORKFLOW.md) | CI/CD pipeline |

## Latest Stable Release

[GitHub Releases](https://github.com/Alrizz-art/ArizenOS/releases/latest) —
download `ArizenOS.apbx`
```

```
git add RELEASE.md
```

**Commit message:**
```
docs(release): update root RELEASE.md as navigation document

All release engineering detail in docs/release/ (e89c784).
Root RELEASE.md is now a quick-navigation index.
```

---

## Phase 4 — Populate playbook/manifests/entries/ (Source Layer)

**Problem:** `playbook/manifests/entries/` contains only `.gitkeep`.
Per `playbook/manifests/README.md` (bac5c48), this is the source and
specification layer for all entry YAMLs.

**Critical constraint:** Do NOT use `git mv`. The originals at `entries/`
must remain at their current paths — AME Wizard reads from `entries/`
as specified in `entries.yaml`. These are copies, not moves.

```
cp entries/restore-point.yaml    playbook/manifests/entries/restore-point.yaml
cp entries/oem-branding.yaml     playbook/manifests/entries/oem-branding.yaml
cp entries/dark-theme.yaml       playbook/manifests/entries/dark-theme.yaml
cp entries/transparency.yaml     playbook/manifests/entries/transparency.yaml
cp entries/debloat.yaml          playbook/manifests/entries/debloat.yaml
cp entries/wallpaper.yaml        playbook/manifests/entries/wallpaper.yaml
cp entries/developer-setup.yaml  playbook/manifests/entries/developer-setup.yaml
cp entries/final-cleanup.yaml    playbook/manifests/entries/final-cleanup.yaml

git add playbook/manifests/entries/
```

**Verification before committing:**

```
diff entries/restore-point.yaml playbook/manifests/entries/restore-point.yaml
```

Expected: zero diff (exact copy).

**Commit message:**
```
feat(playbook): populate playbook/manifests/entries/ source layer

Copies current entries/*.yaml into playbook/manifests/entries/ per
the source/spec architecture established in bac5c48.

Relationship after this commit:
  entries/*.yaml                    AME Wizard reads from here (unchanged)
  playbook/manifests/entries/*.yaml Source layer — canonical spec and design home

The two directories are kept in sync manually (or via build script).
entries/ is always the AME runtime truth; playbook/manifests/entries/
is the human-maintained specification layer.

Files added: 8 (restore-point, oem-branding, dark-theme, transparency,
             debloat, wallpaper, developer-setup, final-cleanup)
```

---

## Phase 5 — Populate playbook/registry/ Source Layer

**Problem:** `playbook/registry/` subdirectories exist but are empty.
Per `playbook/registry/README.md` (bac5c48), they should contain
feature-scoped copies of the flat registry files at `registry/`.

**Critical constraint:** Do NOT use `git mv`. The originals at `registry/`
must remain — AME entry YAMLs reference `registry/{name}.reg`.

```
cp registry/dark-theme.reg    playbook/registry/dark-theme/dark-theme.reg
cp registry/transparency.reg  playbook/registry/transparency/transparency.reg
cp registry/oem-branding.reg  playbook/registry/oem/oem-branding.reg
cp registry/performance.reg   playbook/registry/performance/performance.reg

git add playbook/registry/
```

**Known gap — playbook/registry/debloat/:**

`playbook/registry/debloat/` exists but has no corresponding `registry/debloat.reg`
at root. The debloat telemetry policies are currently applied via
`scripts/debloat.ps1` rather than a standalone .reg file. This gap is
tracked — creating `registry/telemetry-policies.reg` and a corresponding
`playbook/registry/debloat/telemetry-policies.reg` is a separate future commit,
not part of this structural refactor.

**Commit message:**
```
feat(playbook): populate playbook/registry/ feature-scoped source layer

Copies registry/*.reg into playbook/registry/{feature}/ per
the source architecture in bac5c48.

Relationship after this commit:
  registry/*.reg                      AME reads from here (unchanged)
  playbook/registry/{feature}/*.reg   Feature-organized source layer

Known gap: playbook/registry/debloat/ remains empty. The debloat
telemetry policies are script-applied, not .reg-applied. A future
commit will create registry/telemetry-policies.reg to close this gap.

Files added: 4 (dark-theme, transparency, oem-branding, performance)
```

---

## Phase 6 — Populate playbook/assets/ Staging Layer

**Problem:** `playbook/assets/` subdirectories are empty.
Per `playbook/assets/README.md` (bac5c48), they hold production-ready
copies of assets for `.apbx` validation and packaging.

**Critical constraint:** Do NOT use `git mv`. The originals at `assets/`
must remain — `playbook.yaml` configuration options reference `assets/logos/`.

```
cp assets/logos/arizenOS_logo_oem.bmp       playbook/assets/oem/arizenOS_logo_oem.bmp
cp assets/wallpapers/arizenOS_default.jpg   playbook/assets/wallpapers/arizenOS_default.jpg
cp assets/wallpapers/arizenOS_dark.jpg      playbook/assets/wallpapers/arizenOS_dark.jpg
cp assets/wallpapers/arizenOS_lockscreen.jpg playbook/assets/wallpapers/arizenOS_lockscreen.jpg

git add playbook/assets/
```

**Known gap — arizenOS_logo_sm.bmp:**

`playbook/assets/README.md` specifies a small OEM logo at 96×96px
(`arizenOS_logo_sm.bmp`) for the About panel. This file does not yet exist
in `assets/logos/`. This is a known gap — it will be created in the branding
production phase (tracked in `branding/oem/ARCHITECTURE.md`).
This structural refactor does not create it.

**Commit message:**
```
feat(playbook): populate playbook/assets/ packaging staging layer

Copies production-ready assets from assets/ into playbook/assets/
per the packaging architecture in bac5c48.

Root assets/ is unchanged (referenced by playbook.yaml config options).
playbook/assets/ is the validation and .apbx packaging staging layer.

Files added:
  playbook/assets/oem/arizenOS_logo_oem.bmp       (from assets/logos/)
  playbook/assets/wallpapers/arizenOS_default.jpg  (from assets/wallpapers/)
  playbook/assets/wallpapers/arizenOS_dark.jpg     (from assets/wallpapers/)
  playbook/assets/wallpapers/arizenOS_lockscreen.jpg (from assets/wallpapers/)

Known gap: arizenOS_logo_sm.bmp (96x96) not yet in assets/logos/ — tracked.
```

---

## Phase 7 — scripts/ Documentation

**Problem:** No `scripts/README.md` exists. The distinction between
AME-entry scripts and build/maintenance scripts is undocumented in the
`scripts/` directory itself.

**Action:** Create `scripts/README.md`. No file movements.

File to create: `scripts/README.md`

```markdown
# scripts/

PowerShell scripts for ArizenOS.

## AME Wizard Entry Scripts

These scripts are called directly by entry YAMLs during playbook execution.
They must remain at their current paths — moving them breaks AME Wizard.

| Script | Called By | Phase |
|--------|-----------|-------|
| `oem-branding.ps1` | `entries/oem-branding.yaml` | Phase 1 |
| `apply-theme.ps1` | `entries/dark-theme.yaml` | Phase 2a |
| `debloat.ps1` | `entries/debloat.yaml` | Phase 3 |
| `wallpaper.ps1` | `entries/wallpaper.yaml` | Phase 4 |
| `developer-setup.ps1` | `entries/developer-setup.yaml` | Phase 5 |
| `rollback.ps1` | `entries/restore-point.yaml` (rollback hook) | Phase 0 |

## Build and Maintenance Scripts

These scripts are run by developers and CI — not by AME Wizard.

| Script | Purpose |
|--------|---------|
| `build-apbx.ps1` | Package repo into ArizenOS.apbx for distribution |
| `bump-version.ps1` | Bump version in playbook.yaml and manifests |
| `security-audit.ps1` | Run post-install security posture audit |

## Reserved Subdirectories

| Directory | Reserved For |
|-----------|-------------|
| `build/` | Future: build automation helpers (currently empty) |
| `ci/` | Future: CI-local helper scripts (currently empty) |

## Architecture Reference

See `playbook/scripts/README.md` for the organized source layer that
documents each script's design, parameters, and rollback procedures.
```

```
git add scripts/README.md
```

**Commit message:**
```
docs(scripts): add scripts/README.md — maps scripts to entries and purposes

Distinguishes AME entry scripts (path-sensitive, cannot move) from
build/maintenance scripts. Documents reserved build/ and ci/ subdirs.
References playbook/scripts/README.md for the detailed source layer.
```

---

## Phase 8 — Workflow Rename

**Problem:** `.github/workflows/stale.yml` performs the branch hygiene
function. `docs/release/CICD_WORKFLOW.md` (e89c784) specifies this workflow
as `branch-hygiene.yml`.

**Pre-flight check:**

```
grep -r "stale.yml" .github/
```

If `labeler.yml` or any other workflow file references `stale.yml` by name,
update those references first. Then:

```
git mv .github/workflows/stale.yml .github/workflows/branch-hygiene.yml
git add .github/workflows/branch-hygiene.yml
```

**Commit message:**
```
ci: rename stale.yml to branch-hygiene.yml per CICD_WORKFLOW.md

CICD_WORKFLOW.md (e89c784) specifies branch-hygiene.yml as the
workflow responsible for stale branch cleanup.
stale.yml performs this function — rename only, no content changes.
```

---

## Complete git mv Command Reference

All `git mv` operations in execution order. These are the only commands
that move files with history preservation. Everything else is either
`cp` (source-layer population), `git rm` (consolidation), or in-place edits.

```
Phase 2.1:  git mv BRAND_GUIDELINES.md           branding/BRAND_GUIDELINES.md
Phase 2.2:  git mv RELEASE_SCHEDULE.md           docs/release/RELEASE_SCHEDULE_HISTORY.md
Phase 2.3:  git mv docs/VERSIONING.md            docs/release/VERSIONING_LEGACY.md
Phase 2.4:  git mv docs/RELEASE_SCHEDULE.md      docs/release/RELEASE_SCHEDULE_LEGACY.md
Phase 8:    git mv .github/workflows/stale.yml   .github/workflows/branch-hygiene.yml
```

**Total `git mv` operations: 5**

### Non-move operations summary

| Operation | Count | What |
|-----------|-------|------|
| `git rm -r` | 1 | `releases/` directory |
| `cp` (new files in source layers) | 15 | 8 entries + 4 registry + 3 wallpapers |
| `cp` (OEM asset) | 1 | arizenOS_logo_oem.bmp |
| New files (stubs + README) | 7 | Forwarding stubs + scripts/README.md |
| In-place content edits | 3 | ARCHITECTURE.md, VERSIONING.md, RELEASE.md |

---

## Verification Checklist

Run after each phase is committed, and again after all phases.

### Section A — AME Wizard Integrity (CRITICAL — run after every phase)

```
test -f playbook.yaml        && echo "PASS: playbook.yaml"     || echo "FAIL: playbook.yaml MISSING"
test -f entries.yaml         && echo "PASS: entries.yaml"      || echo "FAIL: entries.yaml MISSING"
```

Eight entry files:
```
for f in restore-point oem-branding dark-theme transparency debloat wallpaper developer-setup final-cleanup; do
  test -f "entries/$f.yaml" && echo "PASS: entries/$f.yaml" || echo "FAIL: entries/$f.yaml MISSING"
done
```

Nine PS1 scripts:
```
for f in apply-theme build-apbx bump-version debloat developer-setup oem-branding rollback security-audit wallpaper; do
  test -f "scripts/$f.ps1" && echo "PASS: scripts/$f.ps1" || echo "FAIL: scripts/$f.ps1 MISSING"
done
```

Four .reg files:
```
for f in dark-theme oem-branding performance transparency; do
  test -f "registry/$f.reg" && echo "PASS: registry/$f.reg" || echo "FAIL: registry/$f.reg MISSING"
done
```

Four assets referenced in playbook.yaml:
```
test -f assets/logos/arizenOS_logo_oem.bmp    && echo "PASS: OEM BMP"    || echo "FAIL: OEM BMP MISSING"
test -f assets/logos/arizenOS_w10.png          && echo "PASS: W10 logo"   || echo "FAIL: W10 logo MISSING"
test -f assets/logos/arizenOS_w11.png          && echo "PASS: W11 logo"   || echo "FAIL: W11 logo MISSING"
test -f assets/wallpapers/arizenOS_default.jpg && echo "PASS: wallpaper"  || echo "FAIL: wallpaper MISSING"
```

### Section B — Source Layer Population (run after Phases 4–6)

```
ls playbook/manifests/entries/*.yaml | wc -l          # expect: 8
ls playbook/registry/dark-theme/*.reg | wc -l         # expect: 1
ls playbook/registry/transparency/*.reg | wc -l       # expect: 1
ls playbook/registry/oem/*.reg | wc -l                # expect: 1
ls playbook/registry/performance/*.reg | wc -l        # expect: 1
ls playbook/assets/oem/*.bmp | wc -l                  # expect: 1
ls playbook/assets/wallpapers/*.jpg | wc -l           # expect: 3
```

Verify source layer entries are identical to runtime entries:
```
diff entries/dark-theme.yaml playbook/manifests/entries/dark-theme.yaml
diff entries/debloat.yaml playbook/manifests/entries/debloat.yaml
```

Expected: zero diff.

### Section C — Consolidation Verification (run after Phase 1)

```
test ! -d releases/ && echo "PASS: releases/ removed" || echo "FAIL: releases/ still exists"
test -f playbook/releases/manifests/latest.json && echo "PASS: latest.json in playbook/" || echo "FAIL: latest.json missing"
test -f playbook/releases/README.md             && echo "PASS: README.md in playbook/"   || echo "FAIL: README.md missing"
```

### Section D — Navigation Document Verification (run after Phase 3)

Root files that must exist (as stubs or updated content):
```
for f in ARCHITECTURE.md VERSIONING.md RELEASE.md RELEASE_SCHEDULE.md BRAND_GUIDELINES.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f MISSING"
done
```

Moved files at new locations:
```
test -f branding/BRAND_GUIDELINES.md                   && echo "PASS: branding/BRAND_GUIDELINES.md" || echo "FAIL"
test -f docs/release/RELEASE_SCHEDULE_HISTORY.md       && echo "PASS: RELEASE_SCHEDULE_HISTORY.md"  || echo "FAIL"
test -f docs/release/VERSIONING_LEGACY.md              && echo "PASS: VERSIONING_LEGACY.md"          || echo "FAIL"
test -f docs/release/RELEASE_SCHEDULE_LEGACY.md        && echo "PASS: RELEASE_SCHEDULE_LEGACY.md"   || echo "FAIL"
```

### Section E — git History Verification

Confirm `git mv` preserved history (file history should show both old and new path):
```
git log --follow --oneline branding/BRAND_GUIDELINES.md
git log --follow --oneline docs/release/RELEASE_SCHEDULE_HISTORY.md
git log --follow --oneline .github/workflows/branch-hygiene.yml
```

Each should show at least one commit with a rename indicator (`{old => new}`).

### Section F — No Dangling References

```
grep -r "releases/manifests" entries/ scripts/ playbook.yaml entries.yaml
grep -r "stale\.yml" .github/
```

Both expected: zero results.

---

## Commit Plan

Execute in order. One commit per phase step (some phases have two commits).
Total: 13 commits.

```
Commit 01   chore(releases): remove root releases/ — consolidated into playbook/releases/

Commit 02   docs(branding): move BRAND_GUIDELINES.md into branding/

Commit 03   docs(release): move root RELEASE_SCHEDULE.md into docs/release/

Commit 04   docs(versioning): resolve docs/VERSIONING.md conflict with docs/release/

Commit 05   docs(release): resolve docs/RELEASE_SCHEDULE.md conflict

Commit 06   docs(architecture): update root ARCHITECTURE.md as navigation index

Commit 07   docs(versioning): update root VERSIONING.md as navigation document

Commit 08   docs(release): update root RELEASE.md as navigation document

Commit 09   feat(playbook): populate playbook/manifests/entries/ source layer

Commit 10   feat(playbook): populate playbook/registry/ feature-scoped source layer

Commit 11   feat(playbook): populate playbook/assets/ packaging staging layer

Commit 12   docs(scripts): add scripts/README.md

Commit 13   ci: rename stale.yml to branch-hygiene.yml per CICD_WORKFLOW.md
```

All commit messages follow Conventional Commits format as specified in
`docs/release/CONTRIBUTOR_WORKFLOW.md`. Each commit must leave the repository
in a passing AME-integrity state (Section A of the Verification Checklist).

---

## What This Refactor Does NOT Do

| Out of Scope | Reason |
|-------------|--------|
| Rewrite any `.ps1` script logic | Preserve working code — hard requirement |
| Rewrite any entry `.yaml` content | Preserve working AME configuration |
| Modify `playbook.yaml` or `entries.yaml` | AME-critical — no unnecessary changes |
| Reorganize `kernel/`, `apps/`, `arch/`, etc. | OS-layer code — separate domain, separate refactor |
| Add new playbook features or entries | Structural refactor only — no new functionality |
| Generate `ArizenOS.apbx` | Build step — not part of structural work |
| Update CI workflow logic | Phase 8 is a rename only |
| Compress or rebase git history | History preservation is a hard requirement |
| Merge branches | All work on `main` via PRs |
| Create missing assets (arizenOS_logo_sm.bmp) | Asset production — not structural |
| Create missing registry file (telemetry-policies.reg) | Feature work — separate commit |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| AME Wizard fails to load playbook after a move | Low — protected paths documented | Critical | Run Section A checks after every single commit |
| entry YAML path reference broken | Very Low — entries/ never moved | High | Section A check step 3 |
| Script reference broken | Very Low — scripts/ never moved | High | Section A check step 4 |
| Registry file missing | Very Low — registry/ never moved | High | Section A check step 5 |
| assets/ path in playbook.yaml broken | Very Low — assets/ never moved | High | Section A check step 6 |
| git history lost on rename | Low — using git mv correctly | Medium | Section E: git log --follow verification |
| Forwarding stub omitted | Low — stubs defined per phase | Low | Phase completion checklist |
| stale.yml referenced by another workflow | Low | Medium | grep check before Phase 8 |
| Source layer diverges from runtime (cp gets stale) | Medium — ongoing maintenance concern | Low | Document sync policy in playbook/manifests/README.md |
| releases/ removal breaks an external bookmark | Very Low | Very Low | GitHub and docs/ stubs explain the move |
