# ArizenOS v0.1 -- Final Build Instructions
# From repository root to ArizenOS.apbx ready for testing.

## Prerequisites

  [ ] AME Wizard (latest) installed on build machine
  [ ] PowerShell 5.1 or higher
  [ ] Repository cloned to local machine
  [ ] OI-01 resolved: arizenOS_logo_oem.bmp committed (120x120 24-bit BMP validated)
  [ ] OI-02 resolved: scripts/apply-performance.ps1 has real UserPreferencesMask hex
  [ ] OI-03 resolved: scripts/apply-wallpaper.ps1 has confirmed lock screen paths
  [ ] All 13 PowerShell scripts written and committed to playbook/scripts/
  [ ] All 4 asset files committed to assets/

## Step 1 -- Confirm Zero [TBD] Placeholders

  Run from repo root in PowerShell:
    Select-String -Path ".\playbook\*" -Pattern "\[TBD" -Recurse

  Must return 0 matches before proceeding.

## Step 2 -- Create Staging Directory

  $s = ".\build\staging"
  Remove-Item $s -Recurse -Force -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force $s
  "entries","scripts","assets\logos","assets\wallpapers","manifests" |
    ForEach-Object { New-Item -ItemType Directory -Force "$s\$_" }

## Step 3 -- Copy Files to Staging

  # Root entry point (rename playbook-manifest.yaml -> playbook.yaml)
  Copy-Item ".\playbook\manifests\playbook-manifest.yaml" "$s\playbook.yaml"

  # Entry files (11 YAML files)
  Copy-Item ".\playbook\entries\*.yaml" "$s\entries\"

  # Scripts (13 PS1 files)
  Copy-Item ".\playbook\scripts\*.ps1" "$s\scripts\"

  # Assets
  Copy-Item ".\assets\logos\arizenOS_logo_oem.bmp"       "$s\assets\logos\"
  Copy-Item ".\assets\wallpapers\arizenOS_dark.jpg"       "$s\assets\wallpapers\"
  Copy-Item ".\assets\wallpapers\arizenOS_default.jpg"    "$s\assets\wallpapers\"
  Copy-Item ".\assets\wallpapers\arizenOS_lockscreen.jpg" "$s\assets\wallpapers\"

  # Manifests (reference)
  Copy-Item ".\playbook\manifests\*.yaml" "$s\manifests\"

## Step 4 -- Compute SHA256 and Update Asset Manifest

  Get-ChildItem "$s\assets" -Recurse -File | ForEach-Object {
    $h = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    Write-Host "$($_.Name)  SHA256: $h  Size: $($_.Length)"
  }

  Replace [TBD_SHA256_*] and [TBD_SIZE_*] in asset-manifest.yaml with output above.

## Step 5 -- Verify Staging Layout

  $required = @(
    "$s\playbook.yaml",
    "$s\entries\01-preflight.yaml",  "$s\entries\02-safety-net.yaml",
    "$s\entries\03-asset-deploy.yaml","$s\entries\04-oem-branding.yaml",
    "$s\entries\05-lock-screen.yaml", "$s\entries\06-theme.yaml",
    "$s\entries\07-transparency.yaml","$s\entries\08-performance.yaml",
    "$s\entries\09-developer.yaml",   "$s\entries\10-finalize.yaml",
    "$s\entries\rollback.yaml",
    "$s\scripts\preflight-check.ps1", "$s\scripts\backup-registry.ps1",
    "$s\scripts\deploy-assets.ps1",   "$s\scripts\apply-oem-branding.ps1",
    "$s\scripts\apply-wallpaper.ps1", "$s\scripts\apply-theme.ps1",
    "$s\scripts\apply-performance.ps1","$s\scripts\apply-developer.ps1",
    "$s\scripts\write-manifest.ps1",  "$s\scripts\register-rollback.ps1",
    "$s\scripts\finalize.ps1",        "$s\scripts\rollback.ps1",
    "$s\assets\logos\arizenOS_logo_oem.bmp",
    "$s\assets\wallpapers\arizenOS_dark.jpg",
    "$s\assets\wallpapers\arizenOS_lockscreen.jpg"
  )
  $missing = $required | Where-Object { !(Test-Path $_) }
  if ($missing) { Write-Error "MISSING FILES:"; $missing; exit 1 }
  else { Write-Host "All required files present -- safe to package" }

## Step 6 -- Package as ZIP and Rename to .apbx

  Add-Type -Assembly "System.IO.Compression.FileSystem"
  $zip = ".\build\ArizenOS-v0.1.0.zip"
  [System.IO.Compression.ZipFile]::CreateFromDirectory(
    (Resolve-Path $s).Path, $zip,
    [System.IO.Compression.CompressionLevel]::Optimal, $false
  )
  Rename-Item $zip "ArizenOS-v0.1.0.apbx"
  Write-Host "Archive: .\build\ArizenOS-v0.1.0.apbx"

## Step 7 -- Compute .apbx SHA256

  $apbx = ".\build\ArizenOS-v0.1.0.apbx"
  $hash = (Get-FileHash $apbx -Algorithm SHA256).Hash
  "$hash  ArizenOS-v0.1.0.apbx" | Out-File ".\build\ArizenOS-v0.1.0.apbx.sha256" -Encoding UTF8
  Write-Host "SHA256: $hash"

## Step 8 -- AME Wizard Smoke Test

  [ ] Open AME Wizard
  [ ] Open Playbook > select ArizenOS-v0.1.0.apbx
  [ ] Verify: name = "ArizenOS", version = "0.1.0"
  [ ] Verify: all 10 phases listed, no YAML parse errors
  [ ] Navigate Phase 1 (Preflight) -- confirm 5 checks visible
  [ ] DO NOT INSTALL -- smoke test only

## Step 9 -- Save and Tag Release

  Create directory: releases/v0.1.0/
  Copy into it: ArizenOS-v0.1.0.apbx and ArizenOS-v0.1.0.apbx.sha256
  Stage the directory and create commit: "release: ArizenOS v0.1.0-alpha"
  Apply tag: v0.1.0-alpha

## Step 10 -- RC Validation

  Run full checklist: playbook/RC-VALIDATION-CHECKLIST.md
  All Section I checks (non-destructive) are P0 -- no exceptions.
  All A-K checks must pass before promoting alpha to release.

## Build Output

  build/
  +-- ArizenOS-v0.1.0.apbx
  +-- ArizenOS-v0.1.0.apbx.sha256

  releases/v0.1.0/
  +-- ArizenOS-v0.1.0.apbx
  +-- ArizenOS-v0.1.0.apbx.sha256

Remaining blockers before Step 1: OI-01, OI-02, OI-03, OI-05
Expected build time after blockers resolved: ~1 hour
