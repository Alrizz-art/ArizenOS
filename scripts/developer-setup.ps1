#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Developer Environment Setup
.DESCRIPTION
    Installs and configures a complete developer toolchain:
    WSL2, WinGet packages, Git, Node.js, VS Code, Windows Terminal,
    and developer-friendly OS settings.
.VERSION 2.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$LogPath = "$env:SystemDrive\ArizenOS\Logs\devsetup_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message" | Tee-Object -FilePath $LogPath -Append | Write-Host
}

function Install-WinGetPackage {
    param([string]$Id, [string]$Name)
    Write-Log "Installing $Name ($Id)..."
    $result = winget install --id $Id --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq -1978335189) {
        Write-Log "$Name installed/already present" "OK"
    } else {
        Write-Log "$Name install exit code: $LASTEXITCODE" "WARN"
    }
}

Write-Log "--- Enabling Windows Developer Mode ---"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" `
    -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord -Force

Write-Log "--- Enabling WSL2 ---"
$wsl = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -ErrorAction SilentlyContinue
if ($wsl.State -ne "Enabled") {
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart | Out-Null
}
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart -ErrorAction SilentlyContinue | Out-Null
wsl --set-default-version 2 2>$null

Write-Log "--- Installing Core Developer Packages ---"
$packages = @(
    @{ Id = "Git.Git";                    Name = "Git" }
    @{ Id = "Microsoft.WindowsTerminal";  Name = "Windows Terminal" }
    @{ Id = "Microsoft.VisualStudioCode"; Name = "VS Code" }
    @{ Id = "OpenJS.NodeJS.LTS";          Name = "Node.js LTS" }
    @{ Id = "Python.Python.3.12";         Name = "Python 3.12" }
    @{ Id = "GitHub.cli";                 Name = "GitHub CLI" }
    @{ Id = "Docker.DockerDesktop";       Name = "Docker Desktop" }
    @{ Id = "Microsoft.PowerShell";       Name = "PowerShell 7" }
    @{ Id = "BurntSushi.ripgrep.MSVC";    Name = "ripgrep" }
    @{ Id = "Starship.Starship";          Name = "Starship Prompt" }
)
foreach ($pkg in $packages) { Install-WinGetPackage -Id $pkg.Id -Name $pkg.Name }

Write-Log "--- Configuring Git Defaults ---"
git config --global init.defaultBranch main  2>$null
git config --global core.autocrlf input      2>$null
git config --global core.editor "code --wait" 2>$null
git config --global pull.rebase false        2>$null
git config --global push.autoSetupRemote true 2>$null
git config --global credential.helper manager 2>$null

Write-Log "--- Developer Registry Tweaks ---"
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 0 -Force
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "Hidden" -Value 1 -Force
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Force
Set-Service -Name WSearch -StartupType Manual -ErrorAction SilentlyContinue

Write-Log "=== ArizenOS Developer Setup COMPLETE === Reboot required for WSL2."
