#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Asset Deployment Script (SCR-04)
.DESCRIPTION
    Creates destination directories and copies branding/wallpaper assets.
    Exit 0 = all critical assets deployed, Exit 1 = critical failure, Exit 2 = non-critical warning.
.VERSION 1.0.0
#>

param(
    [ValidateSet("CreateDirs","CopyAssets","All")]
    [string]$Action = "All"
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\assets_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-04] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

$BrandingDest   = "$env:ProgramData\ArizenOS\branding"
$WallpaperDest  = "$env:ProgramData\ArizenOS\wallpapers"
$LogsDest       = "$env:APPDATA\ArizenOS\logs"
$BackupDest     = "$env:APPDATA\ArizenOS\backup"
$PlaybookRoot   = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AssetsRoot     = Join-Path $PlaybookRoot "assets"

function Invoke-CreateDirs {
    Write-Log "Creating ArizenOS directories..."
    foreach ($dir in @($BrandingDest, $WallpaperDest, $LogsDest, $BackupDest)) {
        try {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
            Write-Log "  Created: $dir" "OK"
        } catch {
            Write-Log "  Failed to create: $dir — $($_.Exception.Message)" "ERROR"
            return 1
        }
    }
    return 0
}

function Invoke-CopyAssets {
    $exitCode = 0
    $assets = @(
        @{ src = "logos\arizenOS_logo_oem.bmp";      dst = "$BrandingDest\oemlogo.bmp";             critical = $true  },
        @{ src = "wallpapers\arizenOS_dark.jpg";      dst = "$WallpaperDest\arizenOS_dark.jpg";      critical = $true  },
        @{ src = "wallpapers\arizenOS_lockscreen.jpg"; dst = "$WallpaperDest\arizenOS_lockscreen.jpg"; critical = $true },
        @{ src = "wallpapers\arizenOS_default.jpg";   dst = "$WallpaperDest\arizenOS_default.jpg";   critical = $false }
    )
    foreach ($asset in $assets) {
        $src = Join-Path $AssetsRoot $asset.src
        $dst = $asset.dst
        Write-Log "Deploying: $($asset.src) -> $dst"
        if (-not (Test-Path $src)) {
            if ($asset.critical) {
                Write-Log "  CRITICAL: Source not found: $src" "ERROR"
                $exitCode = 1
            } else {
                Write-Log "  WARNING: Source not found: $src (non-critical, skipping)" "WARN"
                if ($exitCode -eq 0) { $exitCode = 2 }
            }
            continue
        }
        try {
            Copy-Item -Path $src -Destination $dst -Force
            Write-Log "  Deployed OK." "OK"
        } catch {
            if ($asset.critical) {
                Write-Log "  CRITICAL copy failed: $($_.Exception.Message)" "ERROR"
                $exitCode = 1
            } else {
                Write-Log "  Non-critical copy failed: $($_.Exception.Message)" "WARN"
                if ($exitCode -eq 0) { $exitCode = 2 }
            }
        }
    }
    return $exitCode
}

$result = 0
if ($Action -in @("CreateDirs","All")) { $r = Invoke-CreateDirs; if ($r -gt $result) { $result = $r } }
if ($Action -in @("CopyAssets","All")) { $r = Invoke-CopyAssets; if ($r -gt $result) { $result = $r } }

Write-Log "deploy-assets complete. Exit: $result"
exit $result
