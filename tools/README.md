# ArizenOS Internal Tools

> Internal tooling and scripts for the ArizenOS monorepo. Not distributed to users.

## Tools

| Tool | Command | Purpose |
|---|---|---|
| `scaffold` | `pnpm scaffold:package <name>` | Bootstrap a new package with standard structure |
| `scaffold` | `pnpm scaffold:app <name>` | Bootstrap a new app with standard structure |
| `tokens` | `pnpm token:compile` | Compile design tokens from source JSON to CSS/JS |
| `release` | `pnpm release:prepare <version>` | Bump versions, update manifests, draft changelog |
| `audit` | `pnpm audit:deps` | Check dependency graph for cycles and violations |
| `ci` | (internal) | CI helper scripts — not for local use |

## Scaffold Tool

Running `pnpm scaffold:package glass` generates a complete `packages/glass/` directory with the standard structure: `src/index.ts`, `src/types.ts`, `package.json`, `tsconfig.json`, `vitest.config.ts`, and a stub `README.md`.

This ensures every package starts from the same baseline and CI never fails due to missing config files.

## Token Compiler

Reads `branding/tokens/source/*.json` and outputs:
- `branding/tokens/generated/tokens.css` — CSS custom properties
- `branding/tokens/generated/tokens.js` — ESM JS object
- `branding/tokens/generated/tokens.json` — Raw JSON for tooling

Run after any change to token source files. CI validates that generated files are up-to-date.

## Adding a New Tool

Tools are TypeScript scripts. Add to `tools/src/<tool-name>/index.ts`, register in `tools/package.json` scripts, and document here.
