#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Registry Backup Script (SCR-03)
.DESCRIPTION
    Exports all registry keys that will be modified by this playbook to a
    .reg backup file. ABORT if backup fails — rollback is not possible without it.
    Exit 0 = success, Exit 1 = fatal failure.
.VERSION 1.0.0
#>

param(
    [string]$OutputPath = "$env:APPDATA\ArizenOS\backup\registry-backup.reg"
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\backup_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-03] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

$keysToBackup = @(
    "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation",
    "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
    "HKCU\SOFTWARE\Microsoft\Windows\DWM",
    "HKCU\Control Panel\Desktop",
    "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
    "HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization",
    "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP",
    "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
)

$backupDir = Split-Path $OutputPath
try {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Write-Log "Backup directory ensured: $backupDir"
} catch {
    Write-Log "Failed to create backup directory: $($_.Exception.Message)" "ERROR"
    exit 1
}

if (Test-Path $OutputPath) {
    $ts  = Get-Date -f 'yyyyMMdd_HHmmss'
    $old = "$OutputPath.$ts.bak"
    Move-Item -Path $OutputPath -Destination $old -Force
    Write-Log "Existing backup moved to: $old"
}

$combinedContent = "Windows Registry Editor Version 5.00`r`n`r`n"
$successCount    = 0
$failCount       = 0

foreach ($key in $keysToBackup) {
    $tempFile = "$env:TEMP\arizen_reg_$([System.IO.Path]::GetRandomFileName()).reg"
    Write-Log "Backing up: $key"
    $result = reg export "$key" "$tempFile" /y 2>&1
    if ($LASTEXITCODE -eq 0 -and (Test-Path $tempFile)) {
        $content = Get-Content $tempFile -Raw -Encoding Unicode
        $content = $content -replace "^Windows Registry Editor Version 5\.00\r?\n\r?\n", ""
        $combinedContent += $content + "`r`n"
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        $successCount++
        Write-Log "  Backed up OK." "OK"
    } else {
        Write-Log "  Key not found or export failed (may not exist yet — normal for fresh installs)." "WARN"
        $failCount++
    }
}

try {
    [System.IO.File]::WriteAllText($OutputPath, $combinedContent, [System.Text.Encoding]::Unicode)
    Write-Log "Registry backup written: $OutputPath" "OK"
} catch {
    Write-Log "Failed to write backup file: $($_.Exception.Message)" "ERROR"
    exit 1
}

$manifestPath = "$backupDir\manifest.json"
$manifest = @{
    version      = "0.1.0"
    date         = (Get-Date -f 'yyyy-MM-ddTHH:mm:ss')
    backup_path  = $OutputPath
    keys_backed_up = $successCount
    keys_missing   = $failCount
} | ConvertTo-Json
$manifest | Out-File -FilePath $manifestPath -Encoding UTF8 -Force
Write-Log "Backup manifest written: $manifestPath"

if ((Get-Item $OutputPath).Length -gt 0) {
    Write-Log "Backup verified: file is non-empty ($((Get-Item $OutputPath).Length) bytes)." "OK"
    exit 0
} else {
    Write-Log "Backup file is empty — export failed." "ERROR"
    exit 1
}
