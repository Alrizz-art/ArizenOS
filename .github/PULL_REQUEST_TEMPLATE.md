## Summary

<!-- One paragraph: what does this PR do and why? -->

## Type of Change

<!-- Check all that apply -->

- [ ] `fix` — Bug fix (non-breaking)
- [ ] `feat` — New feature (non-breaking)
- [ ] `feat!` — Breaking change (requires migration guide)
- [ ] `docs` — Documentation only
- [ ] `perf` — Performance improvement
- [ ] `refactor` — Code restructuring, no behavior change
- [ ] `test` — Test additions or fixes
- [ ] `chore` — Build, CI, dependency updates

## Related Issues

<!-- Link issues this PR closes or relates to -->
<!-- Use: Closes #N, Fixes #N, Related to #N -->

Closes #

## What Changed

<!-- Bullet list of specific changes. Be precise. -->

-
-
-

## Testing

<!-- Describe how you tested this. Check what you ran. -->

- [ ] `pnpm lint` — zero errors
- [ ] `pnpm typecheck` — zero errors
- [ ] `pnpm test` — all passing
- [ ] Manual smoke test on Windows 10 / 11
- [ ] Visual regression test (for UI changes)
- [ ] Accessibility check (for UI changes)

**Test environment:**
- OS: Windows <!-- 10 22H2 / 11 23H2 -->
- GPU: <!-- integrated / discrete -->
- Display: <!-- single / multi-monitor, DPI -->

## Screenshots / Recordings

<!-- For UI changes, before/after screenshots are required.
     For non-UI changes, delete this section. -->

| Before | After |
|---|---|
| <!-- screenshot --> | <!-- screenshot --> |

## Breaking Changes

<!-- If this is a breaking change, describe what breaks and how to migrate.
     If not breaking, delete this section. -->

**What breaks:**

**Migration path:**

```typescript
// Before
// After
```

## Documentation

<!-- Check what documentation you updated or explain why none was needed. -->

- [ ] JSDoc updated for all changed public APIs
- [ ] `docs/` updated for user-facing changes
- [ ] `CHANGELOG.md` — entry added under `[Unreleased]`
- [ ] Migration guide added (if breaking change)
- [ ] No documentation needed (explain below)

## Checklist

- [ ] PR title follows Conventional Commits format (`type(scope): description`)
- [ ] Branch is up-to-date with `main`
- [ ] No debug code, stray `console.log`, or commented-out blocks
- [ ] No new `TODO`s without `// TODO(username): #issue-link` format
- [ ] Self-reviewed this diff before marking ready for review
