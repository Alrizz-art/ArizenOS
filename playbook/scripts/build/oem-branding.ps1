#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS OEM Branding Script
.DESCRIPTION
    Applies ArizenOS identity to Windows System Information, About page,
    lock screen support info, and OEM logo registration.
.VERSION 2.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LogPath = "$env:SystemDrive\ArizenOS\Logs\oem_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

# ── Asset Paths ───────────────────────────────────────────────────────────────
$OEMDir    = "$env:SystemDrive\ArizenOS\OEM"
$LogoSrc   = "$PSScriptRoot\..\assets\logos\arizenOS_logo_oem.bmp"  # 120x120 BMP required
$LogoDst   = "$OEMDir\arizenOS_logo.bmp"

New-Item -ItemType Directory -Force -Path $OEMDir | Out-Null

# Copy logo if it exists
if (Test-Path $LogoSrc) {
    Copy-Item $LogoSrc $LogoDst -Force
    Write-Log "OEM logo copied to $LogoDst" "OK"
} else {
    Write-Log "OEM logo source not found — branding will apply without logo: $LogoSrc" "WARN"
}

# ── OEM Registry Keys ─────────────────────────────────────────────────────────
$OEMKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation"
New-Item -Path $OEMKey -Force -ErrorAction SilentlyContinue | Out-Null

$OEMInfo = @{
    Manufacturer    = "ArizenOS Project"
    Model           = "ArizenOS Edition"
    SupportURL      = "https://github.com/Alrizz-art/ArizenOS"
    SupportHours    = "Community Support — GitHub Issues"
    SupportPhone    = ""
    Logo            = if (Test-Path $LogoDst) { $LogoDst } else { "" }
}

foreach ($key in $OEMInfo.Keys) {
    Set-ItemProperty -Path $OEMKey -Name $key -Value $OEMInfo[$key] -Type String -Force
    Write-Log "OEM[$key] = $($OEMInfo[$key])" "OK"
}

# ── System Properties Branding (sysdm.cpl) ───────────────────────────────────
$RegKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
Set-ItemProperty -Path $RegKey -Name "RegisteredOrganization" -Value "ArizenOS" -Type String -Force
Set-ItemProperty -Path $RegKey -Name "RegisteredOwner"        -Value "ArizenOS User" -Type String -Force
Write-Log "Registered org/owner updated" "OK"

# ── Lock Screen Support Phone / URL ──────────────────────────────────────────
$LockKey = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability"
New-Item -Path $LockKey -Force -ErrorAction SilentlyContinue | Out-Null
# NOTE: Lock screen OEM text is controlled via MDM or Unattend.xml in full enterprise builds

# ── Remove OEM Bloatware Links ────────────────────────────────────────────────
$quickAssist = "$env:SystemRoot\System32\QuickAssist.exe"
if (Test-Path $quickAssist) {
    Write-Log "Quick Assist present — skipping (user may need)" "INFO"
}

# ── Taskbar / Start Branding (Windows 11) ────────────────────────────────────
$taskbarKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
# Show full taskbar on all monitors
Set-ItemProperty -Path $taskbarKey -Name "MMTaskbarEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
# Align Start button to left (Windows 11 classic feel option)
# Set-ItemProperty -Path $taskbarKey -Name "TaskbarAl" -Value 0 -Type DWord -Force
Write-Log "Taskbar preferences applied" "OK"

Write-Log "=== ArizenOS OEM Branding COMPLETE === Log: $LogPath"
