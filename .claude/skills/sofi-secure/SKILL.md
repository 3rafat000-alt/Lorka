---
name: sofi-secure
description: Run the SOFI security team on any target — threat-model, pentest, vuln scan, or fix-verify — wiring the vendored cyber knowledge base (engine/superpowers/cybersecurity-skills) and the Security & Compliance Architect into one flexible command. Authorized defensive/pentest use on this project only. Grep-first recon, OWASP-driven testing, severity-ranked findings with proof + remediation. Triggers — "security review", "pentest", "threat model", "scan for vulns", "is this secure", "check auth/injection/secrets", "harden", "pen test the api".
---

# /sofi-secure — the security squad, one command

> Scope: **authorized security testing of THIS project only** (owner-run, seed data).
> Never target third parties. Findings, code, and warnings written in **normal prose,
> never compressed** (routing law).
>
> **Knowledge base:** `engine/superpowers/cybersecurity-skills/` — 817 vendored cyber
> skills (knowledge-only, scripts stripped). Curriculum in `CURRICULUM.md`, attack map
> in `ATTACK_COVERAGE.md`, lookup via `index.json`/`mappings/`. Read the relevant
> skill's `SKILL.md` for the method; this command does NOT invoke them as slash commands
> (they were removed from the palette — [[sofi-cybersecurity-skills-library]]).

**Usage:** `/sofi-secure <mode> [target]` — mode ∈
`threat · pentest · scan · verify`. No mode → `scan` (fast recon).

## Modes

| Mode | Does | Drives |
|------|------|--------|
| `threat` | STRIDE threat model, auth/authz design review, PII classification, pentest scope | `sofi-security-compliance-architect` + KB `implementing-threat-modeling-with-mitre-attack` |
| `pentest` | Active exploit attempts on the target (authorized): injection, IDOR/BOLA, mass-assign, XSS, CSRF, SSRF, JWT/OAuth flaws, CORS | KB `testing-*` / `exploiting-*` skills |
| `scan` | Fast static recon — secrets in git, dep CVEs (SBOM), CI/CD supply-chain, container/IaC | KB `implementing-secrets-scanning-in-ci-cd`, `generating-and-analyzing-sboms`, `scanning-iac-and-images-with-trivy` |
| `verify` | Re-test after `/sofi-fix` — confirm the vuln is closed, no regression | re-run the finding's original skill |

## Target → OWASP surface (pentest mode)

`api` → API Top 10 (BOLA, mass-assign, rate-limit) · `auth` → JWT/OAuth/session ·
`input` → SQLi, NoSQLi, XSS, deserialization · `web` → CSRF, SSRF, CORS ·
`payments` → webhook forgery, replay, amount tamper ([[ccpayment-deposit-webhook-shape]]) ·
`secrets` → git history, env leak.

## Procedure

1. **Authorize + scope** — confirm target is this project. State what's in/out of bounds.
2. **Recon (free, Python-first)** — run the engine security pack (0 model tokens):
   ```bash
   python3 engine/tooling/agents/ceo/sofi_scan.py security "<target>" --prj <PRJ> --md
   ```
   Emits pre-flags: XSS (`{!!`), SQLi (raw+interp), mass-assign, hardcoded secrets, IDOR, eval/unserialize, weak randomness, missing-auth, CSRF. Open only flagged `file:line`; then grep/ctx for anything semantic the patterns miss.
3. **Test** — invoke the matching `cyber-*` skill(s). For active exploit, prove impact minimally; do not damage data.
4. **Adversarial self-verify (v5, `verification.md` V2 — before ranking).** For each candidate finding, run a fresh-context refutation pass: try to prove the finding **wrong or unreachable** — is the sink actually reached from untrusted input? is there an upstream guard (middleware, FormRequest, tier check) that already blocks it? is it dead code? A finding that survives a genuine attempt to refute it is real; one that doesn't is a false positive and is dropped. This is fixed-role (refuter, not free-form debate) and cuts the false-positive rate before anything reaches the report. "Can't tell from the evidence" → mark UNKNOWN and escalate, never pad the count.
5. **Rank** — `CVSS-ish SEV · finding · proof · remediation` per surviving issue. 🔴 exploitable now · 🟠 exploitable w/ conditions · 🟡 hardening · ⚪ info. **Every finding carries an Execution Plan block** (v5): the exact specialist-scoped fix steps — owning role, file:line, the change, and the re-test — pre-formatted so `/sofi-fix` can delegate it directly without re-deriving the remediation. Closes the gap between "found" and "assigned-fixable" in one step.
6. **Report** — normal prose. Include reproduction + exact fix. Never expose live secrets in the report — reference location only.
7. **Review desk (standing, before handoff)** — push the security verdict through the desk: `sofi gemini review --prj <PRJ> --json --text "<findings (location-only, no live secrets) + context + ask>"` (inline, no `.md`) → analyze + EXECUTE the reply, loop till done, don't ask. This is also the **family-diverse second opinion** (`verification.md` V2): Gemini judging Claude-produced findings avoids the self-enhancement bias of a same-family verdict. `engine/protocols/external-review-desk.md`.
8. **Handoff** — remediation → `/sofi-fix` (hand it each finding's Execution Plan block); formal writeup → `/sofi-report security`; re-test → `/sofi-secure verify`.

**Refuse:** third-party targets, DoS, mass-targeting, malware, detection-evasion for malice. Dual-use is fine only with this project's authorization.
