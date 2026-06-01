# Contributing to ArizenOS

> Thank you for investing your time in ArizenOS. Every contribution — code, documentation, design, testing, or community support — makes the project better for everyone.

---

## Table of Contents

1. [Before You Begin](#1-before-you-begin)
2. [Ways to Contribute](#2-ways-to-contribute)
3. [Development Setup](#3-development-setup)
4. [Contribution Workflow](#4-contribution-workflow)
5. [Pull Request Policy](#5-pull-request-policy)
6. [Code Review Standards](#6-code-review-standards)
7. [Commit Standards](#7-commit-standards)
8. [Testing Requirements](#8-testing-requirements)
9. [Documentation Requirements](#9-documentation-requirements)
10. [First-Time Contributors](#10-first-time-contributors)

---

## 1. Before You Begin

### Read First

- [Code of Conduct](CODE_OF_CONDUCT.md) — Required reading. Non-negotiable.
- [Governance Model](GOVERNANCE.md) — Understand how decisions are made.
- [Brand Guidelines](BRAND_GUIDELINES.md) — For UI/UX and naming contributions.
- [Product Charter](PRODUCT_CHARTER.md) — Understand what ArizenOS is and is not.

### Check Before Building

Before opening a PR for a new feature or significant change:

1. **Search existing issues** — someone may already be working on it
2. **Search open PRs** — duplicate work wastes everyone's time
3. **Open an issue first** for features, RFCs, or architectural changes — get alignment before writing code
4. **Small bugs and docs** — go ahead and open a PR directly

### Licensing

By contributing to ArizenOS, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). You confirm that you have the right to contribute the code you submit (i.e., it is your original work or you have the rights to it).

If your employer has intellectual property policies, ensure your contribution complies before submitting.

---

## 2. Ways to Contribute

### Code Contributions
- Bug fixes
- Feature implementation (RFC-accepted features only for major additions)
- Performance improvements
- Security patches (see [Security Policy](SECURITY.md) for vulnerabilities)

### Non-Code Contributions
- **Documentation**: Fixing errors, improving clarity, writing tutorials
- **Design**: UI mockups, icon design, theming, accessibility improvements
- **Testing**: Writing tests, reporting bugs, verifying fixes
- **Triage**: Labeling issues, reproducing bugs, closing stale issues
- **Translation**: Localizing UI strings and documentation
- **Community**: Answering questions in Discussions, writing blog posts, making demo videos

All non-code contributions are valued equally alongside code. They are tracked and credited.

---

## 3. Development Setup

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Windows | 10 (22H2+) or 11 (23H2+) | Primary development target |
| Node.js | 20 LTS+ | For build tooling and extensions |
| Git | 2.40+ | |
| pnpm | 8.x+ | `npm install -g pnpm` |
| Rust | 1.75+ | For performance-critical modules |
| VS Code | Latest | Recommended editor (workspace settings included) |

### Clone and Install

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/<your-username>/ArizenOS.git
cd ArizenOS

# Install dependencies
pnpm install

# Copy environment config
cp .env.example .env.local
```

### Build

```bash
# Build all modules
pnpm build

# Build a specific module
pnpm --filter @arizen/glass build

# Development mode (watch)
pnpm dev
```

### Run Tests

```bash
# Full test suite
pnpm test

# Specific module
pnpm --filter @arizen/mind test

# Watch mode
pnpm test:watch
```

### Lint and Format

```bash
# Lint
pnpm lint

# Format (auto-fix)
pnpm format

# Type check
pnpm typecheck
```

All PRs must pass `pnpm lint && pnpm typecheck && pnpm test` before review.

---

## 4. Contribution Workflow

### Standard Workflow

```
1. Fork → 2. Branch → 3. Code → 4. Test → 5. PR → 6. Review → 7. Merge
```

**Step 1: Fork**
Fork the repository to your GitHub account. Do not push branches directly to `Alrizz-art/ArizenOS` unless you are a Core Team member.

**Step 2: Branch**
Create a branch from `main` with a descriptive name following the [naming convention](BRAND_GUIDELINES.md#branch-naming):
```bash
git checkout -b feat/mind-streaming-inference
git checkout -b fix/glass-blur-performance
git checkout -b docs/api-reference-update
```

**Step 3: Code**
Make your changes. Keep commits atomic — each commit should represent one logical change. See [Commit Standards](#7-commit-standards).

**Step 4: Test**
Run the full test suite locally before pushing:
```bash
pnpm lint && pnpm typecheck && pnpm test
```

**Step 5: Push and Open PR**
```bash
git push origin feat/mind-streaming-inference
```
Open a PR against `Alrizz-art/ArizenOS:main`. Fill out the PR template completely.

**Step 6: Review**
Respond to review feedback within 7 days. If you need more time, comment on the PR. PRs with no response for 14 days are marked `stale` and closed after 7 more days.

**Step 7: Merge**
A Core Team member or Module Owner merges your PR after all requirements are met. You do not merge your own PR.

---

## 5. Pull Request Policy

### PR Requirements (All PRs)

- [ ] Title follows Conventional Commits format
- [ ] PR description filled out completely (use template)
- [ ] Branch is up-to-date with `main`
- [ ] `pnpm lint` passes (zero errors)
- [ ] `pnpm typecheck` passes (zero errors)
- [ ] `pnpm test` passes (zero failures)
- [ ] No unresolved merge conflicts
- [ ] No debug code, `console.log`, commented-out code, or `TODO`s introduced (unless tagged with `// TODO(username): ticket-link`)

### Approval Requirements

| PR Type | Required Approvals | Who Can Approve |
|---|---|---|
| Documentation | 1 | Any Reviewer+ |
| Bug fix | 2 | Any Reviewer+ |
| Feature | 2 | Any Reviewer+, at least 1 Core Team |
| Breaking change | 3 | 2 Core Team + 1 TC member |
| New module | 3 | 1 Module Owner + 1 TC + SC notification |
| Governance / policy | TC vote | Technical Council |

### Review Window

PRs must remain open for a minimum review window before merging:

| Type | Minimum Window |
|---|---|
| Typo / docs fix | 24 hours |
| Bug fix | 48 hours |
| Feature | 72 hours |
| Breaking change | 7 days |

### What Blocks a PR

Any of the following blocks merge:
- A formal `-1` from any Reviewer+ (must include written explanation)
- Failing CI checks
- Unresolved review conversations marked "blocking"
- Missing required approvals

Responding to a `-1`: Address the objection in a new commit or explain why you disagree. If disagreement persists, it escalates to TC per the [Conflict Resolution](GOVERNANCE.md#7-conflict-resolution) process.

### Draft PRs

Use draft PRs for work in progress. Draft PRs:
- Are visible to the community and may receive early feedback
- Do not count toward anyone's review queue
- Must be converted to "Ready for Review" manually before approval can begin

### Stale PRs

- **14 days** of no activity → labeled `stale`
- **7 more days** → closed with a comment
- Authors may reopen or push an update to reset the timer

---

## 6. Code Review Standards

### For Reviewers

**The purpose of code review is to improve the code, not to demonstrate expertise.**

**DO:**
- Review the code, not the author
- Be specific — reference line numbers, link to documentation, provide examples
- Distinguish between blocking issues and non-blocking suggestions
  - Prefix blocking: `[blocking]` — must be fixed before merge
  - Prefix non-blocking: `[nit]`, `[suggestion]`, `[question]`
- Approve PRs you'd be comfortable maintaining
- Acknowledge what the PR does well before raising issues
- Respond to re-review requests within 3 business days

**DO NOT:**
- Leave vague feedback like "this could be better"
- Request changes without explaining why
- Apply personal style preferences not covered in linting rules as blocking issues
- Ghost a PR — if you started a review, see it through or explicitly hand off
- Use review as gatekeeping — if a PR meets standards, approve it

**Review Checklist:**

```
□ Does the PR do what it says it does?
□ Are there tests for new behavior?
□ Does it handle error cases?
□ Are there performance implications?
□ Does it follow the naming conventions?
□ Does it break any existing interfaces?
□ Is the documentation updated?
□ Does it meet accessibility requirements (for UI changes)?
□ Could it introduce security issues?
□ Does it stay within its module boundary?
```

### For PR Authors

- Respond to all review comments, even if just to acknowledge `[nit]` feedback
- Do not resolve conversations opened by a reviewer — let the reviewer resolve after re-review
- Use `fixup!` commits during review; squash before final merge (maintainer may do this)
- If you disagree with feedback, say so clearly and explain why — disagreement is healthy when handled professionally

### Review Anti-Patterns (Banned)

The following review behaviors are considered Code of Conduct violations if persistent:

- **Bike-shedding**: Blocking on low-impact stylistic preferences not covered by linter
- **Review bombing**: Multiple nitpick comments with no substantive concerns
- **Scope creep demands**: Requiring the PR to fix unrelated issues
- **Approval withholding**: Approving in spirit but deliberately withholding formal approval

---

## 7. Commit Standards

ArizenOS uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Use When |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no feature/fix |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system, dependencies |
| `ci` | CI/CD pipeline changes |
| `chore` | Maintenance tasks |
| `revert` | Reverting a prior commit |

### Scopes

Use the module name as scope: `mind`, `glass`, `shell`, `flow`, `skin`, `widgets`, `agent`, `sync`, `docs`, `ci`, `deps`

### Rules

- Description is lowercase, imperative mood, no period at end
- Body wraps at 72 characters
- Breaking changes: add `BREAKING CHANGE:` footer with migration path
- Reference issues: `Closes #123`, `Fixes #456`, `Related to #789`

### Examples

```
feat(mind): add streaming inference for llama-3 models

Implements ReadableStream response from ArizenMind.query() using the
llama.cpp streaming API. Consumers pipe the stream directly to UI
renderers without buffering the full response.

Closes #142

---

fix(glass): resolve blur flicker on secondary monitor hotplug

The DWM composition target was not being re-acquired after a display
change event. Added WM_DISPLAYCHANGE handler to force re-initialization.

Fixes #284

---

feat(shell)!: remove legacy widget bridge API

BREAKING CHANGE: The `LegacyWidgetBridge` class and all methods under
`ArizenShell.legacyWidgets.*` have been removed. Migrate to the
ArizenWidgets SDK introduced in v0.3.0. See docs/migration/v0.4.md.
```

---

## 8. Testing Requirements

### Coverage Requirements

| Module | Minimum Coverage | Notes |
|---|---|---|
| ArizenMind | 80% | All inference paths tested |
| ArizenShell | 70% | Window management logic |
| ArizenGlass | 60% | Rendering has integration tests |
| All modules | 60% minimum | Hard floor; CI blocks below this |

### Test Types

**Unit Tests** — Required for all new functions and methods.
```typescript
// Every exported function must have at least one unit test
describe("ArizenMind.query()", () => {
  it("returns a ReadableStream", async () => { ... });
  it("throws ModelNotFoundError when model is missing", async () => { ... });
  it("respects context length limit", async () => { ... });
});
```

**Integration Tests** — Required for module boundaries and API interactions.

**Visual Regression Tests** — Required for all ArizenGlass and ArizenFlow changes.
Use the project's Playwright + screenshot comparison setup.

**Accessibility Tests** — Required for all UI component additions.
Use axe-core integration included in the test suite.

### Test File Naming

```
src/mind/query.ts          → src/mind/query.test.ts
src/glass/renderer.ts      → src/glass/renderer.test.ts
src/shell/taskbar.ts       → src/shell/taskbar.test.ts
```

Integration tests live in `tests/integration/`.
E2E tests live in `tests/e2e/`.

---

## 9. Documentation Requirements

### What Requires Documentation

| Change Type | Required Documentation |
|---|---|
| New public API / function | JSDoc + API reference page |
| New module | `docs/<module>/README.md` + architecture overview |
| New CLI flag | `docs/cli.md` update |
| Configuration change | `docs/configuration.md` update |
| Breaking change | `docs/migration/v<X.Y>.md` |
| New user-facing feature | Guide in `docs/guides/` |

### JSDoc Standard

All exported functions, classes, types, and interfaces must have JSDoc:

```typescript
/**
 * Queries the local inference engine with the provided prompt.
 *
 * Returns a `ReadableStream<string>` that emits tokens as they are generated.
 * The stream closes automatically when inference completes.
 *
 * @param prompt - The input text to send to the model.
 * @param options - Optional configuration for this query.
 * @returns A readable stream of generated tokens.
 * @throws {ModelNotFoundError} When no model is loaded or the specified model is not found.
 * @throws {ContextLengthError} When the prompt exceeds the model's context window.
 *
 * @example
 * const stream = await mind.query("Summarize my open PRs");
 * for await (const token of stream) {
 *   process.stdout.write(token);
 * }
 */
async query(prompt: string, options?: QueryOptions): Promise<ReadableStream<string>>
```

---

## 10. First-Time Contributors

### Good First Issues

Issues tagged [`good first issue`](https://github.com/Alrizz-art/ArizenOS/labels/good%20first%20issue) are scoped, documented, and mentored. They are held for new contributors — please do not claim them if you are already a Reviewer+.

To claim an issue: comment "I'd like to work on this" and a maintainer will assign it to you. Assignments expire after 14 days of no progress update.

### Getting Help

- **GitHub Discussions** — Ask questions in the `Q&A` category
- **Issue comments** — Ask for clarification directly on the issue you're working on
- **Mentorship** — Tag a Core Team member on your draft PR for early feedback

### What to Expect

- First response to your PR within 5 business days
- Honest, specific feedback — not vague rejections
- Credit in the release notes for every merged contribution
- A path to Reviewer status if you want it

We know the first PR is the hardest. We will work with you to get it merged.

---

*ArizenOS Contributing Guide v1.0 — June 2025*
*Questions? Open a GitHub Discussion in the `contributing` category.*
