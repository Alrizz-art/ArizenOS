<#
.SYNOPSIS
    ArizenOS .apbx Build Script
.DESCRIPTION
    Assembles ArizenOS.apbx per the APBX Assembly Specification.
    Stages the correct folder structure into a temp directory, then ZIPs and renames.

    APBX Structure:
      playbook.yaml           <- root (from repo root)
      entries/                <- from playbook/entries/
      scripts/                <- from scripts/ (only APBX scripts, SCR-01..SCR-13)
      assets/logos/           <- from assets/logos/
      assets/wallpapers/      <- from assets/wallpapers/
      manifests/              <- from playbook/manifests/ (reference only)

.VERSION 3.0.0
#>

$ErrorActionPreference = "Stop"
$RepoRoot  = Split-Path $PSScriptRoot -Parent
$OutputDir = $RepoRoot
$StagingDir = Join-Path $env:TEMP "ArizenOS_stage_$(Get-Date -f 'yyyyMMddHHmmss')"
$TempZip   = Join-Path $env:TEMP "ArizenOS_build.zip"
$OutApbx   = Join-Path $OutputDir "ArizenOS.apbx"

function Write-Step { param([string]$msg) Write-Host "  -> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red; exit 1 }

Write-Host "`nArizenOS .apbx Builder v3.0.0" -ForegroundColor White
Write-Host "Repo: $RepoRoot"

# ── [1/5] Pre-flight Validation ────────────────────────────────────────────────
Write-Host "`n[1/5] Validating source structure..." -ForegroundColor White

$requiredSources = @{
    # Root playbook
    "playbook.yaml"                                   = "APBX root entry point"
    # Entries (11 files)
    "playbook\entries\01-preflight.yaml"              = "SCR-01 phase"
    "playbook\entries\02-safety-net.yaml"             = "SCR-02/03 phase"
    "playbook\entries\03-asset-deploy.yaml"           = "SCR-04 phase"
    "playbook\entries\04-oem-branding.yaml"           = "SCR-05 phase"
    "playbook\entries\05-lock-screen.yaml"            = "SCR-06 phase"
    "playbook\entries\06-theme.yaml"                  = "SCR-07 phase"
    "playbook\entries\07-transparency.yaml"           = "SCR-07 DWM phase"
    "playbook\entries\08-performance.yaml"            = "SCR-08 phase"
    "playbook\entries\09-developer.yaml"              = "SCR-09 phase"
    "playbook\entries\10-finalize.yaml"               = "SCR-10/11/12 phase"
    "playbook\entries\rollback.yaml"                  = "SCR-13 rollback"
    # Scripts (SCR-01 through SCR-13)
    "scripts\preflight-check.ps1"                     = "SCR-01"
    "scripts\create-restore-point.ps1"                = "SCR-02"
    "scripts\backup-registry.ps1"                     = "SCR-03"
    "scripts\deploy-assets.ps1"                       = "SCR-04"
    "scripts\apply-oem-branding.ps1"                  = "SCR-05"
    "scripts\apply-wallpaper.ps1"                     = "SCR-06"
    "scripts\apply-theme.ps1"                         = "SCR-07"
    "scripts\apply-performance.ps1"                   = "SCR-08"
    "scripts\apply-developer.ps1"                     = "SCR-09"
    "scripts\write-manifest.ps1"                      = "SCR-10"
    "scripts\register-rollback.ps1"                   = "SCR-11"
    "scripts\finalize.ps1"                            = "SCR-12"
    "scripts\rollback.ps1"                            = "SCR-13"
    # Assets
    "assets\logos\arizenOS_logo_oem.bmp"              = "OEM logo (OI-01)"
    "assets\wallpapers\arizenOS_dark.jpg"             = "Dark wallpaper"
    "assets\wallpapers\arizenOS_default.jpg"          = "Default wallpaper"
    "assets\wallpapers\arizenOS_lockscreen.jpg"       = "Lock screen wallpaper"
}

$missing = 0
foreach ($kv in $requiredSources.GetEnumerator()) {
    $full = Join-Path $RepoRoot $kv.Key
    if (Test-Path $full) {
        Write-OK "$($kv.Key)"
    } else {
        Write-Warn "MISSING: $($kv.Key) [$($kv.Value)]"
        $missing++
    }
}

if ($missing -gt 0) {
    Write-Host "`n  $missing source file(s) missing — build will continue but APBX may be incomplete." -ForegroundColor Yellow
}

# ── [2/5] Stage APBX Structure ────────────────────────────────────────────────
Write-Host "`n[2/5] Staging APBX structure..." -ForegroundColor White
Write-Step "Staging dir: $StagingDir"

if (Test-Path $StagingDir) { Remove-Item $StagingDir -Recurse -Force }
$null = New-Item -ItemType Directory -Force -Path $StagingDir

# Directories
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\entries"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\scripts"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\assets\logos"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\assets\wallpapers"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\manifests"

# Root playbook.yaml
Copy-Item "$RepoRoot\playbook.yaml" "$StagingDir\playbook.yaml" -Force
Write-OK "Staged: playbook.yaml"

# Entries (playbook/entries/ -> entries/)
Get-ChildItem "$RepoRoot\playbook\entries\*.yaml" | ForEach-Object {
    Copy-Item $_.FullName "$StagingDir\entries\$($_.Name)" -Force
    Write-OK "Staged: entries/$($_.Name)"
}

# Scripts (only APBX scripts, SCR-01..SCR-13 + apply-theme)
$apbxScripts = @(
    "preflight-check.ps1", "create-restore-point.ps1", "backup-registry.ps1",
    "deploy-assets.ps1", "apply-oem-branding.ps1", "apply-wallpaper.ps1",
    "apply-theme.ps1", "apply-performance.ps1", "apply-developer.ps1",
    "write-manifest.ps1", "register-rollback.ps1", "finalize.ps1", "rollback.ps1"
)
foreach ($s in $apbxScripts) {
    $src = "$RepoRoot\scripts\$s"
    if (Test-Path $src) {
        Copy-Item $src "$StagingDir\scripts\$s" -Force
        Write-OK "Staged: scripts/$s"
    } else {
        Write-Warn "Script missing, skipped: scripts/$s"
    }
}

# Assets
foreach ($logo in @("arizenOS_logo_oem.bmp","arizenOS_logo_dark.png","arizenOS_logo_white.png")) {
    $src = "$RepoRoot\assets\logos\$logo"
    if (Test-Path $src) { Copy-Item $src "$StagingDir\assets\logos\$logo" -Force; Write-OK "Staged: assets/logos/$logo" }
}
foreach ($wall in @("arizenOS_dark.jpg","arizenOS_default.jpg","arizenOS_lockscreen.jpg")) {
    $src = "$RepoRoot\assets\wallpapers\$wall"
    if (Test-Path $src) { Copy-Item $src "$StagingDir\assets\wallpapers\$wall" -Force; Write-OK "Staged: assets/wallpapers/$wall" }
}

# Manifests (reference only)
Get-ChildItem "$RepoRoot\playbook\manifests\*.yaml" | ForEach-Object {
    Copy-Item $_.FullName "$StagingDir\manifests\$($_.Name)" -Force
    Write-OK "Staged: manifests/$($_.Name)"
}

# ── [3/5] Compute Asset Hashes ────────────────────────────────────────────────
Write-Host "`n[3/5] Computing SHA256 for staged assets..." -ForegroundColor White
$assetDir = "$StagingDir\assets"
Get-ChildItem $assetDir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    $rel  = $_.FullName.Substring($assetDir.Length + 1)
    Write-Host "  SHA256[$rel] = $hash" -ForegroundColor Gray
}

# ── [4/5] Package ─────────────────────────────────────────────────────────────
Write-Host "`n[4/5] Packaging APBX archive..." -ForegroundColor White
if (Test-Path $TempZip) { Remove-Item $TempZip -Force }
if (Test-Path $OutApbx) { Remove-Item $OutApbx -Force }

Add-Type -Assembly "System.IO.Compression.FileSystem"
[System.IO.Compression.ZipFile]::CreateFromDirectory($StagingDir, $TempZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
Move-Item $TempZip $OutApbx -Force
Write-OK "Packaged: $OutApbx"

# ── [5/5] Verify ──────────────────────────────────────────────────────────────
Write-Host "`n[5/5] Verifying archive..." -ForegroundColor White
$sizeMB = [math]::Round((Get-Item $OutApbx).Length / 1MB, 2)
Write-Host "  Size: $sizeMB MB"

$zip      = [System.IO.Compression.ZipFile]::OpenRead($OutApbx)
$entries  = $zip.Entries | ForEach-Object { $_.FullName }
$zip.Dispose()

$checks = @("playbook.yaml","entries/01-preflight.yaml","scripts/preflight-check.ps1","scripts/rollback.ps1")
foreach ($chk in $checks) {
    if ($entries -contains $chk) { Write-OK "Found in archive: $chk" }
    else                          { Write-Warn "NOT in archive: $chk" }
}

Write-Host "`n  Total entries in APBX: $($entries.Count)" -ForegroundColor White

# Cleanup staging dir
Remove-Item $StagingDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n[BUILD COMPLETE] $OutApbx`n" -ForegroundColor Green
