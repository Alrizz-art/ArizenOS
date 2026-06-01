# @arizen/design-system

> Single source of truth for all ArizenOS visual decisions.

Defines all design tokens (colors, spacing, typography, motion, shadows) and
provides a transformer pipeline that outputs CSS custom properties, TypeScript
constants, and a Tailwind config extension.

**Not a React package** — exports raw tokens usable by any framework.

## Token Pipeline

```
tokens/source/*.json  →  transformer  →  tokens/generated/
                                              ├── css/        (CSS custom properties)
                                              ├── js/         (TS constants)
                                              └── tailwind/   (Tailwind config)
```

## Depends on

`@arizen/core` (platform detection only)
