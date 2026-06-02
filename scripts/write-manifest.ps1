#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Installation Manifest Writer (SCR-10)
.DESCRIPTION
    Writes a JSON installation manifest to %ProgramData%\ArizenOS\manifest.json.
    Args: -Version <string> -Channel <string>
    Exit 0 = success, Exit 1 = failure.
.VERSION 1.0.0
#>

param(
    [string]$Version = "0.1.0",
    [string]$Channel = "alpha"
)

$LogDir      = "$env:SystemDrive\ArizenOS\Logs"
$LogPath     = "$LogDir\finalize_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
$ManifestDir = "$env:ProgramData\ArizenOS"
$ManifestOut = "$ManifestDir\manifest.json"
New-Item -ItemType Directory -Force -Path $LogDir         | Out-Null
New-Item -ItemType Directory -Force -Path $ManifestDir    | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-10] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

Write-Log "Writing installation manifest..."

$osBuild = [System.Environment]::OSVersion.Version.Build
$osCaption = (Get-WmiObject Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption

$manifest = [ordered]@{
    product          = "ArizenOS"
    version          = $Version
    channel          = $Channel
    installed_at     = (Get-Date -f 'yyyy-MM-ddTHH:mm:ssZ')
    installed_by     = $env:USERNAME
    machine_name     = $env:COMPUTERNAME
    os_build         = $osBuild
    os_caption       = $osCaption
    playbook_version = "1.0.0"
    features_applied = @(
        "oem_branding",
        "wallpaper",
        "dark_theme",
        "transparency",
        "performance",
        "aero_peek"
    )
    paths = @{
        branding   = "$env:ProgramData\ArizenOS\branding"
        wallpapers = "$env:ProgramData\ArizenOS\wallpapers"
        backup     = "$env:APPDATA\ArizenOS\backup\registry-backup.reg"
        logs       = "$env:SystemDrive\ArizenOS\Logs"
    }
    rollback = @{
        available = $true
        backup_path = "$env:APPDATA\ArizenOS\backup\registry-backup.reg"
        shortcut    = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\ArizenOS\Rollback ArizenOS.lnk"
    }
}

try {
    $json = $manifest | ConvertTo-Json -Depth 5
    $json | Out-File -FilePath $ManifestOut -Encoding UTF8 -Force
    Write-Log "Manifest written: $ManifestOut" "OK"
    exit 0
} catch {
    Write-Log "Failed to write manifest: $($_.Exception.Message)" "ERROR"
    exit 1
}
