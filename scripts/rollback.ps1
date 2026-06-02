#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Rollback Script (SCR-13)
.DESCRIPTION
    Restores system to pre-ArizenOS state using registry backup.
    Args: -Action [VerifyBackup|ImportRegistry|RemoveAssets|RevertDeveloper|Cleanup]
          -Confirm <bool string> (for RemoveAssets)
    Exit 0 = success, Exit 1 = fatal failure, Exit 2 = warning.
.VERSION 2.1.0
#>

param(
    [ValidateSet("VerifyBackup","ImportRegistry","RemoveAssets","RevertDeveloper","Cleanup","Full")]
    [string]$Action = "Full",
    [string]$Confirm = "false",

    # Legacy switch-style params (kept for backward compat)
    [switch]$RestoreRegistry,
    [switch]$RestoreApps,
    [switch]$UseRestorePoint,
    [switch]$Full
)

$BackupRoot  = "$env:APPDATA\ArizenOS\backup"
$BackupFile  = "$BackupRoot\registry-backup.reg"
$AssetsRoot  = "$env:ProgramData\ArizenOS"
$LogDir      = "$env:SystemDrive\ArizenOS\Logs"
$LogPath     = "$LogDir\rollback_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-13] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

# Handle legacy switches
if ($RestoreRegistry) { $Action = "ImportRegistry" }
if ($Full)            { $Action = "Full" }

function Invoke-VerifyBackup {
    Write-Log "Verifying registry backup..."
    if (-not (Test-Path $BackupFile)) {
        Write-Log "Registry backup NOT found: $BackupFile" "ERROR"
        Write-Log "Use Windows System Restore instead: Control Panel > Recovery > Open System Restore" "ERROR"
        return 1
    }
    $size = (Get-Item $BackupFile).Length
    if ($size -lt 100) {
        Write-Log "Backup file appears empty or corrupt ($size bytes)." "ERROR"
        return 1
    }
    Write-Log "Backup found: $BackupFile ($size bytes)" "OK"
    return 0
}

function Invoke-ImportRegistry {
    Write-Log "Restoring registry from backup: $BackupFile"
    if (-not (Test-Path $BackupFile)) {
        Write-Log "Backup file not found. Cannot restore." "ERROR"
        return 1
    }
    try {
        $result = reg import "$BackupFile" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Registry restored successfully." "OK"
            return 0
        } else {
            Write-Log "reg import returned exit code $LASTEXITCODE : $result" "ERROR"
            return 1
        }
    } catch {
        Write-Log "Failed to import registry: $($_.Exception.Message)" "ERROR"
        return 1
    }
}

function Invoke-RemoveAssets {
    param([bool]$DoRemove)
    if (-not $DoRemove) {
        Write-Log "User chose to keep asset files. Skipping removal." "INFO"
        return 0
    }
    Write-Log "Removing ArizenOS asset files..."
    $dirs = @(
        "$AssetsRoot\branding",
        "$AssetsRoot\wallpapers",
        "$AssetsRoot"
    )
    $exitCode = 0
    foreach ($dir in $dirs) {
        if (Test-Path $dir) {
            try {
                Remove-Item -Path $dir -Recurse -Force -ErrorAction Stop
                Write-Log "  Removed: $dir" "OK"
            } catch {
                Write-Log "  Failed to remove $dir : $($_.Exception.Message)" "WARN"
                $exitCode = 2
            }
        }
    }
    return $exitCode
}

function Invoke-RevertDeveloper {
    Write-Log "Reverting developer settings..."
    $devKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    try {
        if (Test-Path $devKey) {
            Set-ItemProperty -Path $devKey -Name "AllowDevelopmentWithoutDevLicense" -Value 0 -Type DWord -Force
            Set-ItemProperty -Path $devKey -Name "AllowAllTrustedApps"               -Value 0 -Type DWord -Force
            Write-Log "Developer Mode disabled." "OK"
        } else {
            Write-Log "Developer Mode key not found — skipping." "INFO"
        }
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
        Write-Log "Long path support reverted." "OK"
        return 0
    } catch {
        Write-Log "Failed to revert developer settings: $($_.Exception.Message)" "WARN"
        return 2
    }
}

function Invoke-Cleanup {
    Write-Log "Cleaning up ArizenOS Start Menu entries..."
    $smDir = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\ArizenOS"
    try {
        if (Test-Path $smDir) {
            Remove-Item -Path $smDir -Recurse -Force
            Write-Log "Start Menu folder removed: $smDir" "OK"
        }
        $stagedScript = "$env:SystemDrive\ArizenOS\rollback.ps1"
        if (Test-Path $stagedScript) {
            Remove-Item -Path $stagedScript -Force
            Write-Log "Staged rollback script removed." "OK"
        }
        return 0
    } catch {
        Write-Log "Cleanup warning: $($_.Exception.Message)" "WARN"
        return 2
    }
}

Write-Log "=== ArizenOS Rollback Starting (Action: $Action) ==="

$result = 0

switch ($Action) {
    "VerifyBackup"   { $result = Invoke-VerifyBackup }
    "ImportRegistry" { $result = Invoke-ImportRegistry }
    "RemoveAssets"   {
        $doRemove = ($Confirm -eq "true" -or $Confirm -eq "1" -or $Confirm -eq "\$true")
        $result = Invoke-RemoveAssets -DoRemove $doRemove
    }
    "RevertDeveloper" { $result = Invoke-RevertDeveloper }
    "Cleanup"         { $result = Invoke-Cleanup }
    "Full" {
        $r1 = Invoke-VerifyBackup;    if ($r1 -gt $result) { $result = $r1 }; if ($r1 -eq 1) { Write-Log "ABORT: no backup found."; exit 1 }
        $r2 = Invoke-ImportRegistry;  if ($r2 -gt $result) { $result = $r2 }
        $r3 = Invoke-RemoveAssets -DoRemove $false
        $r4 = Invoke-RevertDeveloper; if ($r4 -gt $result) { $result = $r4 }
        $r5 = Invoke-Cleanup;         if ($r5 -gt $result) { $result = $r5 }
    }
}

Write-Log "=== Rollback complete. Exit: $result ==="
exit $result
