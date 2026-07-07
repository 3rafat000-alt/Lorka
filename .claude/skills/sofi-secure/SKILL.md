---
name: sofi-secure
description: Run the SOFI Security room on any target — threat-model, pentest, vuln scan, or fix-verify — wiring the vendored cyber knowledge base (company/superpowers/cybersecurity-skills) and the sec-* specialists into one flexible command. Authorized defensive/pentest use on this project only. Grep-first recon, OWASP-driven testing, severity-ranked findings with proof + remediation. Triggers — "security review", "pentest", "threat model", "scan for vulns", "is this secure", "check auth/injection/secrets", "harden", "pen test the api".
---

# /sofi-secure — the Security room, one command

> Scope: **authorized security testing of THIS project only** (owner-run, seed data · Article 07 ·
> `company/constitution/07-security-law.md`). Never target third parties. Findings, code, and warnings
> written in **normal prose, never compressed** (Article 05). The **`brd-cso` security veto is absolute
> below the CEO**; the Security room (`sec-*`) has veto everywhere and gates 3 + 5.
>
> **Knowledge base:** `company/superpowers/cybersecurity-skills/` — 817 vendored cyber skills
> (knowledge-only, scripts stripped). Curriculum in `CURRICULUM.md`, attack map in `ATTACK_COVERAGE.md`,
> lookup via `index.json`/`mappings/`. Read the relevant skill's `SKILL.md` for the method; this command
> does NOT invoke them as slash commands (they are knowledge, not palette skills — [[sofi-cybersecurity-skills-library]]).

**Usage:** `/sofi-secure <mode> [target]` — mode ∈ `threat · pentest · scan · verify`. No mode → `scan` (fast recon).

## Modes → owning agent

| Mode | Does | Agent · KB |
|------|------|-----------|
| `threat` | STRIDE threat model, auth/authz design review, PII classification, pentest scope | `sec-threat-modeler` (+ `dat-privacy-officer` for PII) · KB `implementing-threat-modeling-with-mitre-attack` |
| `pentest` | Active exploit attempts on the target (authorized): injection, IDOR/BOLA, mass-assign, XSS, CSRF, SSRF, JWT/OAuth flaws, CORS | `sec-pentester` · KB `testing-*` / `exploiting-*` skills |
| `scan` | Fast static recon — secrets in git, dep CVEs (SBOM), CI/CD supply-chain, container/IaC | `sec-secrets-warden` + `sec-appsec-engineer` · KB `implementing-secrets-scanning-in-ci-cd`, `generating-and-analyzing-sboms`, `scanning-iac-and-images-with-trivy` |
| `verify` | Re-test after `/sofi-fix` — confirm the vuln is closed, no regression | re-run the finding's original skill · owning `sec-*` agent |

All security work is gated by `sec-lead` (deputy to `brd-cso`).

## Target → OWASP surface (pentest mode)

`api` → API Top 10 (BOLA, mass-assign, rate-limit) · `auth` → JWT/OAuth/session (`sec-authn-engineer`) ·
`input` → SQLi, NoSQLi, XSS, deserialization · `web` → CSRF, SSRF, CORS ·
`payments` → webhook forgery, replay, amount tamper ([[ccpayment-deposit-webhook-shape]]) ·
`secrets` → git history, env leak (`sec-secrets-warden`).

## Procedure

1. **Authorize + scope** — confirm target is this project. State what's in/out of bounds.
2. **Recon (free, Python-first)** — run the engine security pack (0 model tokens):
   ```bash
   python3 company/os/toolkit/ceo/sofi_scan.py security "<target>" --prj <PRJ> --md
   ```
   Emits pre-flags: XSS (`{!!`), SQLi (raw+interp), mass-assign, hardcoded secrets, IDOR, eval/unserialize,
   weak randomness, missing-auth, CSRF. Open only flagged `file:line`; then grep/ctx for anything semantic the patterns miss.
3. **Test** — invoke the matching `sec-*` agent + KB skill(s). For active exploit, prove impact minimally; do not damage data.
4. **Adversarial self-verify (V2 · `company/constitution/03-verification.md` — before ranking).** For each
   candidate finding, run a fresh-context refutation pass: try to prove the finding **wrong or unreachable**
   — is the sink actually reached from untrusted input? is there an upstream guard (middleware, FormRequest,
   role gate) that already blocks it? is it dead code? A finding that survives a genuine attempt to refute it
   is real; one that doesn't is a false positive and is dropped. This is fixed-role (refuter, not free-form
   debate) and cuts the false-positive rate before anything reaches the report. "Can't tell from the evidence"
   → mark UNKNOWN and escalate, never pad the count.
5. **Rank** — `CVSS-ish SEV · finding · proof · remediation` per surviving issue. 🔴 exploitable now ·
   🟠 exploitable w/ conditions · 🟡 hardening · ⚪ info. **Every finding carries an Execution Plan block:**
   the exact specialist-scoped fix steps — owning agent id, file:line, the change, and the re-test —
   pre-formatted so `/sofi-fix` can delegate it directly without re-deriving the remediation.
6. **Report** — normal prose. Include reproduction + exact fix. Never expose live secrets in the report — reference location only (Article 07).
7. **Oracle desk (standing, before handoff)** — push the security verdict through the desk:
   `sofi oracle review --prj <PRJ> --json --text "<findings (location-only, no live secrets) + context + ask>"`
   (inline, no `.md`) → analyze + EXECUTE the reply, loop till done, don't ask. This is also the
   **family-diverse second opinion** (V2): an external mind judging Claude-produced findings avoids the
   self-enhancement bias of a same-family verdict (Teaching VII; operator `gtw-external-reviewer`).
8. **Handoff** — remediation → `/sofi-fix` (hand it each finding's Execution Plan block); formal writeup → `/sofi-report security`; re-test → `/sofi-secure verify`.

**Refuse:** third-party targets, DoS, mass-targeting, malware, detection-evasion for malice. Dual-use is fine only with this project's authorization.
