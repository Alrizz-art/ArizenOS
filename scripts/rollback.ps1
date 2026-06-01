#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Rollback Script
.DESCRIPTION
    Restores system to pre-ArizenOS state using:
    1. Windows System Restore Point (created before installation)
    2. Registry backup restore
    3. Re-provisioning removed AppX packages from Windows image
.VERSION 2.0.0
#>

param(
    [switch]$RestoreRegistry,
    [switch]$RestoreApps,
    [switch]$UseRestorePoint,
    [switch]$Full
)

$BackupRoot = "$env:SystemDrive\ArizenOS\Backups"
$LogPath    = "$env:SystemDrive\ArizenOS\Logs\rollback_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message" | Tee-Object -FilePath $LogPath -Append | Write-Host
}

if ($Full) { $RestoreRegistry = $true; $RestoreApps = $true }

# ── Option 1: Use System Restore Point ───────────────────────────────────────
if ($UseRestorePoint) {
    Write-Log "--- Listing available restore points ---"
    Get-ComputerRestorePoint | Format-Table -AutoSize
    $rpId = Read-Host "Enter Sequence Number of the ArizenOS restore point"
    Write-Log "Initiating restore to point $rpId ..."
    Restore-Computer -RestorePoint $rpId -Confirm:$false
    Write-Log "Restore initiated. System will restart." "OK"
    return
}

# ── Option 2: Registry Restore ───────────────────────────────────────────────
if ($RestoreRegistry) {
    $regBackups = Get-ChildItem "$BackupRoot\registry" -Filter "*.reg" -ErrorAction SilentlyContinue
    if ($regBackups) {
        foreach ($rb in $regBackups) {
            Write-Log "Restoring registry: $($rb.Name)"
            reg import $rb.FullName 2>&1 | ForEach-Object { Write-Log $_ "REG" }
        }
    } else {
        Write-Log "No registry backups found at $BackupRoot\registry" "WARN"
    }
}

# ── Option 3: Re-provision Removed Apps ──────────────────────────────────────
if ($RestoreApps) {
    Write-Log "--- Re-provisioning removed AppX packages ---"
    $windowsDir = Read-Host "Path to Windows installation ISO/mount (e.g. D:\)"
    if (Test-Path "$windowsDir\Windows\System32\appwiz.cpl") {
        $appxPath = "$windowsDir\Windows\SystemApps"
        if (Test-Path $appxPath) {
            Get-ChildItem $appxPath -Filter "*.msix" | ForEach-Object {
                Add-AppxProvisionedPackage -Online -PackagePath $_.FullName -SkipLicense -ErrorAction SilentlyContinue
                Write-Log "Re-provisioned: $($_.Name)" "OK"
            }
        }
    } else {
        Write-Log "Invalid Windows source path — cannot re-provision apps." "WARN"
    }
}

# ── Restore OEM Info to Windows Defaults ─────────────────────────────────────
Write-Log "--- Clearing ArizenOS OEM Branding ---"
$oemKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation"
Remove-ItemProperty -Path $oemKey -Name "Manufacturer","Model","SupportURL","SupportHours","Logo" -ErrorAction SilentlyContinue
Write-Log "OEM keys cleared" "OK"

# ── Re-enable Telemetry Services ─────────────────────────────────────────────
Write-Log "--- Re-enabling disabled services ---"
@("DiagTrack","dmwappushservice","WerSvc","PcaSvc") | ForEach-Object {
    Set-Service -Name $_ -StartupType Automatic -ErrorAction SilentlyContinue
    Start-Service -Name $_ -ErrorAction SilentlyContinue
    Write-Log "Re-enabled: $_" "OK"
}

Write-Log "=== ArizenOS Rollback COMPLETE === Log: $LogPath"
Write-Log "Some changes (WSL2, Hyper-V) require a system restart to fully revert."
