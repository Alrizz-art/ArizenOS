# ArizenOS Playbook Engine

> **Version:** 1.0.0 | **Status:** Implementation

The Playbook Engine is the **primary runtime of ArizenOS**. Every user
action — from creating a project to deploying a service — executes as a
Playbook. No agent is ever called directly; all orchestration flows
through the engine.

---

## Architecture Overview

```
User (Command Nexus)
        │  natural language / hotkey
        ▼
  Arizen Commander
        │  selects or generates Playbook
        ▼
┌───────────────────────────────────────────────────────┐
│                  PLAYBOOK ENGINE                       │
│                                                        │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐             │
│  │Validator│→ │  Graph   │→ │  Queue   │             │
│  │(Pydantic│  │ Builder  │  │(priority │             │
│  │ + YAML) │  │  (DAG)   │  │+ concur) │             │
│  └─────────┘  └──────────┘  └────┬─────┘             │
│                                   │ waves             │
│  ┌──────────┐  ┌──────────┐  ┌───▼──────┐            │
│  │Checkpoint│  │ Observer │  │ Executor │            │
│  │(SQLite)  │  │(events + │  │(template │            │
│  │          │  │ metrics) │  │+ retry)  │            │
│  └──────────┘  └──────────┘  └───┬──────┘            │
└──────────────────────────────────╪────────────────────┘
                                   │ agent calls
              ┌────────────────────┼───────────────┐
              ▼                    ▼               ▼
          CODER              RESEARCHER         MEMORY
          FIXER                DEVOPS           SECURITY
          DESIGNER           COMMANDER (synth)
```

**Data flow for a single run:**

```
1. Commander selects Playbook by name  →  PlaybookEngine.run_named()
2. Validator loads YAML + Pydantic parse + semantic checks
3. GraphBuilder builds DAG → Wave list (topological sort)
4. TemplateContext initialised with user inputs + prior memory
5. For each Wave:
   a. Observer emits WAVE_STARTED
   b. PlaybookTaskQueue enqueues all ready steps (priority-sorted)
   c. Steps execute concurrently (per-agent concurrency cap)
   d. StepExecutor per step:
        i.   Condition check (skip if false)
        ii.  Template render inputs
        iii. Approval gate (if required)
        iv.  Bus.delegate(agent, tool, rendered_inputs)
        v.   RetryEngine (backoff on failure)
        vi.  Store output in TemplateContext
   e. After each step: CheckpointManager.save_step() if declared
   f. Observer emits WAVE_COMPLETED
6. Synthesize: Commander streams final response to UI
7. Memory.store_interaction() commits outcome
```

---

## Playbook YAML Schema

```yaml
# ── Identity ────────────────────────────────────────────────────────
name:        string           # unique playbook identifier
version:     "1.0.0"
description: string
author:      string
tags:        [string, ...]

# ── Trigger ─────────────────────────────────────────────────────────
trigger:
  type: manual | hotkey | cron | file | event | agent | http
  binding: string             # hotkey / cron expr / glob / event name
  filter:  jinja2_condition   # optional, evaluated against event payload
  debounce_ms: 0

# ── Inputs ──────────────────────────────────────────────────────────
inputs:
  my_param:
    type: string | integer | float | boolean | list | dict | file | secret
    required: true
    default: any
    description: string
    enum: [value, ...]        # allowed values
    pattern: "^[a-z]+$"       # regex for strings
    min: 0                    # numeric bounds
    max: 100

# ── Steps ───────────────────────────────────────────────────────────
steps:
  - id: step_id               # lowercase_snake or kebab-case
    name: "Human readable"
    description: string
    agent: commander | coder | researcher | fixer | devops | security | designer | memory
    tool: agent.tool_name     # e.g. code.generate, memory.query
    inputs:
      key: "{{ inputs.param }}"  # Jinja2 templates
    output_var: VAR_NAME      # store result as {{ vars.VAR_NAME }}
    depends_on: [step_id, ...]
    parallel_with: [step_id, ...]  # hint (resolved from DAG)
    condition: "{{ inputs.flag == true }}"  # skip if false
    on_failure: abort | skip | continue | retry | rollback
    retry:
      max_attempts: 3
      backoff: fixed | linear | exponential | jitter
      delay_sec: 2.0
      max_delay_sec: 60.0
      on: [error, timeout]
      not_on: [approval_denied, permission_error]
    timeout_sec: 60
    priority: 5               # 1–10; higher = first in wave queue
    approval:
      required: true
      message: "Explain what is about to happen"
      timeout_sec: 300

# ── Checkpoints ─────────────────────────────────────────────────────
checkpoints:
  - after: step_id
    scope: outputs | memory | all
    ttl_sec: 86400

# ── Error Handling ──────────────────────────────────────────────────
on_error:
  action: abort | skip | continue | rollback
  notify: true
  rollback: true              # execute rollback_steps

rollback_steps:
  - id: rollback_id
    agent: agent_name
    tool: tool_name
    inputs: {}

# ── Observability ───────────────────────────────────────────────────
observability:
  log_level: debug | info | warning | error
  emit_events: true           # publish to arizen-events pipe → HUD
  metrics: [duration, token_usage, step_count, failure_rate]
  trace_inputs: false         # log step inputs (disable in prod)
  hud_overlay: true

# ── Timeout ─────────────────────────────────────────────────────────
timeout_sec: 3600
```

### Template Variables

```
{{ inputs.PARAM_NAME }}           — user-provided input
{{ steps.STEP_ID.output }}        — output of a completed step
{{ vars.VAR_NAME }}               — stored via output_var
{{ env.HOME }}                    — whitelisted env vars
{{ now() }}                       — ISO 8601 current datetime
{{ uuid() }}                      — fresh UUIDv4
```

---

## Execution Graph

Playbooks are executed as a **directed acyclic graph (DAG)** decomposed
into parallel **Waves**.

```
Example: deploy_application

Step graph:
  pre_flight_check
        │
      run_ci
        │
      build
        │
  validate_build
        │
     deploy
        │
  post_deploy_check
        │
  store_release

Wave decomposition:
  Wave 0: [pre_flight_check]                      — serial (dependency)
  Wave 1: [run_ci]                                — serial
  Wave 2: [build]                                 — serial
  Wave 3: [validate_build]                        — serial
  Wave 4: [deploy]                                — serial (approval-gated)
  Wave 5: [post_deploy_check]                     — serial
  Wave 6: [store_release]                         — serial

Example with parallelism: security_audit

  recall_previous_audits
         │
  ┌──────┼──────────────┐
  │      │              │
code_  dep_          process_
scan   audit          audit
  │      │
  └──────┼──────────────┐
         │              │
    research_cves  (only if findings)
         │
    generate_report
         │
    store_audit

Wave 0: [recall_previous_audits]
Wave 1: [code_scan, dependency_audit, process_audit]    ← parallel
Wave 2: [research_cves]
Wave 3: [generate_report]
Wave 4: [store_audit]
```

### Critical Path Calculation

```python
# Longest chain by estimated timeout — used for ETA display in HUD
critical_path = graph.critical_path   # list of step IDs
estimated_sec = graph.estimated_sec   # sum of timeouts on critical path
```

---

## Retry Engine

```
Strategy      │ Delay formula
──────────────┼────────────────────────────────────────
fixed         │ delay = delay_sec
linear        │ delay = delay_sec × attempt
exponential   │ delay = delay_sec × 2^(attempt-1)
jitter        │ delay = exponential × random(0.5, 1.0)

All strategies cap at max_delay_sec.
```

### Circuit Breaker

Each `(agent, tool)` pair has an independent circuit breaker:
- **Trips** after 5 consecutive failures
- **Open** for 60 seconds (no calls allowed)
- **Resets** on first success after cooldown

---

## Checkpoints

Checkpoints are stored in SQLite at `memory/persistent/checkpoints.db`.

```sql
-- checkpoints table
run_id        TEXT  -- UUID for this execution
playbook_name TEXT  -- playbook name
step_id       TEXT  -- which step was saved
outputs       TEXT  -- JSON of step.output
wave          INT   -- which wave
created_at    REAL  -- Unix timestamp
ttl_sec       INT   -- auto-prune after this window
```

**Resume flow:**
```python
engine.resume(run_id="abc-123")
# → loads checkpoint state
# → replays ctx.step_outputs from saved data
# → skips already-completed steps
# → continues from the first incomplete wave
```

---

## Observability Events

All events are emitted to:
1. **Structured logger** — JSON to file
2. **arizen-events pipe** — consumed by HUD overlay
3. **In-memory list** — queryable via `observer.events_for_step()`

```
Event flow for a healthy run:
  PLAYBOOK_STARTED
    WAVE_STARTED (index=0)
      STEP_STARTED (recall_prior)
      STEP_COMPLETED (recall_prior, 45ms)
    WAVE_COMPLETED (index=0, 0.05s)
    WAVE_STARTED (index=1)
      STEP_STARTED (code_scan) ──┐  parallel
      STEP_STARTED (dep_audit) ──┤
      STEP_STARTED (proc_audit)──┘
      STEP_RETRYING (dep_audit, attempt=2, delay=3s)
      STEP_COMPLETED (code_scan, 8200ms)
      STEP_COMPLETED (dep_audit, 11400ms)
      STEP_COMPLETED (proc_audit, 500ms)
    WAVE_COMPLETED (index=1, 11.4s)
    CHECKPOINT_SAVED (after=code_scan)
    ...
    APPROVAL_REQUESTED (deploy, "Deploy to production?")
    APPROVAL_GRANTED (deploy)
    STEP_STARTED (deploy)
    STEP_COMPLETED (deploy, 45000ms)
  PLAYBOOK_COMPLETED
```

### Metrics (per run)

| Metric | Description |
|---|---|
| `duration_sec` | Wall-clock time from start to complete |
| `total_steps` | Steps declared in playbook |
| `completed_steps` | Steps that succeeded |
| `failed_steps` | Steps that exhausted all retries |
| `skipped_steps` | Steps skipped by condition or on_failure |
| `retried_steps` | Steps that retried at least once |
| `token_usage` | Accumulated LLM tokens across all agents |
| `wave_count` | Number of execution waves |
| `success_rate` | completed / (completed + failed) |
| `approvals_granted` | User-approved steps |
| `checkpoints_saved` | Checkpoint writes |

---

## Task Queue

```
PlaybookTaskQueue
  max_concurrency = 8      ← global limit (all agents combined)
  per_agent_limit = 2      ← per-agent limit (prevents saturation)

Within a wave, steps are sorted by priority (10=highest) before
being dispatched. Higher-priority steps claim agent slots first.

Backpressure:
  If all agent slots are occupied, lower-priority steps wait in the
  heap until a slot opens — no dropping, no unbounded goroutines.
```

---

## Approval Gate

Steps with `approval.required: true` pause execution and send an
`APPROVAL_NEEDED` event to Command Nexus. The UI renders a modal
with the tool name, side-effects summary, and rendered inputs.

```
User sees:
  ┌────────────────────────────────────────────────────┐
  │  ⚠ Action requires your approval                  │
  │                                                    │
  │  Step:   deploy                                    │
  │  Tool:   devops.deploy                             │
  │  Agent:  DevOps                                    │
  │  Action: Deploy daemon to production               │
  │                                                    │
  │  [Approve]                        [Deny]           │
  └────────────────────────────────────────────────────┘
  Timeout: 5 minutes → auto-deny
```

---

## Rollback

If a step's `on_failure: rollback` fires, or `on_error.rollback: true`
is set and the playbook fails, `rollback_steps` execute in order.
Rollback steps are simpler — no retry, no approval, no checkpoints.

```yaml
rollback_steps:
  - id: rollback_service
    agent: devops
    tool: devops.service
    inputs:
      action: restart
      service_name: ArizenDaemon
```

---

## File Structure

```
core/
└── playbook-engine/
    ├── engine.py           ← PRIMARY RUNTIME — PlaybookEngine class ✅
    ├── graph.py            ← DAG builder, wave decomposition, critical path ✅
    ├── executor.py         ← Single-step runner (template + approval + retry) ✅
    ├── queue.py            ← Priority task queue with per-agent concurrency ✅
    ├── checkpoint.py       ← SQLite checkpoint store + resume ✅
    ├── observer.py         ← Structured events + metrics + HUD pipe ✅
    ├── retry.py            ← Backoff strategies + circuit breaker ✅
    └── template.py         ← Jinja2 variable interpolation (sandboxed) ✅

playbooks/
├── schema/
│   ├── playbook_schema.py  ← Full Pydantic v2 schema ✅
│   └── validator.py        ← YAML loader + semantic validation ✅
├── library/
│   ├── create_project.yaml    ✅
│   ├── fix_bug.yaml           ✅
│   ├── build_website.yaml     ✅
│   ├── deploy_application.yaml ✅
│   └── security_audit.yaml    ✅
└── user/                   ← user-authored playbooks (empty)
```

---

## Integration with Commander

Commander selects the playbook to run based on classified intent:

```python
# In CommanderAgent.handle():
intent = await self._classify(query, context)

# Map intent → playbook name
INTENT_TO_PLAYBOOK = {
    TaskType.CODE_GENERATE:    "create_project",
    TaskType.DEBUG_ERROR:      "fix_bug",
    TaskType.SECURITY_SCAN:    "security_audit",
    TaskType.DEVOPS_DEPLOY:    "deploy_application",
    TaskType.DESIGN_COMPONENT: "build_website",
    # ... or dynamic inline playbook for composite tasks
}

playbook_name = INTENT_TO_PLAYBOOK.get(intent)
if playbook_name:
    async for token in self._engine.run_named(playbook_name, inputs=extracted_inputs):
        yield token
else:
    # Commander generates an inline Playbook on the fly for novel tasks
    playbook = await self._synthesize_playbook(query, intent, context)
    async for token in self._engine.run(playbook, inputs=extracted_inputs):
        yield token
```

---

## Adding a New Playbook

1. Create `playbooks/library/my_playbook.yaml` following the schema
2. Run validation: `python -c "from playbooks.schema.validator import PlaybookValidator; print(PlaybookValidator().validate_file('playbooks/library/my_playbook.yaml'))"`
3. Test: `python -c "import asyncio; from core.playbook_engine.engine import PlaybookEngine; ..."`
4. Register in `INTENT_TO_PLAYBOOK` in `CommanderAgent` if it should be auto-selected
5. Playbooks in `playbooks/library/` are immediately available to `engine.run_named()`

---

## Design Principles Applied

| Principle | How the Engine Honours It |
|---|---|
| **Sovereign** | Zero network calls in engine itself; Researcher is the only net-capable agent, opt-in |
| **Transparent** | Every step emits a structured event; full metrics stored; approval gate shows rendered inputs |
| **Composable** | Playbooks are pure YAML; swap any agent without changing engine or other playbooks |
| **Human-in-the-Loop** | `approval.required: true` on any step; auto-deny on timeout; no destructive auto-execution |
| **Resumable** | SQLite checkpoints allow any failed run to continue from last good state |
| **Observable** | Events → HUD in real-time; metrics queryable; critical path drives ETA display |
