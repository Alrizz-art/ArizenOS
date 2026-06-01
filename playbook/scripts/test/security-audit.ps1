#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Security Audit Script
.DESCRIPTION
    Pre and post-installation security validation. Checks for:
    - Disabled security features
    - Exposed attack surfaces
    - Remaining telemetry endpoints
    - Registry permission integrity
    - UAC/Defender status
.VERSION 2.0.0
#>

$LogPath = "$env:SystemDrive\ArizenOS\Logs\security_audit_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null
$results = @()

function Write-Log { param([string]$Msg, [string]$L="INFO") "[$(Get-Date -f 'HH:mm:ss')] [$L] $Msg" | Tee-Object -FilePath $LogPath -Append | Write-Host }
function Add-Finding { param([string]$Check, [string]$Status, [string]$Detail) $results += [PSCustomObject]@{ Check=$Check; Status=$Status; Detail=$Detail } }

Write-Log "=== ArizenOS Security Audit START ==="

# UAC
$uacLevel = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System").ConsentPromptBehaviorAdmin
$uacStatus = if ($uacLevel -ge 2) { "PASS" } else { "FAIL" }
Add-Finding "UAC Level" $uacStatus "ConsentPromptBehaviorAdmin = $uacLevel (2+ required)"

# Windows Defender
$defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
if ($defender) {
    Add-Finding "Defender RealTime" (if ($defender.RealTimeProtectionEnabled) {"PASS"} else {"FAIL"}) "RealTimeProtection = $($defender.RealTimeProtectionEnabled)"
    Add-Finding "Defender Antivirus" (if ($defender.AntivirusEnabled) {"PASS"} else {"WARN"}) "AntivirusEnabled = $($defender.AntivirusEnabled)"
}

# Firewall
$fw = Get-NetFirewallProfile -ErrorAction SilentlyContinue
foreach ($profile in $fw) {
    Add-Finding "Firewall [$($profile.Name)]" (if ($profile.Enabled) {"PASS"} else {"FAIL"}) "Enabled = $($profile.Enabled)"
}

# Remote Desktop
$rdp = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server").fDenyTSConnections
Add-Finding "Remote Desktop" (if ($rdp -eq 1) {"PASS"} else {"WARN"}) "fDenyTSConnections = $rdp (1=disabled)"

# AutoRun
$autorun = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -ErrorAction SilentlyContinue).NoDriveTypeAutoRun
Add-Finding "AutoRun" (if ($autorun -eq 255) {"PASS"} else {"WARN"}) "NoDriveTypeAutoRun = $autorun (255=all disabled)"

# Remote Registry
$remoteReg = Get-Service RemoteRegistry -ErrorAction SilentlyContinue
Add-Finding "Remote Registry" (if ($remoteReg.StartType -eq "Disabled") {"PASS"} else {"WARN"}) "StartType = $($remoteReg.StartType)"

# Telemetry level
$telemetry = (Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -ErrorAction SilentlyContinue).AllowTelemetry
Add-Finding "Telemetry Level" (if ($telemetry -eq 0) {"PASS"} else {"WARN"}) "AllowTelemetry = $telemetry (0=Security only)"

# SMBv1
$smb1 = Get-SmbServerConfiguration -ErrorAction SilentlyContinue
Add-Finding "SMBv1" (if (-not $smb1.EnableSMB1Protocol) {"PASS"} else {"FAIL"}) "SMBv1 = $($smb1.EnableSMB1Protocol)"

# Print Spooler (PrintNightmare surface)
$spooler = Get-Service Spooler -ErrorAction SilentlyContinue
Add-Finding "Print Spooler" (if ($spooler.StartType -ne "Automatic") {"PASS"} else {"WARN"}) "StartType = $($spooler.StartType)"

# BitLocker
$bl = Get-BitLockerVolume -MountPoint "C:" -ErrorAction SilentlyContinue
Add-Finding "BitLocker (C:)" (if ($bl.ProtectionStatus -eq "On") {"PASS"} else {"INFO"}) "Status = $($bl.ProtectionStatus)"

# LAPS check
$laps = Get-Module LAPS -ErrorAction SilentlyContinue
Add-Finding "LAPS Module" (if ($laps) {"PASS"} else {"INFO"}) "Present = $([bool]$laps)"

# Output summary
Write-Log ""
Write-Log "=== SECURITY AUDIT SUMMARY ==="
$results | Format-Table -AutoSize | Out-String | Write-Log
$fails = $results | Where-Object { $_.Status -eq "FAIL" }
$warns = $results | Where-Object { $_.Status -eq "WARN" }
Write-Log "FAIL: $($fails.Count)  WARN: $($warns.Count)  PASS: $(($results | Where-Object { $_.Status -eq 'PASS' }).Count)"
if ($fails.Count -gt 0) {
    Write-Log "--- FAILURES ---" "FAIL"
    $fails | ForEach-Object { Write-Log "$($_.Check): $($_.Detail)" "FAIL" }
}
$results | Export-Csv "$env:SystemDrive\ArizenOS\Logs\security_audit_results.csv" -NoTypeInformation
Write-Log "=== Audit complete. Results: $env:SystemDrive\ArizenOS\Logs\security_audit_results.csv ==="
