<#
.SYNOPSIS
    Builds ArizenOS.apbx for AME Wizard Beta.
.DESCRIPTION
    Stages the playbook structure and creates a 7z AES-256 archive
    with the .apbx extension required by AME Wizard Beta.
    Password: malte (standard AME Wizard encryption password).
.NOTES
    Requires 7-Zip (7z.exe) to be installed and in PATH.
    Run from the repo root: .\scripts\build-apbx.ps1
#>

param(
    [string]$OutputPath = ".\ArizenOS.apbx",
    [string]$7ZipExe   = "7z.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== ArizenOS .apbx Builder ===" -ForegroundColor Cyan
Write-Host "AME Wizard Beta — 7z AES-256 format"

# ── Locate 7-Zip ─────────────────────────────────────────────────────────────
$7z = Get-Command $7ZipExe -ErrorAction SilentlyContinue
if (-not $7z) {
    $7z = Get-Command "C:\Program Files\7-Zip\7z.exe" -ErrorAction SilentlyContinue
}
if (-not $7z) {
    throw "7-Zip (7z.exe) not found. Install from https://7-zip.org/"
}
$7ZipExe = $7z.Source
Write-Host "Using 7-Zip: $7ZipExe" -ForegroundColor Green

# ── Validate source structure ────────────────────────────────────────────────
$repoRoot = Split-Path -Parent $PSScriptRoot
foreach ($required in @("playbook.conf","Configuration\main.yml","Configuration\Tasks")) {
    $path = Join-Path $repoRoot $required
    if (-not (Test-Path $path)) {
        throw "Missing required path: $path"
    }
}

# ── Create staging directory ─────────────────────────────────────────────────
$stage = Join-Path $env:TEMP "arizenOS_stage_$(Get-Date -f 'yyyyMMddHHmmss')"
Write-Host "Staging to: $stage" -ForegroundColor Yellow

# playbook.conf
Copy-Item (Join-Path $repoRoot "playbook.conf") (Join-Path $stage "playbook.conf") -Force

# Configuration/
$confSrc = Join-Path $repoRoot "Configuration"
$confDst = Join-Path $stage "Configuration"
Copy-Item $confSrc $confDst -Recurse -Force

# Executables/
$execSrc = Join-Path $repoRoot "Executables"
$execDst = Join-Path $stage "Executables"
if (Test-Path $execSrc) {
    Copy-Item $execSrc $execDst -Recurse -Force
    Write-Host "Copied Executables/" -ForegroundColor Green
} else {
    New-Item -ItemType Directory -Path $execDst | Out-Null
    Write-Host "Created empty Executables/" -ForegroundColor Yellow
}

# ── Build .apbx (7z AES-256) ─────────────────────────────────────────────────
$absOutput = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath
} else {
    Join-Path $repoRoot $OutputPath
}

if (Test-Path $absOutput) { Remove-Item $absOutput -Force }

Write-Host "Building: $absOutput" -ForegroundColor Cyan

& $7ZipExe a `
    -t7z `
    -p"malte" `
    -mhe=on `
    -mx=5 `
    -mmt=on `
    "$absOutput" `
    "$stage\*"

if ($LASTEXITCODE -ne 0) {
    throw "7-Zip failed with exit code $LASTEXITCODE"
}

# ── Cleanup staging ───────────────────────────────────────────────────────────
Remove-Item $stage -Recurse -Force

$size = [math]::Round((Get-Item $absOutput).Length / 1KB, 1)
Write-Host "`n[OK] ArizenOS.apbx built successfully!" -ForegroundColor Green
Write-Host "     Path : $absOutput"
Write-Host "     Size : ${size} KB"
Write-Host "`n     Open AME Wizard Beta and load the .apbx to apply."
