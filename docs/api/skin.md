# @arizen/skin

**Stability:** Beta | Theming SDK and design token system

```bash
pnpm add @arizen/skin
```

`@arizen/skin` manages the ArizenOS design token system — loading, compiling, applying, and hot-reloading themes across all apps and components.

---

## SkinEngine

```typescript
import { SkinEngine } from '@arizen/skin'

const skin = await SkinEngine.create({
  themesDir: `${process.env.LOCALAPPDATA}/ArizenOS/themes`,
  builtinThemes: true,         // Include built-in Void, Aurora, Ash, Prism themes
  hotReload: process.env.NODE_ENV === 'development',
})
```

### Loading & Applying Themes

```typescript
// Get available themes
const themes = await skin.listThemes()
// Returns: Array<{ id, name, author, version, preview: string (base64 PNG) }>

// Load a theme (validates schema, compiles tokens)
const theme = await skin.loadTheme('void')

// Apply globally (broadcasts 'theme:changed' event via core EventBus)
await skin.applyTheme('void')

// Apply to a specific Electron BrowserWindow only
await skin.applyTheme('void', { windowId: mainWindow.id })

// Get current theme
const current = skin.getActiveTheme()
```

### Accessing Compiled Tokens

```typescript
const tokens = skin.getTokens()

tokens.color.base.background      // '#0A0A0F'
tokens.color.accent.primary       // '#6C63FF'
tokens.color.text.primary         // '#F0F0F8'
tokens.glass.blurRadius           // 16 (px, as number)
tokens.glass.tintOpacity          // 0.12
tokens.shadow.z2                  // '0 4px 16px rgba(0,0,0,0.4)'
tokens.motion.durationNormal      // 200 (ms, as number)
tokens.radius.md                  // 12 (px, as number)
tokens.font.familySans            // "'Geist', system-ui, sans-serif"
```

### CSS Variable Injection

For renderer processes, tokens are automatically injected as CSS variables:

```css
/* Auto-injected by @arizen/skin into every renderer */
:root {
  --color-base-background:     #0A0A0F;
  --color-accent-primary:      #6C63FF;
  --color-text-primary:        #F0F0F8;
  --glass-blur-radius:         16px;
  --motion-duration-normal:    200ms;
  --radius-md:                 12px;
  /* ... all tokens */
}
```

### React Hook

```tsx
import { useTheme } from '@arizen/skin/react'

function MyComponent() {
  const { tokens, themeId } = useTheme()

  return (
    <div style={{
      backgroundColor: tokens.color.base.background,
      color: tokens.color.text.primary,
      borderRadius: tokens.radius.md,
    }}>
      Content
    </div>
  )
}
```

### Hot Reload (Development)

```typescript
skin.on('theme:file:changed', async (path) => {
  await skin.reloadTheme(path)
})
```

---

## Theme Validation

```typescript
import { validateTheme } from '@arizen/skin'

const result = validateTheme(themeJson)
if (!result.valid) {
  console.error(result.errors)  // Array of { path, message }
}

// WCAG contrast audit
const audit = await skin.auditAccessibility(themeJson)
audit.issues.forEach(issue => {
  console.warn(`${issue.pair}: contrast ${issue.ratio} < ${issue.required} (${issue.level})`)
})
```

---

## Token Schema Reference

Full schema documented at [https://arizenos.dev/schemas/theme/v1.json](https://arizenos.dev/schemas/theme/v1.json).

Top-level token groups:

| Group | Keys |
|---|---|
| `color.base` | `background`, `surface`, `surface-raised`, `border`, `overlay` |
| `color.accent` | `primary`, `primary-hover`, `secondary`, `destructive`, `warning`, `success` |
| `color.text` | `primary`, `secondary`, `disabled`, `on-accent` |
| `glass` | `blur-radius`, `tint-opacity`, `tint-color`, `border-opacity` |
| `shadow` | `z1`, `z2`, `z3`, `z4` |
| `motion` | `duration-fast`, `duration-normal`, `duration-slow`, `easing-default`, `easing-spring` |
| `radius` | `sm`, `md`, `lg`, `xl`, `full` |
| `font` | `family-sans`, `family-mono`, `size-base`, `weight-normal`, `weight-medium`, `weight-bold` |
| `spacing` | `xs`, `sm`, `md`, `lg`, `xl`, `2xl` |
