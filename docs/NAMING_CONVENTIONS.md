# ArizenOS — Naming Conventions

## System: The Arizen Lexicon

All names in ArizenOS draw from a consistent thematic vocabulary:
- **Arizen core concepts:** Sovereignty, intelligence, architecture, light
- **Agents:** Named after roles with mythological/celestial weight
- **Components:** Named for their function, not their implementation
- **Versions:** Celestial phenomena (Ignition → Kindling → Circuit → Prism → Eclipse → Sovereign)

---

## Repositories & Packages

| Level | Pattern | Example |
|-------|---------|---------|
| Organization | PascalCase | `Alrizz-art` |
| Repository | PascalCase | `ArizenOS` |
| Subpackage | kebab-case | `arizen-daemon`, `llm-gateway` |
| Python package | snake_case | `arizen_daemon`, `llm_gateway` |
| Rust crate | snake_case | `arizen_daemon`, `arizen_ipc` |
| npm package | `@arizen/` scope | `@arizen/command-nexus` |

---

## Agents

Agents are named as proper nouns (not generic labels):

| Role | Name | Etymology |
|------|------|-----------|
| Orchestrator | **Monarch** | Sovereign authority, commands the mesh |
| Knowledge | **Archivist** | Guardian and curator of knowledge |
| Task Execution | **Executor** | Carries out ordered tasks |
| System Monitor | **Sentinel** | Watchful guardian of system state |
| Workflow | **Weaver** | Weaves threads of automation |
| Research | **Oracle** | Source of synthesized insight |

Future agents follow the same convention — a single proper noun with clear semantic meaning.

---

## File & Directory Naming

```
Directories:     kebab-case    /core/llm-gateway/
Source files:    snake_case    monarch_agent.py
Rust files:      snake_case    ipc_router.rs
TS/React files:  PascalCase    CommandPalette.tsx
Config files:    kebab-case    agent-config.toml
Test files:      *_test.py     monarch_agent_test.py  (Python)
                 *.test.ts     CommandPalette.test.ts (TS)
Doc files:       SCREAMING.md  VISION.md, ROADMAP.md
```

---

## Configuration (TOML-first)

All configuration files use **TOML** as the primary format.

```toml
# File: agents/monarch/manifest.toml
[agent]
name       = "monarch"
display    = "Monarch"
version    = "0.1.0"
tier       = "high"
autostart  = true

[capabilities]
tools      = ["delegate", "plan", "synthesize"]
memory     = ["session", "persistent"]
fs_access  = false
net_access = false

[model]
preferred  = "phi3:14b-medium-4k-instruct-q4_K_M"
fallback   = "phi3:mini"
tier       = 2
```

---

## IPC Message Types

All message types use SCREAMING_SNAKE_CASE:

```
TASK_REQUEST
TASK_RESPONSE
TASK_UPDATE
TASK_CANCELLED
AGENT_STATUS
AGENT_STARTED
AGENT_STOPPED
WORKFLOW_TRIGGERED
WORKFLOW_COMPLETED
WORKFLOW_FAILED
APPROVAL_REQUESTED
APPROVAL_GRANTED
APPROVAL_DENIED
SYSTEM_EVENT
HEALTH_CHECK
HEALTH_RESPONSE
```

---

## Version Naming

```
Format:     YYYY.MM.MICRO
Example:    2025.01.0

Codenames (in order):
  v0.1  Ignition   — First light, first fire
  v0.2  Kindling   — Building knowledge
  v0.3  Circuit    — Automation comes alive
  v0.4  Prism      — Intelligence refracts into agents
  v0.5  Eclipse    — The UI takes center stage
  v1.0  Sovereign  — Full autonomy achieved
  v1.x  Horizon    — Expansion beyond the core
  v2.0  Continuum  — The platform becomes infinite
```

---

## Commit Messages

Format: `type(scope): message`

| Type | Meaning |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `perf` | Performance improvement |
| `refactor` | Code refactoring |
| `docs` | Documentation only |
| `test` | Tests only |
| `chore` | Build/tooling/CI |
| `arch` | Architecture change |

```
feat(monarch): add parallel sub-task execution in planning graph
fix(llm-gateway): handle Ollama stream timeout on slow hardware
perf(vault): switch to HNSW index for 10x faster vector search
arch(daemon): replace REST with gRPC for agent communication
```

---

## Branch Strategy

```
main          — Always releasable. Tagged releases only.
dev           — Integration branch for features
feat/*        — Feature branches  (feat/monarch-planning)
fix/*         — Bug fix branches  (fix/vault-timeout)
arch/*        — Architecture changes
docs/*        — Documentation updates
release/*     — Release preparation (release/v0.2-kindling)
```
