# Themes & Customisation Guide

ArizenOS's theming system is built on compiled design tokens. Every visual property — color, blur radius, shadow depth, animation timing — is defined in a token file and applied system-wide in real time.

---

## Built-in Themes

ArizenOS ships with four production themes:

| Theme | Palette | Character |
|---|---|---|
| **Void** | Deep black · `#0A0A0F` base · Luminous purple/blue accents | Immersive, focused, cinematic |
| **Aurora** | Deep navy · `#0D1117` base · Aurora-green highlights | Developer-oriented, minimal |
| **Ash** | Warm grey · `#1C1C1E` base · Muted amber accents | Professional, warm, readable |
| **Prism** | Off-white · `#F5F5F7` base · Sharp contrast | Bright, clean, high-DPI-optimised |

Switch themes instantly: **Hub → Themes → [Theme Name] → Apply**

Theme switches apply in real time with a smooth 200ms cross-fade — no restart required.

---

## Community Themes

Browse and install community themes from **Hub → Themes → Community**.

Community themes are reviewed for:
- Token format compliance
- No embedded JavaScript (themes are declarative data only)
- No external network requests

To install a theme from a file: **Hub → Themes → Install from file** (accepts `.arizen-theme` or `.json`)

---

## Creating a Custom Theme

### 1. Start from a Base

Fork a built-in theme to start:

```bash
# In your ArizenOS data directory
cd %LOCALAPPDATA%\ArizenOS\themes
```

Or duplicate from Hub → Themes → [Theme] → Duplicate.

### 2. Theme File Structure

A theme is a JSON file following the ArizenOS Design Token Schema:

```json
{
  "$schema": "https://arizenos.dev/schemas/theme/v1.json",
  "meta": {
    "name": "My Theme",
    "author": "Your Name",
    "version": "1.0.0",
    "description": "A brief description",
    "tags": ["dark", "minimal"]
  },
  "tokens": {
    "color": {
      "base": {
        "background":     { "value": "#0A0A0F" },
        "surface":        { "value": "#111118" },
        "surface-raised": { "value": "#1A1A24" },
        "border":         { "value": "#ffffff14" }
      },
      "accent": {
        "primary":        { "value": "#6C63FF" },
        "primary-hover":  { "value": "#7B73FF" },
        "secondary":      { "value": "#00E5C8" },
        "destructive":    { "value": "#FF4B4B" }
      },
      "text": {
        "primary":        { "value": "#F0F0F8" },
        "secondary":      { "value": "#8B8BA0" },
        "disabled":       { "value": "#4A4A60" }
      }
    },
    "glass": {
      "blur-radius":      { "value": "16px" },
      "tint-opacity":     { "value": "0.12" },
      "tint-color":       { "value": "#6C63FF" },
      "border-opacity":   { "value": "0.08" }
    },
    "shadow": {
      "z1": { "value": "0 2px 8px rgba(0,0,0,0.3)" },
      "z2": { "value": "0 4px 16px rgba(0,0,0,0.4)" },
      "z3": { "value": "0 8px 32px rgba(0,0,0,0.5)" },
      "z4": { "value": "0 16px 64px rgba(0,0,0,0.6)" }
    },
    "motion": {
      "duration-fast":   { "value": "100ms" },
      "duration-normal": { "value": "200ms" },
      "duration-slow":   { "value": "400ms" },
      "easing-default":  { "value": "cubic-bezier(0.16, 1, 0.3, 1)" }
    },
    "radius": {
      "sm":  { "value": "6px" },
      "md":  { "value": "12px" },
      "lg":  { "value": "20px" },
      "xl":  { "value": "32px" },
      "full":{ "value": "9999px" }
    },
    "font": {
      "family-sans": { "value": "'Geist', 'Inter', system-ui, sans-serif" },
      "family-mono": { "value": "'Geist Mono', 'Fira Code', monospace" },
      "size-base":   { "value": "14px" },
      "weight-normal":{ "value": "400" },
      "weight-medium":{ "value": "500" },
      "weight-bold":  { "value": "700" }
    }
  }
}
```

### 3. Hot Reload

While editing your theme file, enable live preview:
**Hub → Themes → Developer → Enable Hot Reload**

ArizenOS watches the file for changes and applies them in real time — no save-and-apply cycle.

### 4. Test Your Theme

Use **Hub → Themes → Preview** to see your theme applied to all UI components before sharing it.

Check contrast ratios: **Hub → Themes → Accessibility Audit** runs a WCAG 2.1 AA compliance check on your color tokens.

### 5. Share Your Theme

Package and upload to the community:

```bash
arizen theme pack my-theme.json --output my-theme.arizen-theme
arizen theme publish my-theme.arizen-theme  # requires arizen account
```

Or submit a PR to the [ArizenOS Community Themes repository](https://github.com/Alrizz-art/ArizenOS-themes).

---

## Custom Fonts

ArizenOS ships with **Geist** (sans) and **Geist Mono** (mono) by Vercel. To use custom fonts:

1. Drop the font files (`.ttf`, `.otf`, `.woff2`) into `%LOCALAPPDATA%\ArizenOS\fonts\`
2. Reference in your theme: `"family-sans": { "value": "'YourFont', system-ui, sans-serif" }`

---

## Accent Color (Quick Customisation)

For quick customisation without creating a full theme, change the accent color:
**Hub → Settings → Appearance → Accent Color**

This overrides the `color.accent.primary` token of the active theme without changing anything else.

---

## Wallpapers

**Hub → Wallpapers** includes:
- Built-in curated static and animated wallpapers
- Community wallpapers
- AI-generated wallpapers (via Arizen Assistant)
- Import from file (JPEG, PNG, WebP, MP4, WebM)

Dynamic wallpapers (video and live) use GPU-decoded rendering and have negligible CPU overhead on modern hardware.
