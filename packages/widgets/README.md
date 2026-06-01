# @arizen/widgets

> Widget runtime and plugin API for ArizenOS desktop widgets.

ArizenWidgets provides the runtime environment for desktop widgets — composable, AI-aware, live-updating panels that sit on the desktop canvas. Widgets are sandboxed JavaScript modules with declared permissions.

## What's in Here

| Export | Description |
|---|---|
| `WidgetRuntime` | Loads, sandboxes, and renders widgets |
| `WidgetSDK` | API surface available to widget code |
| `WidgetHost` | React component — mounts a widget in a surface |
| `WidgetRegistry` | Install, update, remove widgets |
| `useWidget()` | Hook for widget state and data binding |

## Widget Format

```typescript
// my-widget/index.ts
import { defineWidget } from "@arizen/widgets";

export default defineWidget({
  id: "com.example.my-widget",
  name: "My Widget",
  version: "1.0.0",
  permissions: ["clock", "weather"],
  dimensions: { width: 200, height: 120 },
  render: ({ data, theme }) => ({ ... })
});
```

## Permissions Model

Widgets declare required permissions at install time. Users approve on install. Available permissions: `clock`, `weather`, `system-stats`, `calendar`, `notifications`, `mind` (AI access — requires explicit grant).

No permission = no API access. Sandbox enforced at runtime.
