#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Wallpaper Setup
.DESCRIPTION
    Deploys ArizenOS branded wallpapers to system directory and sets
    the active wallpaper for current user. Also configures lock screen.
.VERSION 2.0.0
#>

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WallpaperHelper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
    public const int SPI_SETDESKWALLPAPER = 20;
    public const int SPIF_UPDATEINIFILE   = 0x01;
    public const int SPIF_SENDCHANGE      = 0x02;
}
"@

$WallpaperSrc  = "$PSScriptRoot\..\assets\wallpapers"
$WallpaperDst  = "$env:SystemDrive\ArizenOS\Wallpapers"
$DefaultWall   = "$WallpaperDst\arizenOS_default.jpg"

New-Item -ItemType Directory -Force -Path $WallpaperDst | Out-Null

if (Test-Path $WallpaperSrc) {
    Copy-Item "$WallpaperSrc\*" $WallpaperDst -Recurse -Force
    Write-Host "[OK] Wallpapers deployed to $WallpaperDst"
} else {
    Write-Host "[WARN] Wallpaper source not found: $WallpaperSrc"
}

if (Test-Path $DefaultWall) {
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name Wallpaper -Value $DefaultWall
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name WallpaperStyle -Value "10"  # Fill
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name TileWallpaper -Value "0"
    [WallpaperHelper]::SystemParametersInfo(
        [WallpaperHelper]::SPI_SETDESKWALLPAPER, 0, $DefaultWall,
        [WallpaperHelper]::SPIF_UPDATEINIFILE -bor [WallpaperHelper]::SPIF_SENDCHANGE
    ) | Out-Null
    Write-Host "[OK] Wallpaper set: $DefaultWall"
}

# Lock Screen via Group Policy
$LockScreenKey = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization"
New-Item -Path $LockScreenKey -Force | Out-Null
$LockImg = "$WallpaperDst\arizenOS_lockscreen.jpg"
if (Test-Path $LockImg) {
    Set-ItemProperty -Path $LockScreenKey -Name "LockScreenImage" -Value $LockImg -Type String -Force
    Set-ItemProperty -Path $LockScreenKey -Name "LockScreenOverlaysDisabled" -Value 1 -Type DWord -Force
    Write-Host "[OK] Lock screen set: $LockImg"
}

Write-Host "=== ArizenOS Wallpaper Setup COMPLETE ==="
