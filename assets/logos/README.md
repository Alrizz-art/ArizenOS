# ArizenOS Logo Assets

Place your logo files here before building the .apbx.

## Required Files

| Filename | Format | Size | Usage |
|----------|--------|------|-------|
| `arizenOS_logo_oem.bmp` | 24-bit BMP | **120×120 px** | Windows OEMInformation registry (System Info page) |
| `arizenOS_logo_white.png` | PNG (transparent) | 800×200 px | White variant for dark backgrounds |
| `arizenOS_logo_dark.png` | PNG (transparent) | 800×200 px | Dark/colored variant |
| `arizenOS_icon.ico` | ICO | 256×256 + multi-res | Desktop shortcuts, file associations |

## Color Palette

```
#0F172A  slate-950  — Deep background
#1E293B  slate-800  — Card background  
#3B82F6  blue-500   — Primary accent
#38BDF8  sky-400    — Bright accent
#F8FAFC  slate-50   — Primary text
```

## OEM Logo Requirements

The OEM logo shown in **Settings → System → About** and **sysdm.cpl** must be:
- **Format:** 24-bit BMP (no alpha channel)
- **Size:** Exactly 120×120 pixels
- **Path after install:** `C:\ArizenOS\OEM\arizenOS_logo.bmp`

Convert from PNG using:
```powershell
$img = [System.Drawing.Image]::FromFile(".\arizenOS_logo.png")
$bmp = New-Object System.Drawing.Bitmap(120, 120)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($img, 0, 0, 120, 120)
$bmp.Save(".\arizenOS_logo_oem.bmp", [System.Drawing.Imaging.ImageFormat]::Bmp)
```
