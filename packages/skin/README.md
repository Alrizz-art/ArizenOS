# @arizen/skin

> Design token loader, theme engine, and hot-reload system for ArizenOS.

ArizenSkin is the single source of truth for visual configuration across every ArizenOS product. It loads compiled design tokens, applies themes, and pushes updates to all consumers in real time — without a restart.

## What's in Here

| Export | Description |
|---|---|
| `SkinEngine` | Core engine — load, apply, and watch themes |
| `useTheme()` | React hook — current theme tokens |
| `ThemeProvider` | React context provider |
| `TokenResolver` | Resolves token aliases to computed values |
| `HotReload` | File-watch based live theme reload (dev) |
| `ThemeValidator` | Validates a theme manifest against the schema |

## Theme Format

```toml
# arizen-skin/themes/midnight.toml
[meta]
name = "Midnight"
author = "community-handle"
version = "1.0.0"
base = "dark"   # extends the dark base token set

[colors]
accent = "#6C63FF"
surface = "rgba(12, 12, 20, 0.72)"
border = "rgba(255, 255, 255, 0.08)"

[blur]
radius = 32
saturation = 1.4

[typography]
scale = 1.0
```

## Token Flow

```
branding/tokens/source/*.json
    → tools/tokens/ (compiler)
    → branding/tokens/generated/tokens.css
    → @arizen/skin (loader)
    → all apps via ThemeProvider
```

Apps never import raw token JSON. All token access goes through `useTheme()`.
