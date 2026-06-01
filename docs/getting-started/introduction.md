# Introduction

ArizenOS is an **open-source desktop experience platform** for Windows 10 and Windows 11.

It is not a new operating system. It is not a Windows mod, a custom ISO, or a compatibility layer. It is an **intelligence layer** — a complete reimagining of the Windows desktop surface, built from the ground up around local AI, GPU-accelerated glass rendering, and a developer ecosystem designed to ship at startup speed.

---

## The Problem

The modern Windows desktop is, architecturally, the same desktop from 2009. Taskbar. Start menu. Window chrome. The AI revolution arrived — and the screen did not change.

Meanwhile, the best hardware in the world is sitting idle. A GPU that can render photorealistic scenes in real time is displaying a flat, opaque taskbar. A CPU powerful enough to run local language models is doing nothing while you wait for a tab to load. 1.4 billion people own the most powerful personal computers in history, running an experience designed for an era before any of this was possible.

---

## The Solution

ArizenOS drops into your existing Windows installation and replaces the experience layer — not the operating system. Your apps, your files, your drivers, your games: all untouched. What changes is everything you see and interact with every day.

```
Windows 10 / Windows 11
        +
ArizenOS (experience layer)
        =
The desktop of the AI generation
```

---

## Core Products

ArizenOS ships as five integrated products that work together as a unified system:

| Product | Package | What It Does |
|---|---|---|
| **Arizen Launcher** | `@arizen/launcher` | Shell replacement: taskbar, spotlight, virtual desktops |
| **Arizen Assistant** | `@arizen/assistant` | Floating AI interface with local inference and context |
| **Arizen Voice** | `@arizen/voice` | Wake-word → Whisper STT → Kokoro TTS, fully local |
| **Arizen Hub** | `@arizen/hub` | Extension marketplace, themes, models, settings |
| **Arizen Agent** | `@arizen/agent` | Autonomous task runner with explicit permission model |

---

## Core Principles

**Local first.** Your AI runs on your hardware. Your prompts never leave your machine unless you explicitly choose cloud inference. No subscription required for the core experience.

**Open by default.** Every component is MIT-licensed. You can read, modify, fork, and redistribute anything in this repository.

**Developer ecosystem.** ArizenOS ships a public Extension SDK (`@arizen/agent-sdk`), a Widget runtime (`@arizen/widgets`), and a Theming SDK (`@arizen/skin`). Building for ArizenOS is a first-class experience.

**Glass, not decoration.** The visual system uses real GPU compositing — depth, blur, and translucency tied to context and state, not applied as a style on top of flat UI.

**Privacy by architecture.** No telemetry. No analytics. No crash reporting. No opt-out, because there is no opt-in.

---

## Who Is ArizenOS For?

**Power users** who want an AI-native desktop that respects their hardware and their privacy.

**Developers** who want to build extensions, themes, and widgets for a rapidly growing ecosystem.

**Designers** who want to work in a theming system built on compiled design tokens with hot-reload.

**Enthusiasts** who want to be part of building the next generation of the personal computing experience.

---

## Project Status

ArizenOS is in **pre-alpha**. The architecture, governance, and documentation are production-grade. The code is being written now.

This is the right time to get involved if you want to shape the direction of the project — architecture decisions, API design, UX patterns, and core infrastructure are all being established now.

→ [System Requirements](system-requirements.md)
→ [Installation](installation.md)
→ [Quick Start](quick-start.md)
→ [Contributing](../../CONTRIBUTING.md)
