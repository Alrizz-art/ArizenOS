# Security Policy — ArizenOS

ArizenOS takes security seriously. This document outlines how to report
vulnerabilities, what to expect from us, and our commitment to responsible disclosure.

---

## Supported Versions

| Version       | Supported          |
|---------------|--------------------|
| `main` branch | ✅ Yes — latest development |
| Tagged releases | ✅ Latest stable only |
| Older releases | ❌ No — please upgrade |

During pre-1.0 development (`v0.x.x`), only the most recent release receives
security patches. Once `v1.0.0` is released, an LTS support policy will be defined.

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities as public GitHub Issues.**
Public disclosure before a fix is available puts all users at risk.

### Preferred — GitHub Private Security Advisory

Use GitHub's built-in private reporting:

👉 **[Open a Private Security Advisory](https://github.com/Alrizz-art/ArizenOS/security/advisories/new)**

This channel is encrypted, visible only to maintainers, and integrated with
the CVE assignment process.

### Alternative — Email

If you cannot use GitHub's advisory system, email the maintainer directly:

- **To:** security@arizenos.dev *(or contact via GitHub profile if this address is unavailable)*
- **Subject:** `[SECURITY] <short description>`
- **Encrypt with GPG if possible** — see [GPG Key](#gpg-key) below

---

## What to Include in Your Report

Please provide as much of the following as possible:

| Field | Details |
|-------|---------|
| **Description** | Clear explanation of the vulnerability |
| **Type** | e.g. privilege escalation, buffer overflow, info leak, DoS, RCE |
| **Component** | Which subsystem is affected (kernel, mm, net, drivers, etc.) |
| **Version** | ArizenOS version or commit hash |
| **Architecture** | e.g. x86_64 |
| **Steps to Reproduce** | Minimal reproduction steps |
| **Proof of Concept** | Code or QEMU commands, if available |
| **Impact** | What an attacker can achieve |
| **Suggested Fix** | Optional — your proposed mitigation |
| **CVE / CWE** | If you already have a CVE/CWE reference |

A clear, detailed report helps us triage and fix faster.

---

## Responsible Disclosure Timeline

We follow a **90-day coordinated disclosure** standard, consistent with
[Google Project Zero](https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-faq.html)
and [CERT/CC](https://www.kb.cert.org/vuls/disclosure/).

| Day | Action |
|-----|--------|
| **Day 0** | Report received — you receive an acknowledgment within **48 hours** |
| **Day 1–7** | Initial triage and severity assessment |
| **Day 7–14** | Maintainer confirms vulnerability and opens private fix branch |
| **Day 14–60** | Fix developed, tested, and staged for release |
| **Day 60** | Fix released with a patch release (`vX.Y.Z`) |
| **Day 90** | Public disclosure — CVE published, security advisory made public |

### Exceptions

- **Critical / actively exploited**: We aim to release a fix within **7 days**
  and will coordinate an accelerated disclosure timeline with you.
- **Complex / systemic**: If a fix requires more than 90 days, we will notify
  you, explain the reason, and agree on an extended deadline together.
- **No response within 90 days**: If we fail to respond or fix within 90 days
  without agreement, you are free to disclose publicly.

---

## Severity Classification

We use the [CVSS v3.1](https://www.first.org/cvss/calculator/3-1) scoring system.

| Severity | CVSS Score | Response Target |
|----------|------------|-----------------|
| 🔴 Critical | 9.0–10.0 | Patch within 7 days |
| 🟠 High | 7.0–8.9 | Patch within 30 days |
| 🟡 Medium | 4.0–6.9 | Patch within 60 days |
| 🟢 Low | 0.1–3.9 | Patch within 90 days |

---

## What to Expect from Us

- **Acknowledgment** within 48 hours of your report
- **Regular updates** (at least every 14 days) on progress
- **Credit** in the security advisory and release notes (unless you prefer anonymity)
- **CVE assignment** coordination for qualifying vulnerabilities
- **No legal action** against researchers acting in good faith under this policy

---

## Scope

### In Scope

- Kernel privilege escalation
- Memory safety bugs (buffer overflows, use-after-free, heap corruption)
- Syscall interface vulnerabilities
- Bootloader integrity bypass
- Filesystem privilege or data exposure bugs
- Network stack vulnerabilities (RCE, DoS, info leak)
- Driver vulnerabilities affecting kernel integrity
- CI/CD pipeline compromise (supply chain)

### Out of Scope

- Bugs requiring physical access with no software component
- Vulnerabilities in third-party tools (QEMU, GCC, Clang) — report to them directly
- Issues in documentation only (use a regular docs issue)
- Spam, social engineering, or phishing

---

## GPG Key

For encrypted email communication, use the maintainer's GPG public key.

**Fingerprint:** *(To be added by maintainer — run `gpg --gen-key` and publish fingerprint here)*

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[Maintainer: export your key with `gpg --armor --export your@email.com`
and paste it here]
-----END PGP PUBLIC KEY BLOCK-----
```

You can also find the key on [keys.openpgp.org](https://keys.openpgp.org)
by searching for the maintainer's email.

---

## Bug Bounty

ArizenOS is an open-source project currently without a formal bug bounty program.
We offer **public recognition** and **CVE credit** for responsibly disclosed vulnerabilities.

If ArizenOS grows to a scale where a bounty program is warranted, this section
will be updated.

---

## References

- [CERT/CC Vulnerability Disclosure Policy](https://www.kb.cert.org/vuls/disclosure/)
- [Google Project Zero Disclosure Policy](https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-faq.html)
- [CVSSv3.1 Calculator](https://www.first.org/cvss/calculator/3-1)
- [GitHub Private Security Advisories](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/creating-a-repository-security-advisory)
- [CWE — Common Weakness Enumeration](https://cwe.mitre.org/)

---

*This policy follows the [CERT Coordinated Vulnerability Disclosure](https://resources.sei.cmu.edu/asset_files/SpecialReport/2017_003_001_503340.pdf) framework.*
