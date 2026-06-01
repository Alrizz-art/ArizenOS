#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Dark Theme + Transparency Tweaks
.DESCRIPTION
    Forces system-wide dark mode, enables MICA/Acrylic effects on Windows 11,
    and applies fine-grained transparency registry tweaks.
.VERSION 2.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

$LogPath = "$env:SystemDrive\ArizenOS\Logs\theme_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message" | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = "DWord")
    New-Item -Path $Path -Force | Out-Null
    Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force
    Write-Log "REG: $Path\$Name = $Value" "OK"
}

# ── System Dark Mode ──────────────────────────────────────────────────────────
Write-Log "--- Applying System Dark Mode ---"
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "AppsUseLightTheme"   0
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "SystemUsesLightTheme" 0
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "AppsUseLightTheme"   0
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "SystemUsesLightTheme" 0
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "EnableTransparency"   1
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "ColorPrevalence"      0

# ── Transparency & Acrylic (Windows 10 + 11) ─────────────────────────────────
Write-Log "--- Applying Transparency Tweaks ---"
# Taskbar translucency
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "UseOLEDTaskbarTransparency" 1
# Acrylic start menu (Windows 10)
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "EnableBlurBehind" 1
# Windows 11 Mica/Acrylic material backend
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "UseWindowsDarkMode"     1
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "EnableAeroPeek"         1
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "AlwaysHibernateThumbnails" 0
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "Composition"            1
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorPrevalence"        0

# ── Title Bar Colors (ARGB format) ────────────────────────────────────────────
Write-Log "--- Applying Title Bar Accent Color ---"
# ArizenOS accent: deep slate blue (#1E293B) in COLORREF = 0x003B291E
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "AccentColor"            0xFF1E293B "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "AccentColorInactive"    0xFF0F172A "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorizationColor"      0xC41E293B "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorizationColorBalance" 89        "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorizationAfterglow"  0xC41E293B "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorizationAfterglowBalance" 10   "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "ColorizationBlurBalance" 1         "DWord"
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\DWM" "GlassOpacity"           85         "DWord"

# ── Taskbar Transparency via OldNewExplorer style ─────────────────────────────
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "TaskbarTranslucent" 1

# ── Notification Center Acrylic ───────────────────────────────────────────────
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ImmersiveShell" "UseAcrylicSurface" 1

# ── Visual Effects (Prefer clarity over animation bloat) ─────────────────────
Write-Log "--- Applying Visual Performance Settings ---"
$VisPerfKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
New-Item -Path $VisPerfKey -Force | Out-Null
# Custom visual effects bitmask: keep smooth edges, shadows for windows, thumbnails
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 3 -Type DWord -Force
$AdvKey = "HKCU:\Control Panel\Desktop"
Set-ItemProperty -Path $AdvKey -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)) -Type Binary -Force
Write-Log "Visual FX custom mask applied" "OK"

# ── Apply Theme (restart Explorer) ───────────────────────────────────────────
Write-Log "--- Restarting Explorer to apply changes ---"
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process explorer
Write-Log "Explorer restarted" "OK"

Write-Log "=== ArizenOS Theme COMPLETE === Log: $LogPath"
