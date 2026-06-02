#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS OEM Branding Registry Writer (SCR-05)
.DESCRIPTION
    Writes OEM branding registry values and logo path.
    Args: -Action [WriteLogo|Verify]
    Exit 0 = success, Exit 1 = failure.
.VERSION 1.0.0
#>

param(
    [ValidateSet("WriteLogo","Verify","All")]
    [string]$Action = "All"
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\oem_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-05] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = "String")
    try {
        if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
        Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force
        Write-Log "  SET: $Name = $Value" "OK"
        return $true
    } catch {
        Write-Log "  FAIL: $Name — $($_.Exception.Message)" "ERROR"
        return $false
    }
}

$OEMKey    = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation"
$LogoPath  = [System.Environment]::ExpandEnvironmentVariables("%ProgramData%\ArizenOS\branding\oemlogo.bmp")

function Invoke-WriteLogo {
    Write-Log "Writing OEM Logo registry path..."
    $ok = Set-Reg -Path $OEMKey -Name "Logo" -Value $LogoPath -Type "String"
    return ($ok ? 0 : 1)
}

function Invoke-Verify {
    Write-Log "Verifying OEM branding registry values (read-back)..."
    $exitCode = 0
    $expected = @{
        Manufacturer = "ArizenOS"
        Model        = "ArizenOS Experience Layer v0.1"
        SupportURL   = "https://github.com/Alrizz-art/ArizenOS"
        Logo         = $LogoPath
    }
    try {
        $props = Get-ItemProperty -Path $OEMKey -ErrorAction Stop
        foreach ($kv in $expected.GetEnumerator()) {
            $actual = $props.($kv.Key)
            if ($actual -eq $kv.Value) {
                Write-Log "  OK: $($kv.Key) = '$actual'" "OK"
            } else {
                Write-Log "  MISMATCH: $($kv.Key) — expected '$($kv.Value)' got '$actual'" "WARN"
                $exitCode = 2
            }
        }
        if (-not (Test-Path $LogoPath)) {
            Write-Log "  WARN: Logo file not found at: $LogoPath" "WARN"
            $exitCode = 2
        }
    } catch {
        Write-Log "  Cannot read OEM key: $($_.Exception.Message)" "ERROR"
        $exitCode = 1
    }
    return $exitCode
}

$result = 0
if ($Action -in @("WriteLogo","All")) { $r = Invoke-WriteLogo; if ($r -gt $result) { $result = $r } }
if ($Action -in @("Verify","All"))    { $r = Invoke-Verify;    if ($r -gt $result) { $result = $r } }

Write-Log "apply-oem-branding complete. Exit: $result"
exit $result
