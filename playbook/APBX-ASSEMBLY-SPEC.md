# ArizenOS v0.1 -- APBX Assembly Specification
# Format: AME Wizard Playbook Bundle (.apbx = AES-256 encrypted ZIP)

## 1. Archive Folder Structure

  ArizenOS.apbx  (AES-256 encrypted ZIP, password: malte)
  |
  +-- playbook.yaml                     <-- ROOT (from repo root playbook.yaml)
  |
  +-- entries/
  |   +-- 01-preflight.yaml
  |   +-- 02-safety-net.yaml
  |   +-- 03-asset-deploy.yaml
  |   +-- 04-oem-branding.yaml
  |   +-- 05-lock-screen.yaml
  |   +-- 06-theme.yaml
  |   +-- 07-transparency.yaml
  |   +-- 08-performance.yaml
  |   +-- 09-developer.yaml
  |   +-- 10-finalize.yaml
  |   +-- rollback.yaml
  |
  +-- scripts/
  |   +-- preflight-check.ps1          SCR-01
  |   +-- create-restore-point.ps1     SCR-02
  |   +-- backup-registry.ps1          SCR-03
  |   +-- deploy-assets.ps1            SCR-04
  |   +-- apply-oem-branding.ps1       SCR-05
  |   +-- apply-wallpaper.ps1          SCR-06
  |   +-- apply-theme.ps1              SCR-07
  |   +-- apply-performance.ps1        SCR-08
  |   +-- apply-developer.ps1          SCR-09
  |   +-- write-manifest.ps1           SCR-10
  |   +-- register-rollback.ps1        SCR-11
  |   +-- finalize.ps1                 SCR-12
  |   +-- rollback.ps1                 SCR-13
  |
  +-- assets/
  |   +-- logos/
  |   |   +-- arizenOS_logo_oem.bmp    (OI-01 validated: 120x120 24-bit BMP)
  |   +-- wallpapers/
  |       +-- arizenOS_dark.jpg
  |       +-- arizenOS_default.jpg
  |       +-- arizenOS_lockscreen.jpg
  |
  +-- manifests/                        (reference only -- not read by AME Wizard)
      +-- playbook-manifest.yaml
      +-- registry-manifest.yaml
      +-- asset-manifest.yaml
      +-- script-manifest.yaml

## 2. Root Entry Point

AME Wizard reads ONLY playbook.yaml at the archive root.
Source: repo root playbook.yaml
Required fields (AME Wizard rejects without these):
  title, description, username, version, entries

## 3. Manifest Placement

  Source (repo)                              | Archive path
  -------------------------------------------|-------------------------------
  playbook.yaml (repo root)                  | playbook.yaml (root)
  playbook/entries/*.yaml (11 files)         | entries/
  playbook/manifests/registry-manifest.yaml  | manifests/ (reference)
  playbook/manifests/asset-manifest.yaml     | manifests/ (reference)
  playbook/manifests/script-manifest.yaml    | manifests/ (reference)

## 4. Asset Placement

  Source (repo)                              | Archive path
  -------------------------------------------|-------------------------------
  assets/logos/arizenOS_logo_oem.bmp         | assets/logos/
  assets/wallpapers/arizenOS_dark.jpg        | assets/wallpapers/
  assets/wallpapers/arizenOS_default.jpg     | assets/wallpapers/
  assets/wallpapers/arizenOS_lockscreen.jpg  | assets/wallpapers/

  NOTE: Only arizenOS_logo_oem.bmp goes into the APBX.
        arizenOS_logo_dark.png and arizenOS_logo_white.png are repo-only assets.

Compute SHA256 for each asset after staging (Step 3) and update
[TBD_SHA256_*] fields in asset-manifest.yaml before release commit.

## 5. Script Placement

  All 13 .ps1 files go into scripts/ at archive root.
  Encoding: UTF-8, no BOM, LF line endings.
  AME Wizard executes via: powershell.exe -ExecutionPolicy Bypass -File <script>

## 6. Packaging Requirements

  ╔══════════════════════════════════════════════════════════════════════╗
  ║  ENCRYPTION IS MANDATORY -- AME Wizard will reject any APBX that   ║
  ║  is not encrypted with AES-256 using the password "malte".          ║
  ║  Error without it: "Playbook must be encrypted using 'malte' as     ║
  ║  the password"                                                       ║
  ╚══════════════════════════════════════════════════════════════════════╝

  Archive format:          ZIP with AES-256 encryption (WinZip method 99)
  Encryption password:     malte  <-- HARDCODED by AME Wizard, never change
  Encryption tool:         7-Zip: 7z a -tzip -p"malte" -mem=AES256 out.zip .
  DO NOT USE:              System.IO.Compression.ZipFile -- no password support
  File extension:          .apbx (renamed from .zip after packaging)
  Internal path separator: Forward slash in ZIP TOC entries
  YAML encoding:           UTF-8, no BOM
  PS1 encoding:            UTF-8, no BOM, LF endings
  Image encoding:          As-is (no re-compression during packaging)
  Max practical size:      < 50 MB uncompressed
