# Local Development Guide

This guide covers setting up a full ArizenOS development environment for contributors working on core packages or apps.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 20 LTS (exact) | `winget install OpenJS.NodeJS.LTS` |
| pnpm | 8.x | `npm install -g pnpm@8` |
| Git | 2.40+ | `winget install Git.Git` |
| Visual Studio Build Tools | 2022 | See below |
| Python | 3.11+ | `winget install Python.Python.3.11` |

### Install Visual Studio Build Tools 2022

Required for compiling N-API native modules (`@arizen/glass`, `@arizen/mind`, `@arizen/shell`).

```powershell
winget install Microsoft.VisualStudio.2022.BuildTools `
  --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended --quiet"
```

Verify the installation:
```bash
cl.exe --version  # Should show MSVC compiler version
```

### Verify Your Environment

```bash
node --version     # v20.x.x
pnpm --version     # 8.x.x
git --version      # 2.40+
python --version   # 3.11+
```

---

## First-Time Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/ArizenOS.git
cd ArizenOS

# 2. Add the upstream remote
git remote add upstream https://github.com/Alrizz-art/ArizenOS.git

# 3. Install all workspace dependencies
# This will also compile native modules — takes 5–15 minutes on first run
pnpm install

# 4. Build all packages (required before running any app)
pnpm build

# 5. Verify everything works
pnpm lint && pnpm typecheck && pnpm test
```

All three verification commands must pass before you start making changes.

---

## Development Workflow

### Starting Development Mode

```bash
# Start everything in parallel (Turborepo coordinates dependencies)
pnpm dev

# Or start a specific package or app
pnpm --filter @arizen/launcher dev
pnpm --filter @arizen/ui dev          # Component library dev server
pnpm --filter @arizen/mind dev        # AI inference library (runs tests in watch mode)
```

Turborepo ensures that when you run `pnpm dev` for an app, all its dependency packages are built first and then watched for changes.

### Making Changes

1. **Create a branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Edit code.** TypeScript, hot-reload, and Turborepo's incremental builds mean most changes take effect within seconds.

3. **Run checks frequently:**
   ```bash
   pnpm lint             # ESLint
   pnpm typecheck        # TypeScript compiler
   pnpm test             # Vitest unit tests
   pnpm test --watch     # Watch mode
   ```

4. **Run the full suite before committing:**
   ```bash
   pnpm lint && pnpm typecheck && pnpm test
   ```

### Native Module Development

If you are working on `@arizen/glass`, `@arizen/mind`, or `@arizen/shell` (C++ N-API modules):

```bash
# Build only the native module
pnpm --filter @arizen/glass build:native

# Rebuild after C++ changes
pnpm --filter @arizen/glass rebuild

# Run native module tests
pnpm --filter @arizen/glass test:native
```

Native module changes require a full rebuild — they do not hot-reload.

---

## Project-wide Scripts

All scripts are defined in the root `package.json` and orchestrated by Turborepo.

| Script | What It Does |
|---|---|
| `pnpm build` | Build all packages and apps |
| `pnpm dev` | Start all apps and packages in dev mode |
| `pnpm lint` | Run ESLint across all packages |
| `pnpm lint:fix` | Auto-fix ESLint issues |
| `pnpm typecheck` | Run TypeScript type checking |
| `pnpm test` | Run all unit and integration tests |
| `pnpm test:watch` | Run tests in watch mode |
| `pnpm test:e2e` | Run Playwright E2E tests |
| `pnpm test:visual` | Run visual regression tests |
| `pnpm test:a11y` | Run accessibility audit |
| `pnpm clean` | Remove all build artifacts and caches |
| `pnpm changeset` | Create a changeset for versioning |
| `pnpm format` | Run Prettier on all files |

---

## Code Standards

### TypeScript Configuration

All packages extend from `@arizen/config` base configs. Do not add custom `tsconfig.json` settings without discussing in an RFC.

Key strictness settings enforced everywhere:
```json
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "exactOptionalPropertyTypes": true,
  "noImplicitReturns": true
}
```

### No `any`
Use `unknown` and narrow with type guards. If you must use `any`, add a comment explaining why.

### Named Exports Only (in packages)
```typescript
// ✅ Good
export function createEngine() {}
export type EngineConfig = { ... }

// ❌ Bad (in packages)
export default function createEngine() {}
```

Default exports are allowed in apps but not in packages.

### JSDoc Required for Public APIs
```typescript
/**
 * Creates a new GlassEngine instance for the given window.
 *
 * @param config - Engine configuration options
 * @returns A promise that resolves to a fully initialised GlassEngine
 * @throws {GlassNotSupportedError} If the GPU does not support DirectComposition
 *
 * @example
 * ```typescript
 * const engine = await GlassEngine.create({ window, blurRadius: 16 })
 * await engine.mount()
 * ```
 */
export async function createGlassEngine(config: GlassEngineConfig): Promise<GlassEngine> {
```

---

## Adding a Changeset

If your change affects a public-facing package, you must add a changeset before opening a PR:

```bash
pnpm changeset
```

The CLI will ask:
1. Which packages were changed?
2. Is this a `major` (breaking), `minor` (feature), or `patch` (fix) change?
3. Write a summary for the changelog

Commit the generated changeset file (`.changeset/your-changeset.md`) with your PR.

---

## Debugging

### Electron DevTools

For apps, open Chrome DevTools in the renderer:

```typescript
// In the app's main process (dev mode only)
if (process.env.NODE_ENV === 'development') {
  mainWindow.webContents.openDevTools()
}
```

Or use the keyboard shortcut `F12` in any ArizenOS app window during development.

### Native Module Debugging

Use the `--inspect` flag when running the main Electron process and attach a native debugger:

```bash
# In apps/launcher
pnpm dev --inspect
# Then attach MSVC debugger to the electron.exe process
```

### Logs

All packages use `@arizen/core`'s Logger:

```typescript
import { createLogger } from '@arizen/core'
const log = createLogger('my-package')

log.debug('Engine initialising', { config })
log.info('Engine ready')
log.warn('GPU VRAM below recommended threshold', { available: vram })
log.error('Engine failed to mount', { error })
```

Logs are written to `%LOCALAPPDATA%\ArizenOS\logs\` and streamed to the console in development.

---

## Common Issues

**`node-gyp` fails on native module compilation**
```bash
npm install -g node-gyp
node-gyp configure --msvs_version=2022
pnpm install --ignore-scripts=false
```

**`pnpm build` fails with "Cannot find module"**
The build order is managed by Turborepo. If a package cannot find a dependency:
```bash
pnpm clean
pnpm install
pnpm build
```

**Electron window is blank / white**
The renderer failed to load. Check the Electron main process console for errors and verify `pnpm build` completed successfully before running `pnpm dev`.
