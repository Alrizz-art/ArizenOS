# Contributing to ArizenOS

Thank you for your interest in contributing. ArizenOS is built by its community — every contribution matters, whether it is a bug fix, a new feature, improved documentation, or better tests.

This document covers everything you need to make a contribution that gets merged.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Repository Structure](#repository-structure)
- [Branching & Commits](#branching--commits)
- [Pull Request Process](#pull-request-process)
- [RFC Process](#rfc-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Release & Versioning](#release--versioning)
- [Community & Communication](#community--communication)
- [Recognition](#recognition)

---

## Code of Conduct

All contributors must follow the [Code of Conduct](CODE_OF_CONDUCT.md). Violations can be reported to [conduct@arizenos.dev](mailto:conduct@arizenos.dev).

---

## Ways to Contribute

| Track | Where to Start |
|---|---|
| 🐛 Bug fixes | [Issues tagged `good first issue`](https://github.com/Alrizz-art/ArizenOS/labels/good%20first%20issue) |
| ✨ Features | Open a [Feature Request](https://github.com/Alrizz-art/ArizenOS/issues/new?template=feature_request.yml) first |
| 📖 Documentation | [`docs/`](docs/) — any improvement welcome |
| 🎨 Design | Open a [Discussion](https://github.com/Alrizz-art/ArizenOS/discussions) in the `Design` category |
| 🔌 Extensions | Read the [`@arizen/agent-sdk`](packages/agent-sdk/README.md) docs |
| 🔒 Security | See [SECURITY.md](SECURITY.md) — never open a public issue |
| 🌍 Localization | Watch for the `i18n` milestone |
| 🧪 Testing | Improve coverage in [`tests/`](tests/) |

---

## Development Setup

**Prerequisites:**

| Tool | Minimum Version |
|---|---|
| Node.js | 20 LTS |
| pnpm | 8.x |
| Git | 2.40+ |
| Visual Studio Build Tools | 2022 (for N-API native modules) |
| Windows | 10 Build 19041+ or Windows 11 |

**Setup:**

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/ArizenOS.git
cd ArizenOS

# 2. Add the upstream remote
git remote add upstream https://github.com/Alrizz-art/ArizenOS.git

# 3. Install all dependencies
pnpm install

# 4. Build all packages
pnpm build

# 5. Start a specific app in development
pnpm --filter @arizen/launcher dev
```

To verify your environment is correctly set up:

```bash
pnpm lint && pnpm typecheck && pnpm test
```

All three must pass before you open a PR.

---

## Repository Structure

```
ArizenOS/
├── apps/           # End-user applications (Electron)
├── packages/       # Shared libraries and SDKs
├── branding/       # Logos, tokens, fonts
├── docs/           # Documentation site + ADRs
├── tests/          # E2E, integration, visual regression, a11y
└── tools/          # Internal build and scaffold tooling
```

**Dependency rule (strictly enforced by CI):**

```
@arizen/core → packages/* → @arizen/ui → apps/*
apps/* must never import each other.
```

---

## Branching & Commits

### Branch Naming

```
type/short-description-kebab-case

feat/glass-depth-blur-api
fix/launcher-crash-on-windows-10
docs/adr-0002-widget-sandbox
test/core-event-bus-coverage
chore/update-electron-33
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <short description>

[optional body — wrap at 72 chars]

[optional footer: Closes #123, BREAKING CHANGE: ...]
```

**Examples:**

```
feat(glass): add depth-aware blur intensity API
fix(launcher): prevent crash when DWM is disabled
docs(mind): document model configuration options
chore(deps): update llama.cpp binding to v0.3.2
feat!: rename ArizenSkin token format — BREAKING CHANGE
```

- Subject line: imperative mood, no period, ≤72 characters
- Breaking changes: append `!` to type and add `BREAKING CHANGE:` footer
- One logical change per commit — squash if necessary before opening a PR

---

## Pull Request Process

### Before Opening a PR

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run the full check suite:**
   ```bash
   pnpm lint && pnpm typecheck && pnpm test
   ```

3. **Add a Changeset** (if your PR changes a public-facing package):
   ```bash
   pnpm changeset
   ```

4. **Write or update tests.** PRs that reduce coverage will not be merged.

5. **Update documentation.** If you added or changed a public API, update JSDoc, README, and any relevant ADRs.

### PR Requirements

- Target: `main` branch (unless a maintainer has directed you to a feature branch)
- Title: follows Conventional Commits format (`feat(scope): description`)
- Description: fills out all required sections of the PR template
- Size: prefer small, focused PRs. Large PRs are hard to review and slow to merge
- Draft PRs are welcome for early feedback — mark them ready when CI is green

### Review Process

1. CI must be green (lint, typecheck, test, build)
2. At least **1 review from a Core Team member** for packages
3. At least **2 reviews including 1 Module Owner** for changes to `@arizen/core`, `@arizen/mind`, or `@arizen/shell`
4. No unresolved `Request Changes` reviews
5. Maintainer merges using **Squash and Merge** — your commit history will be squashed

Reviewers aim to respond within 5 business days. If you haven't heard back in 7 days, ping the PR with a comment.

---

## RFC Process

An RFC (Request for Comments) is required for any change that:

- Introduces or removes a public package or app
- Modifies a stable public API in a breaking way
- Changes the monorepo architecture or build pipeline
- Has significant cross-cutting UX or performance implications

**RFC lifecycle:**

1. Open an [RFC issue](https://github.com/Alrizz-art/ArizenOS/issues/new?template=rfc.yml)
2. Community discussion period: minimum **14 days**
3. Technical Council reviews and votes (lazy consensus or formal majority)
4. RFC is **Accepted**, **Rejected**, or **Deferred**
5. Accepted RFCs are assigned an RFC number and implementation owner
6. Implementation PR links back to the RFC issue

Do not begin implementation until the RFC is formally accepted.

---

## Code Standards

### TypeScript

- Strict mode enabled — no `any`, no `@ts-ignore` without a comment
- Explicit return types on all public functions
- No default exports in packages (named exports only)
- Prefer `const` over `let`; never `var`

### Style

- ESLint + Prettier — enforced by CI
- Run `pnpm lint --fix` to auto-fix formatting
- All public functions and classes must have JSDoc with `@param`, `@returns`, and `@example`

### Testing

- Unit tests: Vitest — one test file per source file
- Coverage minimum: 80% for `@arizen/core` (100% target), 70% for other packages
- E2E tests: Playwright — required for any new UI flow in apps

### Accessibility

- All UI components in `@arizen/ui` must pass WCAG 2.1 AA
- Run `pnpm a11y` to audit. PRs that introduce a11y regressions will be blocked

---

## Testing Requirements

```bash
# Unit + integration tests
pnpm test

# Type checking
pnpm typecheck

# Lint
pnpm lint

# Accessibility audit (UI changes)
pnpm a11y

# Visual regression (UI changes)
pnpm test:visual

# E2E (full app changes)
pnpm test:e2e
```

Not every PR needs all test suites — use judgement and explain in the PR what was tested.

---

## Documentation Standards

- **In-code:** JSDoc for all public symbols. `@internal` to mark internal APIs
- **Package READMEs:** Each package and app has a `README.md`. Update it if you change the public API
- **Architecture decisions:** Significant decisions should be recorded as ADRs in `docs/architecture/`
- **Docs site:** Content in `docs/` — use Markdown, follow existing structure

---

## Release & Versioning

ArizenOS uses [Semantic Versioning](https://semver.org/) and [Changesets](https://github.com/changesets/changesets):

```bash
# After making a change to a public package, add a changeset:
pnpm changeset

# Choose: major (breaking), minor (feature), or patch (fix)
# Write a summary of the change for the changelog
```

You do not manage releases. Maintainers run `pnpm release` as part of the release process described in [RELEASE.md](RELEASE.md).

---

## Community & Communication

| Channel | Purpose |
|---|---|
| [GitHub Issues](https://github.com/Alrizz-art/ArizenOS/issues) | Bug reports and feature requests |
| [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions) | Q&A, ideas, announcements |
| [Discord](https://discord.gg/arizenos) | Real-time chat, quick help |
| [X (Twitter)](https://x.com/arizenos) | Announcements and project news |

For architectural decisions and large proposals, always use GitHub (Discussions or RFC issues) rather than Discord — decisions made only in chat are not discoverable or durable.

---

## Recognition

Every merged contributor is added to the [MAINTAINERS.md](MAINTAINERS.md) contributors list and credited in the release changelog. Sustained contributors are invited to take on formal roles as Reviewers and Core Team members per the [Governance Model](GOVERNANCE.md).

Thank you for contributing. ArizenOS is better because of you.
