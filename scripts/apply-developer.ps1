#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Developer Environment Setup (SCR-09)
.DESCRIPTION
    Enables Developer Mode, app sideloading, long path support.
    Optionally installs developer toolchain via WinGet.
    Exit 0 = success, Exit 1 = fatal, Exit 2 = partial.
.VERSION 1.0.0
#>

param(
    [switch]$SkipWinGet
)

$LogDir  = "$env:SystemDrive\ArizenOS\Logs"
$LogPath = "$LogDir\developer_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [SCR-09] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = "DWord")
    if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
    Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force
    Write-Log "  SET: $Name = $Value" "OK"
}

Write-Log "--- Developer Setup Phase ---"

# 1. Developer Mode
Write-Log "Enabling Developer Mode..."
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" "AllowDevelopmentWithoutDevLicense" 1
Set-Reg "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" "AllowAllTrustedApps"               1

# 2. Long path support
Write-Log "Enabling Long Path Support (>260 chars)..."
Set-Reg "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" "LongPathsEnabled" 1

# 3. Show file extensions and hidden files
Write-Log "Configuring Explorer: show extensions + hidden files..."
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "HideFileExt"       0
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "Hidden"            1
Set-Reg "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "ShowSuperHidden"   0

# 4. WinGet packages (optional)
if (-not $SkipWinGet) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        $packages = @(
            @{ id = "Git.Git";                 name = "Git"            },
            @{ id = "Microsoft.WindowsTerminal"; name = "Windows Terminal" },
            @{ id = "Microsoft.VisualStudioCode"; name = "VS Code"     },
            @{ id = "OpenJS.NodeJS.LTS";         name = "Node.js LTS"  }
        )
        foreach ($pkg in $packages) {
            Write-Log "Installing $($pkg.name)..."
            $out = winget install --id $pkg.id --silent --accept-package-agreements --accept-source-agreements 2>&1
            $code = $LASTEXITCODE
            if ($code -eq 0 -or $code -eq -1978335189) {
                Write-Log "  $($pkg.name): installed/already present." "OK"
            } else {
                Write-Log "  $($pkg.name): exit code $code (non-fatal)." "WARN"
            }
        }
    } else {
        Write-Log "WinGet not found — skipping package installation." "WARN"
    }
}

Write-Log "Developer setup complete." "OK"
exit 0
