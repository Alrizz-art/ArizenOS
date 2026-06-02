# Security Patch Process

> **Owner:** Security-designated Core Maintainer ("Security Lead")  
> **Disclosure Standard:** Coordinated Vulnerability Disclosure (CVD)  
> **Response SLA:** Critical — 24h; High — 72h; Medium — next patch cycle  
> **Contact:** See `SECURITY.md` (repo root) for private reporting channel

---

## 1. Security Classification

Every security issue is classified before any remediation work begins. Classification determines the response timeline, disclosure approach, and release type.

### Severity Levels

| Severity | Definition | ArizenOS Examples | SLA |
|----------|-----------|------------------|-----|
| **Critical** | Exploitation allows system compromise, remote code execution, or privilege escalation | A script fetching and executing untrusted remote content; a WinGet package ID pointing to malicious software | 24 hours to initial response; patch within 48h |
| **High** | Significant weakening of security posture; protection component disabled; user data at risk | An entry accidentally disabling Defender Real-Time Protection; UAC being lowered | 72 hours to initial response; patch within 7 days |
| **Medium** | Security regression that degrades but doesn't eliminate protection | A registry change that weakens but doesn't remove a security feature | Next scheduled patch cycle |
| **Low** | Minor security concern with negligible real-world impact | A log file that writes more verbose info than intended | Next MINOR release |
| **Informational** | Finding with no exploitable impact | A hardcoded but non-sensitive string | Tracked, no SLA |

### Security vs. Bug

A finding is classified as **security** (not a bug) if it:
- Weakens Windows Defender, Firewall, UAC, or Update mechanisms
- Introduces or enables privilege escalation
- Enables execution of code not reviewed by the ArizenOS team
- Exposes user credentials, PII, or system secrets
- Could allow an attacker to weaponize the playbook against the user

---

## 2. Reporting Channels

| Channel | Use For | Response Time |
|---------|---------|--------------|
| **Private email** (listed in `SECURITY.md`) | Critical and High severity | 24–72h |
| **GitHub Security Advisories** | Critical and High — encrypted disclosure | 24–72h |
| **GitHub Issues** (label: `security`) | Medium and Low severity | Best effort |

**Never report Critical or High severity issues in public GitHub Issues.** A public report gives attackers a window before the fix is deployed. Use private channels and allow coordinated disclosure.

---

## 3. Receiving and Triaging a Report

### Step 1 — Acknowledge (within SLA window)

When a security report is received via private channel:

```
Response to reporter:
1. Acknowledge receipt
2. Confirm which version(s) are affected
3. Provide an estimated timeline for the fix
4. Confirm whether public disclosure will be coordinated
5. Assign a tracking ID (e.g. ARIZEN-SEC-001)
```

### Step 2 — Reproduce

Security Lead reproduces the issue on a clean VM (Windows 10 22H2 or Windows 11 23H2, whichever is applicable). This confirms:
- The issue is real (not a misconfiguration or reporter error)
- The scope of impact (which versions, which configurations, which Windows builds)
- Whether it is exploitable in a default ArizenOS configuration

### Step 3 — Classify

Security Lead assigns the severity level (Section 1). If uncertain, classify higher and revise down only after confirmation.

### Step 4 — Notify Core Maintainers

Security Lead notifies all Core Maintainers via private channel with:
- Tracking ID and severity
- Reproduction steps
- Proposed fix approach
- Proposed disclosure timeline

---

## 4. Remediation Workflow

### Critical and High Severity

```
Private security branch: security/ARIZEN-SEC-001
  │
  ├── Branch from: the affected stable release tag (e.g., v0.1.0)
  ├── Fix developed and reviewed privately
  ├── Tested on: clean Win 10 22H2 VM + clean Win 11 23H2 VM
  ├── Security audit script run pre and post
  ├── 1 Core Maintainer review (expedited — 24h window)
  │
  └── Release as hotfix:
        Tag: v{version+patch} on security branch
        Merge to main (cherry-pick the fix)
        Simultaneously: publish GitHub Release + public disclosure
```

**Private branches are not publicly visible.** The fix is merged to a private fork or kept in a local branch until disclosure.

**Do not create a draft PR** — GitHub shows draft PRs to all contributors with repo access.

### Medium Severity

Medium severity issues are remediated through the normal PR process on a public branch, with the security label. The fix enters the next scheduled patch cycle.

The reporter is notified when the fix is released. No coordinated disclosure is required for Medium severity.

---

## 5. Disclosure Policy (Coordinated Vulnerability Disclosure)

ArizenOS follows CVD: the project and the reporter agree on a public disclosure date before any public information is released.

### Standard Timeline

```
Day 0:   Report received
Day 1:   Acknowledgement + classification
Day 7:   Fix completed and tested (Critical/High)
Day 14:  Coordinated disclosure date (default)
         Patch published + advisory posted simultaneously
```

The reporter may request a longer embargo (up to 90 days) if they need time for their own disclosure process (e.g., they are a security researcher with a coordinated publication). The project may also request an extension if the fix is complex.

**Maximum embargo: 90 days from the report date.** After 90 days, the project may disclose unilaterally.

### Disclosure Exceptions

**Early disclosure** (before the fix is ready) may be required if:
- The vulnerability is already publicly known (zero-day exploit in the wild)
- An independent discovery is about to be published by another researcher
- The reporter has not agreed to an embargo

In these cases, the Security Lead immediately notifies Core Maintainers, expedites the fix, and publishes a temporary mitigation alongside the issue.

---

## 6. Security Advisory Publication

For Critical and High severity issues, a GitHub Security Advisory is published simultaneously with the patch release.

### Advisory Content

```
Title:    {Component}: {Short description} in ArizenOS v{affected range}
CVE:      {CVE identifier if assigned, otherwise "pending" or "N/A"}
Severity: {Critical / High / Medium}
CVSS:     {Score} (calculated using CVSS 3.1)

Affected Versions:
  v{X} through v{Y}

Fixed In:
  v{patch version}

Description:
  {Technical description of the vulnerability — what, how, impact}

Impact:
  {What an attacker could do with this vulnerability on an affected system}

Mitigation (before patch):
  {Any steps users can take to reduce exposure before patching}

Resolution:
  {Upgrade to v{patch version}}
  {If reinstallation required: "Users must reinstall the playbook to apply the fix"}

Credit:
  {Reporter handle or "Internal discovery"}
  {Discovered by: {name/handle} via {channel}}
```

### CVE Assignment

For Critical and High severity vulnerabilities, the Security Lead requests a CVE identifier from MITRE after the fix is ready and before public disclosure.

For Medium and Low severity, CVEs are typically not requested unless the issue has broad industry impact.

---

## 7. Security Patch Release Requirements

A security patch release follows the hotfix process (`RELEASE_BRANCHES.md §7`) with these additional requirements:

| Requirement | Standard Hotfix | Security Patch |
|-------------|----------------|---------------|
| PR reviews | 1 Core Maintainer | 1 Core Maintainer (private review) |
| Unit tests | ✅ Required | ✅ Required |
| Integration tests | Optional | ✅ Required for Critical/High |
| Security audit script | Not required | ✅ Required — must show zero new FAIL |
| Smoke tests | Optional | ✅ Required |
| Changelog entry | Required | Required + `Security` section populated |
| GitHub Security Advisory | Not required | Required for Critical/High |
| Announcement | Standard release | Simultaneous with advisory |

---

## 8. Protected Component Violation Protocol

A special category of security issue is a **Protected Component Violation (PCV)**: any shipped entry or script that modifies a component explicitly forbidden by `ARCHITECTURE.md §5`.

PCVs are always treated as **Critical severity**, regardless of exploitability, because:
1. Users trust ArizenOS's explicit promise not to touch these components
2. Even a non-exploitable PCV is a violation of the security contract with users
3. A PCV may have undetected secondary effects on system security

**PCV response:**
1. The release is immediately yanked (pre-release flagged)
2. A hotfix is prepared within 24 hours
3. A public advisory is posted explaining what was touched and why it was wrong
4. The debloat safety test `test-debloat-safety.ps1` and registry audit `test-registry-keys.ps1` are updated to catch the specific bypass that allowed the PCV
5. A post-mortem is mandatory before any further releases

---

## 9. Security Posture Improvement Process

Beyond reactive patching, ArizenOS maintains proactive security improvement:

### Per-Release Security Review

Before every stable release, the Security Lead completes the review in `SECURITY_REVIEW.md`. Any new FAIL in the post-install security audit blocks the release.

### Annual Security Audit

Once per year (or after every MAJOR release), the project commissions an external security review of:
- All PowerShell scripts
- All registry files
- The build process (supply chain integrity)
- All WinGet package IDs in use

Results are published in a Security Audit Report linked from the GitHub repository.

### Dependency Monitoring

The project monitors:
- WinGet package IDs bundled in `developer-setup.ps1` — if a package is compromised or changes maintainer, the entry is updated or the package is removed
- AME Wizard releases — if a new AME Wizard version changes the playbook execution model, the security implications are reviewed

---

## 10. Security Acknowledgements

All reporters who responsibly disclose and coordinate are credited in:
- The GitHub Security Advisory
- The `CHANGELOG.md` Security section for the fixing release
- A `SECURITY_ACKNOWLEDGEMENTS.md` file in the repository (maintained by Security Lead)

If a reporter requests anonymity, their contribution is credited as "Anonymous researcher" unless they provide a preferred pseudonym.
