# ArizenOS Branding Asset Versioning

> **Version:** 1.0.0  
> **Scope:** All versioned assets in `branding/`

---

## 1. Versioning Philosophy

Branding assets follow the **product release version** of ArizenOS — not independent asset versions. This keeps the branding archive coherent with software releases and eliminates "logo-v7-final-FINAL" drift.

**Exception:** Screenshots always carry a version suffix (e.g. `-v1.0`) because they must visually represent a specific product release. Other static assets (SVGs, wallpapers, icons) are the current canonical version — history lives in Git.

---

## 2. Asset Lifecycle States

| State | Meaning | Storage |
|-------|---------|---------|
| `current` | The active, canonical version | Root of each subfolder |
| `deprecated` | Superseded but retained for compatibility | Git history only |
| `archived` | No longer valid — removed from working tree | Git history only |

No `old/`, `v1/`, `legacy/`, or `backup/` subfolders are created inside `branding/`. Git IS the version history.

---

## 3. Version Suffix Rules

### When to include a version suffix in the filename

| Asset Type | Version Suffix | Format |
|-----------|----------------|--------|
| Screenshots | **Required** | `-v{major}.{minor}` |
| Release banners | **Required** | `-v{major}.{minor}` |
| Press kit screenshots | **Required** | `-v{major}.{minor}` |
| Logos (SVG source) | **Never** | Tracked via Git tags |
| Wallpapers | **Never** | Tracked via Git tags |
| Icons | **Never** | Tracked via Git tags |
| OEM assets | **Never** | Tracked via Git tags |

### Version format

```
-v{MAJOR}.{MINOR}
```

- Follows ArizenOS SemVer `MAJOR.MINOR` — patch is omitted (screenshots don't change for patches)
- Examples: `-v0.4`, `-v1.0`, `-v1.2`

---

## 4. Git Tagging for Branding Releases

When a new branding release ships with a product version, the commit is tagged using the pattern:

```
branding/vMAJOR.MINOR.PATCH
```

Example: `branding/v1.0.0` — ships alongside ArizenOS v1.0.0

This allows any branding snapshot to be reconstructed by checking out that tag and targeting the `branding/` directory.

---

## 5. Replacing an Asset

When a logo, wallpaper, icon, or other non-screenshot asset is updated:

1. **Replace in place** — overwrite the existing file at the same path.
2. **Do not rename** — the canonical path does not change across minor updates.
3. **Document the change** in `CHANGELOG.md` under the `[Branding]` section.
4. **Tag the commit** if this is part of a product release.

**Branching:**  
All branding changes are submitted via Pull Request from a `branding/` prefixed branch:

```
branding/update-logo-glass-variant
branding/add-wallpaper-light-4k
branding/v1.0-screenshot-refresh
```

---

## 6. Screenshot Archiving Policy

When a product version ships, its screenshots are:
1. Retained in the repository under their versioned filename
2. New screenshots for the next version are added alongside (not replacing) them
3. Screenshots older than 2 major versions are moved to Git history only (deleted from working tree)

Example progression:
```
arizenos-ss-desktop-dark-v0.4.png    ← archived after v1.2 ships
arizenos-ss-desktop-dark-v1.0.png    ← retained
arizenos-ss-desktop-dark-v1.2.png    ← current
```

---

## 7. CHANGELOG Entry Format

Branding changes in `CHANGELOG.md` use the `[Branding]` section under the relevant version:

```markdown
## [1.0.0] — 2026-MM-DD

### Branding
- Added Liquid Glass logo variant (logos/glass/)
- Refreshed all desktop wallpapers at 4K resolution
- Added light mode wallpapers for all resolutions
- Updated Open Graph image to v1.0 design
```
