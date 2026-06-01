# Security Policy

ArizenOS runs with deep system integration — shell replacement, local AI inference, autonomous agent execution, and Win32 bindings. Security is a first-class priority, not an afterthought.

---

## Supported Versions

| Version | Status | Security Fixes |
|---|---|---|
| `main` (pre-alpha) | Active development | Best-effort |
| `0.x.x` (alpha) | Not yet released | Will receive fixes |
| Older releases | — | Not applicable yet |

Once v1.0.0 ships, the supported version table will be expanded with LTS commitments. See [RELEASE.md](RELEASE.md).

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Public disclosure before a fix is available puts all ArizenOS users at risk.

### Preferred: GitHub Private Vulnerability Reporting

Use GitHub's built-in private advisory system:
[https://github.com/Alrizz-art/ArizenOS/security/advisories/new](https://github.com/Alrizz-art/ArizenOS/security/advisories/new)

This creates a private, encrypted thread between you and the maintainers. It is the fastest path to resolution.

### Alternative: Email

Email: [security@arizenos.dev](mailto:security@arizenos.dev)

Use the subject line: `[SECURITY] <brief description>`

**Include in your report:**

- A clear description of the vulnerability
- The affected component(s) and version(s)
- Steps to reproduce (proof of concept if available)
- Your assessment of impact and severity (CVSS score if known)
- Whether you have already disclosed this elsewhere

We accept PGP-encrypted reports. Our public key is available at [https://arizenos.dev/.well-known/security.pgp](https://arizenos.dev/.well-known/security.pgp).

---

## Response Timeline

| Milestone | Target |
|---|---|
| Acknowledgement of receipt | **48 hours** |
| Initial severity assessment | **5 business days** |
| Status update to reporter | **10 business days** |
| Fix available (critical/high) | **30 days** |
| Fix available (medium/low) | **90 days** |
| Public disclosure | After fix is released |

We follow a **90-day coordinated disclosure policy**. If a fix cannot be delivered within 90 days, we will negotiate an extension with the reporter or recommend temporary mitigations.

---

## Severity Classification

We use [CVSS v3.1](https://www.first.org/cvss/) for severity scoring.

| Severity | CVSS Score | Examples |
|---|---|---|
| **Critical** | 9.0–10.0 | Remote code execution, privilege escalation to SYSTEM |
| **High** | 7.0–8.9 | Local privilege escalation, auth bypass, data exfiltration |
| **Medium** | 4.0–6.9 | Information disclosure, DoS, sandbox escape (widget/agent) |
| **Low** | 0.1–3.9 | Minor info leaks, non-exploitable crashes |

---

## Scope

### In Scope

All code in this repository, including:

- `apps/*` — Arizen Launcher, Assistant, Voice, Hub, Agent
- `packages/*` — all shared libraries, especially `@arizen/agent-sdk`, `@arizen/shell`, `@arizen/mind`, `@arizen/sync`
- The installer and updater
- The widget sandbox and permission model
- The Agent tool execution system (file, shell, browser)
- The local AI inference layer (`@arizen/mind`)

### Out of Scope

- Third-party Electron vulnerabilities (report to [Electron Security](https://github.com/electron/electron/security/policy))
- Third-party models downloaded through Arizen Hub
- Community extensions and themes not authored by ArizenOS maintainers
- Issues only reproducible on unsupported Windows versions
- Social engineering attacks on maintainers
- Theoretical vulnerabilities without a proof of concept

---

## Security Architecture Principles

ArizenOS is designed with the following security principles:

1. **Local by default.** AI inference and agent execution run entirely on your machine. No data is sent to any external server without your explicit opt-in action.

2. **Explicit permission model.** The Arizen Agent requires user approval for tool categories (file write, shell execute, browser control). Permissions are displayed before execution, not after.

3. **Widget sandbox.** Widgets run in a sandboxed JavaScript runtime with a capability-based permission model. They cannot access the filesystem, network, or OS APIs without declared and approved permissions.

4. **E2E encrypted sync.** If you enable Arizen Sync, all data is encrypted on your device before transmission. The sync server never has access to plaintext.

5. **No telemetry.** ArizenOS collects no usage data, crash reports, or analytics by default. There is no opt-out because there is no opt-in.

6. **Signed releases.** All official releases are code-signed and include SHA-256 checksums. Verify before installing.

---

## Security Hall of Fame

We credit all researchers who responsibly disclose security vulnerabilities. With your permission, your name and a description of the finding will be included in the Security Hall of Fame published at [https://arizenos.dev/security/hall-of-fame](https://arizenos.dev/security/hall-of-fame) after the fix is released.

---

## Bug Bounty

A formal bug bounty program is planned for the v1.0.0 release. Until then, we offer:

- Public credit in the Security Hall of Fame
- A mention in the release notes for the fixing version
- Our sincere gratitude

---

## Contact

| Purpose | Contact |
|---|---|
| Vulnerability reports | [security@arizenos.dev](mailto:security@arizenos.dev) |
| Security architecture questions | [GitHub Discussions](https://github.com/Alrizz-art/ArizenOS/discussions) |
| Code of Conduct violations | [conduct@arizenos.dev](mailto:conduct@arizenos.dev) |

---

*This policy is reviewed and updated with each major release.*
