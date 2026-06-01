# ArizenOS — Core Principles

These principles are non-negotiable. Every design decision, every line of code, every feature must be evaluated against them.

---

## 1. Sovereignty First

> *Your data stays on your machine. Always.*

- No telemetry, analytics, or usage reporting — ever
- No cloud dependencies in the default configuration
- All LLM inference runs locally by default
- Network access is opt-in and fully auditable
- Every file the system reads or writes is declared in the audit log

**Corollary:** Features that require cloud connectivity are gated behind explicit user consent and are never enabled by default.

---

## 2. Composable by Design

> *Every component must be independently replaceable.*

- The daemon does not care which agents are running
- Agents do not care which LLM backend is in use
- The UI does not care about agent internals
- Workflows are YAML — no code required to compose them
- The plugin SDK allows third-party components at every layer

**Corollary:** A user should be able to swap Ollama for llama.cpp, or swap the Command Nexus for a custom terminal UI, without touching any other component.

---

## 3. Transparent by Default

> *The system must never be a black box.*

- Every agent decision is logged with full reasoning trace
- Workflow execution is step-by-step auditable
- LLM prompts and responses are stored (opt-out available)
- Resource usage (CPU, GPU, RAM) is always visible in the HUD
- No "magic" — every automation is traceable to its trigger

**Corollary:** Power users must be able to inspect, replay, and debug any system action.

---

## 4. Performance Without Compromise

> *Intelligence must not come at the cost of responsiveness.*

- Command Nexus launches in under 100ms
- Agent responses for Tier 1 tasks under 500ms
- Daemon memory footprint under 50 MB baseline
- Workflow triggers respond within 100ms of the triggering event
- LLM inference never blocks the UI thread

**Corollary:** Performance budgets are defined per component and enforced in CI.

---

## 5. AME-Native, Not AME-Exclusive

> *Built for privacy-first Windows. Compatible with standard Windows.*

- Primary target: Windows 10 AME 22H2
- All features must work without Microsoft Store, Cortana, or Windows Search
- PowerShell 7 is the scripting runtime (no legacy PS5 required)
- No dependency on .NET Framework (only .NET 8+ or native Rust/C)
- Optional: degraded compatibility mode for standard Windows 10/11

---

## 6. Agent Sovereignty

> *Agents are citizens, not servants.*

- Each agent runs as an isolated process with declared capabilities
- Agents communicate through declared channels, not shared memory
- No agent has filesystem access outside its sandboxed directory by default
- Agents must request permission escalation through the daemon
- Agents can be paused, replaced, or removed without system restart

---

## 7. Human-in-the-Loop by Default

> *Automation must not act without acknowledgment on critical tasks.*

- Destructive actions (file deletion, system changes, network calls) require explicit user approval
- Approval can be delegated to a rule ("auto-approve file moves within /Projects")
- All automated actions show in the HUD with a configurable undo window
- Emergency stop: single hotkey pauses all agent activity

---

## 8. Open and Buildable

> *ArizenOS must be fully buildable from source on a clean AME install.*

- Zero proprietary dependencies in the core
- All third-party dependencies are pinned and vendored
- Complete build in under 15 minutes on recommended hardware
- Plugin SDK is fully documented and versioned
- The project ships with a contributor-grade dev environment script
