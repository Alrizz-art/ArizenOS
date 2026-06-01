# @arizen/ui

> Shared glass component library for all ArizenOS products.

The single source of UI primitives used across every ArizenOS app. Built on React 18, powered by `@arizen/glass` for rendering and `@arizen/flow` for motion. Fully accessible (WCAG 2.2 AA), fully themed via `@arizen/skin`.

## Components

| Category | Components |
|---|---|
| **Layout** | `GlassPanel`, `GlassCard`, `GlassModal`, `GlassDrawer`, `GlassSheet` |
| **Navigation** | `TabBar`, `Sidebar`, `Breadcrumb`, `CommandPalette` |
| **Inputs** | `Input`, `TextArea`, `Select`, `Checkbox`, `Toggle`, `Slider`, `Radio` |
| **Actions** | `Button`, `IconButton`, `ContextMenu`, `DropdownMenu`, `Tooltip` |
| **Feedback** | `Toast`, `Progress`, `Spinner`, `Skeleton`, `Badge`, `Alert` |
| **Data** | `Table`, `VirtualList`, `DataGrid`, `SearchBar` |
| **Overlay** | `Dialog`, `Popover`, `HoverCard`, `Sheet` |
| **Typography** | `Heading`, `Text`, `Code`, `Kbd` |

## Usage

```tsx
import { GlassCard, Button, useTheme } from "@arizen/ui";

function MyComponent() {
  const { tokens } = useTheme();
  return (
    <GlassCard elevation={2}>
      <Button variant="primary">Launch</Button>
    </GlassCard>
  );
}
```

## Rules

- Every component exports its Props type
- Every component has a Storybook story
- Every component has axe-core a11y test
- No component imports from any `apps/` package
- All animations use `@arizen/flow` — no raw CSS transitions
