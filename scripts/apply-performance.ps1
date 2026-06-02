#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Performance Tweaks Script (SCR-08)
.DESCRIPTION
    Applies visual effects and performance registry tweaks.
    Detects OS version and applies appropriate UserPreferencesMask.
    Args: -Action [UserPrefsMask]
    Exit 0 = success, Exit 1 = failure, Exit 2 = warning.
.VERSION 1.0.0
#>

param(
    [ValidateSet("UserPrefsMask","All")]
    [string]$Action = "All"
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\performance_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-08] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = "DWord")
    if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
    Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force
    Write-Log "  SET: $Path\$Name = $Value [$Type]" "OK"
}

function Invoke-UserPrefsMask {
    $build = [System.Environment]::OSVersion.Version.Build
    Write-Log "Detected OS Build: $build"

    # UserPreferencesMask — balanced visual quality + performance
    # Win10 (build < 22000): 0x9E,0x1E,0x07,0x80,0x12,0x00,0x00,0x00
    # Win11 (build >= 22000): 0x9E,0x3E,0x07,0x80,0x12,0x00,0x00,0x00
    if ($build -ge 22000) {
        $mask = [byte[]](0x9E,0x3E,0x07,0x80,0x12,0x00,0x00,0x00)
        Write-Log "Applying Win11 UserPreferencesMask"
    } else {
        $mask = [byte[]](0x9E,0x1E,0x07,0x80,0x12,0x00,0x00,0x00)
        Write-Log "Applying Win10 UserPreferencesMask"
    }

    try {
        $regPath = "HKCU:\Control Panel\Desktop"
        if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
        Set-ItemProperty -Path $regPath -Name "UserPreferencesMask" -Value $mask -Type Binary -Force
        Write-Log "UserPreferencesMask applied." "OK"
        return 0
    } catch {
        Write-Log "Failed to write UserPreferencesMask: $($_.Exception.Message)" "ERROR"
        return 1
    }
}

$result = 0
if ($Action -in @("UserPrefsMask","All")) {
    $r = Invoke-UserPrefsMask
    if ($r -gt $result) { $result = $r }
}

Write-Log "apply-performance complete. Exit: $result"
exit $result
