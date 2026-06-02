#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Wallpaper & Lock Screen Script (SCR-06)
.DESCRIPTION
    Sets desktop wallpaper and configures lock screen via dual-path strategy.
    Args: -Action [SetDesktopWallpaper|LockScreenPolicy|LockScreenCSP|GpUpdate] -Asset <filename>
    Exit 0 = success, Exit 1 = failure, Exit 2 = warning.
.VERSION 1.0.0
#>

param(
    [ValidateSet("SetDesktopWallpaper","LockScreenPolicy","LockScreenCSP","GpUpdate")]
    [string]$Action,
    [string]$Asset = "arizenOS_dark.jpg"
)

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WallpaperAPI {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
    public const int SPI_SETDESKWALLPAPER = 20;
    public const int SPIF_UPDATEINIFILE   = 0x01;
    public const int SPIF_SENDCHANGE      = 0x02;
}
"@ -ErrorAction SilentlyContinue

$LogDir       = "$env:SystemDrive\ArizenOS\Logs"
$LogPath      = "$LogDir\wallpaper_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
$WallpaperDir = "$env:ProgramData\ArizenOS\wallpapers"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-06] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = "String")
    if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
    Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force
}

switch ($Action) {

    "SetDesktopWallpaper" {
        $wallPath = "$WallpaperDir\$Asset"
        Write-Log "Setting desktop wallpaper: $wallPath"
        if (-not (Test-Path $wallPath)) {
            Write-Log "Wallpaper file not found: $wallPath" "WARN"
            exit 2
        }
        try {
            Set-Reg -Path "HKCU:\Control Panel\Desktop" -Name "Wallpaper" -Value $wallPath
            Set-Reg -Path "HKCU:\Control Panel\Desktop" -Name "WallpaperStyle" -Value "10" -Type "String"
            Set-Reg -Path "HKCU:\Control Panel\Desktop" -Name "TileWallpaper" -Value "0" -Type "String"
            $result = [WallpaperAPI]::SystemParametersInfo([WallpaperAPI]::SPI_SETDESKWALLPAPER, 0, $wallPath, [WallpaperAPI]::SPIF_UPDATEINIFILE -bor [WallpaperAPI]::SPIF_SENDCHANGE)
            Write-Log "SystemParametersInfo result: $result" "OK"
            exit 0
        } catch {
            Write-Log "Failed to set wallpaper: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }

    "LockScreenPolicy" {
        $lsPath = "$WallpaperDir\arizenOS_lockscreen.jpg"
        Write-Log "Writing lock screen via Policy path: $lsPath"
        if (-not (Test-Path $lsPath)) {
            Write-Log "Lock screen file not found: $lsPath" "WARN"; exit 2
        }
        try {
            Set-Reg -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization" -Name "LockScreenImage" -Value $lsPath
            Write-Log "Policy LockScreenImage set." "OK"
            exit 0
        } catch {
            Write-Log "Failed to write LockScreenPolicy: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }

    "LockScreenCSP" {
        $lsPath = "$WallpaperDir\arizenOS_lockscreen.jpg"
        Write-Log "Writing lock screen via PersonalizationCSP: $lsPath"
        if (-not (Test-Path $lsPath)) {
            Write-Log "Lock screen file not found: $lsPath" "WARN"; exit 2
        }
        try {
            $cspKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"
            Set-Reg -Path $cspKey -Name "LockScreenImagePath"   -Value $lsPath
            Set-Reg -Path $cspKey -Name "LockScreenImageUrl"    -Value $lsPath
            Set-Reg -Path $cspKey -Name "LockScreenImageStatus" -Value 1 -Type "DWord"
            Write-Log "PersonalizationCSP lock screen values set." "OK"
            exit 0
        } catch {
            Write-Log "Failed to write LockScreenCSP: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }

    "GpUpdate" {
        Write-Log "Running gpupdate /force..."
        try {
            $out = gpupdate /force 2>&1
            Write-Log "gpupdate output: $out"
            Write-Log "Group Policy refreshed." "OK"
            exit 0
        } catch {
            Write-Log "gpupdate failed: $($_.Exception.Message)" "WARN"
            exit 2
        }
    }
}
