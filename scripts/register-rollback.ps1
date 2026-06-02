#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Rollback Shortcut Registration (SCR-11)
.DESCRIPTION
    Creates a Start Menu shortcut for ArizenOS rollback.
    Exit 0 = success, Exit 1 = failure.
.VERSION 1.0.0
#>

$LogDir   = "$env:SystemDrive\ArizenOS\Logs"
$LogPath  = "$LogDir\register_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-11] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

$StartMenuDir = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\ArizenOS"
$ShortcutPath = "$StartMenuDir\Rollback ArizenOS.lnk"
$ScriptTarget = "$env:SystemDrive\ArizenOS\rollback.ps1"

Write-Log "Registering ArizenOS Start Menu shortcuts..."

try {
    New-Item -ItemType Directory -Force -Path $StartMenuDir | Out-Null

    # Copy rollback script to accessible location
    $rollbackSrc = Join-Path $PSScriptRoot "rollback.ps1"
    if (Test-Path $rollbackSrc) {
        New-Item -ItemType Directory -Force -Path "$env:SystemDrive\ArizenOS" | Out-Null
        Copy-Item $rollbackSrc $ScriptTarget -Force
        Write-Log "Rollback script staged at: $ScriptTarget" "OK"
    }

    $WScript  = New-Object -ComObject WScript.Shell
    $Shortcut = $WScript.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath       = "powershell.exe"
    $Shortcut.Arguments        = "-NonInteractive -ExecutionPolicy Bypass -File `"$ScriptTarget`" -Action ImportRegistry"
    $Shortcut.WorkingDirectory = "$env:SystemDrive\ArizenOS"
    $Shortcut.Description      = "Roll back ArizenOS changes"
    $Shortcut.WindowStyle      = 1
    $Shortcut.Save()

    Write-Log "Start Menu shortcut created: $ShortcutPath" "OK"
    exit 0
} catch {
    Write-Log "Failed to create shortcut: $($_.Exception.Message)" "ERROR"
    exit 1
}
