# ArizenOS Wallpaper Assets

Place your wallpaper files here before building the .apbx.

## Required Files

| Filename | Format | Resolution | Max Size | Usage |
|----------|--------|------------|----------|-------|
| `arizenOS_default.jpg` | JPEG | **3840×2160** (4K) | 2 MB | Primary desktop wallpaper |
| `arizenOS_dark.jpg` | JPEG | 3840×2160 | 2 MB | Dark minimal variant |
| `arizenOS_lockscreen.jpg` | JPEG | **1920×1080** minimum | 5 MB | Lock screen image |
| `arizenOS_alt.jpg` | JPEG | 3840×2160 | 2 MB | Alternate colorway (optional) |

## Design Guidelines

### Recommended Color Palette
```
Deep background:   #0F172A  (primary base)
Mid background:    #1E293B  (secondary elements)
Accent blue:       #3B82F6  (highlights, glows)
Accent sky:        #38BDF8  (secondary highlights)
Text/light:        #F8FAFC  (if text used)
```

### Style Suggestions
- Abstract geometric / topographic line art on deep dark background
- Subtle noise/grain texture for depth
- Soft glowing orbs or nebula-like gradients in blue/slate tones
- ArizenOS logo watermark at low opacity (bottom right or center)
- Avoid busy patterns that compete with desktop icons

### Lock Screen Notes
- Keep center 60% clear (Windows login UI overlay)
- Branding/logo in upper or lower thirds only
- Must pass readability check with white text overlay

## Wallpaper Style (wallpaper.ps1 behavior)

The wallpaper script uses **WallpaperStyle = 10 (Fill)** — crops to fill the screen.
Design for center-weighted compositions; edges may be cropped on non-16:9 monitors.
