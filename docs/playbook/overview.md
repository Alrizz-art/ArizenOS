# Playbook Documentation

> Complete reference for the ArizenOS AME Wizard Playbook.

## Contents

| Section | Description |
|---|---|
| [installation-guide](./installation-guide.md) | How to apply the playbook |
| [registry-reference](./registry-reference.md) | Every tweak, package, and service entry |
| [rollback-guide](./rollback-guide.md) | How to undo the playbook |
| [customizing](./customizing.md) | Fork and customize for personal use |

## Quick Start

1. Download the latest `.apbx` from [GitHub Releases](https://github.com/Alrizz-art/ArizenOS/releases)
2. Install [AME Wizard](https://ameliorated.io)
3. Drag the `.apbx` file onto AME Wizard
4. Follow the on-screen configuration options

## Playbook Source

The playbook source lives at:
```
playbook/
├── manifests/v2.0.0/    ← playbook.yaml + entries.yaml
├── registry/            ← individual tweak + package entries
└── scripts/             ← build, test, release, rollback
```
