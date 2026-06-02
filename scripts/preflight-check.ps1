#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Preflight Check Script (SCR-01)
.DESCRIPTION
    Validates that the target machine meets minimum requirements.
    Exit 0 = pass, Exit 1 = hard fail (abort), Exit 2 = soft warning (prompt).
.VERSION 1.0.0
#>

param(
    [ValidateSet("OsBuild","Elevation","SMode","DiskSpace","DomainJoined")]
    [string]$Check,
    [int]$MinBuild = 19045,
    [int]$MinMB    = 500
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\preflight_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-01] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

switch ($Check) {

    "OsBuild" {
        $build = [System.Environment]::OSVersion.Version.Build
        Write-Log "OS Build detected: $build (minimum: $MinBuild)"
        if ($build -ge $MinBuild) {
            Write-Log "OS build check PASSED" "OK"
            exit 0
        } elseif ($build -ge 17763) {
            Write-Log "OS build is below minimum. ArizenOS requires Windows 10 22H2 (build $MinBuild) or later." "WARN"
            exit 2
        } else {
            Write-Log "OS build is critically below minimum. Installation cannot proceed." "ERROR"
            exit 1
        }
    }

    "Elevation" {
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if ($isAdmin) {
            Write-Log "Administrator privileges confirmed." "OK"
            exit 0
        } else {
            Write-Log "ArizenOS must be run as Administrator." "ERROR"
            exit 1
        }
    }

    "SMode" {
        $sModeVal = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy" -ErrorAction SilentlyContinue).SkuPolicyRequired
        if ($sModeVal -eq 1) {
            Write-Log "Windows S Mode detected. ArizenOS cannot be installed on Windows S Mode." "ERROR"
            exit 1
        } else {
            Write-Log "S Mode check PASSED (not in S Mode)." "OK"
            exit 0
        }
    }

    "DiskSpace" {
        $freeGB  = [math]::Round((Get-PSDrive -Name C).Free / 1GB, 2)
        $freeMB  = [math]::Round((Get-PSDrive -Name C).Free / 1MB, 0)
        $warnMB  = 1024
        Write-Log "Free disk space: ${freeMB} MB (${freeGB} GB)"
        if ($freeMB -ge $warnMB) {
            Write-Log "Disk space check PASSED." "OK"
            exit 0
        } elseif ($freeMB -ge $MinMB) {
            Write-Log "Less than 1 GB free. Minimum is $MinMB MB. Proceed with caution." "WARN"
            exit 2
        } else {
            Write-Log "Insufficient disk space. ArizenOS requires at least $MinMB MB free." "ERROR"
            exit 1
        }
    }

    "DomainJoined" {
        $isDomain = (Get-WmiObject Win32_ComputerSystem -ErrorAction SilentlyContinue).PartOfDomain
        if ($isDomain) {
            Write-Log "Domain-joined machine detected. Group Policy Objects may override some ArizenOS settings. Warning only." "WARN"
            exit 2
        } else {
            Write-Log "Domain check PASSED (workgroup machine)." "OK"
            exit 0
        }
    }

    default {
        Write-Log "Unknown check: '$Check'. Valid values: OsBuild, Elevation, SMode, DiskSpace, DomainJoined" "ERROR"
        exit 1
    }
}
