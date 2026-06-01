# Installation

ArizenOS offers two installation paths: a graphical installer for end users, and a source build for developers and contributors.

---

## Option 1 — Graphical Installer

The recommended path for most users. The installer handles all dependencies, Windows integration, and initial configuration.

### Step 1 — Download

Download the latest installer from the [GitHub Releases page](https://github.com/Alrizz-art/ArizenOS/releases):

```
ArizenOS-Setup-x.y.z.exe
```

> Always download from the official GitHub Releases page. Verify the SHA-256 checksum published alongside each release before running the installer.

**Verify the checksum (PowerShell):**
```powershell
Get-FileHash .\ArizenOS-Setup-x.y.z.exe -Algorithm SHA256
# Compare the output to the SHA256 file in the release assets
```

### Step 2 — Run the Installer

Run `ArizenOS-Setup-x.y.z.exe`. The installer will:

1. Check your system meets [minimum requirements](system-requirements.md)
2. Install Visual C++ Redistributables 2022 if missing
3. Install ArizenOS to `C:\Program Files\ArizenOS\` (configurable)
4. Create user configuration at `%LOCALAPPDATA%\ArizenOS\`
5. Register Arizen Launcher as an optional shell replacement
6. Add ArizenOS to Windows startup

### Step 3 — First Launch

On first launch, the **Setup Wizard** walks you through:

- **Shell mode** — Replace the taskbar now, or run ArizenOS alongside the default shell
- **AI model** — Download a starter model (Phi-3 Mini recommended — fast, ~2 GB), or skip and configure later
- **Theme** — Choose from the built-in themes or install from Hub
- **Sync** — Enable cross-device sync (optional, E2E encrypted) or run fully local

### Step 4 — Configure Local AI (Optional)

If you skipped model download during setup, open **Arizen Hub → AI Models** to browse and download models. Models are stored at:

```
%LOCALAPPDATA%\ArizenOS\models\
```

---

## Option 2 — Build from Source

For developers, contributors, and anyone who wants full control over their build.

### Prerequisites

Install the required tools:

```powershell
# Node.js 20 LTS
winget install OpenJS.NodeJS.LTS

# pnpm (package manager)
npm install -g pnpm@8

# Git
winget install Git.Git

# Visual Studio Build Tools 2022 (for native modules)
winget install Microsoft.VisualStudio.2022.BuildTools `
  --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended --quiet"
```

Verify your environment:
```bash
node --version    # v20.x.x
pnpm --version    # 8.x.x
git --version     # 2.40+
```

### Clone & Install

```bash
# Clone the repository
git clone https://github.com/Alrizz-art/ArizenOS.git
cd ArizenOS

# Install all workspace dependencies
pnpm install

# Build all packages (required before running any app)
pnpm build
```

The first `pnpm install` will compile native N-API modules against your Node.js version. This takes 3–10 minutes depending on your machine.

### Running in Development

```bash
# Start all apps in parallel (uses Turborepo)
pnpm dev

# Or start a specific app
pnpm --filter @arizen/launcher dev
pnpm --filter @arizen/assistant dev
pnpm --filter @arizen/hub dev
pnpm --filter @arizen/voice dev
pnpm --filter @arizen/agent dev
```

### Building a Production Package

```bash
# Build all packages and apps
pnpm build

# Package the installer
pnpm --filter @arizen/launcher package

# Output: apps/launcher/dist/ArizenOS-Setup-x.y.z.exe
```

---

## Updating ArizenOS

### Via Installer
ArizenOS checks for updates automatically on startup (requires internet). Updates are delivered through Arizen Hub → Updates. You will be notified and can install at your convenience — no forced restarts.

### Via Source Build
```bash
git pull origin main
pnpm install   # updates dependencies
pnpm build     # rebuilds changed packages (Turborepo caches unchanged packages)
```

---

## Uninstalling

### Via Windows Settings
Settings → Apps → Installed apps → ArizenOS → Uninstall

This removes all ArizenOS binaries and shell integrations. User configuration and AI models are preserved at `%LOCALAPPDATA%\ArizenOS\`.

To also remove user data:
```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\ArizenOS"
```

### Via Source Build
```bash
# Remove build artifacts
pnpm clean

# Restore Windows shell (if Arizen Launcher was set as default shell)
# This is done automatically by the uninstaller — if building from source,
# run in an elevated PowerShell:
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" `
  -Name "Shell" -Value "explorer.exe"
```

---

## Troubleshooting Installation

**Installer fails with "Visual C++ Redistributables missing"**
Run the installer as Administrator. If it still fails, manually install:
[https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

**`pnpm install` fails on native module compilation**
Ensure Visual Studio Build Tools 2022 are installed with the "Desktop development with C++" workload. Then:
```bash
npm install -g node-gyp
pnpm install --ignore-scripts=false
```

**Glass effects not showing (all windows appear flat)**
Your GPU may not support DirectComposition. Check:
- GPU drivers are up to date
- DirectX 12 is supported (`dxdiag` → Display tab)
- Hardware acceleration is enabled in Windows display settings

**ArizenOS won't start after a Windows update**
Some Windows updates can reset shell settings. Run the ArizenOS Repair tool from:
`%LOCALAPPDATA%\ArizenOS\bin\arizen-repair.exe`

→ See [Troubleshooting Reference](../reference/troubleshooting.md) for a complete guide.
