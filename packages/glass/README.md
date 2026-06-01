# @arizen/glass

> GPU-accelerated blur, depth, translucency, and light simulation for ArizenOS.

ArizenGlass is the rendering engine behind every frosted surface, shadow, and depth cue in ArizenOS. It wraps Windows' Desktop Window Manager (DWM) APIs and extends them with a custom compositing pipeline.

## What's in Here

| Export | Description |
|---|---|
| `GlassRenderer` | Main renderer — manages composition layers |
| `BlurStack` | GPU blur pipeline (Gaussian + acrylic) |
| `DepthSystem` | 6-level elevation and shadow system |
| `LightSim` | Ambient light direction simulation |
| `GlassLayer` | Per-window glass configuration |
| `PerformanceBudget` | FPS target enforcement and degradation |

## Architecture

ArizenGlass wraps DWM via N-API native bindings. The blur pipeline runs on the GPU via Direct2D. On systems below the performance budget, effects degrade gracefully (blur radius reduction → opacity fallback → solid fallback).

## Performance Budgets

| Effect | GPU Budget | Fallback |
|---|---|---|
| Full blur (32px) | <8ms/frame | Reduce to 16px |
| Depth shadows | <2ms/frame | Opacity only |
| Light simulation | <1ms/frame | Disable |
