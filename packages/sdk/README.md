# @arizen/sdk

> Public plugin API for ArizenAgent extensions.

Third-party developers use the Agent SDK to register custom tools that ArizenAgent can call. Tools are sandboxed, permission-gated, and distributed through Arizen Hub.

## What's in Here

| Export | Description |
|---|---|
| `defineTool()` | Register a callable tool with schema + handler |
| `ToolContext` | Runtime context injected into every tool call |
| `ToolPermission` | Typed permission declarations |
| `SDKPlugin` | Plugin manifest interface |
| `z` | Re-exported Zod for tool input schema definition |

## Writing a Tool

```typescript
import { defineTool, z } from "@arizen/sdk";

export const readFileTool = defineTool({
  name: "read_file",
  description: "Read the contents of a file on the user's filesystem",
  permissions: ["filesystem:read"],
  input: z.object({
    path: z.string().describe("Absolute path to the file"),
  }),
  handler: async ({ input, ctx }) => {
    ctx.log(`Reading: ${input.path}`);
    const content = await fs.readFile(input.path, "utf-8");
    return { content };
  },
});
```

## Distribution

Tools are packaged as npm packages with the `arizen-agent-tool` keyword and distributed via Arizen Hub. Arizen Technologies reviews all tools before marketplace listing.
