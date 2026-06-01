# Building Extensions (Agent Tools)

Arizen Agent can be extended with custom tools using `@arizen/agent-sdk`. An extension declares a tool — its name, description, parameter schema, and handler — and registers it with the Agent runtime.

---

## Overview

When a user gives the Agent a task, ArizenOS:
1. Sends the task + available tools to the local LLM
2. The LLM decides which tools to call, in what order, with what arguments
3. The Agent executes those tool calls in a sandboxed environment
4. Results are returned to the LLM to continue planning
5. The final result is presented to the user

Your extension adds entries to step 2: new tools the LLM can choose to call.

---

## Quickstart

### 1. Create an Extension Package

```bash
# From the ArizenOS monorepo root
node tools/scaffold/extension.mjs my-extension-name
```

This creates:
```
packages/ext-my-extension-name/
├── src/
│   ├── index.ts          # Extension entry point
│   └── tools/
│       └── my-tool.ts    # Example tool
├── package.json
├── tsconfig.json
└── README.md
```

### 2. Define a Tool

```typescript
// src/tools/weather.ts
import { defineTool } from '@arizen/agent-sdk'
import { z } from 'zod'

export const weatherTool = defineTool({
  name: 'get_weather',
  description: 'Get the current weather for a city. Use this when the user asks about weather conditions.',
  parameters: z.object({
    city: z.string().describe('The city name, e.g. "Tokyo"'),
    units: z.enum(['celsius', 'fahrenheit']).default('celsius'),
  }),
  permissions: [],  // This tool makes no OS calls — only an HTTP request
  async execute({ city, units }) {
    const response = await fetch(`https://wttr.in/${city}?format=j1`)
    const data = await response.json()
    const temp = data.current_condition[0]
    return {
      type: 'text',
      content: `Current weather in ${city}: ${temp.temp_C}°C, ${temp.weatherDesc[0].value}`,
    }
  },
})
```

### 3. Register the Extension

```typescript
// src/index.ts
import { createExtension } from '@arizen/agent-sdk'
import { weatherTool } from './tools/weather'

export default createExtension({
  id: 'com.yourname.weather',
  name: 'Weather Tool',
  version: '1.0.0',
  author: 'Your Name',
  description: 'Adds weather lookup capability to Arizen Agent',
  tools: [weatherTool],
})
```

### 4. Test Your Extension

```bash
pnpm --filter @arizen/agent-sdk test:extension packages/ext-my-extension-name
```

### 5. Load in Development

```bash
pnpm --filter @arizen/hub dev

# In Hub → Extensions → Developer → Load Unpacked → select your extension directory
```

---

## Tool Definition API

### `defineTool(config)`

```typescript
interface ToolConfig<TParams extends ZodSchema> {
  /** Internal name — snake_case, globally unique. Used by the LLM to call the tool. */
  name: string

  /**
   * Natural language description of what the tool does and when to use it.
   * Write this for an LLM reader, not a human. Be specific about when to use vs not use.
   */
  description: string

  /** Zod schema defining the tool's parameters. Each field should have a .describe() */
  parameters: TParams

  /**
   * OS-level permissions this tool requires.
   * Declared permissions are shown to the user before the extension is enabled.
   */
  permissions: Permission[]

  /**
   * The tool's execute function. Receives parsed, validated parameters.
   * Must return a ToolResult.
   */
  execute: (params: z.infer<TParams>, context: ToolContext) => Promise<ToolResult>
}
```

### Permissions

Declare the OS permissions your tool requires:

```typescript
import { Permission } from '@arizen/agent-sdk'

permissions: [
  Permission.FileSystemRead('/Users/you/Documents'),   // Scoped to a path
  Permission.FileSystemWrite('/Users/you/Downloads'),
  Permission.ShellRun,                                  // Unscoped — careful
  Permission.BrowserNavigate,
  Permission.ClipboardRead,
  Permission.ClipboardWrite,
]
```

Undeclared permissions will be denied at runtime. Users see declared permissions before enabling an extension.

### Tool Results

```typescript
// Text result
return { type: 'text', content: 'Operation completed successfully.' }

// Markdown result (rendered in the Assistant panel)
return { type: 'markdown', content: '**Done.** Created 5 files.' }

// Data result (structured, LLM can reason over it)
return { type: 'data', data: { filesCreated: 5, totalSize: '12.3 MB' } }

// File result (presented as a downloadable file in the UI)
return { type: 'file', path: '/path/to/output.csv', mimeType: 'text/csv' }

// Error result
return { type: 'error', message: 'File not found', code: 'ENOENT' }
```

---

## Tool Context

The `context` argument passed to `execute` provides:

```typescript
interface ToolContext {
  /** Scoped logger for this tool invocation */
  log: Logger

  /** User's active conversation (read-only) */
  conversation: {
    id: string
    messages: Message[]
    activeModel: string
  }

  /** Desktop context at the time of invocation */
  desktop: {
    activeWindowTitle: string
    activeWindowProcess: string
    clipboardText: string | null
  }

  /** Abort signal — cancelled if user clicks Stop */
  signal: AbortSignal

  /** Request user confirmation for a sensitive action */
  confirm: (message: string) => Promise<boolean>

  /** Report incremental progress */
  reportProgress: (message: string, percent?: number) => void
}
```

### Using `confirm` for Sensitive Actions

For destructive or irreversible actions, call `context.confirm()` — this pauses execution and presents a confirmation dialog to the user:

```typescript
const approved = await context.confirm(
  `Delete ${filesToDelete.length} files? This cannot be undone.`
)
if (!approved) {
  return { type: 'text', content: 'Operation cancelled by user.' }
}
```

---

## Packaging & Publishing

### Package for Distribution

```bash
pnpm --filter ext-my-extension-name build
node tools/pack-extension.mjs packages/ext-my-extension-name
# Output: releases/extensions/my-extension-1.0.0.arizen-ext
```

### Publish to Hub

```bash
arizen publish-extension releases/extensions/my-extension-1.0.0.arizen-ext
```

Publishing requires an [Arizen Developer account](https://hub.arizenos.dev/developer) and a one-time code signing step. Extensions are reviewed for security compliance before appearing in the community Hub.

### Self-Distribution

You can distribute `.arizen-ext` files directly. Users install via:
**Hub → Extensions → Install from file**

---

## Best Practices

**Write for the LLM.** The `description` field is read by a language model at inference time. Write it precisely: what the tool does, what parameters it expects, and crucially — when *not* to use it. Bad descriptions cause the LLM to call your tool at wrong times.

**Be narrow with permissions.** Request the minimum scope needed. Scoped file system permissions (`FileSystemRead('/specific/path')`) are always preferred over unscoped access.

**Handle errors gracefully.** Return `{ type: 'error', ... }` rather than throwing. Thrown errors crash the tool execution and give the LLM no useful signal.

**Use `reportProgress` for long operations.** Users see progress in the Execution View. Update it every meaningful step.

**Respect the abort signal.** Check `context.signal.aborted` in long loops and return early if the user cancelled.
