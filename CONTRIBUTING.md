# Contributing to ArizenOS

## Before You Start

1. Read [Core Principles](docs/PRINCIPLES.md)
2. Read [Dependency Rules](docs/DEPENDENCY_RULES.md) — **these are enforced in CI**
3. Read [Naming Conventions](docs/NAMING_CONVENTIONS.md)
4. Check [Roadmap](docs/ROADMAP.md) for what's in scope
5. Open an issue before large PRs

## Quick Start (Development)

```powershell
# Requirements: Windows 10+ (AME recommended), PS7+, Rust 1.79+, Python 3.12+, Node 20+
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS
.\scripts\dev\dev-setup.ps1

# Start daemon in watch mode
.\scripts\dev\watch-daemon.ps1

# In a new terminal, start Command Nexus dev server
.\scripts\dev\watch-nexus.ps1
```

## Code Standards

| Layer | Linter | Formatter | Type check |
|-------|--------|-----------|------------|
| Rust  | clippy | rustfmt   | n/a (compile-time) |
| Python | ruff  | black     | mypy (strict) |
| TS/React | eslint | prettier | tsc --strict |

## Adding a New Agent

1. Create `agents/<name>/` directory
2. Inherit from `agents/_base.BaseAgent`
3. Declare `MANIFEST: AgentManifest` with all capabilities
4. Add `manifest.toml` — this is the source of truth for capability enforcement
5. Register in `MODULE_MANIFEST.toml`
6. Add docs/guides entry

## Adding a New Skill

1. Create `skills/<category>/<name>.py`
2. Inherit from `skills.sdk.BaseSkill`
3. Declare `MANIFEST: SkillManifest` with correct `side_effects`
4. Add TOML entry to `skills/_manifest/<category>.toml`
5. Skills must be **stateless** — no memory imports

## Adding a Playbook

1. Create YAML in `playbooks/library/<name>.yaml` (built-in) or `playbooks/user/` (user-defined)
2. Validate against schema: `python -m playbooks.schema.schema your_playbook.yaml`

## Branch Strategy

```
main          ← always releasable, tagged releases only
dev           ← integration branch
feat/*        ← new features (merges to dev)
fix/*         ← bug fixes
arch/*        ← architecture changes (require ADR in docs/decisions/)
```

## Commit Convention

```
feat(agents): add parallel task execution to Monarch
fix(lm-studio): handle connection timeout with exponential backoff
arch(ipc): switch event bus encoding to MessagePack
docs(guides): add LM Studio setup guide
perf(knowledge): HNSW index reduces P99 search latency by 8x
```

## What We Will Not Merge

- Cloud dependencies in Tier 0/1/2 (use feature flag at minimum)
- Telemetry or analytics of any kind
- LLM calls that bypass `integrations/lm-studio` priority
- Cross-agent direct Python imports (must use IPC bus)
- TypeScript code that imports Python packages
