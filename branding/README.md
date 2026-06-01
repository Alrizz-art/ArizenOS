# ArizenOS Branding Architecture

> **Status:** Production-Grade v1.0  
> **Last Updated:** June 2026  
> **Owner:** Arizen Technologies  
> **License:** All rights reserved — ArizenOS Contributors

---

## Overview

This directory contains the complete branding system for ArizenOS — the open-source, AI-first desktop experience platform for Windows. Every asset produced under the ArizenOS name must originate from or comply with the specifications defined here.

**Design DNA:** 70% macOS Tahoe 26 · 20% Solo Leveling System UI · 10% JARVIS  
**Design Language:** Liquid Glass · Glassmorphism · Premium · Minimal · Intelligent · Professional  
**Tagline:** *The Future of Personal AI Computing*

---

## Directory Structure

```
branding/
├── README.md                    ← You are here — master index
├── ARCHITECTURE.md              ← Full structural spec + rationale
├── NAMING_CONVENTIONS.md        ← File naming rules for all asset types
├── VERSIONING.md                ← Asset versioning policy
├── CONTRIBUTOR_GUIDE.md         ← Guidelines for branding contributors
├── MIGRATION.md                 ← Migration plan from legacy assets/
│
├── logos/                       ← All logo variants (SVG + PNG)
│   └── README.md                ← Logo spec, variants, usage rules
│
├── wallpapers/                  ← Desktop and lockscreen wallpapers
│   └── README.md                ← Resolution standards, naming rules
│
├── icons/                       ← System icons, app icons, favicons
│   └── README.md                ← Icon grid, sizes, format requirements
│
├── screenshots/                 ← Official product screenshots
│   └── README.md                ← Screenshot standards and composition rules
│
├── oem/                         ← OEM partner branding assets
│   └── README.md                ← OEM guidelines and customization limits
│
├── marketing/                   ← Marketing collateral and campaign assets
│   └── README.md                ← Marketing asset standards
│
└── templates/                   ← Production templates for contributors
    └── README.md                ← Template usage and contribution workflow
```

> **Legacy:** `assets/logos/` and `assets/wallpapers/` contain v0 assets retained for backwards compatibility. New work belongs exclusively in `branding/`. See `MIGRATION.md`.

---

## Quick Reference

| I need to…                    | Go to…                          |
|-------------------------------|----------------------------------|
| Add or update a logo          | `branding/logos/README.md`      |
| Add a wallpaper               | `branding/wallpapers/README.md` |
| Add a system or app icon      | `branding/icons/README.md`      |
| Add a product screenshot      | `branding/screenshots/README.md`|
| Produce OEM branding          | `branding/oem/README.md`        |
| Create a marketing asset      | `branding/marketing/README.md`  |
| Use or submit a template      | `branding/templates/README.md`  |
| Understand the full structure | `branding/ARCHITECTURE.md`      |
| Learn asset naming rules      | `branding/NAMING_CONVENTIONS.md`|
| Understand versioning         | `branding/VERSIONING.md`        |
| Contribute branding assets    | `branding/CONTRIBUTOR_GUIDE.md` |

---

## Core Principles

### 1. Depth Before Decoration
Every visual element must serve a functional purpose before an aesthetic one. Glass, blur, and translucency communicate hierarchy — not decoration.

### 2. Motion Carries Meaning
Every transition communicates spatial relationship. Nothing moves without reason.

### 3. Intelligence is Invisible
The AI layer should be the least visible and most useful part of the system. ArizenOS branding communicates capability through restraint, not spectacle.

---

## Color Quick Reference

| Token | Hex | Usage |
|-------|-----|-------|
| `arizen-500` | `#1470CC` | Primary brand blue |
| `arizen-400` | `#3D8FE0` | Interactive (dark mode) |
| `void-900` | `#0D1117` | Primary dark background |
| `void-100` | `#CDD9E5` | Primary text (dark) |

Full palette: `branding/tokens/source/color.json`

---

*Questions and amendments are submitted via GitHub Issues tagged `brand`.*
