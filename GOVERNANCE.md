# ArizenOS Governance Model

> Arizen Technologies — Open Source Governance v1.0
> Modeled after Linux Foundation, Apache Software Foundation, and CNCF governance standards.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Governance Structure](#2-governance-structure)
3. [Decision Making](#3-decision-making)
4. [Roles and Responsibilities](#4-roles-and-responsibilities)
5. [Maintainer Rules](#5-maintainer-rules)
6. [Committees](#6-committees)
7. [Conflict Resolution](#7-conflict-resolution)
8. [Amendments](#8-amendments)

---

## 1. Overview

ArizenOS is an open-source project governed by **Arizen Technologies** in collaboration with its community of contributors and maintainers. This document defines the formal governance structure for the ArizenOS project and all repositories under the `Alrizz-art/ArizenOS` namespace.

### Governance Principles

- **Transparency**: All governance decisions are made in public, on GitHub.
- **Meritocracy**: Influence is earned through consistent, high-quality contribution.
- **Inclusion**: The project actively works to lower barriers for new contributors.
- **Stability**: Governance changes require broad consensus and a formal process.
- **Accountability**: Every role carries documented responsibilities and expectations.

---

## 2. Governance Structure

```
┌──────────────────────────────────────────┐
│          Steering Committee              │
│   (Strategic + Legal + Funding)          │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│           Technical Council              │
│   (Architecture + Roadmap + Standards)   │
└──┬──────────────┬───────────────┬────────┘
   │              │               │
┌──▼───┐    ┌────▼────┐    ┌─────▼──────┐
│ Core │    │ Module  │    │ Community  │
│ Team │    │ Owners  │    │ Moderators │
└──┬───┘    └────┬────┘    └─────┬──────┘
   │              │               │
┌──▼───────────────▼───────────────▼──────┐
│              Contributors               │
│   (All merged-PR authors)               │
└─────────────────────────────────────────┘
```

### Body Definitions

| Body | Size | Term | Quorum |
|---|---|---|---|
| **Steering Committee** | 3–5 seats | Annual | 3 of 5 |
| **Technical Council** | 5–7 seats | 6 months | 4 of 7 |
| **Core Team** | Unlimited | Ongoing | N/A |
| **Module Owners** | 1–3 per module | Ongoing | N/A |
| **Community Moderators** | 3–6 seats | 6 months | Majority |

---

## 3. Decision Making

### Lazy Consensus (Default)

All routine decisions — merging PRs, tagging releases, updating documentation, closing issues — operate on **lazy consensus**: a proposal is considered approved unless an objector raises a formal `-1` within the defined review window.

Review windows by decision type:

| Decision Type | Window |
|---|---|
| Bug fix PR merge | 24 hours after 2 approvals |
| Feature PR merge | 72 hours after 2 approvals |
| Breaking change PR | 7 days after 3 approvals (1 must be TC) |
| Module addition | 7 days after TC discussion |
| Roadmap change | 14 days after public RFC |
| Governance amendment | 21 days + formal vote |

### Formal Voting

Used for: governance amendments, new Steering Committee members, project-wide policy changes, license changes, and breaking API changes.

**Voting Rules:**
- One vote per seated role (SC member, TC member)
- Votes are cast publicly in the relevant GitHub Discussion
- `+1` = approve, `0` = abstain, `-1` = block (must include written objection)
- Simple majority (`>50%`) for most decisions
- Supermajority (`>66%`) for governance amendments and license changes
- Steering Committee holds veto power on legal, funding, and trademark decisions only

### Request for Comments (RFC)

Any contributor may open an RFC for substantial changes. RFC process:

1. Open a GitHub Discussion in the `RFC` category
2. Tag `kind/rfc` and the relevant module label
3. 14-day public comment period (minimum)
4. Technical Council reviews and summarizes feedback
5. TC votes: `accept`, `defer`, or `reject` (with rationale)
6. Accepted RFCs become `tracking issues` with assigned owner

---

## 4. Roles and Responsibilities

### Contributor

**Who:** Anyone who has had at least one PR merged into any ArizenOS repository.

**Rights:**
- Participate in all public discussions
- Open issues and pull requests
- Vote in community polls (non-binding)
- Be credited in release notes

**Responsibilities:**
- Follow the Code of Conduct
- Follow contribution guidelines

**How to become one:** Get a PR merged.

---

### Reviewer

**Who:** Active contributors nominated by a Core Team member and confirmed by the Technical Council.

**Rights:**
- All Contributor rights
- Leave official code review approvals on PRs
- Triage and label issues

**Responsibilities:**
- Review assigned PRs within 5 business days
- Maintain constructive, written code review standards
- Stay active (minimum 1 review per 60 days)

**How to become one:**
- 5+ merged PRs across at least 2 modules
- Nominated by a Core Team member
- 7-day lazy consensus from TC (no `-1`)

**How to lose the role:**
- 90 days of inactivity → automatic move to Emeritus
- Code of Conduct violation → immediate review by SC

---

### Core Team Member

**Who:** Trusted contributors with merge access to one or more repositories.

**Rights:**
- All Reviewer rights
- Merge PRs in their assigned scope
- Open and close milestones
- Participate in Technical Council discussions (non-voting unless also TC)

**Responsibilities:**
- Review PRs in assigned areas within 72 hours of request
- Participate in weekly async TC sync (written summary)
- Mentor Reviewers and new Contributors
- Stay active (minimum 2 contributions per 30 days)

**How to become one:**
- 3+ months as an active Reviewer
- 15+ merged PRs with positive review history
- Formal nomination by a TC member
- 7-day vote by Technical Council (simple majority)

**How to lose the role:**
- 60 days of inactivity → Emeritus status
- Serious Code of Conduct violation → Removal by SC vote

---

### Module Owner

**Who:** The primary maintainer of a specific ArizenOS module (ArizenShell, ArizenMind, ArizenGlass, etc.). Maximum 3 per module.

**Rights:**
- All Core Team rights within their module scope
- Final merge authority for their module's PRs (after required approvals)
- Input on module roadmap in RFC and TC discussions

**Responsibilities:**
- Maintain module-level documentation
- Respond to module-tagged issues within 5 business days
- Communicate breaking changes to TC with minimum 30-day notice
- Produce module release notes for each ArizenOS release

**How to become one:**
- Current Core Team member
- Deep expertise in the relevant module (demonstrated through contribution history)
- Nominated by TC, approved by SC

---

### Technical Council (TC)

**Who:** Elected body of 5–7 senior contributors responsible for technical direction.

**Rights:**
- All Module Owner rights
- Vote on RFC acceptance
- Vote on new Reviewer and Core Team appointments
- Propose roadmap items and architecture changes

**Responsibilities:**
- Publish a written TC sync summary every 2 weeks (GitHub Discussions)
- Review and vote on all open RFCs within 21 days of submission
- Maintain the public roadmap and milestone assignments
- Represent technical community interests to the Steering Committee

**Election:**
- Held every 6 months
- Any Core Team member may stand for election
- All Contributors may vote (one vote per GitHub account with merged PR)
- Top vote-getters fill available seats
- No more than 2 seats from the same employer

---

### Steering Committee (SC)

**Who:** 3–5 appointed members responsible for organizational, legal, funding, and trademark decisions.

**Rights:**
- Veto on legal, funding, trademark, and licensing decisions
- Approve Arizen Technologies partnership announcements
- Set and modify project-wide policies with TC input

**Responsibilities:**
- Hold at least one public SC meeting per quarter (written minutes published)
- Manage trademark licensing and press inquiries
- Ensure project financial sustainability
- Appoint and remove Technical Council chairs

**Initial Composition:**
The Steering Committee at v1.0 is appointed by Arizen Technologies. The SC will transition to a community-election model at `v1.0.0` general availability.

---

### Emeritus

Former Core Team, TC, or Module Owner members who have stepped back from active contribution. Receive credit in project documentation, may return to active status by request and TC vote.

---

## 5. Maintainer Rules

### Activity Requirements

| Role | Minimum Activity | Inactivity Grace Period |
|---|---|---|
| Reviewer | 1 review / 60 days | 30-day notice before demotion |
| Core Team | 2 contributions / 30 days | 60-day notice before demotion |
| Module Owner | 1 module contribution / 30 days | 30-day notice before handoff |
| TC Member | 1 TC sync response / 14 days | 2 missed syncs → automatic review |

### Stepping Down

Any maintainer may step down voluntarily at any time by:
1. Opening a GitHub issue tagged `governance/step-down`
2. Proposing a successor if applicable
3. TC acknowledges within 7 days and transitions responsibilities

Voluntary step-downs receive Emeritus status immediately. There is no shame in stepping down — it is expected and respected.

### Reinstatement

Emeritus maintainers may request reinstatement via GitHub Discussion. TC votes (simple majority, 7-day window). No minimum waiting period.

### Removal for Cause

Removal of a maintainer for Code of Conduct violations or sustained negligence:
1. Formal complaint filed with Steering Committee (privately or via `conduct@arizenos.dev`)
2. SC investigates within 14 days (subject may respond)
3. SC votes in private session
4. Decision communicated to subject privately first, then publicly (without sensitive details)
5. Removed maintainer may appeal to SC within 14 days

---

## 6. Committees

### Security Response Team (SRT)

- 3 members appointed by SC
- Handles private vulnerability disclosures via `security@arizenos.dev`
- 90-day disclosure policy (CVE coordination)
- Publishes security advisories on GitHub Security Advisories

### Design Review Committee (DRC)

- 3 members: 1 TC, 1 Core Team, 1 community designer
- Reviews all UI/UX changes that affect the ArizenOS visual language
- Required approval for changes to ArizenGlass, ArizenFlow, or any public-facing design surface

### Accessibility Working Group (AWG)

- Open membership — any contributor may join
- Maintains the `accessibility-backlog` milestone
- Required review for any UI component change

---

## 7. Conflict Resolution

### Interpersonal Conflicts

Handled by Community Moderators. Parties may request private mediation at any time. Moderators publish anonymized summaries of enforcement actions for community trust.

### Technical Disagreements

1. Both parties write up their position in the relevant GitHub issue
2. TC reviews both positions and solicits additional community input (7 days)
3. TC votes; majority rules
4. Either party may escalate to SC within 14 days if they believe the TC decision violated governance rules (not simply that they disagreed)

### Governance Disputes

Escalated to SC. SC decision is final except in cases of license change (requires supermajority vote of all Contributors who have voted in the prior election).

---

## 8. Amendments

This governance document may be amended by:
1. Any SC or TC member opening a PR against `GOVERNANCE.md`
2. 21-day public comment period
3. Supermajority vote of SC + TC (combined)
4. Announcement in GitHub Discussions, project newsletter, and README

Minor editorial amendments (typos, formatting, clarifications that do not change rights or responsibilities) may be merged by any Core Team member with a 7-day lazy consensus window.

---

*ArizenOS Governance Model v1.0 — June 2025*
*Arizen Technologies — github.com/Alrizz-art/ArizenOS*
*License: CC BY 4.0*
