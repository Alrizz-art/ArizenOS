# Building Widgets

ArizenOS Widgets are sandboxed JavaScript components that render on the desktop as glass panels. They can display live data, respond to user interaction, and request specific system permissions.

---

## What Is a Widget?

A widget is:
- A React component rendered in a sandboxed iframe by the `@arizen/widgets` runtime
- Declared with a manifest specifying its permissions, dimensions, and refresh policy
- Sandboxed by default — it cannot access the file system, make arbitrary network requests, or call OS APIs without declared permissions

Widgets are different from extensions (Agent tools). Widgets are **visual** — they render on the desktop. Extensions are **functional** — they give the Agent new capabilities.

---

## Quickstart

### 1. Scaffold a Widget

```bash
node tools/scaffold/widget.mjs my-widget-name
```

Creates:
```
packages/widget-my-widget-name/
├── src/
│   ├── Widget.tsx         # Main component
│   ├── widget.manifest.json
│   └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

### 2. Define the Manifest

```json
// widget.manifest.json
{
  "$schema": "https://arizenos.dev/schemas/widget/v1.json",
  "id": "com.yourname.my-widget",
  "name": "My Widget",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A brief description of what this widget shows.",
  "dimensions": {
    "default": { "width": 320, "height": 200 },
    "min":     { "width": 200, "height": 120 },
    "max":     { "width": 640, "height": 480 },
    "resizable": true
  },
  "refresh": {
    "interval": 60,
    "strategy": "background"
  },
  "permissions": [
    "network:fetch:https://api.example.com"
  ]
}
```

### 3. Write the Widget Component

```tsx
// src/Widget.tsx
import { useWidgetData, useWidgetTheme } from '@arizen/widgets/react'

interface WeatherData {
  temp: number
  condition: string
  city: string
}

export function Widget() {
  const theme = useWidgetTheme()
  const { data, loading, error } = useWidgetData<WeatherData>({
    async fetch() {
      const res = await fetch('https://wttr.in/Tokyo?format=j1')
      const json = await res.json()
      return {
        temp: Number(json.current_condition[0].temp_C),
        condition: json.current_condition[0].weatherDesc[0].value,
        city: 'Tokyo',
      }
    },
    refreshInterval: 60_000,
  })

  if (loading) return <div style={{ color: theme.colors.text.secondary }}>Loading…</div>
  if (error) return <div style={{ color: theme.colors.accent.destructive }}>Error: {error.message}</div>

  return (
    <div style={{
      padding: 16,
      fontFamily: theme.fonts.sans,
      color: theme.colors.text.primary,
    }}>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>{data.temp}°C</h2>
      <p style={{ margin: '4px 0 0', color: theme.colors.text.secondary }}>{data.condition}</p>
      <p style={{ margin: '2px 0 0', fontSize: 12 }}>{data.city}</p>
    </div>
  )
}
```

### 4. Preview Your Widget

```bash
pnpm --filter widget-my-widget-name dev
# Opens a preview in Arizen Hub's widget sandbox
```

---

## Widget SDK API

### `useWidgetTheme()`

Returns the current ArizenOS theme tokens, automatically updated when the user changes themes.

```typescript
const theme = useWidgetTheme()

theme.colors.base.background      // '#0A0A0F'
theme.colors.text.primary         // '#F0F0F8'
theme.colors.accent.primary       // '#6C63FF'
theme.glass.blurRadius            // '16px'
theme.shadows.z2                  // '0 4px 16px rgba(0,0,0,0.4)'
theme.motion.durationNormal       // '200ms'
theme.fonts.sans                  // "'Geist', system-ui, sans-serif"
theme.radius.md                   // '12px'
```

### `useWidgetData<T>(config)`

Fetches and caches data with automatic refresh.

```typescript
const { data, loading, error, refresh } = useWidgetData<T>({
  /** Async function that fetches the data */
  fetch: () => Promise<T>,

  /** Refresh interval in milliseconds. 0 = no auto-refresh */
  refreshInterval?: number,

  /** Initial data to show while the first fetch is in progress */
  initialData?: T,

  /** Called when fetch throws. Return fallback data or rethrow. */
  onError?: (error: Error) => T | Promise<T>,
})
```

### `useWidgetConfig<T>()`

Read user-defined widget settings (if you declared configurable settings in your manifest).

```typescript
const config = useWidgetConfig<{ city: string; units: 'C' | 'F' }>()
// config.city, config.units
```

### `useWidgetSize()`

React to widget resize events.

```typescript
const { width, height } = useWidgetSize()
```

### `sendToAgent(instruction: string)`

Request the Arizen Agent to take an action in response to a widget interaction:

```typescript
<button onClick={() => sendToAgent('Open my email inbox')}>
  Open Email
</button>
```

---

## Permissions Model

Widgets are sandboxed in an iframe with a strict Content Security Policy. To do anything beyond rendering static content, you must declare permissions:

| Permission String | What It Allows |
|---|---|
| `network:fetch:<url-prefix>` | HTTP GET requests to matching URLs |
| `network:fetch:*` | HTTP requests to any URL |
| `clipboard:read` | Read clipboard text |
| `clipboard:write` | Write to clipboard |
| `notifications:send` | Send desktop notifications |
| `agent:send` | Call `sendToAgent()` |
| `storage:local` | Persist data in widget local storage |

Permissions are declared in `widget.manifest.json`. Users see declared permissions when installing a widget and can revoke them at any time.

---

## Packaging & Publishing

```bash
pnpm --filter widget-my-widget-name build
node tools/pack-widget.mjs packages/widget-my-widget-name
# Output: releases/widgets/my-widget-1.0.0.arizen-widget

# Publish to Hub
arizen publish-widget releases/widgets/my-widget-1.0.0.arizen-widget
```

---

## Design Guidelines

**Use theme tokens — never hardcoded colors.** Your widget will automatically adapt when the user changes their theme.

**Respect the glass surface.** Widgets are rendered on a glass panel. Use `theme.colors.base.background` at low opacity for nested containers — don't add a fully opaque background that breaks the glass effect.

**Design for all sizes.** The user can resize your widget. Use flexbox and relative units so your layout adapts gracefully from `min` to `max` dimensions.

**Show loading states.** Data fetching is asynchronous. Always handle `loading` and `error` states explicitly — a widget that shows a blank panel while loading feels broken.

**Keep refresh intervals sensible.** A widget that fetches data every second is wasteful. Use the longest interval that still feels live (weather: 60s, stocks: 15s, system metrics: 5s).
