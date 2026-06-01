# @arizen/config

> Shared build configuration for the ArizenOS monorepo.

Contains the base configs for TypeScript, ESLint, Vitest, and Prettier. All packages and apps extend these — never rewrite them.

## Exports

| File | Usage |
|---|---|
| `tsconfig.base.json` | Base TS config — strict, ESM, path aliases |
| `eslint.config.base.js` | Base ESLint config — TS, React, a11y rules |
| `vitest.config.base.ts` | Base Vitest config — coverage thresholds, reporters |
| `prettier.config.js` | Prettier config — shared formatting rules |

## Extending in a Package

```json
// packages/glass/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

## Rules

- No application code lives here
- Config changes require TC review (they affect every package)
- Vitest coverage thresholds are a floor, not a target
