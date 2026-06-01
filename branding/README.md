# ArizenOS Branding Assets

> Single source of truth for all ArizenOS visual assets.

## Structure

| Directory | Contents |
|---|---|
| `logos/` | All logo variants — SVG source + PNG exports (1×, 2×, 3×) |
| `fonts/` | Licensed typefaces: Inter, Geist Mono, Instrument Serif (OFL) |
| `icons/` | System icon set (SVG) + per-app icons |
| `tokens/` | Design tokens: source JSON → compiled CSS/JS |
| `wallpapers/` | Default + community wallpaper collection |
| `press/` | Official screenshots, press kit, product descriptions |

## Design Token Pipeline

Tokens flow in one direction — never edit `generated/` by hand:

```
tokens/source/*.json  →  tools/tokens/ (compiler)  →  tokens/generated/
                                                              ↓
                                                    @arizen/skin (runtime)
                                                              ↓
                                                         all apps
```

To recompile tokens after editing source files:

```bash
pnpm --filter @arizen/tools token:compile
```

## Logo Usage

See [`/BRAND_GUIDELINES.md`](../BRAND_GUIDELINES.md) — Logo Rules section for clear space, minimum sizes, color rules, and do/don'ts.

## Contributing Assets

Design contributions (icons, wallpapers, themes) are reviewed by the Design Review Committee. See [`/GOVERNANCE.md`](../GOVERNANCE.md) — Committees section.
