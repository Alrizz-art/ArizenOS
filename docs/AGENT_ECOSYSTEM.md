# ArizenOS Agent Ecosystem

> **Version:** 1.0.0 | **Status:** Architecture + Implementation

This document defines the full design of the ArizenOS Agent Ecosystem — eight
specialist agents orchestrated by a single authority, **Arizen Commander**.

---

## Overview

```
                         ┌─────────────────────────────┐
                         │      USER (Command Nexus)    │
                         │  natural language · hotkeys  │
                         └──────────────┬──────────────┘
                                        │  Named Pipe
                                        ▼
                         ┌─────────────────────────────┐
                         │      ARIZEN COMMANDER        │
                         │  Intent → DAG → Synthesize   │
                         │  Emergency Stop · Approval   │
                         └──┬──┬──┬──┬──┬──┬──┬───────┘
                            │  │  │  │  │  │  │
          ┌─────────────────┘  │  │  │  │  │  └─────────────────┐
          │          ┌─────────┘  │  │  │  └──────┐             │
          │          │       ┌────┘  │  └──┐       │             │
          ▼          ▼       ▼       ▼     ▼       ▼             ▼
      ┌───────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
      │ CODER │ │RESEARCH│ │FIXER │ │ DEVOPS │ │SECURITY│ │DESIGNER  │ │  MEMORY  │
      └───────┘ └────────┘ └──────┘ └────────┘ └────────┘ └──────────┘ └──────────┘
```

**Rule:** Every user request enters through Commander. No agent is ever called
directly. Agents may only return results to Commander, and may only read from Memory.
Direct agent-to-agent communication is prohibited by the permission matrix.

---

## 1. Arizen Commander

### Responsibilities
- Receive all user input from the Command Nexus UI
- Classify intent into one of 16 typed `TaskType` categories
- Enrich context by querying Memory before planning
- Build an execution DAG (`ExecutionPlan`) of typed `SubTask` nodes
- Gate destructive tasks behind the approval system
- Execute the DAG with dependency-aware parallelism
- Synthesize the final streaming response from agent results
- Commit outcomes back to Memory
- Broadcast `EMERGENCY_STOP` on hotkey — halts all running agents instantly

### Permissions
| Capability | Allowed |
|---|---|
| Delegate to any agent | ✅ |
| Filesystem read/write | ❌ (delegates to Coder/Memory) |
| Network access | ❌ |
| Approve own tasks | ❌ (always prompts user for destructive ops) |
| Emergency stop broadcast | ✅ |
| Spawn new agents | ✅ (via daemon) |

### Tools
```python
"bus.delegate"          # send task to a specialist agent
"bus.broadcast"         # fan-out message to all agents (e.g. EMERGENCY_STOP)
"bus.emergency_stop"    # immediate halt — highest priority
"plan.classify"         # LLM-powered intent classification
"plan.build_dag"        # decompose composite request into SubTask graph
"plan.approve"          # present approval gate to user
"agent.list"            # enumerate running agents + health
"agent.health_check"    # ping individual agent
```

### Communication Contract
```
Direction     │ Message Kind      │ Payload
──────────────┼───────────────────┼─────────────────────────────
User → Cmd    │ (raw text/event)  │ query string from named pipe
Cmd → Agent   │ TASK_REQUEST      │ TaskRequestPayload
Agent → Cmd   │ TASK_RESULT       │ TaskResultPayload
Agent → Cmd   │ TASK_STREAM       │ TaskStreamPayload (token chunk)
Agent → Cmd   │ APPROVAL_NEEDED   │ ApprovalNeededPayload
Cmd → All     │ EMERGENCY_STOP    │ {}
Cmd → UI      │ (stream)          │ synthesized response tokens
```

### Execution Model
```
1. classify(query)              → TaskType            [Tier 0 or Nano LLM]
2. memory.context_for_query()   → context dict        [always, non-blocking]
3. build_dag(query, intent)     → ExecutionPlan        [Nano LLM for composite]
4. approval_gate(plan)          → filtered plan        [sync, may prompt UI]
5. execute_dag(plan)            → results dict         [async, dependency-ordered]
   ├── ready tasks run in parallel via asyncio.gather
   ├── dependent tasks wait for their deps via polling
   └── each task is timeout-gated (default 30s)
6. synthesize(query, results)   → streaming tokens     [Standard LLM]
7. memory.store_interaction()   → fire-and-forget      [background task]
```

---

## 2. Arizen Coder

### Responsibilities
- Generate new code from natural language descriptions
- Review existing code for bugs, security issues, and style
- Refactor code with unified diff output
- Explain code in plain language
- Generate unit tests (pytest / cargo test / vitest)
- Read and write files within the declared filesystem sandbox

### Permissions
| Capability | Allowed |
|---|---|
| Filesystem read | ✅ (declared paths: agents/, core/, ui/, apps/, docs/, scripts/) |
| Filesystem write | ✅ with approval gate |
| Network access | ❌ |
| Shell execution | ❌ (delegates to DevOps) |
| LLM tier | Power (code quality demands it) |

### Tools
```python
"filesystem.read"       # read source files (sandboxed)
"filesystem.write"      # write files — triggers approval gate
"filesystem.diff"       # produce unified diff
"filesystem.list_dir"   # list directory contents
"shell.syntax_check"    # validate syntax (delegated to DevOps)
"shell.run_tests"       # run test suite after patch
```

### Filesystem Sandbox
```toml
allowlist = [
  "agents/", "core/", "integrations/",
  "skills/", "ui/", "apps/", "docs/",
  "scripts/", "playbooks/"
]
# Coder may NOT access: memory/, branding/ (Designer), .git/, config secrets
```

### Execution Model
```
1. detect_language(file_path | query)   → Language enum
2. load_file(file_path)                 → existing code context
3. route → generate | review | refactor | explain | test
4. LLM call with role-specific system prompt
5. strip_fences() → clean code
6. [refactor only] make_diff(original, result)
7. [write ops] assert_allowed() → write_file() with approval
8. return CodeResult → Commander
```

---

## 3. Arizen Researcher

### Responsibilities
- Query a local SearXNG instance (private, no tracking)
- Fetch and parse web pages (text extraction, not browser rendering)
- Summarize long documents using chunked RAG
- Synthesize multi-source answers with inline citations
- Hybrid mode: combine local Memory search + web results

### Permissions
| Capability | Allowed |
|---|---|
| Network (SearXNG, HTTP fetch) | ✅ — all requests are logged |
| Filesystem | ❌ |
| Store to Memory | ✅ (via Memory agent) |
| Max sources per query | 5 |
| Max content per source | 4,000 chars |

### Tools
```python
"web.search"            # SearXNG query → ranked Source list
"web.fetch"             # fetch + extract text from single URL
"web.fetch_parallel"    # concurrent fetch for multiple sources
"docs.local_search"     # delegate to Memory for local knowledge
"docs.summarize"        # chunk + summarize long document
```

### Search Modes
| Mode | Strategy |
|---|---|
| `web` | SearXNG → fetch top 5 → synthesize |
| `docs` | Memory semantic search → synthesize |
| `hybrid` | Both in parallel → merge → rerank → synthesize |

### Execution Model
```
1. parse mode (web | docs | hybrid)
2. [web]  searxng(query) → Source list
3. [docs] memory.semantic_search(query) → Source list
4. fetch_all(sources, parallel, timeout=10s)
5. build_rag_context(sources, max_chars=20k)
6. llm.complete(rag_prompt, tier="standard")
7. attach citations → return ResearchResult
```

---

## 4. Arizen Fixer

### Responsibilities
- Parse error logs and stack traces (Python / Rust / TypeScript / Node)
- Locate the affected source file and load ±50 lines of context
- Diagnose root cause with severity rating and confidence score
- Generate a targeted patch (not whole-file rewrite)
- Optionally run the test suite to verify the patch before proposing it
- Always propose — never auto-apply without Commander's approval gate

### Permissions
| Capability | Allowed |
|---|---|
| Filesystem read | ✅ (all source paths, read-only by default) |
| Filesystem write | ✅ with approval gate (apply patch) |
| Shell (run tests) | ✅ read-only, sandboxed |
| Auto-apply patch | ❌ always requires approval |

### Stack Trace Parsers
| Language | Pattern |
|---|---|
| Python | `File "path", line N` |
| TypeScript/Node | `at path:N:col` |
| Rust | `--> path:N:col` |
| flake8/mypy | `path.py:N: error:` |

### Execution Model
```
1. parse_report(error_text) → BugReport
   ├── regex extract file_path + line_number
   └── identify stack_trace block
2. load_context(file, line, window=50) → numbered source lines
3. llm.complete(diagnosis_prompt, tier="power") → JSON diagnosis
4. parse Severity + ROOT_CAUSE + EXPLANATION + PATCH + CONFIDENCE
5. make_diff(original_context, patch)
6. return Diagnosis → Commander
7. [if approved] apply_patch() → run_tests() → verify
```

---

## 5. Arizen DevOps

### Responsibilities
- Build the ArizenOS components (Rust daemon, Tauri UI, Python agents)
- Run CI pipelines (clippy, cargo test, flake8, pytest)
- Control Windows services (ArizenDaemon — start/stop/restart/status)
- Orchestrate release packaging via PowerShell scripts
- Monitor running processes and resource usage
- All destructive ops (deploy, service restart) require user approval

### Permissions
| Capability | Allowed |
|---|---|
| Shell — allowlisted commands | ✅ |
| Shell — arbitrary commands | ❌ |
| Service control | ✅ with approval |
| Filesystem (build artifacts) | ✅ |
| Network | ❌ |

### Command Allowlist
```python
{
  "cargo", "rustup",          # Rust toolchain
  "npm", "pnpm", "npx",       # JS/TS toolchain
  "python", "pip", "pytest",  # Python toolchain
  "sc", "net",                # Windows service control
  "powershell", "pwsh",       # Shell scripting
  "git", "gh",                # Version control
  "docker", "docker-compose", # Containers (optional)
}
# Any command NOT in this set raises PermissionError
```

### Build Targets
| Target | Command |
|---|---|
| `daemon` | `cargo build --release` (arizen-daemon) |
| `ui` | `pnpm --filter command-nexus build` |
| `agents` | `pip install -r requirements.txt` |
| `all` | `pwsh -File scripts/build/build_all.ps1` |

### Execution Model
```
1. parse action (build | ci | deploy | monitor | service)
2. assert_command_allowed(cmd[0])
3. [deploy / service restart] → approval gate
4. shell.run(cmd, timeout=30-600s)
5. parse stdout/stderr → structured result
6. emit HUD event (build-complete / ci-passed / service-started)
7. return result → Commander
```

---

## 6. Arizen Security

### Responsibilities
- Scan code for secret leakage (GitHub tokens, AWS keys, passwords, connection strings)
- Detect dangerous code patterns (eval, exec, shell=True, SQL injection, pickle)
- Audit Python and Rust dependencies for known CVEs (pip-audit, cargo audit)
- Report findings with severity, location, CVE ID, and remediation
- **Never auto-remediate** — all findings are returned for human review

### Permissions
| Capability | Allowed |
|---|---|
| Filesystem read (all source) | ✅ |
| Filesystem write | ❌ |
| Network | ❌ (fully offline — no external CVE DB) |
| Auto-quarantine files | ❌ always requires approval |
| LLM | Standard (for contextual analysis) |

### Secret Detection Patterns
| Category | Pattern |
|---|---|
| GitHub Token | `ghp_[A-Za-z0-9]{36}` |
| AWS Key | `AKIA[0-9A-Z]{16}` |
| Private Key | `-----BEGIN * PRIVATE KEY-----` |
| Env Password | `(password\|secret\|token) = "..."` |
| Connection String | `(mongodb\|postgresql\|mysql)://...` |

### Dangerous Code Patterns
| Severity | Pattern |
|---|---|
| HIGH | `eval()`, `exec()`, SQL string concatenation |
| MEDIUM | `shell=True`, `pickle.loads()` |
| LOW | `print()` with credential variables |

### Scoring
```
score = max(0, 100 - (findings_count × weight))
weight: critical=20, high=10, medium=5, low=2, info=1
```

### Execution Model
```
1. parse target (file | directory | deps)
2. [scan] walk files matching SCAN_EXTENSIONS
   ├── secret_scan() → regex across full content
   └── code_danger_scan() → dangerous pattern regex
3. [audit] dep_audit()
   ├── pip-audit --format=json
   └── cargo audit --json
4. merge findings → sort by severity → score
5. format_report() → return AuditReport → Commander
# NEVER write, never remediate, never delete
```

---

## 7. Arizen Designer

### Responsibilities
- Generate React/TypeScript UI components following the ArizenOS design system
- Update design tokens in `branding/tokens/tokens.toml` (CSS vars, colors, spacing)
- Generate clean SVG icons (24×24, monochrome, currentColor)
- Audit existing UI for accessibility issues (WCAG AA: alt text, aria-labels, keyboard)
- Generate Storybook CSF3 stories for new components
- Write to `ui/` and `branding/` directories only (requires approval)

### Permissions
| Capability | Allowed |
|---|---|
| Filesystem read/write | ✅ (ui/, apps/, branding/ only) |
| Network | ❌ |
| Run dev server | ❌ (delegates to DevOps) |
| LLM tier | Power |
| Autostart | ❌ (on-demand) |

### Design System Constraints
```
Stack:    React 18 + TypeScript + Tauri 2.0 + CSS Modules
No:       Tailwind, inline styles, Electron patterns
Tokens:   CSS variables from branding/tokens/tokens.toml
Motion:   Framer Motion, 150–250ms transitions
A11y:     aria-label on all interactive, keyboard handlers with onClick
Theme:    Dark-first; data-theme="light" on :root for light mode
Language: Monospace accents, sharp geometry, terminal-inspired palette
```

### Execution Model
```
1. parse action (component | theme | icon | audit | storybook)
2. load_tokens() → branding/tokens/tokens.toml
3. [component] llm(design_system_prompt + tokens + query)
   ├── split TSX / CSS Module
   ├── check_accessibility() → warnings
   └── write_file() with approval
4. [theme] llm(token_update_prompt) → new TOML → write
5. [icon] llm(svg_prompt) → SVG → write
6. [audit] walk ui/**/*.tsx → check_accessibility() per file
7. return DesignResult → Commander
```

---

## 8. Arizen Memory

### Responsibilities
- Maintain three memory scopes simultaneously:
  - **Working**: in-process dict, fastest, cleared on restart
  - **Session**: SQLite rows, current session only
  - **Persistent**: ChromaDB vectors + SQLite FTS5, cross-session
- Serve context pre-flight for Commander's planning phase
- Ingest arbitrary files into persistent knowledge (embedder pipeline)
- Compress old session entries into persistent summaries nightly
- `forget()` operation always requires user approval

### Permissions
| Capability | Allowed |
|---|---|
| Filesystem read | ✅ (agents/, core/, memory/, knowledge/, docs/, playbooks/) |
| ChromaDB write | ✅ |
| SQLite write | ✅ |
| Network | ❌ |
| Delete memories | ✅ with approval gate |
| Call other agents | ❌ |

### Memory Scopes
| Scope | Backend | Latency | Lifespan |
|---|---|---|---|
| Working | Python dict | <1ms | Process lifetime |
| Session | SQLite | <10ms | User session |
| Persistent | ChromaDB + SQLite FTS5 | <100ms | Indefinite |

### Query Pipeline
```
query string
    │
    ├── working: dict scan (substring match)    ← fastest
    ├── session: SQLite LIKE query              ← recent
    └── persistent: hybrid search
            ├── vector: embed(query) → ChromaDB cosine sim
            └── keyword: SQLite FTS5 full-text search
                    │
                    └── merge + rerank (MMR) → top-k results
```

### Execution Model
```
1. parse action (store | query | semantic_search | context_for_query |
                 store_interaction | compress_session | forget)
2. [store] chunk(content, 512 tokens, 64 overlap)
           → embed each chunk (nomic-embed-text v1.5)
           → chroma.add() + sqlite INSERT
3. [query] hybrid: dict + sqlite LIKE + chroma cosine → merge → top-k
4. [context_for_query] query(limit=3) + session_summary() → dict
5. [compress_session] summarize old rows → store(persistent) → DELETE old
6. [forget] approval gate → DELETE from chroma + sqlite
```

---

## Communication Contracts

### Message Envelope (MessagePack over Named Pipe)

```python
@dataclass
class ArizenMessage:
    message_id:   str       # UUIDv4
    correlation:  str       # links result to request
    source:       str       # agent name
    target:       str       # agent name | "broadcast"
    kind:         MsgKind   # TASK_REQUEST | TASK_RESULT | ...
    payload:      dict      # kind-specific body
    timestamp_ms: int       # Unix milliseconds
    priority:     int       # 0 (lowest) → 10 (emergency)
    ttl_sec:      int       # message expiry window
```

### Permission Matrix

```
             ┌──────────────────────────────────────────────────────────┐
             │          TARGET AGENT                                    │
SOURCE       │ cmd   coder  rsch  fixer  dvps  sec   dsgn  mem         │
─────────────┼──────────────────────────────────────────────────────────┤
commander    │  —     ✓     ✓      ✓     ✓     ✓     ✓     ✓           │
coder        │  ✓     —     ✗      ✗     ✗     ✗     ✗     ✓(read)    │
researcher   │  ✓     ✗     —      ✗     ✗     ✗     ✗     ✓(read)    │
fixer        │  ✓     ✗     ✗      —     ✗     ✗     ✗     ✓(read)    │
devops       │  ✓     ✗     ✗      ✗     —     ✗     ✗     ✓(read)    │
security     │  ✓     ✗     ✗      ✗     ✗     —     ✗     ✓(read)    │
designer     │  ✓     ✗     ✗      ✗     ✗     ✗     —     ✓(read)    │
memory       │  ✓     ✗     ✗      ✗     ✗     ✗     ✗     —          │
└────────────┴──────────────────────────────────────────────────────────┘
✓ = permitted  ✗ = PermissionError raised  ✓(read) = read-only Memory access
```

### Approval-Required Tools
All of these prompt the user before execution:
```
filesystem.delete  |  filesystem.move  |  filesystem.write
devops.deploy      |  devops.service.restart
security.quarantine|  shell.execute_arbitrary  |  memory.forget
```

---

## Implementation Plan

### Phase 1 — Foundation (Week 1–2)

| Task | Owner | Depends |
|---|---|---|
| Implement `CommanderAgent` class | Coder | base_agent ✅ |
| Wire Commander to daemon IPC bus | Daemon | Commander class |
| Implement `MemoryAgent` with SQLite | Coder | base_agent ✅ |
| Integrate ChromaDB + nomic embedder | Memory | SQLite done |
| Write agent_registry.toml | Done ✅ | — |
| Write message_schema.py | Done ✅ | — |
| Define permission matrix enforcement | Commander | contracts ✅ |

### Phase 2 — Core Agents (Week 3–4)

| Task | Owner | Depends |
|---|---|---|
| Implement `CoderAgent` | Coder | Commander + Memory |
| Implement `FixerAgent` | Coder | Commander + Memory |
| Implement `ResearcherAgent` | Coder | Commander + Memory |
| Implement `DevOpsAgent` + shell runner | Coder | Commander |
| Implement `SecurityAgent` | Coder | Commander |
| Unit tests for all agents | Coder | All agents |

### Phase 3 — Designer + Integration (Week 5–6)

| Task | Owner | Depends |
|---|---|---|
| Implement `DesignerAgent` | Coder | Commander + Memory |
| Integrate agents into daemon process manager | Daemon | All agents |
| Wire Command Nexus UI → Commander | UI | Commander running |
| DAG visualizer in HUD overlay | Designer | Commander |
| Integration test: full user request → all agents | All | Phase 2 done |
| Emergency stop hotkey binding | Daemon | Commander |

### Phase 4 — Hardening (Week 7–8)

| Task | Owner | Depends |
|---|---|---|
| Approval gate UI in Command Nexus | Designer | UI wired |
| Memory compression scheduler (nightly) | Memory | Phase 2 done |
| Agent health dashboard | Designer | All agents |
| Security audit of all agent manifests | Security | All agents |
| Performance profiling (latency budgets) | DevOps | All agents |
| Documentation + developer guide | All | Phase 3 done |

---

## File Structure

```
agents/
├── _base/
│   ├── base_agent.py          # BaseAgent, AgentContext, AgentManifest ✅
│   └── tool_registry.py       # @tool decorator, ToolMeta ✅
├── contracts/
│   ├── message_schema.py      # ArizenMessage, MsgKind, permission matrix ✅ NEW
│   └── agent_registry.toml   # agent metadata, LLM tiers, pipe map ✅ NEW
├── commander/
│   └── commander_agent.py     # CommanderAgent ✅ NEW
├── coder/
│   └── coder_agent.py         # CoderAgent ✅ NEW
├── researcher/
│   └── researcher_agent.py    # ResearcherAgent ✅ NEW
├── fixer/
│   └── fixer_agent.py         # FixerAgent ✅ NEW
├── devops/
│   └── devops_agent.py        # DevOpsAgent ✅ NEW
├── security/
│   └── security_agent.py      # SecurityAgent ✅ NEW
├── designer/
│   └── designer_agent.py      # DesignerAgent ✅ NEW
└── memory/
    └── memory_agent.py        # MemoryAgent ✅ NEW
```

---

## Design Principles Applied

| Principle | How Agents Honour It |
|---|---|
| **Sovereignty First** | No agent has net_access by default; Researcher's is opt-in + fully logged |
| **Composable by Design** | Each agent is a separate process; swap or disable any without touching others |
| **Transparent by Default** | Every tool call is logged; all agent decisions are auditable |
| **Performance Without Compromise** | LLM tier routing (Nano/Standard/Power) per agent; Commander context fetch is non-blocking |
| **Agent Sovereignty** | Each agent runs isolated; FS sandbox enforced by assert_allowed(); agent-to-agent calls blocked by permission matrix |
| **Human-in-the-Loop** | All write/destroy/deploy/service ops gate on user approval before execution |
