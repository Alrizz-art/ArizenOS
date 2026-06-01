# Security Policy

> Arizen Technologies — ArizenOS Security Policy v1.0

---

## Supported Versions

Only the versions listed below receive security patches. If you are on an unsupported version, upgrade before reporting.

| Version | Supported |
|---|---|
| Latest stable (`vX.Y.Z`) | ✅ Yes |
| Previous stable (`vX.Y-1.Z`) | ✅ Yes (critical only) |
| LTS branch | ✅ Yes (for LTS window) |
| Pre-release (alpha/beta/rc) | ⚠️ Best effort |
| `< 0.4.0` | ❌ No |

---

## Reporting a Vulnerability

**Do not report security vulnerabilities via public GitHub Issues, Discussions, or PRs.**

Disclosing a vulnerability publicly before a patch is available puts all ArizenOS users at risk.

### Private Disclosure

Email **`security@arizenos.dev`** with:

- Subject: `[SECURITY] <short description>`
- Affected component(s) and version(s)
- Description of the vulnerability and impact
- Steps to reproduce (as detailed as possible)
- Any proof-of-concept code or screenshots
- Your preferred credit name/handle for the advisory (optional)

You will receive acknowledgment within **48 hours** and a substantive response within **7 days**.

### GitHub Private Vulnerability Reporting

You may also use GitHub's built-in [private vulnerability reporting](https://github.com/Alrizz-art/ArizenOS/security/advisories/new) feature, available in the **Security** tab of the repository.

---

## Disclosure Policy

ArizenOS follows **coordinated disclosure** with a **90-day deadline**:

| Day | Action |
|---|---|
| 0 | Report received, acknowledged within 48 hours |
| 7 | Substantive response: confirmed, investigating, or declined |
| 30 | Status update to reporter |
| 60 | Patch development complete, testing begins |
| 75 | Patch released to stable channel |
| 90 | Public advisory published (CVE if applicable) |

If a patch cannot be produced within 90 days, we communicate this to the reporter and coordinate an extended timeline. We do not simply ignore the deadline.

**Zero-day exceptions:** If a vulnerability is already publicly known or actively exploited, we accelerate to the shortest safe timeline, typically 24–72 hours.

---

## Severity Classification

We use the [CVSS v3.1](https://www.first.org/cvss/) scoring system.

| CVSS Score | Severity | Response SLA |
|---|---|---|
| 9.0–10.0 | Critical | 24–48 hours |
| 7.0–8.9 | High | 72 hours |
| 4.0–6.9 | Medium | Next patch release |
| 0.1–3.9 | Low | Next minor release |

---

## Security Commitments

- **Local-first**: ArizenOS AI inference runs locally by default. No prompt data is sent to external servers without explicit user opt-in.
- **No telemetry by default**: ArizenOS does not collect usage data, crash reports, or system information unless the user explicitly enables it.
- **No auto-update code execution**: The update mechanism downloads and verifies signatures before execution. No remote code execution via update channel.
- **Extension sandboxing**: Third-party extensions run in an isolated context with declared permissions. Extensions cannot access the ArizenMind API without explicit user grant.

---

## Hall of Fame

Security researchers who responsibly disclose vulnerabilities are credited in our Security Hall of Fame (published in GitHub Security Advisories) with their preferred name/handle, unless they request anonymity.

---

*ArizenOS Security Policy v1.0 — June 2025*
*Contact: security@arizenos.dev*
