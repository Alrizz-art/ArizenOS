# ArizenOS Roadmap

This page describes the high-level milestones for ArizenOS. Detailed scope for each milestone is in the linked pages.

ArizenOS follows **milestone-based releases**, not calendar-based ones. Milestones are closed when their scope is complete — not on a fixed date.

Track real-time progress on the [GitHub Project board](https://github.com/Alrizz-art/ArizenOS/projects).

---

## Milestone Overview

```
Now (Pre-Alpha)
│
├─── v0.1.0 ─── First Alpha
│     Core packages, shell MVP, assistant MVP, Hub MVP
│     Target: Internal testing + invited contributors
│
├─── v0.2.0 ─── Alpha 2
│     @arizen/widgets runtime, Arizen Voice, widget marketplace
│
├─── v0.3.0 ─── Alpha 3
│     Arizen Agent, @arizen/agent-sdk public preview
│
├─── v0.4.0 ─── Public Beta
│     Extension marketplace, @arizen/sync, cloud AI opt-in
│     Target: Public availability
│
├─── v0.5.0 ─── Beta 2
│     Performance, accessibility, multi-monitor polish
│
└─── v1.0.0 ─── General Availability
      LTS program, ARM64, Foundation governance, enterprise preview
```

---

## Current Status: Pre-Alpha

| Component | Status |
|---|---|
| Repository architecture | ✅ Complete |
| Governance model | ✅ Complete |
| Brand guidelines | ✅ Complete |
| Documentation architecture | ✅ In progress |
| `@arizen/core` | 🔨 In development |
| `@arizen/glass` | 🔨 In development |
| `@arizen/mind` | 🔨 In development |
| `@arizen/shell` | 🔨 In development |
| `@arizen/ui` | 📅 Planned (v0.1.0) |
| `@arizen/skin` | 📅 Planned (v0.1.0) |
| Arizen Launcher | 📅 Planned (v0.1.0) |
| Arizen Assistant | 📅 Planned (v0.1.0) |
| Arizen Hub | 📅 Planned (v0.1.0) |
| Arizen Voice | 📅 Planned (v0.2.0) |
| Arizen Agent | 📅 Planned (v0.3.0) |
| `@arizen/widgets` | 📅 Planned (v0.2.0) |
| `@arizen/sync` | 📅 Planned (v0.4.0) |
| ARM64 support | 📅 Planned (v1.0.0) |

---

## Milestone Details

- [v0.1.0 — First Alpha](v0.1.0.md)
- [v0.4.0 — Public Beta](v0.4.0.md)
- [v1.0.0 — General Availability](v1.0.0.md)

---

## Principles Guiding the Roadmap

**Depth before breadth.** We will not add new products until the existing ones are excellent. Launcher, Assistant, and Hub must be great before Voice and Agent ship.

**Public APIs after internal stability.** `@arizen/agent-sdk` and `@arizen/widgets` are published when the internal packages they depend on have stabilised. We do not ship a public API on an unstable foundation.

**No artificial deadlines.** Milestones close when the scope is done and quality targets are met. We will not rush a release to hit a date.

**Regressions block milestones.** A known regression in a core user flow blocks milestone close, regardless of how many other features are complete.

---

## How to Influence the Roadmap

1. **File a Feature Request** — [issues/new?template=feature_request.yml](https://github.com/Alrizz-art/ArizenOS/issues/new?template=feature_request.yml)
2. **Open an RFC** — for significant or architectural changes — [issues/new?template=rfc.yml](https://github.com/Alrizz-art/ArizenOS/issues/new?template=rfc.yml)
3. **React to issues** — 👍 reactions on open issues signal community interest to maintainers
4. **Contribute** — The fastest way to get something on the roadmap is to build it — see [CONTRIBUTING.md](../../CONTRIBUTING.md)
