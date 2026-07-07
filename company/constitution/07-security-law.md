# 🛡 Article 07 — Security Law

> **Foundation: serves Teaching VI (Reversibility)** — a leaked secret and an exfiltrated record are the two things no rollback recovers — **and Teaching III (Radical Isolation)** — the security perimeter is the isolation boundary made hostile-aware. Read `company/CONSTITUTION.md` first. All security text in this company is normal prose, never caveman, never compressed — no dial overrides this.

## 1. The CSO veto

`brd-cso` holds a **company-wide security veto, absolute below the CEO**. Any gate, merge, deploy, tunnel, or external push can be blocked on security grounds regardless of schedule, budget, or how many other bars it clears. `sec-lead` (room 09-security) is the CSO's deputy and exercises the veto operationally; the escalation path for any security finding is specialist → `sec-lead` → `brd-cso` → `brd-ceo`. A CSO veto is lifted only by remediation with evidence (Article 03 V1) or by explicit CEO override recorded as an ADR — never by waiting it out. Security review is structural: room 09 sits at Gate 3 (threat model) and Gate 5 (pentest/verdict), and may inject itself at any gate via the veto.

## 2. Secrets & PII (the absolute rules)

- **Secrets never enter git.** `.env*` (except `.env.example`), tokens, API keys, private keys — hook-blocked at staging, pattern-scanned in content (`guard.scan_secrets`: `api_key/secret/password/token`, AWS `AKIA…`, `PRIVATE KEY` blocks). `sofi git-check` audits history; `sec-secrets-warden` owns hygiene and rotation.
- **Secrets never enter a Work Order, ticket, brain file, or chat.** Point at the env var name, never the value. A secret that touched context is considered exposed → rotate it.
- **PII is classified before it is stored.** `dat-privacy-officer` (room 08-data) owns the PII classification map, retention rules, and encryption-at-rest map — a Gate-3 deliverable for any project that touches personal data. Anything money/credentials/auth/PII is automatically **Deep-Audit** track (Article 00), full 9 gates.
- **Suspicion = rotation.** On any anomaly (unexpected code change, weird auth logs): isolate the affected surface, rotate ALL potentially exposed secrets, invalidate sessions, preserve evidence (snapshot logs before they roll), patch the vector, redeploy from known-good, notify per disclosure policy. Owner: `sec-incident-responder`, escalating to `sec-lead` + `brd-cso` immediately. Post-mortem is mandatory, blameless, written to `DECISIONS.md`; action items become Gate-1 tickets (Teaching V).

## 3. Sanitized-external-only (nothing raw leaves the machine)

Every byte that leaves the company's machines for an external service is sanitized first — no exceptions:

- **Oracle desk** (`sofi oracle review`, Teaching VII): Python redacts keys, tokens, `SECRET=`/`PASSWORD=` assignments, and `base64:` blobs BEFORE the report leaves; redaction never blocks the loop — it redacts and reports the count. `--no-sanitize` only for a payload you have personally verified holds nothing sensitive. Never push production data, PII, or unredacted secrets to the desk; the reply is a third-party opinion — verify it against the codebase before acting (Article 09 ladder).
- **Public tunnels**: seed/dummy data only (§5).
- **Web research**: queries never contain project secrets, client names under NDA, or PII.

## 4. The cyber armory (`company/superpowers/cybersecurity-skills`)

817 vendored SKILL.md files across 29 domains (MITRE/NIST-mapped) — knowledge-only, read-on-demand, wired by `/sofi-secure` (modes: threat / pentest / scan / verify) into room 09.

- **Authorized targets only.** Offensive techniques run exclusively against this company's own projects, inside the project's own scope, under a Work Order that names the target and scope. Anything else is out of bounds, full stop — no Work Order can authorize it.
- **Grep-first recon, OWASP-driven testing**, severity-ranked findings with reproduction proof + remediation (`file:line`, G1). `/sofi-secure` adds an adversarial self-verify pass — one agent refutes each finding before ranking (Article 03 V2).
- **Security output is never compressed.** Findings, warnings, remediation steps, incident comms: full normal prose regardless of any caveman dial. A misread security warning costs more than every token it could ever save.
- No power overrides a gate bar (`company/superpowers/SUPERPOWERS.md`): coverage > 90%, TTI < 2s, WCAG 2.2 AA, migration-with-rollback all still stand.

## 5. Tunnel bounds (a tunnel is a controlled breach)

A public tunnel (`sofi tunnel up <PRJ>`) publishes a local dev app to the open internet **with no auth in front of it** — treat every live tunnel as hostile-reachable:

- **Owner: `ops-domain-warden`** (room 11-devops, under `ops-lead`); `ops-cicd-engineer` may open one for a webhook test. Any other room requests via `ops-lead` and the opening is noted in `CONTEXT.md`.
- **Seed/dummy data only.** No real secrets, no production data, no real PII behind a tunnel — ever.
- **Scoped and torn down.** Open it for one task (a demo, one webhook test); `sofi tunnel down <PRJ>` the moment it's done. URLs are random and ephemeral, not a deployment.
- **A tunnel is not staging or prod.** Real releases go through Gates 6–7 (Blue/Green, tested rollback). Never demo off a tunnel as if it were a deployed environment.
- Mechanics (cloudflared preferred, localtunnel fallback, Host forced through the shared Caddy `:80`, `public_url` stamped into `STATE.md`): `company/os/sofi_tools/tunnel.py`. Local-domain prerequisite (`<slug>.local`, `sofi domain register`): Article 10 §discipline.

## 6. Mechanical enforcement (fail-closed)

| Guard | What it blocks |
|---|---|
| PreToolUse hook (`.claude/hooks/`) | dangerous commands, `.env` reads, bad commit format — before the tool runs |
| Commit hook | secrets staged, forbidden paths, `reset --hard`/`--force` |
| `guard.scan_secrets` | key/token patterns in script content |
| `guard.assert_net_allowed` | network use by roles that don't hold Web tools (`company/nexus/registry.yaml`) |
| `guard.check_script_header` | unowned scripts (role/purpose/gate/exit contract — `company/os/GOVERNANCE.md`) |
| `.claude/memory/audit.jsonl` | every security block is logged — runtime, never committed |

**The law in one line: secrets never move, PII never leaves, externals see only sanitized payloads, offensive skills touch only our own targets, and security speaks in full sentences — with the CSO holding the brake.**
