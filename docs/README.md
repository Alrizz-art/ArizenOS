# ArizenOS Documentation

> All documentation for the ArizenOS platform lives here.

## Structure

| Directory | Contents |
|---|---|
| `site/` | Docusaurus documentation site (deployed to docs.arizenos.dev) |
| `architecture/` | Architecture Decision Records (ADRs) |
| `rfcs/` | Accepted RFCs (moved here after TC acceptance) |
| `migration/` | Version migration guides |

## Local Development

```bash
pnpm --filter @arizen/docs dev    # Start docs site locally
pnpm --filter @arizen/docs build  # Build static site
```

## Contributing to Docs

Documentation contributions follow the same process as code. See [`/CONTRIBUTING.md`](../CONTRIBUTING.md) — Documentation Requirements section.

All docs are written in Markdown. The docs site is built with Docusaurus v3 and deployed automatically on merge to `main`.

## ADR Process

Create a new ADR by copying the template at `architecture/ADR-NNNN-template.md`. Increment the number. Open a PR — Architecture changes require TC review.
