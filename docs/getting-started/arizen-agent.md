# Arizen Agent User Guide

Arizen Agent is an autonomous task runner. It translates natural language instructions into OS-level actions — file operations, shell commands, browser control, application automation — executed with your explicit permission.

---

## Philosophy

Arizen Agent is built on one principle: **you are always in control.**

The Agent does not take any action without:
1. A tool permission you have explicitly granted
2. A task you have explicitly initiated (or a scheduled task you have set up)
3. Clear, visible logging of every action taken

The Agent will never silently escalate privileges, call external APIs, or send data anywhere without your knowledge.

---

## Setting Up the Agent

### Enable Tool Permissions

Open **Hub → Settings → Agent → Tool Permissions** and enable the categories you want the Agent to have access to:

| Tool Category | What the Agent Can Do |
|---|---|
| **File System — Read** | Read file contents, list directories, search files |
| **File System — Write** | Create, rename, move, delete files and folders |
| **Shell — Run** | Execute PowerShell and CMD commands |
| **Browser — Navigate** | Open URLs, navigate browser tabs |
| **Browser — Read** | Read page content, extract data |
| **Browser — Interact** | Fill forms, click buttons, scroll |
| **Clipboard** | Read and write clipboard content |
| **Calendar — Read** | Read calendar events |
| **Calendar — Write** | Create and modify calendar events |
| **Email — Read** | Read emails from connected accounts |
| **Email — Send** | Send emails (requires confirmation each time) |
| **Applications** | Launch applications, switch focus |

**Recommended starting configuration:** Enable File System Read, Browser Navigate, and Clipboard only. Add more as you discover you need them.

### Restrict File System Access

Rather than granting access to your entire drive, restrict the Agent to specific folders:

**Hub → Settings → Agent → File System → Allowed Paths**

Example allowed paths:
```
C:\Users\you\Documents\Work\
C:\Users\you\Downloads\
```

The Agent will decline any operation outside these paths.

---

## Running Tasks

### From Arizen Assistant

Any conversation in Arizen Assistant can be escalated to the Agent:

1. Type your task naturally: *"Go through my Downloads folder and delete any .tmp files older than 30 days"*
2. The Assistant generates an execution plan — a list of steps the Agent would take
3. Review the plan. Approve, edit, or cancel.
4. Click **Run** — the Agent executes step by step with live progress

### Quick Command

Press **Win + G** to open the Agent quick command bar. Type a task and press Enter. For tasks that require multiple steps, the Agent opens a full execution view automatically.

### Scheduled Tasks

Create recurring automated tasks: **Hub → Agent → Scheduled Tasks → New Task**

Examples:
- Daily: *"Clear my Downloads folder of files older than 7 days"*
- Weekly: *"Summarise my calendar for next week and email it to me"*
- On startup: *"Open my work apps and check my email"*

Scheduled tasks require the relevant tool permissions and run at the configured time even if the Agent panel is closed.

---

## Execution View

When a task is running, the Execution View shows:

```
Task: Organise project files
Status: Running — Step 3 of 7

✅  Read directory: C:\Projects\Q3-Report\
✅  Identified 23 files, 4 folders
✅  Created subfolder: /assets/
▶️  Moving image files to /assets/ [4/11]
⏳  Rename numbered files sequentially
⏳  Generate README.md with file index
⏳  Open folder in Explorer
```

At any point you can:
- **Pause** — suspend execution after the current step completes
- **Stop** — cancel all remaining steps (completed steps are not reversed)
- **Undo** — reverse the last completed step (available for file and clipboard operations)

---

## Safety Features

### Pre-Execution Plan Review
For any task with more than one step, or any step that involves writing, deleting, or running shell commands, the Agent always shows a plan for review before executing.

### Destructive Action Confirmation
Actions that cannot be undone (deleting files, sending emails, running shell commands with output) require an explicit confirmation click even when they are part of an approved plan.

### Audit Log
Every action the Agent takes is logged:
- **Hub → Agent → Activity Log** — in-app searchable history
- **File log:** `%LOCALAPPDATA%\ArizenOS\logs\agent.log`

Log entries include: timestamp, task ID, tool called, arguments, result, and whether it was user-approved or scheduled.

### Undo

File operations (create, rename, move) are undoable within 5 minutes via:
- **Win + Z** (if Agent is focused)
- **Hub → Agent → Activity Log → [Action] → Undo**

Shell command execution is not undoable — the Agent will warn you before running commands with irreversible effects.

---

## Third-Party Extensions

The `@arizen/agent-sdk` enables developers to add custom tools to Arizen Agent. Community tools are available in **Hub → Extensions → Agent Tools**.

Installing a community tool adds it to your Tool Permissions list — you control whether to enable it.

See [Building Extensions](../developer/building-extensions.md) if you want to build your own Agent tools.

---

## Troubleshooting

**"Permission denied" for an action I thought I allowed**
Check that the specific file path or domain is within your allowed scope. Hub → Settings → Agent → Tool Permissions shows the exact permission scope granted to each tool.

**The Agent plan looks wrong before I approve it**
Cancel, then re-phrase your instruction with more specificity. The Agent generates plans based on your instruction — if the plan is wrong, the instruction was ambiguous.

**Scheduled task didn't run**
Check: 1) ArizenOS was running at the scheduled time, 2) The required tool permissions were still enabled, 3) The task log in Hub → Agent → Scheduled Tasks for error details.
