#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS System Restore Point Creator (SCR-02)
.DESCRIPTION
    Creates a Windows System Restore Point before any changes are applied.
    Exit 0 = created, Exit 2 = failed (soft warn, user prompted).
.VERSION 1.0.0
#>

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\restore_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-02] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

Write-Log "Creating System Restore Point: 'Before ArizenOS v0.1'..."

try {
    Enable-ComputerRestore -Drive "$env:SystemDrive\" -ErrorAction SilentlyContinue
    Checkpoint-Computer -Description "Before ArizenOS v0.1" -RestorePointType APPLICATION_INSTALL -ErrorAction Stop
    Write-Log "System Restore Point created successfully." "OK"
    exit 0
} catch {
    Write-Log "System Restore Point creation failed: $($_.Exception.Message)" "WARN"
    Write-Log "Installation can continue using registry backup as rollback mechanism." "WARN"
    exit 2
}
