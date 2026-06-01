# Arizen Agent

> `@arizen/agent` — Autonomous OS-level task execution.

The Agent can take actions across your desktop using structured tool calls: open apps, read and write files, browse the web, run shell commands, and interact with system APIs. Powered by ArizenMind's local inference with an explicit permission model.

## Responsibilities

- LLM-based task planner (chain-of-thought, local)
- Tool execution engine (filesystem, browser, shell, clipboard, calendar)
- Working memory and task state management
- Explicit permission model — every tool requires user grant
- Execution trace viewer and audit log

## Tech Stack

| Layer | Technology |
|---|---|
| Planner | `@arizen/mind` (function-calling capable model) |
| Plugin API | `@arizen/agent-sdk` |
| Runtime | Node.js service + Electron control panel |
| OS bindings | `@arizen/shell` |
| State | SQLite (task history + memory) |

## Development

```bash
pnpm --filter @arizen/agent dev
pnpm --filter @arizen/agent test
pnpm --filter @arizen/agent build
```

## Security Model

Every tool the Agent can invoke requires an explicit one-time or persistent permission grant from the user. No action is taken silently. All executions are logged to an immutable audit trail stored locally. See [`/SECURITY.md`](../../SECURITY.md).

## Module Owner

See [`/MAINTAINERS.md`](../../MAINTAINERS.md)
