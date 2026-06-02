#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Installation Finalizer (SCR-12)
.DESCRIPTION
    Writes a final entry to the installation log and performs cleanup.
    Args: -Version <string>
    Exit 0 = success, Exit 1 = failure.
.VERSION 1.0.0
#>

param(
    [string]$Version = "0.1.0"
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\install.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-12] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

Write-Log "============================================"
Write-Log "ArizenOS v$Version — Installation Complete"
Write-Log "============================================"
Write-Log "Timestamp : $(Get-Date -f 'yyyy-MM-dd HH:mm:ss')"
Write-Log "Machine   : $env:COMPUTERNAME"
Write-Log "User      : $env:USERNAME"
Write-Log "OS Build  : $([System.Environment]::OSVersion.Version.Build)"

# Verify key artifacts exist
$checks = @(
    @{ path = "$env:ProgramData\ArizenOS\manifest.json";           label = "Installation manifest" },
    @{ path = "$env:ProgramData\ArizenOS\branding\oemlogo.bmp";     label = "OEM logo" },
    @{ path = "$env:ProgramData\ArizenOS\wallpapers\arizenOS_dark.jpg"; label = "Dark wallpaper" },
    @{ path = "$env:APPDATA\ArizenOS\backup\registry-backup.reg";   label = "Registry backup" }
)

Write-Log ""
Write-Log "--- Post-install artifact verification ---"
$warnings = 0
foreach ($chk in $checks) {
    if (Test-Path $chk.path) {
        Write-Log "  [PRESENT] $($chk.label)" "OK"
    } else {
        Write-Log "  [MISSING] $($chk.label): $($chk.path)" "WARN"
        $warnings++
    }
}

Write-Log ""
if ($warnings -gt 0) {
    Write-Log "Installation complete with $warnings warning(s). See log for details." "WARN"
} else {
    Write-Log "All artifacts verified. Installation successful." "OK"
}
Write-Log "Log location: $LogPath"
Write-Log "============================================"

exit 0
