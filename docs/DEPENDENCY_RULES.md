# ArizenOS — Dependency Rules

## The Fundamental Rule

> **Lower tiers cannot know about higher tiers.**

```
Tier 0 (core)          ← imports nothing internal
Tier 1 (runtime, services, integrations) ← imports Tier 0 only
Tier 2 (agents, memory, knowledge, skills) ← imports Tier 0 + Tier 1
Tier 3 (apps, voice, playbooks) ← imports Tier 0, 1, 2
Tier 4 (branding, docs, scripts) ← no runtime imports
```

**Cross-tier calls that violate this rule are build-time errors.**
CI enforces this via `scripts/build/check-deps.ps1` which scans imports.

---

## Module-Level Rules

### `core/` (Tier 0)
```
ALLOWED imports:   std, serde, tokio (re-exported types only), thiserror
FORBIDDEN imports: anything in the ArizenOS workspace
```

### `runtime/` (Tier 1)
```
ALLOWED imports:   core/*, std, tokio, tonic, rmp-serde, windows-rs
FORBIDDEN imports: agents/*, memory/*, knowledge/*, skills/*, apps/*
```

### `integrations/` (Tier 1)
```
ALLOWED imports:   core/*, reqwest, windows-rs, serde_json
FORBIDDEN imports: agents/*, memory/*, runtime/* (except core primitives)
```

### `services/` (Tier 1)
```
ALLOWED imports:   core/*, runtime/ipc (event bus publish only), notify, sysinfo
FORBIDDEN imports: agents/*, memory/*, integrations/* (use runtime event bus)
```

### `memory/` (Tier 2 — Python)
```
ALLOWED imports:   core/ (config path only), chromadb, sqlite3, pydantic
FORBIDDEN imports: agents/*, knowledge/*, skills/*
Note: memory/ is consumed BY knowledge/ and agents/, not the reverse
```

### `knowledge/` (Tier 2 — Python)
```
ALLOWED imports:   core/, memory/, integrations/lm-studio (embedding)
FORBIDDEN imports: agents/*, skills/*, playbooks/*
```

### `skills/` (Tier 2 — Python)
```
ALLOWED imports:   core/, integrations/ (via IPC only, no direct Rust import)
FORBIDDEN imports: agents/*, memory/*, knowledge/*
Skills are STATELESS. No memory reads/writes inside a skill.
```

### `agents/` (Tier 2 — Python)
```
ALLOWED imports:   core/, memory/, knowledge/, skills/, integrations/lm-studio
FORBIDDEN cross-agent imports: agents/monarch cannot import agents/archivist directly
Cross-agent calls: MUST go through runtime/ipc bus
```

### `playbooks/` (Tier 3 — Python)
```
ALLOWED imports:   core/, agents/ (via IPC dispatch), skills/
FORBIDDEN imports: apps/*, voice/*
```

### `voice/` (Tier 3 — Python)
```
ALLOWED imports:   core/, agents/monarch (via IPC), memory/session
FORBIDDEN imports: apps/*, knowledge/*
```

### `apps/` (Tier 3 — TypeScript + Rust)
```
ALLOWED imports:   core/ (Rust types), runtime/ipc (client only)
FORBIDDEN imports: agents/*, memory/*, knowledge/*, skills/* (MUST use IPC)
TypeScript side:   zero Python imports — all communication via Tauri invoke + listen
```

---

## The LM Studio-First Rule

Every code path that calls an LLM must route through the following priority:

```python
# Enforced by: integrations/lm-studio/lm_studio.py
# DO NOT call Ollama directly from agent code

llm_backends = [
    "integrations.lm_studio.LMStudioClient",    # PRIMARY
    "integrations.ollama.OllamaClient",          # FALLBACK 1
    "integrations.llamacpp.LlamaCppClient",      # FALLBACK 2
]
```

**Rule:** If you add a new code path that calls an LLM, it MUST use `LLMGateway` from `core/`.
Direct instantiation of any backend client in agent code is a lint error.

---

## The IPC Boundary

```
┌──────────────────────────────────────────────────────────────┐
│  TypeScript (apps/)         │   Python (agents/, etc.)        │
│                             │                                  │
│  tauri::invoke()     ───────┼──► runtime::ipc::PipeServer     │
│  tauri::listen()     ◄──────┼─── runtime::ipc::EventBus      │
│                             │                                  │
│  NO Python imports          │   NO Tauri imports              │
└──────────────────────────────────────────────────────────────┘
```

Any feature that requires TypeScript to call Python logic must:
1. Define a new message type in `core/primitives/message.rs`
2. Add a handler in `runtime/ipc/router.rs`
3. Implement the Python handler as an agent tool or skill

**No exceptions. This is the contract that keeps the UI replaceable.**

---

## Circular Dependency Policy

Circular imports are **build errors**. CI fails if any cycle is detected.

Tools used:
- Rust workspace: `cargo deny` with `bans` config
- Python: `pydeps` scan in CI on every PR to `dev`
- TypeScript: `madge` for circular import detection

---

## External Dependency Policy

Before adding any new external dependency, ask:

1. Is there a std/built-in equivalent?
2. Does this create a cloud or network dependency by default?
3. Is it maintained and does it have a permissive license (MIT/Apache)?
4. Does it work on Windows without MSVC/MinGW compilation issues?

New Rust dependencies: approved in `Cargo.deny.toml`
New Python dependencies: added to `requirements.txt` with pinned version
New Node dependencies: reviewed in `package.json` review checklist
