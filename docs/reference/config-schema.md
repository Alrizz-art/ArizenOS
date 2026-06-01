# Configuration Schema Reference

ArizenOS is configured via TOML files. The user configuration file is at:
```
%LOCALAPPDATA%\ArizenOS\config.toml
```

All settings in `config.toml` are optional — ArizenOS provides sensible defaults for everything. You only need to add the keys you want to override.

---

## Full Schema

```toml
# ArizenOS Configuration
# All values shown are defaults. Remove a key to use the default.

# ─── Shell ────────────────────────────────────────────────────────────────────

[shell]
# Shell integration mode
# "full"     Replace the Windows taskbar and start menu
# "overlay"  Show ArizenOS alongside the default shell
# "headless" No shell replacement (AI and Agent only)
mode = "full"

# Launch ArizenOS with Windows
startup = true

# ─── Launcher ─────────────────────────────────────────────────────────────────

[launcher]
# Taskbar position: "bottom" | "top" | "left" | "right"
taskbar_position = "bottom"

# Taskbar height in pixels (40–72)
taskbar_height = 48

# Show clock in taskbar
show_clock = true

# Show system tray in taskbar
show_tray = true

# Show notification badges on taskbar icons
show_badges = true

# Virtual desktop animation style: "slide" | "fade" | "none"
desktop_switch_animation = "slide"

# ─── Display & Glass ──────────────────────────────────────────────────────────

[display]
# Glass rendering quality
# "ultra" | "high" | "medium" | "low" | "off"
glass_quality = "high"

# Blur radius in pixels (4–32)
blur_radius = 16

# Shadow intensity (0–100)
shadow_intensity = 80

# Override system reduced-motion preference
# "system" | "always" | "never"
reduced_motion = "system"

# ─── AI / ArizenMind ──────────────────────────────────────────────────────────

[mind]
# Default model to load on startup (model file stem, without .gguf)
default_model = "phi-3-mini-instruct-q4_k_m"

# Path to model directory
model_path = "%LOCALAPPDATA%/ArizenOS/models"

# GPU layers to offload (-1 = all, 0 = CPU-only)
gpu_layers = 32

# Context length in tokens (0 = model maximum)
context_length = 0

# CPU threads for inference (0 = auto)
threads = 0

# Batch size for prompt evaluation
batch_size = 512

# ─── Arizen Assistant ─────────────────────────────────────────────────────────

[assistant]
# Keyboard shortcut to toggle the Assistant panel
shortcut = "Win+Space"

# Store conversation history
store_history = true

# History encryption (requires store_history = true)
encrypt_history = true

# Default system prompt (empty = none)
system_prompt = ""

# Context sources included automatically
[assistant.context]
active_window = true    # Include active window title and process
clipboard = true        # Include clipboard text (up to 2000 chars)
recent_files = true     # Include last 5 opened file paths
datetime = true         # Include current date and time

# ─── Arizen Voice ─────────────────────────────────────────────────────────────

[voice]
# Enable Arizen Voice
enabled = false

# Wake word (default model bundled; custom requires compatible model)
wake_word = "hey arizen"

# Whisper model size: "tiny" | "base" | "small" | "medium"
whisper_model = "base"

# TTS voice (Piper voices bundled)
tts_voice = "en-gb-alan-low"

# PTT shortcut (alternative to wake word)
ptt_shortcut = "Win+Shift+A"

# ─── Arizen Agent ─────────────────────────────────────────────────────────────

[agent]
# Enable the Agent
enabled = true

# Keyboard shortcut for quick command
shortcut = "Win+G"

# Maximum steps per task (safety limit)
max_steps = 20

# Require confirmation for all tool calls (overrides per-tool settings)
require_confirmation = false

# Permitted file system paths (empty = deny all file system access)
[agent.filesystem]
allowed_read_paths = []
allowed_write_paths = []

# ─── Arizen Hub ───────────────────────────────────────────────────────────────

[hub]
# Keyboard shortcut
shortcut = "Win+Shift+H"

# Automatically check for updates
auto_update_check = true

# ─── Sync ─────────────────────────────────────────────────────────────────────

[sync]
# Enable cross-device sync (E2E encrypted, opt-in)
enabled = false

# Sync interval in minutes (0 = manual only)
interval = 15

# Items to sync
[sync.include]
settings = true
themes = true
history = false     # Conversation history — disabled by default for privacy
widgets = true
shortcuts = true

# ─── Performance ──────────────────────────────────────────────────────────────

[performance]
# Performance profile: "efficiency" | "balanced" | "performance"
profile = "balanced"

# ─── Logging ──────────────────────────────────────────────────────────────────

[log]
# Log level: "debug" | "info" | "warn" | "error"
level = "info"

# Maximum log file size in MB
max_file_size_mb = 50

# Maximum number of log files to retain
max_files = 5

# ─── Keyboard Shortcuts ───────────────────────────────────────────────────────

[shortcuts]
# All shortcuts can be overridden here.
# Format: modifier+key — modifiers: Win, Ctrl, Alt, Shift
launcher_spotlight = "Win+`"
assistant_toggle   = "Win+Space"
hub_open           = "Win+Shift+H"
agent_command      = "Win+G"
voice_ptt          = "Win+Shift+A"
dnd_toggle         = "Win+Shift+D"
```

---

## Environment Variables

ArizenOS reads the following environment variables (override config file values):

| Variable | Type | Description |
|---|---|---|
| `ARIZEN_CONFIG_PATH` | path | Override the user config file path |
| `ARIZEN_LOG_LEVEL` | string | Override log level |
| `ARIZEN_MODEL_PATH` | path | Override model directory |
| `ARIZEN_DEV` | boolean | Enable development mode |
| `ARIZEN_DISABLE_GPU` | boolean | Force CPU-only rendering and inference |

---

## Validating Your Config

```bash
arizen config validate
# → Config valid
# → Active config:
#     shell.mode = full
#     mind.default_model = phi-3-mini-instruct-q4_k_m
#     ...
```

```bash
arizen config dump
# → Prints fully-merged config (defaults + machine + user) as TOML
```
