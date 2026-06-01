# ArizenOS Releases

> Machine-readable release manifests, per-product changelogs, and artifact checksums.

## Structure

| Directory | Contents |
|---|---|
| `manifests/` | Per-version JSON release manifests + `latest.json` pointer |
| `changelogs/` | Per-product CHANGELOG.md files |
| `checksums/` | SHA256 checksums for all release artifacts |

## Manifest Schema

Every stable release produces a manifest at `manifests/vX.Y.Z.json`. See [`/ARCHITECTURE.md`](../ARCHITECTURE.md) — Release Layout for the full schema.

`manifests/latest.json` always points to the current stable manifest. The ArizenOS auto-updater reads this file on a defined interval to check for updates.

## Checksums

Every release artifact has a corresponding SHA256 checksum in `checksums/vX.Y.Z-SHA256SUMS.txt`. Users should verify checksums before installing from unofficial mirrors.

```bash
# Verify on Windows (PowerShell)
Get-FileHash ArizenOS-Setup-0.5.0.exe -Algorithm SHA256

# Compare against checksums/v0.5.0-SHA256SUMS.txt
```

## Automating Releases

See [`/RELEASE.md`](../RELEASE.md) for the full release process and the `tools/release/` scripts.
