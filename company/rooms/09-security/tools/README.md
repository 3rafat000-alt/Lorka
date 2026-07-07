# Room 09-security — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule (Rule 8, restated because security scripts are checked hardest): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only for the specialists whose spawnable frontmatter grants `WebSearch`/`WebFetch` (`sec-threat-modeler`, `sec-pentester`, `sec-compliance-auditor`) — `sec-appsec-engineer`, `sec-authn-engineer`, `sec-secrets-warden`, `sec-incident-responder`, and `sec-lead` route research needs through them or through `sec-lead`.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner | What it does |
|---|---|---|
| `company/os/agents/tier-1-architecture/security-compliance-architect/stride_scaffold.py` | `sec-threat-modeler` | Generates a STRIDE (Spoofing/Tampering/Repudiation/Information Disclosure/Denial of Service/Elevation of Privilege) threat-model skeleton for a named feature — assets section + a findings table with all six categories pre-listed, so no surface gets skipped by omission. `sec-threat-modeler` fills every mitigation; the scaffold itself does none of that judgment work, it only guarantees the shape is complete before a human/model starts writing. Ported and re-owned from v5's `security-compliance-architect` toolkit (the room's own history — `09-security` descends directly from v5's Tier-1 Security & Compliance Architect role, now the room Lead). Inputs: `<feature-name> [--prj PRJ-ID] [--out docs/<file>.md]`. Exit: `0` ok · `2` bad args · `3` governance (write outside project). |
| `company/os/sofi_tools/guard.py` (`scan_secrets`, `check_script_header`, `assert_net_allowed`) | `sec-secrets-warden` (primary), all `09-security` agents (indirect, via `sofi git-check`/checkpoint hooks) | `scan_secrets(text)` — pattern-matches API-key/token/password/private-key shapes (AWS `AKIA…`, `PRIVATE KEY` blocks, `key/secret/password/token=` literal assignments) and returns the offending snippets (truncated) so promotion/checkpoint can be refused before a secret ever reaches git. `check_script_header(path)` — Rule 8/4 enforcement: refuses an unowned or secret-carrying script. `assert_net_allowed(role)` — Rule 2 enforcement: raises if a role with no Web-tool grant tries to reach the network. This is the mechanical backbone `sec-secrets-warden`'s entire job runs on top of — it is not this room's own script (it's the shared `sofi_tools` library), but it is this room's primary console. |
| `company/os/agents/ceo/sofi_scan.py` (`security` mode) | `sec-appsec-engineer` + `sec-pentester` (Phase-1 recon, both gate-3-5-security-pass.md and pentest-execution.md open with this) | The zero-token static security sweep every `09-security` code/build review opens with — pre-flags XSS (`{!!`), SQLi (raw + interpolated), mass-assignment, hardcoded secrets, IDOR-shaped ID handling, `eval`/`unserialize`, weak randomness, missing-auth patterns, CSRF gaps. `--md` for a markdown report. Neither `sec-appsec-engineer` nor `sec-pentester` reads a file by hand before this sweep has run and been triaged. |
| `company/os/sofi_tools/gitops.py` (`sofi git-check`) | `sec-secrets-warden` (primary), `sec-lead` (before every checkpoint the room signs) | Mechanical secret-in-history audit + the standard git-discipline checks (branch correctness, uncommitted-drift). `sec-secrets-warden` runs this before *every* checkpoint the room signs off on — not just at Gate 3/5, cross-gate, standing. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `sec-lead` | Mechanical Gate-3/Gate-5 validation against `company/nexus/gates.yaml` (`id: 3` and `id: 5`) — artifact existence, evidence-block presence, no unmitigated High/Critical left unblocked. Runs before any adversarial verify, never substitutes for one. |
| `company/os/agents/ceo/gemini_review.py` (`sofi oracle review`) | `sec-lead` / `sec-pentester` (Gate-5 verdicts, Article 03 V2 family-diverse second opinion for money/auth/PII findings) | The oracle desk driver — sanitizes (redacts keys/secrets before anything leaves the machine, Article 07 §3), pushes, captures, parses, ingests a digest into `HANDOFFS.md`. Every Gate-5 security verdict on a money/auth/PII surface routes through this before the room's contribution is called final. |
| `company/superpowers/cybersecurity-skills/` (817 `SKILL.md` files, knowledge-only) | every `09-security` agent, read-on-demand | Not a script — a vendored reference library (see `skills/README.md` §Cyber armory below). Scripts/assets stripped on purpose (Article 07 §4); technique is read, never fetch-and-run. |

No script above is owned exclusively by this room's *process* except `stride_scaffold.py` — the shared `sofi_tools` modules and the `ceo/`-housed scanners are the company's standing console, invoked here under the specialist's own agent id and logged to `.claude/memory/audit.jsonl`.

## What a new Security tool would look like

A genuinely new script belongs at `company/rooms/09-security/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/agents/tier-1-architecture/security-compliance-architect/`, or `company/os/agents/ceo/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. sec-appsec-engineer>
purpose: <one-line purpose>
gate:    3|5|cross
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network unless the
owning role holds Web tools.
"""
```

Candidates that would justify a new Security-owned script (none exist yet — build only on real recurring need):
- An `authz-matrix-check.py` for `sec-appsec-engineer` that mechanically cross-references every endpoint in `docs/<PRJ>_OpenAPI.yaml` against a declared authorization-rule table, flagging any endpoint with no matching row before a human review starts — pre-flagging the exact gap `sec-appsec-engineer`'s bar exists to catch, at zero model tokens.
- A `token-lifetime-lint.py` for `sec-authn-engineer` that greps the shipped auth config/code for JWT/session construction and flags any that sets no expiry or an expiry above a stated policy ceiling, closing the same gap the AuthN review does manually today.
- An `idor-relationship-map.py` for `sec-pentester` that walks `docs/<PRJ>_Schema.sql`'s foreign keys and emits the candidate ID-substitution test matrix (every object relationship, both directions) so the pentest's IDOR/BOLA pass starts from a generated checklist instead of an ad hoc read of the schema.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.09-security` and get an entry in this table — never silently added.
