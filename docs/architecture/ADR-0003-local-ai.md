# ADR-0003 — Local AI Inference Stack

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2025-06-01 |
| **Authors** | Arizen Technologies Steering Committee |
| **Supersedes** | — |

---

## Context

ArizenOS requires a local AI inference engine for Arizen Assistant and Arizen Voice. The engine must:

1. Run entirely on-device — no cloud API calls for the core experience
2. Support the most widely used open-weight model families (Llama, Mistral, Phi, Gemma)
3. Run efficiently on consumer hardware including CPU-only setups
4. Support streaming token generation for real-time assistant responses
5. Expose a JavaScript/TypeScript API usable from an Electron process
6. Support multiple model backends (CUDA, ROCm, OpenCL, CPU)

Evaluated options:

**Option A — OpenAI API (cloud)**
Call the OpenAI API for all inference.

*Rejected:* ArizenOS's core principle is local-first and privacy-by-architecture. Cloud inference is a planned opt-in — it cannot be the default or the only path.

**Option B — llama.cpp via subprocess**
Spawn `llama.cpp` as a child process, communicate over stdin/stdout.

*Problems:* High latency per-call due to process startup. Stateful conversations require keeping the process alive, complicating lifecycle management. JSON serialisation overhead for streaming tokens.

**Option C — llama.cpp via WebAssembly (Wasm)**
Compile `llama.cpp` to WebAssembly, run in Electron's renderer.

*Problems:* WebAssembly cannot access the GPU. Performance is significantly worse than native. Memory limits in the Wasm environment restrict context length. SIMD Wasm support on Windows is inconsistent across Electron versions.

**Option D — llama.cpp via N-API native binding (Chosen)**
Wrap `llama.cpp` with a Node.js N-API native module (`arizen-llama-native`), called directly from the Electron main process without spawning a subprocess.

---

## Decision

We adopt **Option D — llama.cpp via N-API native binding** as the local AI inference stack, implemented in `@arizen/mind`.

### Architecture

```
┌─────────────────────────────────────────────────┐
│           @arizen/mind (TypeScript API)           │
│  MindEngine · Conversation · StreamingResult      │
│  ModelManager · ToolCallingParser · EmbeddingsAPI │
└──────────────────────┬──────────────────────────┘
                       │ N-API
┌──────────────────────▼──────────────────────────┐
│        arizen-llama-native (C++ / N-API)          │
│  llama.cpp · ggml · CUDA/ROCm/Metal/OpenCL       │
└──────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌───────────┐  ┌──────────────┐  ┌──────────┐
│ CUDA      │  │ ROCm (AMD)   │  │ CPU/AVX2 │
│ (NVIDIA)  │  │              │  │          │
└───────────┘  └──────────────┘  └──────────┘
```

### TypeScript API Design

```typescript
// Model management
const engine = await MindEngine.create({ modelPath, gpuLayers: 32 })

// Streaming inference
for await (const token of engine.generate({
  prompt: 'Explain quantum entanglement simply.',
  maxTokens: 512,
  temperature: 0.7,
})) {
  process.stdout.write(token)
}

// Structured tool calling
const result = await engine.generateWithTools({
  messages: conversation.messages,
  tools: [fileReadTool, webSearchTool],
})

// Embeddings (for semantic search)
const vector = await engine.embed('search query')
```

### Model Format

ArizenOS supports **GGUF** — the llama.cpp native format. GGUF supersedes GGML (deprecated) and is the format used by:
- Hugging Face model hub (most popular models)
- LM Studio, Ollama, and other local AI tools
- TheBloke and other community quantizers

Users can download models from Hugging Face directly through Arizen Hub's model browser, or manually drop `.gguf` files into `%LOCALAPPDATA%\ArizenOS\models\`.

### GPU Backend Selection

The native module probes available GPU backends at startup and selects in order of preference:

1. **CUDA** (if NVIDIA GPU + CUDA toolkit detected)
2. **ROCm** (if AMD GPU + ROCm detected)
3. **Vulkan** (if Vulkan-capable GPU, cross-vendor fallback)
4. **OpenCL** (if OpenCL 2.0+ supported)
5. **CPU with AVX2** (all modern x86-64 CPUs)
6. **CPU without SIMD** (last resort fallback)

The selected backend is reported in Hub → AI Models → [Model] → Info.

### Context Management

ArizenOS runs a multi-tenant context manager for conversations:

- **Per-conversation context windows** — each conversation maintains its own KV cache
- **Priority eviction** — when GPU VRAM is constrained, lower-priority conversations lose their cached state
- **Context length capping** — the manager prevents context overflow by evicting oldest messages when approaching the model's maximum context length
- **System prompt pinning** — system prompts are pinned and never evicted

---

## Consequences

**Positive:**
- Full GPU acceleration with automatic backend selection
- Zero subprocess overhead — inference runs in-process
- Native token streaming with microsecond latency per token
- Broad model support via GGUF format
- Works on any modern hardware, including CPU-only

**Negative:**
- N-API native module significantly increases build complexity
- Shipping pre-built binaries for all platform/GPU combinations requires a robust build matrix
- llama.cpp evolves rapidly — the native binding requires periodic updates to track upstream
- Memory safety risks in the C++ layer — must be carefully bounded

**Mitigations:**
- Pre-built binaries are distributed via the installer for all major configurations (CUDA 12, ROCm 6, CPU-AVX2)
- Source builds automatically compile the correct variant for the detected platform
- `@arizen/mind` TypeScript API shields application code from native module complexity
- The C++ layer has a strict boundary — all memory management is isolated within the native module

---

## Review

This decision will be reviewed when `@arizen/mind` reaches v1.0.0. The review should assess:
- Whether to expose an OpenAI-compatible local server endpoint (enabling third-party tool compatibility)
- Whether to support multi-GPU inference for larger models
- Whether Whisper.cpp should share the native binding architecture with llama.cpp
