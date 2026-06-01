# Arizen Assistant User Guide

Arizen Assistant is a context-aware AI interface that runs entirely on your device. It understands your desktop, your files, and your workflow — and it acts on them.

---

## Opening the Assistant

| Method | Action |
|---|---|
| **Win + Space** | Toggle open/close |
| **System tray icon** | Click the Arizen icon |
| **Voice** | Say your wake word (default: "Hey Arizen") |
| **Spotlight** | Type `@` in Spotlight to switch to Assistant mode |

---

## Interface Overview

The Assistant opens as a floating glass panel. It has three zones:

- **Conversation area** — scrollable message history
- **Input bar** — type your prompt; supports multiline with Shift+Enter
- **Context strip** — shows what the Assistant is currently aware of (active window, clipboard, recent files)

The panel can be:
- **Detached** — drag the title bar to position it anywhere
- **Docked** — pin to any screen edge; it will stay above other windows
- **Minimised to tray** — conversation history persists

---

## Context

ArizenOS Assistant maintains **layered context** — it does not just see your prompt, it sees what you're working on.

### Automatic Context (On by default)
| Context Source | What Is Shared |
|---|---|
| Active window | App name and window title |
| Clipboard | Last copied text (if under 2,000 characters) |
| Recent files | Last 5 opened file paths |
| Time & date | Current date and time |
| System state | Battery level, active monitors, running apps |

Configure which sources are included: **Hub → Settings → Assistant → Context Sources**

### Manual Context
Add context explicitly in any conversation:
- **@file** — drag a file onto the input bar, or type `@file:` and paste a path
- **@clip** — attach current clipboard content
- **@screen** — attach a screenshot of the current window
- **@selection** — attach currently selected text

### Context Window Management
The Assistant shows a context usage meter in the bottom-right corner of the panel. When approaching the model's context limit, the Assistant automatically summarises earlier parts of the conversation and evicts them from the active context.

---

## Conversation Features

### Streaming Responses
Responses stream token-by-token as the model generates them. You do not wait for the full response before you can start reading.

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Send message |
| `Shift + Enter` | New line in input |
| `Ctrl + K` | Clear conversation |
| `Ctrl + C` | Copy last response |
| `Ctrl + /` | Command palette |
| `Esc` | Close panel |
| `Alt + ↑/↓` | Navigate conversation history |

### Response Actions
Every response has an action toolbar:
- **Copy** — copy full response as plain text
- **Copy as Markdown** — preserve formatting
- **Edit & Resend** — regenerate with a modified prompt
- **Create task** — send to Arizen Agent for execution
- **Bookmark** — save to Hub → Saved Responses

---

## AI Models

### Changing the Active Model
**Hub → AI Models → [Model] → Set as Default**

You can also switch models mid-conversation from the model selector in the Assistant panel's header. Switching models does not clear conversation history.

### Recommended Models by Use Case

| Use Case | Recommended Model | Why |
|---|---|---|
| General assistant | Llama 3 8B Q4 | Best balance of quality and speed |
| Quick tasks | Phi-3 Mini Q4 | Fastest responses, smallest footprint |
| Coding | Mistral 7B Instruct Q4 | Strong code generation |
| Long documents | Llama 3 8B Q8 | Higher quality quantisation |
| Complex reasoning | Llama 3 70B Q4 (GPU required) | Most capable |

### Downloading Models
**Hub → AI Models → Browse** shows curated, tested models. All models are downloaded from Hugging Face. Progress is shown in the Hub notification bar.

You can also manually install any GGUF model:
1. Download the `.gguf` file
2. Drop it into `%LOCALAPPDATA%\ArizenOS\models\`
3. Open **Hub → AI Models → Scan** to detect it

---

## System Prompt & Personality

### Custom System Prompt
Define a persistent system prompt that is prepended to every conversation:
**Hub → Settings → Assistant → System Prompt**

Example: *"You are a terse assistant. Always reply in under 3 sentences unless asked to elaborate. Use British English spelling."*

### Personas
Save multiple system prompts as named Personas and switch between them from the model selector. Useful for switching between professional, creative, and coding modes.

---

## Privacy

All inference runs locally. No conversation data is sent anywhere by default.

- Conversation history is stored locally at `%LOCALAPPDATA%\ArizenOS\assistant\history.db` (SQLite, AES-256 encrypted)
- To clear history: **Hub → Settings → Assistant → Clear History**
- To disable history entirely: **Hub → Settings → Assistant → Store History → Off**

---

## Troubleshooting

**Responses are very slow**
- Check which model is active — larger models are slower
- Enable GPU layers: Hub → AI Models → [Model] → Settings → GPU Layers → Auto
- Close GPU-heavy applications

**"Model not loaded" error**
The model failed to load, usually due to insufficient VRAM. Try:
- Reducing GPU layers: Hub → AI Models → [Model] → Settings → GPU Layers → 0 (CPU only)
- Switching to a smaller model

**Assistant panel not opening**
- Check the shortcut hasn't been reassigned: Hub → Settings → Keyboard
- Restart the Assistant process: Hub → Settings → Advanced → Restart Assistant
