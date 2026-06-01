# @arizen/core

**Stability:** Stable | **Version:** See [releases](https://github.com/Alrizz-art/ArizenOS/releases)

The foundation package. Every other `@arizen/*` package depends on it. Zero external dependencies.

```bash
# Already included as a peer dependency in all @arizen/* packages
# Direct installation (for extension authors):
pnpm add @arizen/core
```

---

## Logger

Structured logger with log-level filtering, caller attribution, and automatic rotation.

```typescript
import { createLogger } from '@arizen/core'

const log = createLogger('my-module')

log.debug('Detailed trace', { payload })      // Only in development
log.info('Operation completed', { duration }) // Standard informational
log.warn('Approaching limit', { usage })      // Non-critical issues
log.error('Operation failed', { error })      // Errors requiring attention
log.fatal('Unrecoverable failure', { error }) // Process will exit
```

### Configuration

```typescript
import { configureLogger } from '@arizen/core'

configureLogger({
  level: 'info',           // 'debug' | 'info' | 'warn' | 'error' | 'fatal'
  output: 'file',          // 'console' | 'file' | 'both'
  filePath: '%LOCALAPPDATA%/ArizenOS/logs/app.log',
  maxFileSizeMB: 50,
  maxFiles: 5,
  format: 'json',          // 'json' | 'pretty'
})
```

### Types

```typescript
interface Logger {
  debug(message: string, context?: Record<string, unknown>): void
  info(message: string, context?: Record<string, unknown>): void
  warn(message: string, context?: Record<string, unknown>): void
  error(message: string, context?: Record<string, unknown>): void
  fatal(message: string, context?: Record<string, unknown>): void
  child(namespace: string): Logger
}

function createLogger(namespace: string, options?: LoggerOptions): Logger
```

---

## EventBus

Typed publish/subscribe event bus. Used for cross-component communication within a process.

```typescript
import { createEventBus } from '@arizen/core'

// Define event types
interface AppEvents {
  'theme:changed':  { themeId: string; tokens: ThemeTokens }
  'model:loaded':   { modelId: string; vram: number }
  'model:unloaded': { modelId: string }
  'agent:task:started': { taskId: string; instruction: string }
  'agent:task:completed': { taskId: string; result: TaskResult }
}

const bus = createEventBus<AppEvents>()

// Subscribe
const unsubscribe = bus.on('theme:changed', ({ themeId, tokens }) => {
  applyTheme(tokens)
})

// Subscribe once
bus.once('model:loaded', ({ modelId }) => {
  console.log(`Model ${modelId} is ready`)
})

// Publish
bus.emit('theme:changed', { themeId: 'void', tokens: currentTokens })

// Unsubscribe
unsubscribe()

// Remove all listeners for an event
bus.off('theme:changed')
```

### Types

```typescript
interface EventBus<TEvents extends Record<string, unknown>> {
  on<K extends keyof TEvents>(event: K, handler: (payload: TEvents[K]) => void): () => void
  once<K extends keyof TEvents>(event: K, handler: (payload: TEvents[K]) => void): void
  off<K extends keyof TEvents>(event: K, handler?: (payload: TEvents[K]) => void): void
  emit<K extends keyof TEvents>(event: K, payload: TEvents[K]): void
}

function createEventBus<TEvents extends Record<string, unknown>>(): EventBus<TEvents>
```

---

## IPC

Type-safe Electron IPC wrapper. Used by apps to communicate between the main process and renderer(s).

```typescript
// In main process
import { createIpcMain } from '@arizen/core/ipc'

const ipc = createIpcMain()

ipc.handle('assistant:generate', async ({ prompt, modelId }) => {
  return await mindEngine.generate({ prompt, modelId })
})

ipc.handle('theme:set', async ({ themeId }) => {
  await skinEngine.applyTheme(themeId)
  return { success: true }
})
```

```typescript
// In renderer process
import { createIpcRenderer } from '@arizen/core/ipc'

const ipc = createIpcRenderer()

// Type-safe invocation
const response = await ipc.invoke('assistant:generate', {
  prompt: 'Hello, world',
  modelId: 'llama-3-8b',
})

// Typed streaming
for await (const token of ipc.stream('assistant:generate:stream', { prompt })) {
  appendToken(token)
}
```

---

## Config

Hierarchical configuration system. Loads from defaults → machine config → user config, with the later layers overriding earlier ones.

```typescript
import { Config } from '@arizen/core'

const config = Config.load({
  schema: z.object({
    mind: z.object({
      defaultModel: z.string().default('phi-3-mini-q4'),
      gpuLayers: z.number().min(0).default(32),
      contextLength: z.number().default(4096),
    }),
    glass: z.object({
      quality: z.enum(['off', 'low', 'medium', 'high', 'ultra']).default('high'),
      blurRadius: z.number().min(4).max(32).default(16),
    }),
  }),
  paths: {
    defaults: 'built-in',
    machine: `${process.env.PROGRAMDATA}/ArizenOS/config.toml`,
    user: `${process.env.LOCALAPPDATA}/ArizenOS/config.toml`,
  },
})

// Access values (type-safe)
const model = config.get('mind.defaultModel')  // string
const quality = config.get('glass.quality')     // 'off' | 'low' | 'medium' | 'high' | 'ultra'

// Watch for changes
config.watch('glass.quality', (newValue) => {
  glassEngine.setQuality(newValue)
})

// Update user config
await config.set('mind.defaultModel', 'llama-3-8b-q4')
```

---

## Error Types

```typescript
import {
  ArizenError,      // Base class for all ArizenOS errors
  ConfigError,      // Configuration loading/validation errors
  IpcError,         // IPC communication errors
} from '@arizen/core'

// All ArizenOS errors extend ArizenError
class ArizenError extends Error {
  readonly code: string
  readonly context: Record<string, unknown>
  constructor(message: string, code: string, context?: Record<string, unknown>)
}
```

---

## Utilities

```typescript
import {
  sleep,          // sleep(ms: number): Promise<void>
  retry,          // retry<T>(fn, { attempts, delay, backoff }): Promise<T>
  debounce,       // debounce<T>(fn, ms): T
  throttle,       // throttle<T>(fn, ms): T
  deepMerge,      // deepMerge<T>(target, source): T
  generateId,     // generateId(): string (ULID)
  assert,         // assert(condition, message): asserts condition
  invariant,      // invariant(condition, message): asserts condition (dev-only)
} from '@arizen/core/utils'
```
