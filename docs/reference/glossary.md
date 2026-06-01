# Glossary

Terms and concepts used throughout the ArizenOS documentation and codebase.

---

## A

**ADR (Architecture Decision Record)**
A document that captures a significant architectural decision: the context, options considered, the decision made, and its consequences. ArizenOS ADRs live in `docs/architecture/`. See the [first ADR](../architecture/ADR-0001-monorepo.md).

**Agent** (Arizen Agent)
The autonomous task runner component of ArizenOS. Translates natural language instructions into OS-level actions using tools with explicit user-granted permissions.

**Agent SDK** (`@arizen/agent-sdk`)
The public TypeScript API for building custom Agent tools. The only `@arizen/*` package with a public stability guarantee. See the [API reference](../api/agent-sdk.md).

**Arizen Hub**
The central control panel for ArizenOS. Manages themes, models, extensions, settings, and updates.

---

## C

**Changeset**
A small YAML file (in `.changeset/`) that records what changed in a PR and whether it is a major/minor/patch change. Used by the [Changesets](https://github.com/changesets/changesets) tool to automate versioning and changelog generation.

**Context (AI)**
The working memory of an AI model during a conversation. Measured in tokens. ArizenOS's `@arizen/mind` manages context windows automatically, evicting older messages when the limit is approached.

**Context (Desktop)**
Information about the user's current desktop state shared with Arizen Assistant: active window, clipboard content, recent files. Configured in Hub → Settings → Assistant → Context Sources.

**Conventional Commits**
A commit message format used by ArizenOS: `type(scope): description`. Types include `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`. Breaking changes append `!` and include a `BREAKING CHANGE:` footer.

---

## D

**Design Token**
A named, platform-agnostic design variable — color, size, duration, radius — that can be compiled into CSS custom properties, JSON, or native values. ArizenOS tokens live in theme JSON files and are managed by `@arizen/skin`.

**DirectComposition**
A Windows system API for off-screen GPU surface composition. Used by `@arizen/glass` to render and composite glass effects without going through the Chromium compositor.

**DWM (Desktop Window Manager)**
The Windows component that composites all windows onto the screen. ArizenOS uses DWM APIs (thumbnail capture, window composition attributes) for authentic glass rendering.

---

## E

**Electron**
The framework used to build ArizenOS applications. Wraps Chromium (renderer) and Node.js (main process) into a single distributable. ArizenOS uses Electron for cross-version Windows compatibility while retaining access to native APIs via N-API.

**EventBus**
The typed publish/subscribe system in `@arizen/core` used for decoupled communication between components within a process.

**Extension**
A package that adds new tools to Arizen Agent. Built with `@arizen/agent-sdk`. Distributed via the Arizen Hub marketplace or as `.arizen-ext` files. See [Building Extensions](../guides/developer/building-extensions.md).

---

## G

**GGUF**
The binary model file format used by `llama.cpp`. Replaces the older GGML format. All models in ArizenOS are GGUF files. Downloaded from Hugging Face and stored in `%LOCALAPPDATA%\ArizenOS\models\`.

**Glass**
ArizenOS's GPU-accelerated visual system — real-time gaussian blur of desktop content behind UI surfaces, depth layers, and ambient lighting. Rendered by `@arizen/glass` via DirectComposition + Direct2D.

**GPU Layers**
In local AI inference, the number of model layers offloaded to the GPU. More layers = faster inference, but higher VRAM usage. Configured per-model in Hub → AI Models → [Model] → GPU Layers.

---

## I

**IPC (Inter-Process Communication)**
Communication between Electron's main process and renderer process(es). ArizenOS uses `@arizen/core` IPC utilities which provide type-safe wrappers over Electron's `ipcMain`/`ipcRenderer` APIs.

---

## L

**llama.cpp**
An open-source C++ library for local LLM inference. ArizenOS's `@arizen/mind` wraps llama.cpp via an N-API native binding. Supports CUDA, ROCm, Vulkan, OpenCL, and CPU backends.

**LTS (Long-Term Support)**
A release designation indicating extended support (security patches and critical fixes) for a defined period. ArizenOS v1.0.0 begins an LTS cycle with 3-year support.

---

## M

**Monorepo**
A single repository containing multiple packages and applications. ArizenOS uses a pnpm workspace monorepo with Turborepo for build orchestration. All `@arizen/*` packages and all five apps live in one repository.

**MotionToken**
A design token in `@arizen/skin` that defines animation timing (`duration-fast`, `duration-normal`, `duration-slow`) and easing curves. `@arizen/flow` reads these tokens to produce animations that respect the active theme and the user's reduced-motion preference.

---

## N

**N-API**
Node.js Native API — a stable C ABI for building native Node.js addons. ArizenOS uses N-API for `@arizen/glass` (DirectComposition), `@arizen/mind` (llama.cpp), and `@arizen/shell` (Win32/DWM). N-API binaries are ABI-stable across Node.js versions.

**Namespace (Logger)**
A string identifier passed to `createLogger()` that appears in every log line from that module. Example: `createLogger('glass:engine')` → logs appear as `[glass:engine] Message...`.

---

## P

**Permission (Agent)**
An explicit grant given by the user to allow Arizen Agent to use a specific tool category (e.g. File System Write, Shell Run). Permissions are shown before an extension is enabled and can be revoked at any time.

**pnpm**
The package manager used in the ArizenOS monorepo. Version 8.x required. Significantly faster than npm/yarn for monorepo workloads due to its symlink-based store.

---

## R

**RFC (Request for Comments)**
A formal proposal for a significant design change, filed as a GitHub issue using the [RFC template](https://github.com/Alrizz-art/ArizenOS/issues/new?template=rfc.yml). RFCs must be accepted by the Technical Council before implementation begins.

---

## S

**Sandbox**
The isolated execution environment for widgets and extensions. Widgets run in a sandboxed iframe with a strict Content Security Policy. Tools declared in extensions run in a restricted process context. Neither can access OS resources beyond their declared permissions.

**SemVer (Semantic Versioning)**
The versioning scheme used by all `@arizen/*` packages: `MAJOR.MINOR.PATCH`. Breaking changes bump MAJOR, new features bump MINOR, bug fixes bump PATCH. `@arizen/agent-sdk` and `@arizen/widgets` follow SemVer strictly.

**Streaming**
Delivering AI-generated tokens to the user as they are produced by the model, rather than waiting for the full response. ArizenOS uses streaming by default for all Assistant responses.

---

## T

**Technical Council**
The elected governance body of ArizenOS. Responsible for approving RFCs, overseeing major releases, managing the public API stability commitment, and handling escalated community disputes. See [GOVERNANCE.md](../../GOVERNANCE.md).

**Token (AI)**
The fundamental unit of text for language models — roughly 3–4 characters on average in English. Context lengths and inference speeds are measured in tokens.

**Token (Design)**
A named design variable (color, size, duration). Not to be confused with AI tokens. Context disambiguates which meaning is intended.

**Turborepo**
The build orchestration tool for the ArizenOS monorepo. Manages task dependency ordering, parallel execution, and incremental caching so only changed packages are rebuilt.

---

## W

**Widget**
A sandboxed JavaScript component rendered as a glass panel on the desktop. Widgets display live data and support user interaction. Built with `@arizen/widgets` SDK. See [Building Widgets](../guides/developer/building-widgets.md).

**Whisper.cpp**
An open-source C++ implementation of OpenAI's Whisper speech-to-text model. Used by Arizen Voice for local, offline speech recognition. No cloud API required.
