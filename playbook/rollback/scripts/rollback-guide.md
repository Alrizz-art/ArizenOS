# ArizenOS Rollback Runbook

> See `playbook/ROLLBACK_WORKFLOW.md` for the full decision tree and procedures.

## Quick Reference

| Problem | Command |
|---------|---------|
| Full rollback (restore point) | `scripts\rollback.ps1 -UseRestorePoint` |
| Undo registry changes only | `scripts\rollback.ps1 -RestoreRegistry` |
| Re-provision removed apps | `scripts\rollback.ps1 -RestoreApps` |
| Full registry + apps | `scripts\rollback.ps1 -Full` |

## Log Location

All rollback operations log to: `C:\ArizenOS\Logs\rollback_{timestamp}.log`

Attach this file to any GitHub Issue reporting a rollback failure.
