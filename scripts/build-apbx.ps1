<#
.SYNOPSIS
    ArizenOS .apbx Build Script
.DESCRIPTION
    Packages the ArizenOS playbook directory into a valid AME Wizard .apbx file.
    Validates required assets and structure before packaging.
.VERSION 2.0.0
#>

$ErrorActionPreference = "Stop"
$RepoRoot   = Split-Path $PSScriptRoot -Parent
$OutputName = "ArizenOS"
$OutputDir  = $RepoRoot
$TempZip    = Join-Path $env:TEMP "ArizenOS_build.zip"
$OutApbx    = Join-Path $OutputDir "$OutputName.apbx"

function Write-Step { param([string]$msg) Write-Host "  → $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$msg) Write-Host "  ✗ $msg" -ForegroundColor Red; exit 1 }

Write-Host "`nArizenOS .apbx Builder v2.0.0" -ForegroundColor White

# ── Pre-flight Validation ─────────────────────────────────────────────────────
Write-Host "`n[1/4] Validating structure..." -ForegroundColor White

$requiredFiles = @(
    "playbook.yaml"
    "scripts\debloat.ps1"
    "scripts\oem-branding.ps1"
    "scripts\apply-theme.ps1"
    "scripts\wallpaper.ps1"
    "scripts\developer-setup.ps1"
    "scripts\rollback.ps1"
    "scripts\security-audit.ps1"
    "registry\dark-theme.reg"
    "registry\transparency.reg"
    "registry\oem-branding.reg"
    "registry\performance.reg"
)

foreach ($f in $requiredFiles) {
    $fullPath = Join-Path $RepoRoot $f
    if (Test-Path $fullPath) { Write-OK $f }
    else { Write-Warn "MISSING: $f (playbook may still work if entry is optional)" }
}

# ── Asset Check ───────────────────────────────────────────────────────────────
Write-Host "`n[2/4] Checking assets..." -ForegroundColor White
$oemLogo   = Join-Path $RepoRoot "assets\logos\arizenOS_logo_oem.bmp"
$wallpaper = Join-Path $RepoRoot "assets\wallpapers\arizenOS_default.jpg"
if (-not (Test-Path $oemLogo))   { Write-Warn "OEM logo missing — branding will skip logo: assets\logos\arizenOS_logo_oem.bmp" }
else                              { Write-OK "OEM logo found" }
if (-not (Test-Path $wallpaper)) { Write-Warn "Default wallpaper missing — wallpaper step will skip: assets\wallpapers\arizenOS_default.jpg" }
else                              { Write-OK "Default wallpaper found" }

# ── Package ───────────────────────────────────────────────────────────────────
Write-Host "`n[3/4] Packaging..." -ForegroundColor White
Write-Step "Source: $RepoRoot"
Write-Step "Output: $OutApbx"

if (Test-Path $TempZip) { Remove-Item $TempZip -Force }
if (Test-Path $OutApbx) { Remove-Item $OutApbx -Force }

# Exclude build artifacts, git dir, and the output file itself
$exclude = @(".git", ".gitignore", "*.apbx", "*.zip", "node_modules", ".vs")
$items   = Get-ChildItem $RepoRoot | Where-Object { $_.Name -notin $exclude }
Compress-Archive -Path $items.FullName -DestinationPath $TempZip -CompressionLevel Optimal
Rename-Item $TempZip $OutApbx
Write-OK "Packaged → $OutApbx"

# ── Verify ────────────────────────────────────────────────────────────────────
Write-Host "`n[4/4] Verifying..." -ForegroundColor White
$size = (Get-Item $OutApbx).Length / 1MB
Write-OK "File size: $([math]::Round($size, 2)) MB"
$zip = [System.IO.Compression.ZipFile]::OpenRead($OutApbx)
$manifest = $zip.Entries | Where-Object { $_.Name -eq "playbook.yaml" }
if ($manifest) { Write-OK "playbook.yaml found inside archive" }
else           { Write-Warn "playbook.yaml NOT found — AME Wizard may reject this file" }
$zip.Dispose()

Write-Host "`n✅ Build complete: $OutApbx`n" -ForegroundColor Green
