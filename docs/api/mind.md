# @arizen/mind

**Stability:** Beta | Local AI inference via llama.cpp N-API binding

```bash
pnpm add @arizen/mind
```

`@arizen/mind` provides a TypeScript API for local LLM inference, model management, embeddings, and structured tool calling. It wraps `llama.cpp` via an N-API native module for zero-subprocess, GPU-accelerated inference.

---

## MindEngine

The primary class. Manages model lifecycle and exposes inference APIs.

### `MindEngine.create(config)`

```typescript
import { MindEngine } from '@arizen/mind'

const engine = await MindEngine.create({
  modelPath: 'C:/Users/you/.arizen/models/llama-3-8b-instruct-q4_k_m.gguf',
  contextLength: 4096,           // Maximum context tokens (model-dependent)
  gpuLayers: 32,                 // Layers offloaded to GPU. 0 = CPU-only. -1 = all.
  threads: 8,                    // CPU threads (used even with GPU for non-offloaded layers)
  batchSize: 512,                // Tokens per batch for prompt evaluation
  memoryMapMode: true,           // Memory-map model file (reduces RAM usage)
})
```

### `engine.generate(config)`

Generate text. Returns an async iterator of string tokens.

```typescript
// Streaming (recommended)
for await (const token of engine.generate({
  prompt: 'Explain quantum entanglement in simple terms.',
  maxTokens: 512,
  temperature: 0.7,         // 0.0 = deterministic, 1.0 = creative, >1.0 = chaotic
  topP: 0.9,                // Nucleus sampling threshold
  topK: 40,                 // Top-K sampling
  repeatPenalty: 1.1,       // Penalise token repetition
  stop: ['\n\n', '```'],   // Stop sequences (stops generation when any is encountered)
})) {
  process.stdout.write(token)
}

// Collect full response
const response = await engine.generateText({
  prompt: 'Summarise this: ' + document,
  maxTokens: 256,
})
```

### `engine.chat(config)`

Chat-format inference with message history.

```typescript
const response = engine.chat({
  messages: [
    { role: 'system',    content: 'You are a helpful assistant.' },
    { role: 'user',      content: 'What is the capital of France?' },
    { role: 'assistant', content: 'Paris.' },
    { role: 'user',      content: 'And its population?' },
  ],
  maxTokens: 128,
  temperature: 0.5,
})

// Streaming
for await (const token of response) {
  process.stdout.write(token)
}
```

### `engine.generateWithTools(config)`

Structured inference with function/tool calling. The model outputs structured JSON to invoke one or more tools.

```typescript
import { defineTool } from '@arizen/agent-sdk'
import { z } from 'zod'

const searchTool = defineTool({
  name: 'web_search',
  description: 'Search the web for information',
  parameters: z.object({ query: z.string() }),
  permissions: [],
  execute: async ({ query }) => ({ type: 'text', content: await search(query) }),
})

const result = await engine.generateWithTools({
  messages: conversation.messages,
  tools: [searchTool],
  toolChoice: 'auto',       // 'auto' | 'none' | { name: 'tool_name' }
  maxToolRounds: 5,         // Maximum tool call iterations
})

console.log(result.content)     // Final text response
console.log(result.toolCalls)   // Array of { tool, args, result }
```

### `engine.embed(text)`

Generate a vector embedding for semantic search.

```typescript
const vector = await engine.embed('How do I configure GPU layers?')
// Returns: Float32Array of length model.embeddingDimension
```

### `engine.tokenize(text)` / `engine.detokenize(tokens)`

```typescript
const tokens = await engine.tokenize('Hello, world!')
// Returns: number[]  e.g. [9906, 29892, 1724, 29991]

const text = await engine.detokenize(tokens)
// Returns: 'Hello, world!'
```

### `engine.countTokens(text)`

Count tokens without inference — useful for context management.

```typescript
const count = await engine.countTokens(longDocument)
if (count > engine.contextLength - 512) {
  // Truncate or summarise
}
```

### `engine.dispose()`

Release GPU memory and native resources. Always call when done.

```typescript
await engine.dispose()
```

---

## ModelManager

Manages the lifecycle of multiple loaded models.

```typescript
import { ModelManager } from '@arizen/mind'

const manager = ModelManager.getInstance()

// Load a model
const engine = await manager.load({
  id: 'llama-3-8b',
  path: 'C:/Users/you/.arizen/models/llama-3-8b-instruct-q4_k_m.gguf',
  gpuLayers: 32,
  priority: 'high',       // 'high' | 'normal' | 'low' — affects VRAM eviction order
})

// Get a loaded model
const engine = manager.get('llama-3-8b')

// List all loaded models
const models = manager.list()
// Returns: Array<{ id, path, state: 'loading' | 'ready' | 'evicted', vramUsageMB }>

// Unload a model (free VRAM)
await manager.unload('llama-3-8b')

// Memory usage
const usage = manager.getMemoryUsage()
// Returns: { totalVramMB, usedVramMB, models: { id, vramMB }[] }
```

---

## Types

```typescript
interface GenerateConfig {
  prompt: string
  maxTokens?: number          // default: 512
  temperature?: number        // default: 0.7
  topP?: number               // default: 0.9
  topK?: number               // default: 40
  repeatPenalty?: number      // default: 1.1
  stop?: string[]             // default: []
  signal?: AbortSignal        // Cancel generation
}

interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  toolCallId?: string         // For 'tool' role messages
}

interface MindEngineConfig {
  modelPath: string
  contextLength?: number      // default: model max
  gpuLayers?: number          // default: 32
  threads?: number            // default: half logical CPUs
  batchSize?: number          // default: 512
  memoryMapMode?: boolean     // default: true
}

// Errors
class MindError extends ArizenError {}
// error.code: 'MODEL_NOT_FOUND' | 'MODEL_LOAD_FAILED' | 'INSUFFICIENT_VRAM' |
//             'CONTEXT_OVERFLOW' | 'INFERENCE_FAILED' | 'TOKENIZATION_FAILED'
```

---

## Events

```typescript
engine.on('token', (token: string) => {})
engine.on('generation:start', (config: GenerateConfig) => {})
engine.on('generation:end', (stats: GenerationStats) => {})
engine.on('error', (error: MindError) => {})

// GenerationStats
interface GenerationStats {
  promptTokens: number
  generatedTokens: number
  tokensPerSecond: number
  durationMs: number
}
```
