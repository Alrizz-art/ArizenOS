# ADR-0002 — Glass Rendering Engine

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2025-06-01 |
| **Authors** | Arizen Technologies Steering Committee |
| **Supersedes** | — |

---

## Context

ArizenOS requires a GPU-accelerated glass rendering system that:

1. Produces real-time gaussian blur of the content behind any ArizenOS surface
2. Supports depth layering — surfaces at different Z-levels cast and receive depth shadows
3. Responds to ambient context (window position, system brightness, user theme)
4. Degrades gracefully on hardware that does not support advanced compositing
5. Works within the constraints of Electron's Chromium renderer

Several approaches were evaluated:

**Option A — CSS `backdrop-filter`**
The simplest implementation. Chromium exposes `backdrop-filter: blur()` natively. No native code required.

*Problems:* `backdrop-filter` in Chromium on Windows does not blur the actual desktop content behind the Electron window — it blurs within the Chromium compositor boundary. A glass panel in ArizenOS would blur other web content, not the windows below it. This would produce a fake "glass" effect that does not reflect the actual desktop.

**Option B — Windows Acrylic / Mica (WinUI3)**
Use the native Windows Acrylic material system via WinUI3.

*Problems:* Acrylic and Mica are controlled by Windows and offer limited customization. They cannot be driven programmatically at the per-pixel level ArizenOS requires. They do not support depth layering. The material appearance is dictated by the OS theme, conflicting with ArizenOS's design token system.

**Option C — DirectComposition + Direct2D via N-API**
Capture the desktop content behind ArizenOS windows using DWM APIs, render a real-time blurred version using Direct2D Gaussian blur effects, and composite it back as the background of ArizenOS surfaces via DirectComposition.

*Problems:* Significant implementation complexity. Requires native N-API modules. DWM thumbnail capture has privacy implications (capturing all visible content on screen).

**Option D — Hybrid (Chosen)**
Use DirectComposition for off-screen surface management and Direct2D for blur rendering, combined with a CPU-side blur compositor for the depth layering pass. Fall back to a CSS `backdrop-filter`-based approximation on hardware that does not support DirectComposition.

---

## Decision

We adopt **Option D — Hybrid DirectComposition + Direct2D rendering** as the glass rendering engine, implemented in `@arizen/renderer`.

### Architecture

```
┌─────────────────────────────────────────────┐
│          @arizen/renderer (TypeScript API)      │
│  GlassEngine · GlassSurface · GlassTheme    │
└─────────────────────┬───────────────────────┘
                      │ N-API
┌─────────────────────▼───────────────────────┐
│         arizen-glass-native (C++ / N-API)    │
│  DirectComposition · Direct2D · DWM APIs     │
└─────────────────────────────────────────────┘
                      │
        ┌─────────────┴────────────┐
        ▼                          ▼
┌──────────────┐          ┌─────────────────┐
│DirectComposite│          │  Direct2D       │
│(surface tree) │          │  Effect Graph   │
│               │          │  (blur, shadow) │
└──────────────┘          └─────────────────┘
```

### Key Design Points

**Surface capture:** ArizenOS uses `DwmRegisterThumbnail` to obtain a real-time composite of the desktop content behind each glass surface. This is the same API used by Windows taskbar preview thumbnails — it is sanctioned by Microsoft and does not require elevated privileges.

**Blur rendering:** Direct2D's `ID2D1Effect` with `CLSID_D2D1GaussianBlur` renders the captured surface through a blur effect graph at native GPU resolution. The blur radius is driven by the `blur-radius` design token from `@arizen/skin`.

**Depth layers:** ArizenOS defines 5 depth levels (Z0–Z4). Each level contributes an additive drop shadow rendered via Direct2D. Shadow parameters (offset, spread, opacity) are defined in the design token system.

**Fallback:** When `DwmIsCompositionEnabled()` returns false (e.g. on VMs without GPU passthrough), the engine falls back to the CSS renderer with `backdrop-filter`. In this mode, glass effects blur within the Chromium context only, which is visually adequate for non-GPU environments.

**Performance:** The native blur is rendered asynchronously on the GPU. The JavaScript API exposes a `RequestAnimationFrame`-aligned update loop. Surfaces that are not visible are automatically suspended.

---

## Consequences

**Positive:**
- Authentic real-time glass that reflects actual desktop content
- Full control over blur radius, depth, and color tinting via the design token system
- Hardware-appropriate fallback that degrades gracefully
- No dependency on Windows Acrylic/Mica — design tokens fully control appearance

**Negative:**
- Significant native module complexity (C++ N-API binding required)
- DWM thumbnail capture requires the ArizenOS process to be visible — glass doesn't work when the process is fully minimized
- Additional build toolchain requirements for contributors (MSVC compiler required)
- The fallback renderer produces a visually different result to the full renderer

**Mitigations:**
- Native module is isolated in `@arizen/renderer` — contributors working on other packages are not affected by the C++ toolchain requirement
- Visual regression tests run both the full and fallback renderers to catch regressions in both paths
- CI Windows runners have MSVC pre-installed

---

## Review

This decision will be reviewed at the `@arizen/renderer` v1.0.0 milestone. The review should assess:
- Whether DirectComposition thumbnail capture remains performant at scale
- Whether DWM API changes in future Windows versions affect the approach
- Whether the Visual regression test suite catches all meaningful regressions in the fallback path
