# Troubleshooting

Common issues and their solutions. If your issue is not listed here, search [GitHub Issues](https://github.com/Alrizz-art/ArizenOS/issues) or ask in [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions).

---

## Installation

### Installer fails silently or crashes

**Causes:** Antivirus software blocking the installer, insufficient permissions, or missing Visual C++ Redistributables.

**Solutions:**
1. Run the installer as Administrator (right-click → "Run as administrator")
2. Temporarily disable antivirus real-time protection during installation
3. Manually install VC++ Redistributables: [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
4. Check Windows Event Viewer → Application Log for more detail

### "Windows protected your PC" SmartScreen warning

This appears for new releases that haven't yet accumulated enough installation count to pass SmartScreen's reputation check. It does not indicate the software is unsafe.

**Solution:** Click "More info" → "Run anyway". Verify the publisher is "Arizen Technologies" and the code signature is valid before proceeding.

---

## Glass Effects

### Glass effects not showing — all panels appear flat and opaque

**Cause:** GPU does not support DirectComposition, or DWM is disabled.

**Diagnose:**
1. Run `dxdiag` → Display tab — check DirectX version (must be 11+)
2. Run `arizen diagnostics glass` in a terminal for a detailed hardware check

**Solutions:**
- Update GPU drivers to the latest version
- Check: Windows Settings → System → Display → Graphics → Hardware-accelerated GPU scheduling (enable if available)
- If running in a VM: enable DirectX passthrough or GPU passthrough in your hypervisor settings
- If on Intel UHD graphics: the glass renderer uses a reduced-resolution fallback — see Hub → Settings → Display → Glass Quality → Medium

### Glass effects are present but blurry/artifacts visible

**Cause:** GPU driver issue or DirectComposition surface size mismatch after a display configuration change.

**Solution:** Hub → Settings → Display → Glass → Reset glass surfaces. If persistent, update GPU drivers.

### Glass effects cause frame drops / screen tearing

**Cause:** GPU is being pushed beyond its capacity at the current glass quality setting.

**Solution:** Hub → Settings → Display → Glass Quality → reduce from High to Medium or Low. Check GPU load in Task Manager → Performance → GPU.

---

## Arizen Assistant

### "No model loaded" error

**Cause:** The default model could not be loaded, usually due to insufficient VRAM or the model file being corrupted.

**Diagnose:**
```
%LOCALAPPDATA%\ArizenOS\logs\mind.log
```
Look for `MODEL_LOAD_FAILED` or `INSUFFICIENT_VRAM` entries.

**Solutions:**
- Try a smaller model: Hub → AI Models → Phi-3 Mini Q4 → Set as Default
- Reduce GPU layers: Hub → AI Models → [Model] → GPU Layers → 0 (CPU-only)
- Re-download the model: Hub → AI Models → [Model] → Delete and re-download

### Responses are very slow (> 30 seconds for first token)

**Cause:** Model is running on CPU with no GPU offloading, or model is too large for available VRAM.

**Solutions:**
1. Check GPU layers: Hub → AI Models → [Model] → GPU Layers — if 0, increase to 16–32
2. Verify GPU is detected: Hub → Settings → Performance → shows GPU name and VRAM
3. Switch to a faster model: Phi-3 Mini Q4 is the fastest model ArizenOS ships
4. Close other GPU-intensive applications (games, video editors)

### Responses cut off mid-sentence

**Cause:** Context window overflow — the conversation has exceeded the model's maximum context length.

**Solution:**
- Clear the conversation: Ctrl + K in the Assistant panel
- Use a model with a larger context window
- Reduce `context_length` in config to trigger earlier context management

### Assistant panel shortcut doesn't work

**Cause:** Shortcut conflict with another application.

**Solution:**
1. Check Hub → Settings → Keyboard — confirm the shortcut is configured
2. Check for conflicts with other applications using the same key combination
3. Reassign the shortcut to a different key combination

---

## Arizen Agent

### Agent refuses to perform a task

**Cause:** The task requires a tool permission that has not been granted.

**Solution:** Hub → Settings → Agent → Tool Permissions — enable the required category. The Agent's refusal message will indicate which permission is needed.

### Agent's plan looks wrong before execution

**Cause:** The instruction was ambiguous. The Agent generates plans based on the language model's interpretation of your instruction.

**Solution:** Cancel and rephrase with more specificity. For example:
- ❌ "Clean up my files"
- ✅ "In C:\Users\me\Downloads, delete all files with .tmp or .bak extensions that are older than 7 days"

### Scheduled task didn't run

**Causes:** ArizenOS was not running, a required permission was revoked, or the task configuration has an error.

**Diagnose:** Hub → Agent → Scheduled Tasks → [Task] → View last run log

**Solutions:**
1. Ensure ArizenOS launches with Windows: Hub → Settings → General → Launch with Windows
2. Re-enable required tool permissions: Hub → Settings → Agent → Tool Permissions
3. Recreate the scheduled task with the corrected configuration

---

## Arizen Hub

### Hub won't open

**Solution:** Try restarting the Hub process: right-click the system tray icon → Restart Hub. If that fails, restart ArizenOS entirely.

### Model download fails or stalls

**Cause:** Network issue, insufficient disk space, or Hugging Face rate limiting.

**Solutions:**
1. Check available disk space — GGUF models are 2–35 GB depending on size
2. Check network connection and retry
3. If rate limited: wait 30 minutes and retry, or log in to Hugging Face via Hub → Settings → Accounts

---

## Development Environment

### `pnpm install` fails on native module compilation

**Full error:** `gyp ERR! build error` or `LINK : fatal error`

**Solutions:**
```bash
# Ensure Visual Studio Build Tools 2022 are installed
npm install -g node-gyp
node-gyp configure --msvs_version=2022

# Then retry
pnpm install --ignore-scripts=false
```

If using multiple VS Build Tools versions, explicitly set the version:
```bash
$env:GYP_MSVS_VERSION = "2022"
pnpm install
```

### Electron window is blank (white screen)

**Cause:** Renderer process failed to start. Check for JavaScript errors in the main process.

**Diagnose:**
```bash
# Run with console output visible
pnpm --filter @arizen/launcher dev 2>&1 | head -100
```

**Solutions:**
1. Ensure `pnpm build` completed successfully before `pnpm dev`
2. Clear Electron's AppData cache: `%APPDATA%\arizen-launcher\` → delete contents
3. Check for port conflicts if running multiple app instances

---

## Collecting Diagnostic Information for Bug Reports

When opening a bug report, include:

```bash
# ArizenOS version
arizen --version

# System diagnostics
arizen diagnostics --output diagnostics.txt

# Relevant logs (attach to the issue)
%LOCALAPPDATA%\ArizenOS\logs\
```

Or use the in-app report tool: **Hub → Help → Report a Bug** — this automatically collects version info, logs, and system specs (review before sending).
