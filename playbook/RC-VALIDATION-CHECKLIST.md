# ArizenOS v0.1 -- Release Candidate Validation Checklist
# Implementation checks only. No governance. No architecture.

## A -- Playbook Structure

  A-01  AME Wizard opens ArizenOS.apbx without error               [ ]
  A-02  Playbook name shows "ArizenOS" in header                    [ ]
  A-03  Version shows "0.1.0"                                       [ ]
  A-04  All 10 install phases visible in phase list                 [ ]
  A-05  Developer Setup shows as optional/conditional               [ ]
  A-06  All 13 scripts present in archive (unzip + inspect)         [ ]
  A-07  All 4 asset files present in archive                        [ ]

## B -- Preflight

  B-01  Playbook aborts on Win10 build < 19045                      [ ]
  B-02  Playbook aborts on Windows S Mode                           [ ]
  B-03  Playbook aborts when run without Administrator              [ ]
  B-04  Disk space warning shown at < 1 GB (does not abort)         [ ]
  B-05  Domain-join shows warning (does not abort)                  [ ]

## C -- Safety Net

  C-01  Restore point created with description "Before ArizenOS v0.1"  [ ]
  C-02  registry-backup.reg created at correct path                     [ ]
  C-03  Backup .reg is valid (re-import succeeds without error)         [ ]
  C-04  Playbook aborts if backup creation fails (not silent continue)  [ ]

## D -- Asset Deployment

  D-01  oemlogo.bmp present at ProgramData path                     [ ]
  D-02  arizenOS_dark.jpg present at ProgramData path               [ ]
  D-03  arizenOS_lockscreen.jpg present at ProgramData path         [ ]
  D-04  All assets match expected SHA256 hashes                     [ ]

## E -- OEM Branding

                                          Win10  Win11
  E-01  Manufacturer = "ArizenOS"         [ ]    [ ]
  E-02  Model = "ArizenOS Experience Layer v0.1"
                                          [ ]    [ ]
  E-03  Support URL visible and clickable [ ]    [ ]
  E-04  OEM logo renders in System Properties / Settings About
                                          [ ]    [ ]

## F -- Theme

                                          Win10  Win11
  F-01  Apps in dark mode                 [ ]    [ ]
  F-02  Taskbar and Start are dark        [ ]    [ ]
  F-03  Transparency visible on taskbar   [ ]    [ ]
  F-04  No accent color on title bars     [ ]    [ ]
  F-05  Desktop wallpaper = ArizenOS dark [ ]    [ ]
  F-06  Aero Peek thumbnails on hover     [ ]    [ ]

## G -- Lock Screen

                                          Win10  Win11
  G-01  ArizenOS wallpaper shown          [ ]    [ ]
  G-02  No letterboxing                   [ ]    [ ]
  G-03  Spotlight tips not shown          [ ]    [ ]

## H -- Performance

  H-01  Window animations play (minimize/maximize)     [ ]
  H-02  Font edges smooth (not jagged)                 [ ]
  H-03  Explorer shows thumbnails not generic icons    [ ]
  H-04  Menu response fast (< 400ms)                   [ ]
  H-05  Taskbar thumbnails are live previews           [ ]
  H-06  Performance Settings shows "Custom"            [ ]

## I -- Non-Destructive Guarantees (P0 -- NO EXCEPTIONS)

  I-01  Defender:     Get-Service WinDefend = Running  [ ]
  I-02  Win Update:   Get-Service wuauserv = Running   [ ]
  I-03  Firewall:     Get-Service MpsSvc = Running     [ ]
  I-04  Store:        Microsoft Store loads without error  [ ]
  I-05  Network:      ping 8.8.8.8 succeeds            [ ]
  I-06  UAC:          still active in Settings         [ ]

## J -- Rollback

  J-01  Rollback shortcut in Start Menu after install  [ ]
  J-02  Rollback executes without error                [ ]
  J-03  OEM branding reverted after rollback           [ ]
  J-04  Light mode restored after rollback             [ ]
  J-05  Default wallpaper restored after rollback      [ ]
  J-06  Windows Defender running after rollback (P0)   [ ]
  J-07  rollback.log written to correct path           [ ]

## K -- Logs

  K-01  install.log created at correct path            [ ]
  K-02  Timestamped entry per phase in log             [ ]
  K-03  Zero unhandled exceptions in log               [ ]
  K-04  manifest.json is valid JSON, correct version   [ ]

## RC Pass Criteria

  P0 (blocks release, no exceptions):
    B-01 B-02 B-03 C-04 I-01 I-02 I-03 I-04 I-05 I-06 J-06

  P1 (waivable for alpha with documented note):
    G-02 (letterboxing on 16:10), F-06 (Aero Peek GPU-specific), E-04 (150% DPI)

  All other checks: must pass before promoting alpha to release.
