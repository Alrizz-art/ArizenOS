# Quick Start

This guide gets you from zero to a working ArizenOS setup in under 10 minutes.

---

## 1. Install ArizenOS

Download and run the installer from [GitHub Releases](https://github.com/Alrizz-art/ArizenOS/releases).

> Full installation details: [Installation Guide](installation.md)

---

## 2. Choose Your Shell Mode

On first launch, you will be asked how to integrate ArizenOS with your desktop:

| Mode | What It Does | When to Use |
|---|---|---|
| **Full Shell** | Replaces Windows taskbar and start menu | Recommended — full ArizenOS experience |
| **Overlay** | ArizenOS sits alongside the default taskbar | Try before you commit |
| **Headless** | AI and Agent only, no shell replacement | Power users, minimal setups |

You can change this at any time in **Hub → Settings → Shell Mode**.

---

## 3. Download a Model (Optional but Recommended)

Arizen Assistant works best with a local AI model. The Setup Wizard will offer you a model download — choose **Phi-3 Mini Q4** if you're unsure. It's fast, small (~2 GB), and works well for everyday tasks.

If you skip this step:
- Open **Arizen Hub**
- Go to **AI Models**
- Click **Download** next to Phi-3 Mini Q4

Model downloads from Hugging Face. You need an internet connection once for the download — after that, everything runs locally.

---

## 4. Open Arizen Assistant

Press **Win + Space** (default shortcut) to open Arizen Assistant.

Try these to get a feel for what it can do:

```
"Summarise the last 5 files I opened"
"Draft a reply to this email: [paste email]"
"Search my documents for anything about Q3 budget"
"Explain this code: [paste code]"
"Open Spotify and play something lo-fi"
```

All of this runs locally on your machine. No cloud, no subscription.

---

## 5. Customise Your Theme

ArizenOS ships with four built-in themes:

| Theme | Palette |
|---|---|
| **Void** | Deep black, luminous accents — the default |
| **Aurora** | Deep navy with aurora-green highlights |
| **Ash** | Warm grey, minimal, professional |
| **Prism** | Clean white glass, high contrast |

Switch themes: **Hub → Themes → Browse**

To install community themes: **Hub → Themes → Community**

---

## 6. Set Up Arizen Agent (Optional)

Arizen Agent lets ArizenOS take actions on your behalf — file operations, web searches, running scripts, controlling applications.

Open **Hub → Settings → Agent** and configure which tool categories to enable:

| Tool | What It Can Do |
|---|---|
| **File System** | Read, write, organise files and folders |
| **Shell** | Run PowerShell and CMD commands |
| **Browser** | Open URLs, read page content, fill forms |
| **Clipboard** | Read and write clipboard content |
| **Calendar** | Read your calendar, create events |

Each tool category requires explicit approval before first use. You can revoke permissions at any time.

---

## 7. Explore the Ecosystem

**Arizen Hub** is your control centre:

- **Extensions** — productivity tools, integrations, automations
- **Themes** — community-built visual themes
- **Widgets** — desktop widgets with live data
- **AI Models** — browse and download local models
- **Updates** — manage ArizenOS and extension updates

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Win + Space` | Open / close Arizen Assistant |
| `Win + \`` | Open Arizen Launcher (spotlight) |
| `Win + Shift + A` | Start voice input (Arizen Voice) |
| `Win + Shift + H` | Open Arizen Hub |
| `Win + Tab` | Virtual desktop switcher (enhanced) |
| `Win + G` | Arizen Agent quick command |
| `Alt + F4` | Close focused window (unchanged) |

Customise all shortcuts in **Hub → Settings → Keyboard**.

---

## What's Next

- [User Guide — Desktop Setup](../guides/user/desktop-setup.md)
- [User Guide — Arizen Assistant](../guides/user/ai-assistant.md)
- [User Guide — Themes & Customisation](../guides/user/themes-and-customization.md)
- [Developer Guide — Building Extensions](../guides/developer/building-extensions.md)
- [API Reference](../api/README.md)
