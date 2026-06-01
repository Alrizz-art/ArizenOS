# ArizenOS Logo Assets

## Usage Rules

- Always maintain minimum 16px clear space on all sides
- Minimum display size: 32×32px (icon only), 120px wide (full logo)
- Never distort, rotate, or recolor without Design Review approval
- Use `arizen-logo-dark.png` on light backgrounds
- Use `arizen-logo-light.png` on dark/glass backgrounds
- Use `arizen-logo-mono.svg` for single-color contexts

## Structure

| Directory | Contents |
|---|---|
| `primary/` | Full logo (icon + wordmark) — all variants |
| `icon/` | Standalone icon mark — no wordmark |
| `wordmark/` | Text-only wordmark — no icon |
| `exports/png/` | PNG exports at 7 sizes (16–1024px) |
| `exports/ico/` | Windows .ico (multi-size: 16/32/48/256) |
| `exports/webp/` | WebP for web use |

## File Naming Convention

`{product}-{variant}-{modifier}.{ext}`

Examples: `arizen-logo-dark.svg`, `arizen-icon-256.png`, `launcher-icon.svg`
