<#
.SYNOPSIS
    ArizenOS .apbx Build Script
.DESCRIPTION
    Assembles ArizenOS.apbx per the APBX Assembly Specification.
    Stages the correct folder structure into a temp directory, then packages
    as a ZipCrypto (PKZIP 2.0) encrypted ZIP (password: malte) required by AME Wizard.

    APBX Structure:
      playbook.conf           <- root (AME Wizard Beta entry point)
      entries/                <- from playbook/entries/
      scripts/                <- SCR-01..SCR-13 only
      assets/logos/           <- arizenOS_logo_oem.bmp only (per spec)
      assets/wallpapers/      <- 3 wallpaper files
      manifests/              <- from playbook/manifests/ (reference only)

    ENCRYPTION:
      AME Wizard requires ZipCrypto (PKZIP 2.0) encryption with password "malte".
      System.IO.Compression.ZipFile does NOT support password encryption.
      This script uses 7-Zip (7z.exe). Install 7-Zip before running:
        https://www.7-zip.org/

.VERSION 5.0.0
#>

$ErrorActionPreference = "Stop"
$RepoRoot   = Split-Path $PSScriptRoot -Parent
$OutputDir  = $RepoRoot
$StagingDir = Join-Path $env:TEMP "ArizenOS_stage_$(Get-Date -f 'yyyyMMddHHmmss')"
$TempZip    = Join-Path $env:TEMP "ArizenOS_build.zip"
$OutApbx    = Join-Path $OutputDir "ArizenOS.apbx"

function Write-Step { param([string]$msg) Write-Host "  -> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red; exit 1 }

Write-Host "`nArizenOS .apbx Builder v4.0.0" -ForegroundColor White
Write-Host "Repo: $RepoRoot"

# ── [0/5] Locate 7-Zip ────────────────────────────────────────────────────────
Write-Host "`n[0/5] Locating 7-Zip..." -ForegroundColor White

$7zCandidates = @(
    "C:\Program Files\7-Zip\7z.exe",
    "C:\Program Files (x86)\7-Zip\7z.exe"
)
$7zFromPath = (Get-Command 7z -ErrorAction SilentlyContinue)?.Source
if ($7zFromPath) { $7zCandidates = @($7zFromPath) + $7zCandidates }

$7z = $7zCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $7z) {
    Write-Fail @"
7-Zip not found. Install 7-Zip and re-run:
  https://www.7-zip.org/
  winget install 7zip.7zip
AME Wizard requires ZipCrypto -- use 7-Zip with -mem=ZipCrypto (NOT -mem=AES256).
"@
}
Write-OK "7-Zip: $7z"

# ── [1/5] Pre-flight Validation ───────────────────────────────────────────────
Write-Host "`n[1/5] Validating source structure..." -ForegroundColor White

$requiredSources = @{
    "playbook.conf"                                   = "APBX root entry point"
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
    Write-Fail "$missing required source file(s) missing -- resolve before building."
}

# ── [2/5] Stage APBX Structure ────────────────────────────────────────────────
Write-Host "`n[2/5] Staging APBX structure..." -ForegroundColor White
Write-Step "Staging dir: $StagingDir"

if (Test-Path $StagingDir) { Remove-Item $StagingDir -Recurse -Force }
$null = New-Item -ItemType Directory -Force -Path $StagingDir
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\entries"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\scripts"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\assets\logos"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\assets\wallpapers"
$null = New-Item -ItemType Directory -Force -Path "$StagingDir\manifests"

# Root playbook.yaml
Copy-Item "$RepoRoot\playbook.conf" "$StagingDir\playbook.conf" -Force
Write-OK "Staged: playbook.conf  (XML descriptor for AME Wizard Beta)"

# Entries (playbook/entries/ -> entries/)
Get-ChildItem "$RepoRoot\playbook\entries\*.yaml" | ForEach-Object {
    Copy-Item $_.FullName "$StagingDir\entries\$($_.Name)" -Force
    Write-OK "Staged: entries/$($_.Name)"
}

# Scripts -- ONLY SCR-01..SCR-13 (13 files per spec, hard-listed to avoid extras)
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
        Write-Fail "Required script missing: scripts/$s"
    }
}

# Assets -- OEM logo ONLY per APBX-ASSEMBLY-SPEC.md (extra logos excluded)
Copy-Item "$RepoRoot\assets\logos\arizenOS_logo_oem.bmp" "$StagingDir\assets\logos\arizenOS_logo_oem.bmp" -Force
Write-OK "Staged: assets/logos/arizenOS_logo_oem.bmp"

foreach ($wall in @("arizenOS_dark.jpg", "arizenOS_default.jpg", "arizenOS_lockscreen.jpg")) {
    Copy-Item "$RepoRoot\assets\wallpapers\$wall" "$StagingDir\assets\wallpapers\$wall" -Force
    Write-OK "Staged: assets/wallpapers/$wall"
}

# Manifests (reference only -- not read by AME Wizard)
Get-ChildItem "$RepoRoot\playbook\manifests\*.yaml" | ForEach-Object {
    Copy-Item $_.FullName "$StagingDir\manifests\$($_.Name)" -Force
    Write-OK "Staged: manifests/$($_.Name)"
}

# ── [3/5] Compute Asset Hashes ────────────────────────────────────────────────
Write-Host "`n[3/5] Computing SHA256 for staged assets..." -ForegroundColor White
Get-ChildItem "$StagingDir\assets" -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    $rel  = $_.FullName.Substring("$StagingDir\assets\".Length)
    Write-Host "  SHA256[$rel] = $hash" -ForegroundColor Gray
}

# ── [4/5] Package with AES-256 Encryption (password: malte) ──────────────────
Write-Host "`n[4/5] Packaging APBX with ZipCrypto encryption..." -ForegroundColor White
Write-Host "  Password : malte  (required by AME Wizard -- do not change)" -ForegroundColor Yellow
Write-Host "  Method   : ZipCrypto (PKZIP 2.0, method 8)" -ForegroundColor Gray
Write-Host "  Tool     : $7z" -ForegroundColor Gray

if (Test-Path $TempZip) { Remove-Item $TempZip -Force }
if (Test-Path $OutApbx) { Remove-Item $OutApbx -Force }

Push-Location $StagingDir
& $7z a -tzip -p"malte" -mem=ZipCrypto $TempZip "." | Out-Null
$exitCode = $LASTEXITCODE
Pop-Location

if ($exitCode -ne 0) {
    Write-Fail "7-Zip packaging failed (exit code: $exitCode)"
}

Move-Item $TempZip $OutApbx -Force
Write-OK "Packaged: $OutApbx"

# ── [5/5] Verify ──────────────────────────────────────────────────────────────
Write-Host "`n[5/5] Verifying archive..." -ForegroundColor White

$sizeMB = [math]::Round((Get-Item $OutApbx).Length / 1MB, 2)
Write-Host "  Size: $sizeMB MB"

# Confirm archive requires password (test without password must fail)
$testNoPass = & $7z t $OutApbx 2>&1
if ($testNoPass -match "Wrong password|Cannot open encrypted") {
    Write-OK "Encryption confirmed: archive rejects access without password"
} else {
    Write-Warn "Could not auto-confirm encryption -- verify in AME Wizard"
}

# Confirm correct password works and required entries exist
$listResult = & $7z l -p"malte" $OutApbx 2>&1 | Out-String

$checks = @(
    "playbook.conf",
    "entries/01-preflight.yaml",
    "entries/rollback.yaml",
    "scripts/preflight-check.ps1",
    "scripts/rollback.ps1",
    "assets/logos/arizenOS_logo_oem.bmp",
    "assets/wallpapers/arizenOS_default.jpg"
)
foreach ($chk in $checks) {
    if ($listResult -match [regex]::Escape($chk)) { Write-OK "Verified in archive: $chk" }
    else { Write-Warn "NOT found in archive: $chk" }
}

# Cleanup staging dir
Remove-Item $StagingDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n  ╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║  BUILD COMPLETE                          ║" -ForegroundColor Green
Write-Host "  ║  Output  : ArizenOS.apbx                ║" -ForegroundColor Green
Write-Host "  ║  Encrypt : ZipCrypto  password = malte  ║" -ForegroundColor Green
Write-Host "  ║  Size    : $sizeMB MB$((' ' * (27 - "$sizeMB MB".Length)))║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n  Test: AME Wizard > Open Playbook > ArizenOS.apbx" -ForegroundColor Cyan
