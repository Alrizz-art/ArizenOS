#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ArizenOS Safe Debloat Script
.DESCRIPTION
    Removes telemetry, advertising, non-essential apps while preserving
    core OS functionality and recovery capabilities.
.VERSION 2.0.0
#>

param(
    [ValidateSet("Safe","Minimal")]
    [string]$Level = "Safe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ── Logging ───────────────────────────────────────────────────────────────────
$LogPath = "$env:SystemDrive\ArizenOS\Logs\debloat_$(Get-Date -f 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    $entry | Tee-Object -FilePath $LogPath -Append | Write-Host
}

# ── App Removal Lists ─────────────────────────────────────────────────────────
$MinimalRemoval = @(
    "Microsoft.BingNews"
    "Microsoft.BingWeather"
    "Microsoft.BingFinance"
    "Microsoft.BingSports"
    "Microsoft.BingFoodAndDrink"
    "Microsoft.BingHealthAndFitness"
    "Microsoft.BingTravel"
    "Microsoft.Advertising.Xaml"
    "Microsoft.MicrosoftStickyNotes"       # Optional: keep if user uses it
    "Microsoft.WindowsFeedbackHub"
    "Microsoft.WindowsMaps"
    "Microsoft.ZuneMusic"                  # Old Groove Music
    "Microsoft.ZuneVideo"                  # Movies & TV
    "Microsoft.MixedReality.Portal"
    "Microsoft.GetHelp"
    "Microsoft.Getstarted"
    "Microsoft.Wallet"
    "Microsoft.People"
    "Microsoft.YourPhone"
    "MicrosoftTeams"                       # Teams Chat (consumer)
    "Clipchamp.Clipchamp"
    "Microsoft.549981C3F5F10"              # Cortana
)

$SafeRemoval = $MinimalRemoval + @(
    "Microsoft.3DBuilder"
    "Microsoft.Print3D"
    "Microsoft.Microsoft3DViewer"
    "Microsoft.MicrosoftSolitaireCollection"
    "king.com.CandyCrushSaga"
    "king.com.CandyCrushFriends"
    "king.com.BubbleWitch3Saga"
    "Facebook.Facebook"
    "Twitter.Twitter"
    "Spotify.Spotify"
    "Microsoft.Xbox.TCUI"
    "Microsoft.XboxApp"
    "Microsoft.XboxGameOverlay"
    "Microsoft.XboxGamingOverlay"
    "Microsoft.XboxIdentityProvider"
    "Microsoft.XboxSpeechToTextOverlay"
    "Microsoft.GamingApp"
    "Microsoft.Office.OneNote"             # UWP OneNote (not desktop)
    "Microsoft.SkypeApp"
    "Microsoft.PowerAutomateDesktop"
    "Microsoft.Todos"
    "Microsoft.MicrosoftOfficeHub"
    "Microsoft.NetworkSpeedTest"
    "Microsoft.News"
    "Microsoft.OutlookForWindows"          # New UWP Outlook
    "Microsoft.OneDrive"                   # Optional: comment out if OneDrive used
)

# ── Packages to NEVER remove (safety guard) ───────────────────────────────────
$ProtectedApps = @(
    "Microsoft.WindowsStore"
    "Microsoft.StorePurchaseApp"
    "Microsoft.DesktopAppInstaller"        # WinGet
    "Microsoft.WindowsCalculator"
    "Microsoft.WindowsNotepad"
    "Microsoft.Paint"
    "Microsoft.MSPaint"
    "Microsoft.WindowsTerminal"
    "Microsoft.WindowsCamera"
    "Microsoft.MicrosoftEdge"
    "Microsoft.Edge"
    "Microsoft.NET"
    "Microsoft.VCLibs"
    "Microsoft.UI.Xaml"
    "Microsoft.WindowsAlarms"
    "Microsoft.WindowsSoundRecorder"
    "Microsoft.PowerShell"
)

# ── Telemetry Services ────────────────────────────────────────────────────────
$TelemetryServices = @(
    "DiagTrack"          # Connected User Experiences and Telemetry
    "dmwappushservice"   # WAP Push Message Routing Service
    "WerSvc"             # Windows Error Reporting
    "PcaSvc"             # Program Compatibility Assistant
    "RetailDemo"         # Retail Demo Service
    "MapsBroker"         # Downloaded Maps Manager
    "lfsvc"              # Geolocation Service
    "SharedAccess"       # Internet Connection Sharing (if not needed)
    "TapiSrv"            # Telephony (if not VoIP user)
    "Fax"                # Fax Service
    "RemoteRegistry"     # Remote Registry
)

# ── Scheduled Tasks to Disable ────────────────────────────────────────────────
$TelemetryTasks = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser"
    "\Microsoft\Windows\Application Experience\ProgramDataUpdater"
    "\Microsoft\Windows\Autochk\Proxy"
    "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator"
    "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip"
    "\Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask"
    "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector"
    "\Microsoft\Windows\Feedback\Siuf\DmClient"
    "\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload"
    "\Microsoft\Windows\Windows Error Reporting\QueueReporting"
    "\Microsoft\Windows\Device Information\Device"
)

# ── Functions ─────────────────────────────────────────────────────────────────
function Remove-AppxSafely {
    param([string]$PackageName)
    if ($ProtectedApps -contains $PackageName) {
        Write-Log "SKIPPED (protected): $PackageName" "WARN"
        return
    }
    try {
        $pkg = Get-AppxPackage -Name $PackageName -AllUsers -ErrorAction SilentlyContinue
        if ($pkg) {
            Remove-AppxPackage -Package $pkg.PackageFullName -AllUsers -ErrorAction Stop
            Write-Log "Removed AppX: $PackageName" "OK"
        }
        $prov = Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -eq $PackageName }
        if ($prov) {
            Remove-AppxProvisionedPackage -Online -PackageName $prov.PackageName -ErrorAction Stop | Out-Null
            Write-Log "Removed Provisioned: $PackageName" "OK"
        }
    } catch {
        Write-Log "Failed to remove $PackageName : $_" "WARN"
    }
}

function Disable-ServiceSafely {
    param([string]$ServiceName)
    try {
        $svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($svc) {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            Set-Service -Name $ServiceName -StartupType Disabled -ErrorAction Stop
            Write-Log "Disabled service: $ServiceName" "OK"
        }
    } catch {
        Write-Log "Failed to disable $ServiceName : $_" "WARN"
    }
}

function Disable-TelemetryTasks {
    foreach ($task in $TelemetryTasks) {
        try {
            Disable-ScheduledTask -TaskPath (Split-Path $task) -TaskName (Split-Path $task -Leaf) -ErrorAction Stop | Out-Null
            Write-Log "Disabled task: $task" "OK"
        } catch {
            Write-Log "Task not found (skip): $task" "INFO"
        }
    }
}

function Set-TelemetryRegistryPolicies {
    $policies = @{
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection"      = @{ AllowTelemetry = 0 }
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" = @{ AllowTelemetry = 0; MaxTelemetryAllowed = 0 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent"         = @{ DisableWindowsConsumerFeatures = 1 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo"      = @{ DisabledByGroupPolicy = 1 }
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"= @{ Enabled = 0 }
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy"        = @{ TailoredExperiencesWithDiagnosticDataEnabled = 0 }
        "HKCU:\SOFTWARE\Microsoft\InputPersonalization"                  = @{ RestrictImplicitInkCollection = 1; RestrictImplicitTextCollection = 1 }
        "HKCU:\SOFTWARE\Microsoft\Personalization\Settings"              = @{ AcceptedPrivacyPolicy = 0 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Speech"                       = @{ AllowSpeechModelUpdate = 0 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\TabletPC"             = @{ PreventHandwritingDataSharing = 1 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\CurrentVersion\Software Protection Platform" = @{ NoGenTicket = 1 }
        "HKLM:\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config"     = @{ AutoConnectAllowedOEM = 0 }
        "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WifiNetworkManager"  = @{ AllowAutoConnectToWiFiSenseHotspots = 0; AllowWiFiHotSpotReporting = 0 }
    }
    foreach ($path in $policies.Keys) {
        New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        foreach ($name in $policies[$path].Keys) {
            try {
                Set-ItemProperty -Path $path -Name $name -Value $policies[$path][$name] -Type DWord -Force -ErrorAction Stop
                Write-Log "Registry set: $path\$name = $($policies[$path][$name])" "OK"
            } catch {
                Write-Log "Registry failed: $path\$name : $_" "WARN"
            }
        }
    }
}

# ── Main Execution ────────────────────────────────────────────────────────────
Write-Log "=== ArizenOS Debloat START === Level: $Level"

Write-Log "--- Phase 1: Registry Telemetry Policies ---"
Set-TelemetryRegistryPolicies

Write-Log "--- Phase 2: Disable Telemetry Services ---"
foreach ($svc in $TelemetryServices) { Disable-ServiceSafely $svc }

Write-Log "--- Phase 3: Disable Scheduled Tasks ---"
Disable-TelemetryTasks

Write-Log "--- Phase 4: Remove AppX Packages ---"
$removeList = if ($Level -eq "Safe") { $SafeRemoval } else { $MinimalRemoval }
foreach ($app in $removeList) { Remove-AppxSafely $app }

Write-Log "--- Phase 5: Disable Cortana (All Versions) ---"
$cortanaPolicies = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search"
New-Item -Path $cortanaPolicies -Force -ErrorAction SilentlyContinue | Out-Null
Set-ItemProperty -Path $cortanaPolicies -Name "AllowCortana" -Value 0 -Type DWord -Force

Write-Log "--- Phase 6: Disable Activity History & Timeline ---"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableActivityFeed" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "PublishUserActivities" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

Write-Log "=== ArizenOS Debloat COMPLETE === Log: $LogPath"
