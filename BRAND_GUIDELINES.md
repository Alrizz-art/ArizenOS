# ArizenOS Brand Guidelines
### Arizen Technologies — Official Design Handbook v1.0

> *"The Future of Personal AI Computing"*

---

## Table of Contents

1. [Brand Story](#1-brand-story)
2. [Brand Voice](#2-brand-voice)
3. [Design Philosophy](#3-design-philosophy)
4. [Typography Rules](#4-typography-rules)
5. [Color System](#5-color-system)
6. [Logo Rules](#6-logo-rules)
7. [Accessibility Standards](#7-accessibility-standards)
8. [Documentation Standards](#8-documentation-standards)
9. [Naming Conventions](#9-naming-conventions)
10. [Marketing Guidelines](#10-marketing-guidelines)

---

## 1. Brand Story

### Where We Come From

The personal computer changed everything. It moved power from institutions to individuals. For two decades, that power sat dormant inside an interface paradigm designed for an era of folders, files, and desktops that mimicked physical desks.

Then AI arrived — and nothing changed on the screen.

**Arizen Technologies** was founded on a single, uncomfortable observation: the most transformative technology in a generation was being delivered through chat boxes and browser tabs, bolted onto operating systems that hadn't fundamentally rethought their design since Windows Vista. The interface hadn't arisen to meet the moment.

ArizenOS is our answer.

### The Name

**Arizen** — past participle of *arise*. To come into being. To emerge from what came before.

It carries two meanings simultaneously: the system has risen to meet the AI era, and the user — the developer, the student, the researcher — *rises* through the power of their tools. Software that doesn't lift its users hasn't earned the name.

The name is short, pronounceable in every major language, and owns its domain. It is not a portmanteau. It is not an acronym. It is a posture.

### What We Build

ArizenOS is not a Windows replacement. It is not a theme. It is not a chatbot.

It is a **desktop experience platform** — an open-source intelligence layer that runs on top of Windows 10 and Windows 11, reimagining the interface for an age where the most important tool on your computer is no longer a spreadsheet but an AI collaborator.

We draw from the best: Apple's obsession with material and light, OpenAI's clarity of thought, Linear's respect for the user's time, Arc Browser's willingness to question what a browser — or a desktop — *has to be*.

And we give it back, freely, to everyone who wants to build.

### Our Belief

We believe that the best software in history was built in the open, by people who were dissatisfied with what existed and talented enough to replace it.

We believe that great design is not a luxury for users who can afford $3,000 hardware.

We believe that AI should be local, private, and yours.

We believe the interface should disappear when you don't need it and be exactly right when you do.

**We believe the system can always arise.**

---

## 2. Brand Voice

### Personality Pillars

ArizenOS speaks with **four voices**, applied in proportion to context:

| Pillar | Description | When to Use |
|---|---|---|
| **Intelligent** | Precise, considered, never verbose | Technical docs, error messages, system copy |
| **Confident** | Direct and assured without arrogance | Marketing, announcements, positioning |
| **Human** | Warm, real, never corporate | Community communications, onboarding, changelogs |
| **Forward** | Optimistic about what's possible | Vision statements, product reveals, roadmaps |

### Tone by Context

**Product UI Copy**
- Short. Purposeful. Every word earns its place.
- Use active voice. Never passive.
- No filler words: "simply", "just", "easily", "quick".
- Errors should be honest and actionable, never apologetic or vague.

> ✅ `Model not found. Check your inference config at Settings → AI → Runtime.`
> ❌ `Oops! Something went wrong. Please try again.`

**Developer Documentation**
- Precise and code-forward. Assume intelligence, not familiarity.
- Explain the *why*, not just the *what*.
- Code examples over prose when a choice exists.
- No hand-holding. No condescension.

> ✅ `ArizenMind.query() returns a ReadableStream. Pipe it directly to your renderer.`
> ❌ `Now we're going to look at how you can use the query function!`

**Marketing & Web**
- Confident, punchy, and vision-forward.
- Short sentences. Short paragraphs. White space is a feature.
- Lead with outcomes, not features.
- Avoid superlatives without proof ("best", "most powerful", "revolutionary").

> ✅ `The desktop, rethought. Open source. Built for AI.`
> ❌ `The most revolutionary, powerful, cutting-edge AI desktop platform ever created.`

**Community & Social**
- Human. Real. Opinionated but not tribal.
- Celebrate contributors by name.
- Share reasoning behind decisions, not just decisions.
- Acknowledge when something is hard.

### Words We Use

| Use | Avoid |
|---|---|
| desktop experience platform | desktop OS, skin, theme, mod |
| intelligence layer | AI assistant, chatbot, copilot |
| open source | free (when referring to license) |
| contributors | users (for people who build on ArizenOS) |
| local inference | on-device AI (too marketing-speak) |
| Arizen Technologies | "we" in formal contexts |
| ArizenOS | Arizen OS, ArizeOS, arizen |

### What We Never Say

- We do not claim to "revolutionize" anything. We show it.
- We do not punch at Microsoft, Apple, or any competitor by name in marketing.
- We do not use AI buzzwords without meaning: "paradigm shift", "synergy", "next-gen", "game-changing".
- We do not overpromise on roadmap items. If it ships, we talk about it.

---

## 3. Design Philosophy

### The Three Laws of Arizen Design

**I. Depth Before Decoration**
Every visual element must serve a functional purpose before it serves an aesthetic one. Glass, blur, and translucency in ArizenOS communicate layer hierarchy, focus state, and system depth — they are not applied for beauty alone. If removing an effect doesn't change how the user understands the interface, it should be removed.

**II. Motion Carries Meaning**
Animation in ArizenOS is never decorative. Every transition communicates something: where an element came from, where it is going, what its relationship is to surrounding elements. Animations must be physically plausible — elements have mass, momentum, and friction. Snap-in transitions are banned except for system-critical feedback.

**III. Intelligence is Invisible**
The AI layer of ArizenOS should be the least visible and most useful part of the system. It should surface when needed and disappear when not. It must never interrupt. It must never demand attention it hasn't earned. A well-designed AI feature is one the user doesn't think about — they just notice their work gets done faster.

### Design References

**Apple (macOS Tahoe 26 / Liquid Glass)**
We study Apple not to copy but to understand what it means to take material seriously. Liquid Glass is not a visual trick — it is a design language that encodes depth, hierarchy, and focus through light behavior. We extend this language onto Windows with our own GPU rendering pipeline.

**OpenAI**
OpenAI's product aesthetic is defined by restraint. White space. Helvetica-grade precision. Interfaces that make complexity feel approachable. We apply this discipline to AI-surface design: the interface for interacting with intelligence should feel effortless, never technical.

**Linear**
Linear's contribution to product design is the understanding that speed is a design value. Fast UI is not just faster — it *feels* more intelligent, more trustworthy, more alive. ArizenOS has a frame-rate target, a render budget, and a latency budget. Meeting them is a design requirement, not an engineering one.

**Arc Browser**
Arc demonstrated that a product category everyone thought was solved could be fundamentally rethought with enough conviction. We apply that same conviction to the desktop. Nothing is sacred. Every interaction pattern on Windows was designed for a pre-AI world. We question all of it.

### Visual Hierarchy System

```
Level 0: System Glass (background diffusion layer)
Level 1: Desktop canvas (widgets, wallpaper, ambient elements)
Level 2: Shell chrome (taskbar, tray, launcher) — frosted
Level 3: Application windows — clear glass with depth shadow
Level 4: Active window — elevated, focused, full material depth
Level 5: Modal / AI overlay — maximum elevation, maximum blur radius
```

Each level has a defined blur radius, opacity value, border luminance, and shadow spread. No element may render at a level above its semantic role.

---

## 4. Typography Rules

### Type Scale Philosophy

ArizenOS uses a **dual-family system**: a geometric sans-serif for UI chrome and a humanist sans-serif for reading content. The combination creates a system that feels both engineered and warm — precise when it needs to be, approachable when it should be.

### Primary Typeface — Inter

**Usage:** UI chrome, system labels, settings, navigation, code comments in documentation

Inter was designed specifically for computer screens and UI interfaces. Its optical corrections at small sizes, its extensive OpenType feature set, and its legibility under translucent glass surfaces make it the right choice for ArizenOS's shell layer.

```
Font Family: Inter
Variable Font: Inter Variable (preferred)
Fallback Stack: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

**Scale:**

| Name | Size | Weight | Line Height | Tracking | Usage |
|---|---|---|---|---|---|
| `label-xs` | 10px | 500 | 14px | +0.4px | System badges, tags |
| `label-sm` | 12px | 500 | 16px | +0.2px | Tooltips, captions |
| `label-md` | 13px | 500 | 18px | 0 | Default UI label |
| `label-lg` | 14px | 500 | 20px | -0.1px | Prominent UI labels |
| `body-sm` | 13px | 400 | 20px | 0 | Secondary body copy |
| `body-md` | 14px | 400 | 22px | 0 | Primary body copy |
| `body-lg` | 16px | 400 | 26px | -0.1px | Large body, onboarding |
| `title-sm` | 18px | 600 | 24px | -0.2px | Section titles |
| `title-md` | 24px | 600 | 30px | -0.4px | Page headings |
| `title-lg` | 32px | 700 | 38px | -0.6px | Hero headings |
| `display-sm` | 48px | 700 | 54px | -1.0px | Marketing hero |
| `display-lg` | 64px | 800 | 70px | -1.5px | Brand moments |

### Secondary Typeface — Geist

**Usage:** Code blocks, terminal output, configuration files, developer documentation inline code

Geist (by Vercel) is a monospace typeface engineered for code legibility. Its clean geometry and generous x-height make it readable at small sizes in dark terminal environments.

```
Font Family: Geist Mono
Fallback Stack: "Cascadia Code", "JetBrains Mono", "Fira Code", monospace
```

### Tertiary Typeface — Instrument Serif

**Usage:** Marketing headlines, brand moments, product announcements, press releases

Instrument Serif brings editorial weight to ArizenOS's outward-facing brand moments. It is never used in product UI.

```
Font Family: Instrument Serif
Fallback Stack: Georgia, serif
Usage: Marketing only. Never in product UI.
```

### Typography Rules

**DO:**
- Use Inter Variable with `font-feature-settings: "cv01", "cv02", "tnum"` for tabular numerals in data displays
- Set `text-rendering: optimizeLegibility` on body text
- Use optical sizing (`font-optical-sizing: auto`) when available
- Maintain a maximum line length of 72 characters for body text in documentation

**DO NOT:**
- Use font weights below 400 in UI (illegible on glass surfaces)
- Apply text shadows to body copy
- Use italic on UI labels (reserve for documentation emphasis only)
- Mix more than two type families on a single surface
- Set `letter-spacing` on weights above 600 (distorts optical kerning)

---

## 5. Color System

### Design Intent

ArizenOS's color system is built around **three principles**:
1. Colors must look correct on glass surfaces (translucent backgrounds shift apparent hue)
2. The system must adapt across light mode, dark mode, and high-contrast mode
3. The accent color is user-selected — the brand palette must coexist with any accent

### Brand Palette

#### Void (Primary Dark)
The foundational dark tone of ArizenOS — deep, not flat black. Retains a faint blue-gray character that reads as sophisticated rather than harsh.

| Token | Hex | RGB | Usage |
|---|---|---|---|
| `void-950` | `#080B0F` | 8, 11, 15 | Deepest background, true dark |
| `void-900` | `#0D1117` | 13, 17, 23 | Primary dark background |
| `void-800` | `#161B22` | 22, 27, 34 | Elevated surfaces (dark) |
| `void-700` | `#21262D` | 33, 38, 45 | Cards, panels (dark) |
| `void-600` | `#2D333B` | 45, 51, 59 | Borders, dividers (dark) |
| `void-500` | `#444C56` | 68, 76, 86 | Muted icons, disabled states |
| `void-400` | `#545D68` | 84, 93, 104 | Secondary text (dark) |
| `void-300` | `#768390` | 118, 131, 144 | Tertiary text (dark) |
| `void-200` | `#ADBAC7` | 173, 187, 199 | Secondary text (dark) |
| `void-100` | `#CDD9E5` | 205, 217, 229 | Primary text (dark) |
| `void-50` | `#E6EDF4` | 230, 237, 244 | Inverted / light background |

#### Arizen Blue (Signature Accent)
The default system accent. A precise, AI-associated blue with enough saturation to register on glass without oversaturating.

| Token | Hex | RGB | Usage |
|---|---|---|---|
| `arizen-950` | `#030D1A` | 3, 13, 26 | Deepest |
| `arizen-900` | `#051A33` | 5, 26, 51 | |
| `arizen-800` | `#0A2D57` | 10, 45, 87 | |
| `arizen-700` | `#0D3E78` | 13, 62, 120 | |
| `arizen-600` | `#1057A8` | 16, 87, 168 | |
| `arizen-500` | `#1470CC` | 20, 112, 204 | Primary brand blue |
| `arizen-400` | `#3D8FE0` | 61, 143, 224 | Interactive blue (dark mode) |
| `arizen-300` | `#6AABEE` | 106, 171, 238 | Hover states, focus rings |
| `arizen-200` | `#A8CEEF` | 168, 206, 239 | |
| `arizen-100` | `#D4E8F9` | 212, 232, 249 | Tint backgrounds |
| `arizen-50` | `#EEF6FD` | 238, 246, 253 | Subtle tints |

#### Glass Whites
Semi-transparent whites for layering on glass surfaces. Never use solid white — always prefer a glass white.

| Token | Value | Usage |
|---|---|---|
| `glass-white-5` | `rgba(255,255,255,0.05)` | Subtle surface lift |
| `glass-white-8` | `rgba(255,255,255,0.08)` | Card surface (dark) |
| `glass-white-12` | `rgba(255,255,255,0.12)` | Elevated card, panel |
| `glass-white-16` | `rgba(255,255,255,0.16)` | Active/hover on dark glass |
| `glass-white-24` | `rgba(255,255,255,0.24)` | Modal, sheet on dark |
| `glass-white-48` | `rgba(255,255,255,0.48)` | Light mode glass base |
| `glass-white-80` | `rgba(255,255,255,0.80)` | Light mode foreground glass |

#### Glass Blacks
| Token | Value | Usage |
|---|---|---|
| `glass-black-4` | `rgba(0,0,0,0.04)` | Light mode: surface lift |
| `glass-black-8` | `rgba(0,0,0,0.08)` | Light mode: card |
| `glass-black-16` | `rgba(0,0,0,0.16)` | Light mode: hover |
| `glass-black-40` | `rgba(0,0,0,0.40)` | Dark mode: overlay scrim |
| `glass-black-60` | `rgba(0,0,0,0.60)` | Modal scrim |

#### Semantic Colors

| Token | Light Mode | Dark Mode | Usage |
|---|---|---|---|
| `semantic-success` | `#1A9B4F` | `#3DD68C` | Confirmation, connected states |
| `semantic-warning` | `#C97B1F` | `#F59E0B` | Caution, degraded performance |
| `semantic-error` | `#C42B2B` | `#F87171` | Errors, destructive actions |
| `semantic-info` | `#1470CC` | `#60A5FA` | Informational, AI suggestions |

### Color Rules

**DO:**
- Always test color pairings against both light and dark glass backgrounds
- Use the `arizen-400` blue for interactive elements in dark mode, `arizen-600` in light mode
- Apply `glass-white-*` tokens for all overlay surfaces in dark mode
- Ensure accent color swap (user-customizable) only affects interactive tokens, not brand tokens

**DO NOT:**
- Use pure `#000000` or `#FFFFFF` anywhere in the product UI
- Apply saturated colors to backgrounds larger than a component (button, badge, tag only)
- Use more than two hue families on a single surface
- Use the brand blue as a background color on surfaces wider than 200px

---

## 6. Logo Rules

### Logo Concept

The ArizenOS logomark is an abstract geometric form — an upward-pointing form composed of layered, glass-translucent planes, suggesting both an arrow rising and a layered system architecture. The negative space between layers implies depth and intelligence operating beneath the visible surface.

The wordmark is set in **Inter** at weight 700, with modified letter-spacing at `-0.04em`. The "OS" suffix renders at weight 500 to create a deliberate typographic hierarchy.

### Logo Variants

| Variant | Usage |
|---|---|
| **Full Lockup — Horizontal** | Primary: website headers, press kits, official docs |
| **Full Lockup — Stacked** | App stores, square formats, social media profiles |
| **Logomark Only** | Favicon, app icon, tray icon, watermarks |
| **Wordmark Only** | Text-constrained environments where mark does not render clearly |
| **Monochrome — Dark** | On light backgrounds, print, single-color applications |
| **Monochrome — Light** | On dark or glass backgrounds |

### Clear Space

The minimum clear space around any logo variant is equal to the height of the capital **A** in "ArizenOS" — referred to as **1A**.

```
     ┌─────────────────────────┐
     │         1A              │
     │   ┌─────────────┐       │
1A   │   │   LOGO      │  1A  │
     │   └─────────────┘       │
     │         1A              │
     └─────────────────────────┘
```

No text, imagery, UI element, or border may enter the clear space zone.

### Minimum Size

| Application | Minimum Width |
|---|---|
| Digital — Full Lockup | 120px |
| Digital — Logomark Only | 24px |
| Print — Full Lockup | 30mm |
| Print — Logomark Only | 8mm |

Below minimum size, use the wordmark-only variant.

### Logo Color Rules

**On dark backgrounds:**
Use the light monochrome variant (white wordmark, white or luminous blue mark)

**On light backgrounds:**
Use the dark monochrome variant (void-900 wordmark, arizen-500 mark)

**On glass surfaces:**
Use the light monochrome variant with `opacity: 0.92`

**On brand color backgrounds:**
Use the light monochrome variant only

**On photography:**
Always place logo on a solid background plate (void-900 at 72% opacity, minimum) before placing over photography. Never float the logo directly over complex imagery.

### Logo Don'ts

- Do not rotate the logo
- Do not change the proportional relationship between mark and wordmark
- Do not apply drop shadows to the logo
- Do not apply gradients to the wordmark
- Do not outline the wordmark
- Do not recreate the logomark using system fonts or emoji
- Do not place the logo on backgrounds that create insufficient contrast (minimum 4.5:1)
- Do not animate the logo with effects not approved in the motion guidelines
- Do not combine the ArizenOS logo with any other company's logo in a single lockup without approval from Arizen Technologies

---

## 7. Accessibility Standards

### Commitment

ArizenOS is used by developers, students, and researchers across a wide range of visual, motor, and cognitive abilities. Accessibility is not a compliance checkbox — it is a design constraint that produces better outcomes for everyone.

We target **WCAG 2.2 Level AA** as our minimum standard. We target **WCAG 2.2 Level AAA** for all text-based interfaces.

### Color Contrast Requirements

| Context | Minimum Ratio | Target |
|---|---|---|
| Body text (≥ 14px, regular weight) | 4.5:1 | 7:1 |
| Large text (≥ 18px, or ≥ 14px bold) | 3:1 | 4.5:1 |
| UI components and focus indicators | 3:1 | 4.5:1 |
| Decorative elements | No requirement | — |
| Disabled states | No requirement | — |

**Glass Surface Rules:**
Because ArizenOS renders text over translucent glass, contrast ratios must be calculated against the *minimum visible background* — the lightest or darkest background that can appear behind the glass at any wallpaper configuration.

All text must meet contrast requirements against the system's wallpaper-agnostic base color, not against a single static background.

### Focus Management

- All interactive elements must have a visible focus ring. ArizenOS uses a **2px solid** focus ring in `arizen-400` (dark mode) or `arizen-600` (light mode), with a 2px offset.
- Focus must always be visible. The glass blur effect must never render a focus ring invisible.
- Focus order must be logical — matching visual reading order. Tab stops follow visual Z-order.
- Modal dialogs trap focus. When a modal closes, focus returns to the element that triggered it.

### Motion and Animation

- All animations above 250ms duration must respect `prefers-reduced-motion: reduce`.
- When reduced motion is enabled, transitions collapse to instant or sub-50ms crossfades.
- No animation may flash more than 3 times per second (WCAG 2.3.1 — Three Flashes or Below Threshold).
- Parallax effects must be disabled under `prefers-reduced-motion`.

### Screen Reader Support

- All UI elements must have appropriate ARIA labels, roles, and states.
- Glass surfaces must not create aria-hidden content that is visually meaningful.
- System tray notifications must announce to assistive technology via ARIA live regions.
- The AI command layer must be fully operable via keyboard alone.

### Keyboard Navigation

Every feature of ArizenOS must be accessible without a mouse:
- Launcher: `Win` key opens, arrow keys navigate, `Enter` selects, `Esc` closes
- Window management: Full keyboard shortcut set, documented and remappable
- AI command layer: `Win + Space` (default) → type → `Enter` to execute
- All context menus: navigable by keyboard

### High Contrast Mode

ArizenOS must detect and respect Windows High Contrast mode (now "Contrast Themes"). When active:
- Glass effects disable completely
- All backgrounds render as system colors (`Canvas`, `WindowText`, etc.)
- Focus rings increase to 3px
- Animations disable

### Dyslexia-Friendly Mode

A documented accessibility setting that:
- Increases body text to `body-lg` minimum
- Increases line-height by 30%
- Increases letter-spacing by `+0.05em`
- Offers optional dyslexia-specialized typeface override (e.g., OpenDyslexic)

---

## 8. Documentation Standards

### Documentation Types

| Type | Purpose | Format | Audience |
|---|---|---|---|
| **API Reference** | Complete function/method signatures | Auto-generated + hand-edited | Developers |
| **Guides** | Step-by-step task completion | Markdown | All |
| **Concepts** | Mental models for ArizenOS architecture | Markdown | Developers |
| **Tutorials** | End-to-end project walkthroughs | Markdown + code | Developers |
| **Changelogs** | What changed and why | Keep A Changelog format | All |
| **RFCs** | Architectural decisions, open for comment | Markdown | Core contributors |
| **Charter / Guidelines** | Product and brand policy | This document | Team + Community |

### Writing Standards

**Structure:**
- Every doc starts with a one-sentence purpose statement in the first paragraph. No preamble.
- Use H2 for top-level sections, H3 for subsections, H4 sparingly. Never exceed H4.
- Code examples before explanatory prose when the task is primarily technical.
- End every guide with a "Next Steps" or "Related" section.

**Tone:**
- Second person ("you", "your") throughout. Never "the user" or "one".
- Active voice. If you find yourself writing "was configured by", rewrite it.
- No jargon without definition on first use. No acronyms without expansion on first use.

**Code Blocks:**
- All code blocks must specify language for syntax highlighting
- Use `arizen` as the language tag for ArizenOS-specific config syntax
- Provide a copy button implementation in all doc sites
- Inline code (backtick) for: function names, file paths, config keys, CLI flags
- Code blocks (triple backtick) for: multi-line samples, terminal output, file contents

```typescript
// ✅ Good: language-specified, minimal, purpose-clear
const mind = await ArizenMind.create({ model: "llama-3-8b" });
const response = await mind.query("Summarize my open PRs");
```

```
// ❌ Bad: no language, no context, wall of unrelated code
var x = new Thing();
x.doSomething();
x.doOtherThing();
x.doAnotherThing();
```

**File Naming:**
- All documentation files: `SCREAMING_SNAKE_CASE.md` for root-level official docs
- Guide and tutorial files: `kebab-case.md`
- RFC files: `RFC-NNNN-short-description.md`
- Changelog: `CHANGELOG.md` (singular, at repo root)

### Version Tagging

All documentation must specify the ArizenOS version it applies to:
```markdown
> Applies to: ArizenOS 0.4.0 and later
```

Docs that apply to `main` only:
```markdown
> Applies to: Unreleased (main branch)
```

### Changelog Format

ArizenOS follows [Keep a Changelog](https://keepachangelog.com):

```markdown
## [0.4.0] — 2025-09-12

### Added
- ArizenMind v2 with local streaming inference

### Changed
- Glass blur radius reduced from 48px to 32px for performance

### Deprecated
- `ArizenMind.ask()` — use `ArizenMind.query()` instead

### Removed
- Legacy Rainmeter widget bridge (shipped in 0.1.0, deprecated in 0.3.0)

### Fixed
- Taskbar flicker on secondary monitor hotplug (#284)

### Security
- Patched local inference endpoint exposed on 0.0.0.0 by default (#291)
```

---

## 9. Naming Conventions

### Product Naming

| Name | Usage | Notes |
|---|---|---|
| **ArizenOS** | Full product name | No space. Capital A, capital OS. |
| **Arizen Technologies** | Company name | Full form for legal, press, formal contexts |
| **Arizen** | Short brand reference | Acceptable in community/social. Never "Arizen OS" |
| **ArizenMind** | AI layer module | One word, no space |
| **ArizenShell** | Shell module | One word, no space |
| **ArizenGlass** | Rendering engine | One word, no space |
| **ArizenFlow** | Animation system | One word, no space |
| **ArizenSkin** | Theming SDK | One word, no space |
| **ArizenWidgets** | Widget runtime | One word, plural, no space |
| **ArizenAgent** | Agentic task runner | One word, no space |
| **ArizenSync** | Cross-device sync service | One word, no space |

### Module Naming Rules

- All first-party ArizenOS modules use the `Arizen` prefix followed by a single descriptive word.
- Module names are PascalCase with no separator.
- Third-party extensions and plugins must NOT use the `Arizen` prefix — this namespace is reserved for Arizen Technologies official modules.
- Community extensions use the format: `arizen-<author>-<name>` (all lowercase, hyphen-separated)

### Code Naming Conventions

**TypeScript / JavaScript:**
```typescript
// Classes, types, interfaces — PascalCase
class ArizenMindClient { }
interface QueryOptions { }
type ModelProvider = "local" | "cloud";

// Functions, methods, variables — camelCase
const queryResult = await mind.query(prompt);
function initializeGlassRenderer() { }

// Constants — SCREAMING_SNAKE_CASE
const MAX_CONTEXT_LENGTH = 8192;
const DEFAULT_BLUR_RADIUS = 32;

// React components — PascalCase
function GlassPanel({ children }: GlassPanelProps) { }

// Hooks — camelCase with "use" prefix
function useArizenMind() { }

// Event handlers — camelCase with "handle" prefix
function handleQuerySubmit() { }

// CSS custom properties — kebab-case with "arizen" namespace
--arizen-blur-radius: 32px;
--arizen-glass-opacity: 0.12;
--arizen-accent: var(--arizen-blue-500);
```

**File Naming:**
```
components/GlassPanel.tsx         # React components — PascalCase
hooks/useArizenMind.ts            # Hooks — camelCase
lib/glass-renderer.ts             # Utilities/lib — kebab-case
types/mind.d.ts                   # Type definitions — kebab-case
constants/glass.ts                # Constants — kebab-case
styles/glass-panel.css            # Styles — kebab-case matching component
```

**Branch Naming:**
```
feat/mind-v2-streaming
fix/taskbar-flicker-secondary-monitor
docs/glass-renderer-api
chore/bump-inter-font-2.1
refactor/glass-layer-system
```

**Commit Messages (Conventional Commits):**
```
feat(mind): add local streaming inference for llama-3
fix(taskbar): resolve flicker on secondary monitor hotplug (#284)
docs(api): update ArizenMind.query() signature for v2
chore(deps): bump Inter from 4.0 to 4.1
refactor(glass): extract blur stack into isolated renderer module
perf(glass): reduce default blur radius from 48px to 32px
```

### Version Numbering

ArizenOS follows **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH[-prerelease]

0.1.0      — Initial public alpha
0.4.0-rc.1 — Release candidate
1.0.0      — Stable, general availability
```

- **MAJOR** bumps when breaking changes are introduced to the Plugin API or Skin SDK
- **MINOR** bumps when new modules or capabilities are added
- **PATCH** bumps for bug fixes and performance improvements

Pre-release identifiers: `alpha`, `beta`, `rc` (release candidate)

---

## 10. Marketing Guidelines

### Brand Positioning Statement

> *ArizenOS is the open-source, AI-first desktop experience platform for Windows — for the developers, students, and researchers building the next decade of technology.*

This statement is used verbatim in press kits and formal positioning documents. It is not tagline copy.

### Tagline

**Primary Tagline:**
> The Future of Personal AI Computing

This tagline is used on: the website hero, product launch announcements, press kit header, and App Store/product listings.

**Secondary Tagline Options (context-dependent):**
> Open. Intelligent. Yours. *(developer and open-source contexts)*
> Your desktop, arisen. *(consumer-facing, social media)*
> AI-native. Open source. Runs on what you have. *(technical audiences)*

### Campaign Voice Principles

**Lead with the outcome, not the feature.**
Never write "ArizenOS includes local LLM inference." Write "Your AI runs on your machine. Your data goes nowhere."

**Use white space aggressively.**
ArizenOS marketing copy should breathe. Short sentences. Line breaks. Punctuated pauses. Never write dense paragraph marketing copy.

**Show, don't describe.**
Screenshots, screen recordings, and demos are primary. Prose is support.

**The community is the product.**
Feature contributors in marketing materials. Use real usernames. Link to real repos. The open-source community is a marketing asset and deserves credit.

### Website Copy Hierarchy

```
1. Tagline — 5 words max
2. Sub-headline — single sentence outcome statement
3. Primary CTA — verb-forward ("Download", "Get Started", "Explore")
4. Secondary CTA — "View on GitHub"
5. Social proof — contributor count, GitHub stars, testimonials
```

### Social Media Guidelines

**Twitter / X:**
- Max 2 marketing tweets per day from official account
- Code snippets perform better than prose with this audience
- Always link to a real artifact (repo, doc, release note) — no link-free announcements
- Retweet contributors. Credit by @handle.

**GitHub:**
- Release notes must follow the changelog format
- Every release gets a pinned discussion for community Q&A
- The README is a marketing document. Treat it accordingly.

**Reddit (r/unixporn, r/windows, r/programming, r/LocalLLaMA):**
- Always include screenshots in posts. Text-only posts do not perform in visual communities.
- Never post promotional content without a demo. Community first.
- Mods contribute to discussions as individuals, not as Arizen Technologies.

### Press Kit Contents

Every press kit release includes:
- Company one-pager (Arizen Technologies overview)
- Product one-pager (ArizenOS capabilities)
- Logo package (all variants, SVG + PNG, light + dark)
- Screenshots (minimum 8: launcher, desktop, AI layer, settings, multiple themes)
- Screen recording (90-second demo, no voiceover, music optional)
- Founding team bios
- Product Charter link
- GitHub repository link

### Partnership Guidelines

All partnership announcements must:
- Be coordinated with co-announcement from both parties
- Not include any revenue figures or user counts not confirmed in writing
- Link to both parties' GitHub repositories when applicable
- Be reviewed by a core maintainer before publication

ArizenOS does not accept paid placement in marketing materials. If a third-party tool is featured, it is because the community uses it and the recommendation is genuine.

---

## Document Control

| Field | Value |
|---|---|
| **Document** | ArizenOS Brand Guidelines |
| **Version** | 1.0 |
| **Published** | June 2025 |
| **Owner** | Arizen Technologies |
| **Review Cycle** | Every major product release |
| **Repository** | `github.com/Alrizz-art/ArizenOS` |
| **License** | CC BY 4.0 — share with attribution |

---

*This document is the single source of truth for ArizenOS brand and design decisions. All product, marketing, and community materials produced under the ArizenOS name are expected to comply with this handbook. Questions, amendments, and exceptions are submitted via GitHub Issues tagged `brand`.*

---

**Arizen Technologies**
*The Future of Personal AI Computing*
