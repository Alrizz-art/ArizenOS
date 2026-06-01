#Requires -Version 5.1
<#
.SYNOPSIS
    ArizenOS Version Bump Script
.DESCRIPTION
    Automatically bumps the version in playbook.yaml following SemVer 2.0.0.
    Updates CHANGELOG.md and prints the git tag command.
.VERSION 1.0.0
.EXAMPLE
    .\scripts\bump-version.ps1 -Type patch
    .\scripts\bump-version.ps1 -Type minor
    .\scripts\bump-version.ps1 -Type major
    .\scripts\bump-version.ps1 -Type minor -Pre beta.1
#>
param(
    [Parameter(Mandatory)]
    [ValidateSet("major","minor","patch")]
    [string]$Type,
    [string]$Pre = ""
)

$ErrorActionPreference = "Stop"
$Root          = Split-Path $PSScriptRoot -Parent
$PlaybookPath  = Join-Path $Root "playbook.yaml"
$ChangelogPath = Join-Path $Root "CHANGELOG.md"

$playbookContent = Get-Content $PlaybookPath -Raw
if ($playbookContent -notmatch 'version:\s*"?([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([^"]+))?"?') {
    Write-Error "Could not find version field in playbook.yaml"; exit 1
}
$curMajor = [int]$Matches[1]; $curMinor = [int]$Matches[2]; $curPatch = [int]$Matches[3]
$curVersion = "$curMajor.$curMinor.$curPatch"
if ($Matches[4]) { $curVersion += "-$($Matches[4])" }
Write-Host "Current version: $curVersion" -ForegroundColor Cyan

$newMajor = $curMajor; $newMinor = $curMinor; $newPatch = $curPatch
switch ($Type) {
    "major" { $newMajor++; $newMinor = 0; $newPatch = 0 }
    "minor" { $newMinor++; $newPatch = 0 }
    "patch" { $newPatch++ }
}
$newVersion = "$newMajor.$newMinor.$newPatch"
if ($Pre -ne "") { $newVersion += "-$Pre" }
Write-Host "New version:     $newVersion" -ForegroundColor Green

$confirm = Read-Host "Bump $curVersion to $newVersion? [y/N]"
if ($confirm -notmatch '^[Yy]$') { Write-Host "Aborted."; exit 0 }

$playbookContent = $playbookContent -replace `
    'version:\s*"?[0-9]+\.[0-9]+\.[0-9]+(?:-[^"]+)?"?', `
    "version: `"$newVersion`""
Set-Content $PlaybookPath $playbookContent -NoNewline
Write-Host "  [OK] playbook.yaml -> version: $newVersion" -ForegroundColor Green

$today     = Get-Date -Format "yyyy-MM-dd"
$changelog = Get-Content $ChangelogPath -Raw
if ($changelog -match '\[Unreleased\]') {
    $newHeader = "## [$newVersion] - $today"
    $changelog = $changelog -replace '## \[Unreleased\]', "## [Unreleased]`n`n---`n`n$newHeader"
    $repoUrl   = "https://github.com/Alrizz-art/ArizenOS"
    $prevTag   = "v$curMajor.$curMinor.$curPatch"
    $newTag    = "v$newVersion"
    if ($changelog -match '\[Unreleased\]: ') {
        $changelog = $changelog -replace '\[Unreleased\]: [^\n]+', "[Unreleased]: $repoUrl/compare/$newTag...HEAD"
    }
    $changelog += "`n[$newVersion]: $repoUrl/compare/$prevTag...$newTag"
    Set-Content $ChangelogPath $changelog -NoNewline
    Write-Host "  [OK] CHANGELOG.md -> [$newVersion] - $today" -ForegroundColor Green
} else {
    Write-Host "  [WARN] No [Unreleased] section in CHANGELOG.md" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Run these commands to complete the release:" -ForegroundColor White
Write-Host "    git add playbook.yaml CHANGELOG.md"
Write-Host "    git commit -m `"chore: bump version to $newVersion`""
Write-Host "    git tag -a v$newVersion -m `"Release v$newVersion`""
Write-Host "    git push origin --follow-tags"
