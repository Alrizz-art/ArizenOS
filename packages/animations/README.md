# @arizen/animations

> Physics-based animation engine for ArizenOS.

ArizenAnimations drives every motion in the platform. Transitions, entrance animations, hover states, drag physics — all governed by a shared animation system with a consistent physical vocabulary. Nothing snaps unless it should.

## What's in Here

| Export | Description |
|---|---|
| `animate()` | Core animation primitive — value over time |
| `spring()` | Spring physics preset factory |
| `ease()` | Standard easing curve library |
| `stagger()` | List entrance stagger utility |
| `Transition` | React component for declarative transitions |
| `useMotion()` | React hook for imperative animation control |
| `MotionTokens` | Canonical duration and easing constants |

## Motion Token System

```typescript
export const MotionTokens = {
  duration: {
    instant:  50,   // Tooltips, badges
    fast:    150,   // Hover states, button press
    normal:  250,   // Panel open/close, page transitions
    slow:    400,   // Modal entrance, full-page transitions
    ambient: 600,   // Background, ambient animations
  },
  spring: {
    snappy:  { stiffness: 400, damping: 30 },
    smooth:  { stiffness: 200, damping: 25 },
    bouncy:  { stiffness: 300, damping: 20 },
    gentle:  { stiffness: 100, damping: 20 },
  },
} as const;
```

## Reduced Motion

All ArizenAnimations animations respect `prefers-reduced-motion`. When active, durations collapse to ≤50ms and spring animations become instant crossfades. No code required from consumers — the engine handles it.
