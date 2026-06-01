# Setting Up LM Studio for ArizenOS

ArizenOS uses LM Studio as its primary LLM and embedding backend.
This guide walks you through the one-time setup.

## 1. Install LM Studio

Download from [lmstudio.ai](https://lmstudio.ai) and run the installer.

Minimum requirements:
- Windows 10 (64-bit)
- 8 GB RAM (16 GB recommended)
- 10 GB free disk space for models

## 2. Download Recommended Models

ArizenOS uses a tiered model strategy. Download at least one model per tier you intend to use.

### Tier 1 — Nano (fast, 1-3B)
- `lmstudio-community/Phi-3-mini-4k-instruct-GGUF` → `Phi-3-mini-4k-instruct-Q4_K_M.gguf`

### Tier 2 — Standard (balanced, 7-14B)
- `lmstudio-community/Phi-3-medium-4k-instruct-GGUF` → `Phi-3-medium-4k-instruct-Q4_K_M.gguf`
- `lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF`

### Tier 3 — Power (high quality, 30-70B, GPU recommended)
- `lmstudio-community/Meta-Llama-3-70B-Instruct-GGUF` (GPU required, 8+ GB VRAM)

### Embedding Model (required for Knowledge Vault)
- `nomic-ai/nomic-embed-text-v1.5-GGUF`

## 3. Start the LM Studio Server

1. Open LM Studio
2. Click **Local Server** in the left sidebar
3. Select your Tier 2 model (or Tier 1 on low-RAM machines)
4. Click **Start Server**
5. Verify: server should show `localhost:1234`

## 4. Load the Embedding Model

1. In the Local Server panel, find **Embeddings Model**
2. Select `nomic-embed-text-v1.5`
3. The embedding endpoint activates automatically: `localhost:1234/v1/embeddings`

## 5. Configure ArizenOS

Edit `%LOCALAPPDATA%\ArizenOS\config.toml`:

```toml
[llm]
primary_backend   = "lm-studio"
lm_studio_url     = "http://localhost:1234"
embedding_model   = "nomic-ai/nomic-embed-text-v1.5-GGUF"

[llm.tier_map]
nano     = "phi3:mini"           # matches model name in LM Studio
standard = "phi3:medium"
power    = "llama3:70b"

[llm.fallback]
enabled  = true
backends = ["ollama", "llamacpp"]
```

## 6. Verify

```powershell
arizen doctor lm-studio
# Expected:
# ✅ LM Studio reachable at localhost:1234
# ✅ Chat completions: OK (phi3:medium, 847ms)
# ✅ Embeddings: OK (nomic-embed, 23ms)
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Connection refused | Ensure LM Studio Server is running |
| Slow responses | Reduce context length in LM Studio settings |
| Out of memory | Use a smaller model (Tier 1) or enable model offloading |
| Embeddings fail | Load embedding model separately in Server panel |
