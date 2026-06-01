# Frequently Asked Questions

---

## General

**What exactly is ArizenOS?**
ArizenOS is an open-source desktop experience platform for Windows. It replaces the Windows shell (taskbar, launcher) and adds an AI layer — local inference, voice control, and an autonomous agent — all running on your hardware. It is not a new operating system and does not modify Windows itself.

**Is ArizenOS free?**
Yes. ArizenOS is MIT-licensed and free to use, modify, and distribute. The core experience — shell, AI, voice, agent — will always be free. Premium themes or extensions from the community marketplace may be paid at the creator's discretion.

**Does ArizenOS send any data to the cloud?**
No. By default, ArizenOS runs entirely locally. There is no telemetry, no analytics, no crash reporting. If you enable Arizen Sync, data is encrypted end-to-end on your device before transmission — the sync server never sees your plaintext data.

**Is this safe to install?**
Yes. ArizenOS is open source — every line of code is publicly auditable. Releases are code-signed by Arizen Technologies. Always download from the official [GitHub Releases](https://github.com/Alrizz-art/ArizenOS/releases) page and verify the SHA-256 checksum.

**Will ArizenOS slow down my computer?**
ArizenOS is designed to be lightweight at idle. The shell replacement uses less memory than Windows Explorer in most configurations. The AI components only load models on demand — they do not run continuously in the background.

---

## Installation & Compatibility

**What Windows versions are supported?**
Windows 10 Build 19041 (20H1) and above, and all Windows 11 versions. See [System Requirements](system-requirements.md) for details.

**Does it work with Windows ARM (Snapdragon X)?**
ARM64 support is planned for v1.0.0. It is not available in the pre-alpha.

**Can I run ArizenOS on a VM?**
The shell and AI components work in most VMs. Glass effects require GPU passthrough or a VM with DirectX 12 support. VMs with basic display adapters will fall back to flat rendering automatically.

**Does it conflict with other shell replacements (Rainmeter, StartAllBack, etc.)?**
ArizenOS is designed to be the primary shell replacement. Running it alongside other shell tools may cause visual conflicts. We recommend running ArizenOS as the sole shell replacement for the best experience.

**Can I uninstall it without any trace?**
Yes. The uninstaller in Windows Settings → Apps restores the default Windows shell and removes all ArizenOS files. User data in `%LOCALAPPDATA%\ArizenOS\` can be removed manually if desired.

---

## Local AI

**Do I need a GPU for the AI features?**
No. ArizenOS uses `llama.cpp` which supports CPU-only inference. A GPU significantly improves speed — responses will be noticeably faster. See [System Requirements](system-requirements.md) for recommended hardware.

**Which AI models are supported?**
Any GGUF-format model compatible with llama.cpp. The Hub's model browser includes curated, tested models. You can also manually add models by dropping a `.gguf` file into `%LOCALAPPDATA%\ArizenOS\models\`.

**Does it support NVIDIA, AMD, and Intel GPUs?**
Yes. `llama.cpp` supports CUDA (NVIDIA), ROCm (AMD), and OpenCL (Intel and others). ArizenOS automatically detects and uses the best available backend.

**Can I use OpenAI or Anthropic as a cloud fallback?**
Cloud providers are planned as an opt-in configuration for Arizen Assistant (v0.4.0 milestone). You will be able to configure a cloud API key alongside local models, with a preference order you control.

**My model responses are slow. What can I do?**
1. Use a smaller, quantized model (Q4 recommended for everyday use)
2. Enable GPU acceleration: Hub → AI Models → [Model] → Settings → GPU Layers
3. Reduce context length: Hub → AI Models → [Model] → Settings → Context
4. Close other GPU-heavy applications

---

## Arizen Agent

**Is Arizen Agent safe?**
Arizen Agent requires explicit permission for every tool category before first use. It will not take any OS action without your approval. You can revoke permissions at any time in Hub → Settings → Agent. All actions are logged at `%LOCALAPPDATA%\ArizenOS\logs\agent.log`.

**Can Arizen Agent access my passwords or private files?**
Only if you explicitly grant file system access to directories containing them. We recommend granting access to specific folders rather than the entire drive. Arizen Agent never reads `.env` files, credential stores, or system key vaults unless you directly instruct it to and have granted that permission.

**Can I build my own tools for Arizen Agent?**
Yes. The `@arizen/agent-sdk` is designed for exactly this. See [Building Extensions](../guides/developer/building-extensions.md).

---

## Development & Contributing

**What language and framework is ArizenOS built with?**
TypeScript throughout. Electron for the application runtime. React for UI. N-API native modules for Windows-specific APIs (DWM, DirectComposition, Win32). Vitest for testing.

**How do I set up the development environment?**
See [Local Development](../guides/developer/local-development.md).

**How do I report a bug?**
Open a [Bug Report](https://github.com/Alrizz-art/ArizenOS/issues/new?template=bug_report.yml) on GitHub. Please include your ArizenOS version, Windows version, and steps to reproduce.

**I have a large feature idea — where do I start?**
For significant changes, open an [RFC](https://github.com/Alrizz-art/ArizenOS/issues/new?template=rfc.yml) first. For smaller features, a [Feature Request](https://github.com/Alrizz-art/ArizenOS/issues/new?template=feature_request.yml) issue is the right place.

---

## Roadmap & Future

**When is v1.0.0?**
There is no fixed date. ArizenOS is pre-alpha. The [Roadmap](../roadmap/README.md) describes what needs to happen for each major milestone.

**Will ArizenOS ever support macOS or Linux?**
The current architecture is built around Windows-specific APIs (DWM, DirectComposition, Win32). Cross-platform support is not on the current roadmap. It may be revisited after v1.0.0.

**Is there an enterprise offering planned?**
Enterprise support programs (SLA, managed deployment, custom theming) are planned alongside the v1.0.0 General Availability release. Contact [enterprise@arizenos.dev](mailto:enterprise@arizenos.dev) for early evaluation.
