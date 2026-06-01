# System Requirements

ArizenOS integrates deeply with the Windows graphics stack and system APIs. Before installing, verify your system meets the following requirements.

---

## Minimum Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10 Build 19041 (20H1) | Windows 11 23H2 |
| **CPU** | Intel Core i5 8th gen / AMD Ryzen 5 3600 | Intel Core i7 12th gen+ / AMD Ryzen 7 5800X+ |
| **RAM** | 8 GB | 16 GB (32 GB for heavy local AI use) |
| **Storage** | 2 GB (ArizenOS only) | 10+ GB (with local AI models) |
| **GPU** | DirectX 11-capable GPU | DirectX 12 GPU with 4 GB VRAM |
| **Display** | 1080p | 1440p or 4K |

> **Note:** The minimum requirements cover the core shell (Launcher, Hub). Running **local AI inference** via Arizen Assistant or Arizen Voice requires additional resources — see the AI section below.

---

## Windows Version Details

| Windows Version | Status | Notes |
|---|---|---|
| Windows 11 24H2 | ✅ Fully supported | Best experience — native WinUI3 + DWM APIs |
| Windows 11 23H2 | ✅ Fully supported | |
| Windows 11 22H2 | ✅ Supported | |
| Windows 10 22H2 | ✅ Supported | Some glass effects use fallback rendering |
| Windows 10 21H2 | ✅ Supported | |
| Windows 10 Build 19041 | ⚠️ Minimum | Limited glass compositing support |
| Windows 10 below 19041 | ❌ Not supported | Missing required DWM APIs |
| Windows 8.1 / 7 | ❌ Not supported | |
| Windows Server | ❌ Not tested | |

---

## GPU Requirements

The glass rendering engine (`@arizen/glass`) uses DirectComposition and Direct2D for GPU-accelerated blur and depth effects.

| GPU Tier | Effect Quality | Recommendation |
|---|---|---|
| No dedicated GPU (Intel UHD / Iris) | Reduced — blur at 50% resolution | Works, but effects are softer |
| Dedicated GPU, DirectX 11, < 2 GB VRAM | Standard glass effects | Acceptable for most use cases |
| Dedicated GPU, DirectX 12, 4–8 GB VRAM | Full glass + depth + real-time blur | Recommended |
| High-end GPU, DirectX 12, 8+ GB VRAM | Full effects + GPU-accelerated AI layers | Optimal for Arizen Assistant with local AI |

**Effect quality** can be manually adjusted in Hub → Settings → Display → Glass Quality.

---

## Local AI Requirements (Arizen Assistant & Voice)

Arizen Assistant and Arizen Voice run entirely local. The hardware required depends on the model you choose.

| Model | VRAM (GPU) | RAM (CPU-only) | Speed (GPU) |
|---|---|---|---|
| Phi-3 Mini Q4 (~2 GB) | 2 GB | 6 GB | Fast |
| Llama 3 8B Q4 (~5 GB) | 5 GB | 10 GB | Good |
| Mistral 7B Q4 (~4 GB) | 4 GB | 8 GB | Good |
| Llama 3 70B Q4 (~35 GB) | 40 GB+ | 40+ GB | Slow on CPU |

> **CPU-only inference** is fully supported via `llama.cpp`. It is slower but works on any hardware. For real-time conversation, a GPU with 4+ GB VRAM is strongly recommended.

---

## Software Dependencies

ArizenOS is a self-contained installer. The following are bundled and do not require manual installation:

- **Electron** (application runtime)
- **Node.js 20 LTS** (bundled with Electron)
- **llama.cpp** (local AI inference engine)
- **Whisper.cpp** (speech-to-text, included with Arizen Voice)
- **Piper TTS** (text-to-speech, included with Arizen Voice)
- **Visual C++ Redistributables 2022** (auto-installed by the setup wizard if missing)

---

## Developer Requirements

If you are building from source or developing extensions:

| Tool | Required Version |
|---|---|
| Node.js | 20 LTS (exact match) |
| pnpm | 8.x |
| Git | 2.40+ |
| Visual Studio Build Tools | 2022 (for N-API native modules) |
| Windows SDK | 10.0.19041+ |
| Python | 3.11+ (for native module build scripts) |

Install Visual Studio Build Tools:
```bash
winget install Microsoft.VisualStudio.2022.BuildTools
```

---

## Frequently Asked Questions

**Can I run ArizenOS on Windows ARM (Snapdragon X)?**
ARM64 support is on the [v1.0.0 roadmap](../roadmap/v1.0.0.md). It is not supported in the pre-alpha.

**Does ArizenOS replace Windows Explorer?**
Arizen Launcher replaces the taskbar and start menu by default. Windows Explorer (file manager) remains unchanged. You can toggle the shell replacement at any time in Hub → Settings → Shell.

**Will it affect my games or other apps?**
No. ArizenOS runs at the shell layer. It does not hook into application processes, modify system DLLs, or interfere with the graphics pipeline of other applications. Game performance is unaffected.

**Does it work with multiple monitors?**
Multi-monitor support is included from the first alpha release.
