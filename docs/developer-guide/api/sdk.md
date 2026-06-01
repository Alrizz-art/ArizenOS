# @arizen/sdk

**Stability:** Beta (public API — SemVer strict) | The public extension API for Arizen Agent

```bash
pnpm add @arizen/sdk
```

`@arizen/sdk` is the only `@arizen/*` package intended for third-party developers. It provides everything you need to build custom tools for Arizen Agent and publish them to Arizen Hub.

For a full walkthrough, see [Building Extensions](../guides/developer/building-extensions.md).

---

## `defineTool(config)`

Define a single Agent tool.

```typescript
import { defineTool } from '@arizen/sdk'
import { z } from 'zod'

export const myTool = defineTool({
  name: 'tool_name',              // snake_case, globally unique
  description: '...',             // Written for an LLM reader
  parameters: z.object({ ... }), // Zod schema
  permissions: [],                // Required OS permissions
  execute: async (params, context) => { ... },
})
```

### Config Reference

```typescript
interface ToolConfig<TParams extends ZodSchema> {
  /**
   * Unique tool name in snake_case.
   * This is what the LLM uses to invoke your tool.
   * Use a namespaced prefix to avoid conflicts: 'yourname_tool_name'
   */
  name: string

  /**
   * LLM-facing description of the tool.
   * Be specific: what it does, what it returns, and when NOT to use it.
   * Good descriptions significantly improve tool selection accuracy.
   */
  description: string

  /**
   * Zod schema for the tool's parameters.
   * Each field should have a .describe() for LLM context.
   * Keep parameters minimal — LLMs make fewer mistakes with simple schemas.
   */
  parameters: TParams

  /**
   * OS permissions this tool requires.
   * These are displayed to the user before the extension is enabled.
   * Undeclared permissions are denied at runtime.
   */
  permissions: Permission[]

  /**
   * The tool's execute function.
   * Receives validated parameters and a ToolContext.
   * Must return a ToolResult. Do not throw — return { type: 'error' } instead.
   */
  execute: (
    params: z.infer<TParams>,
    context: ToolContext
  ) => Promise<ToolResult>
}
```

---

## `createExtension(config)`

Package one or more tools into a distributable extension.

```typescript
import { createExtension } from '@arizen/sdk'
import { myTool, anotherTool } from './tools'

export default createExtension({
  id: 'com.yourname.extension-name',   // Reverse-DNS identifier
  name: 'Human-readable name',
  version: '1.0.0',
  author: 'Your Name',
  description: 'What this extension adds to Arizen Agent.',
  homepage: 'https://github.com/you/arizen-ext-name',
  tools: [myTool, anotherTool],
  onInstall: async () => { /* optional setup */ },
  onUninstall: async () => { /* optional cleanup */ },
})
```

---

## Permission API

```typescript
import { Permission } from '@arizen/sdk'

// File system — always scope to specific paths where possible
Permission.FileSystemRead('/Users/you/Documents')    // Read-only, scoped
Permission.FileSystemWrite('/Users/you/Downloads')   // Write, scoped
Permission.FileSystemReadAll                         // Read-only, entire FS (shown with warning)
Permission.FileSystemWriteAll                        // Write, entire FS (shown with warning)

// Shell
Permission.ShellRun                                  // Execute PowerShell/CMD

// Browser
Permission.BrowserNavigate                           // Open URLs
Permission.BrowserRead                               // Read page content
Permission.BrowserInteract                           // Click, fill forms

// System
Permission.ClipboardRead
Permission.ClipboardWrite
Permission.CalendarRead
Permission.CalendarWrite
Permission.NotificationsRead                         // Read system notifications
Permission.ApplicationLaunch                         // Launch applications

// Network (for tools that make HTTP calls)
// Note: network access from tool execute() is allowed by default.
// These permissions only affect the *widget* runtime, not tools.
```

---

## ToolContext

The `context` argument passed to every `execute()` call.

```typescript
interface ToolContext {
  /** Scoped logger — logs appear in Hub → Agent → Activity Log */
  log: Logger

  /** Current conversation at the time of invocation */
  conversation: {
    id: string
    messages: ReadonlyArray<ChatMessage>
    activeModelId: string
  }

  /** Desktop state at the time of invocation */
  desktop: {
    activeWindowTitle: string
    activeWindowProcess: string
    clipboardText: string | null
    focusedFilePaths: string[]
  }

  /**
   * AbortSignal — aborted when the user clicks Stop in the Execution View.
   * Check signal.aborted in long-running loops and return early.
   */
  signal: AbortSignal

  /**
   * Request user confirmation before a sensitive or destructive action.
   * Pauses execution and shows a modal to the user.
   * Returns true if approved, false if cancelled.
   */
  confirm: (message: string, detail?: string) => Promise<boolean>

  /**
   * Report progress to the Execution View.
   * @param message - Human-readable step description
   * @param percent - Optional progress 0–100
   */
  reportProgress: (message: string, percent?: number) => void

  /**
   * Access the local AI for reasoning within a tool.
   * Useful for classification, extraction, or planning sub-steps.
   */
  mind: {
    generate: (prompt: string, options?: GenerateOptions) => Promise<string>
  }
}
```

---

## ToolResult Types

```typescript
type ToolResult =
  | TextResult
  | MarkdownResult
  | DataResult
  | FileResult
  | ErrorResult

interface TextResult {
  type: 'text'
  content: string    // Plain text — shown in conversation and passed to LLM
}

interface MarkdownResult {
  type: 'markdown'
  content: string    // Rendered in the Assistant panel, passed as text to LLM
}

interface DataResult {
  type: 'data'
  data: unknown      // Serialisable. LLM sees JSON representation.
  summary?: string   // Optional human-readable summary shown in the UI
}

interface FileResult {
  type: 'file'
  path: string       // Absolute path to the output file
  mimeType: string
  label?: string     // Display label in the UI
}

interface ErrorResult {
  type: 'error'
  message: string    // Human-readable error description
  code?: string      // Machine-readable error code
  recoverable?: boolean  // Whether the Agent should retry
}
```

---

## Testing Your Extension

```typescript
import { createTestContext, runTool } from '@arizen/sdk/testing'
import { myTool } from './tools/my-tool'

describe('myTool', () => {
  it('returns expected result', async () => {
    const context = createTestContext({
      desktop: { activeWindowTitle: 'Test', activeWindowProcess: 'test.exe', clipboardText: null, focusedFilePaths: [] },
    })

    const result = await runTool(myTool, { myParam: 'value' }, context)

    expect(result.type).toBe('text')
    expect((result as TextResult).content).toContain('expected output')
  })

  it('respects abort signal', async () => {
    const context = createTestContext()
    const controller = new AbortController()
    context.signal = controller.signal

    const promise = runTool(myTool, { myParam: 'value' }, context)
    controller.abort()

    const result = await promise
    expect(result.type).toBe('error')
  })
})
```

---

## Changelog

See the [sdk CHANGELOG](https://github.com/Alrizz-art/ArizenOS/blob/main/packages/sdk/CHANGELOG.md) for version history.
