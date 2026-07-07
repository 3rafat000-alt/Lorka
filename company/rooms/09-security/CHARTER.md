# 🛡️ Room 09 — Security (الأمن)

> Gates: **3 + 5 — veto everywhere.** The Security room is the only room in the company whose reach is not bounded by a gate span. It threat-models before code exists (Gate 3, squad partner to `04-architecture`), it attacks the system after it's built (Gate 5, squad partner to `10-quality`), and it can inject itself into any gate, any merge, any deploy, any tunnel, at any time, on security grounds — the `brd-cso` veto, exercised operationally by `sec-lead` as the CSO's deputy, is **absolute below the CEO** (`company/constitution/07-security-law.md` §1). Eight colleagues, one gateway: `sec-lead` sequences the seven specialists, wires the vendored cyber armory (`company/superpowers/cybersecurity-skills`, 817 skills, read-on-demand), and signs — or blocks — every security surface this room touches.

## Mission

Design the threat model, the auth/authz posture, and the pen-test scope before a line of code exists (Gate 3); review every secure-code surface — injection, authorization, IDOR, SSRF — and the auth/session/crypto implementation as the Build rooms ship it (cross-gate, ahead of Gate 5); attack the actual running, built system with real exploitation attempts and reproduce every finding with severity (Gate 5); keep secrets out of git and PII handling honest at every gate (`sec-secrets-warden`, standing); map every regulatory obligation the project carries (`sec-compliance-auditor`); and hold the incident-response runbook ready before it's ever needed (`sec-incident-responder`). `sec-lead` is the room's sole gateway — no specialist inside `09-security` reaches `arc-lead`, `bck-lead`, `qa-lead`, `dat-lead`, or any other room's Lead directly; every cross-room artifact and every veto leaves through him, forwarded verbatim, never re-authored. Security output — findings, warnings, remediation, incident comms — is **never compressed**, no dial overrides this (Article 07 §4).

## Members

| id | persona | role | route |
|---|---|---|---|
| `sec-lead` | ★ Dr. Ruth Goldberg | Room Lead / sole gateway — deputy to `brd-cso`, wires the cyber armory, sequences the room, signs or vetoes | `inherit` · gatekeeper · max · full |
| `sec-threat-modeler` | Aditi Bhargava | STRIDE threat model, auth/authz design review, pen-test scope — before code exists | `inherit` · gatekeeper · max · full |
| `sec-appsec-engineer` | Baptiste Rousseau | Secure code review: injection, authz, IDOR, SSRF — findings never compressed | `sonnet` · workhorse · high · full |
| `sec-pentester` | ★ Sirak Haile | Execution-level attacks on the built, running system — reproductions + severity, authorized targets only | `sonnet` · workhorse · max · full |
| `sec-authn-engineer` | Mireille Ngozi Adeyemi | Auth/session/crypto implementation review — token lifetimes, rotation, hashing | `sonnet` · workhorse · high · full |
| `sec-secrets-warden` | Pekka Laitinen | Keys/env hygiene, secret scans, vault discipline — `.env` never enters git | `haiku` · mechanical · low · full |
| `sec-compliance-auditor` | Consuelo Prado Vidal | Compliance checklists, regulatory mapping | `sonnet` · workhorse · medium · full |
| `sec-incident-responder` | Damian Wozniak | Security incident runbooks, containment procedures | `sonnet` · workhorse · high · full |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The seven specialists `reports_to: sec-lead`; `sec-lead` `reports_to: brd-cso`, and `brd-cso` `reports_to: brd-ceo`.

## Gate ownership

`09-security` owns no gate outright in `company/nexus/gates.yaml`; it is a named **squad partner** at two gates and holds a standing **veto** that overrides gate ownership everywhere else:

- **Gate 3 — Architecture** (`gates.yaml id: 3`, owner `04-architecture`). `sec-lead` runs as a squad partner to `arc-lead` and `dat-lead`, all three fanned out behind the *same* frozen `Prototype_Spec.md` + `Content_Strings.json` (`effort_scaling.cross-room`). `gates.yaml`'s Gate-3 agent list names `sec-lead`, `sec-threat-modeler`, and `sec-authn-engineer` explicitly: `sec-threat-modeler` produces and signs `docs/<PRJ>_Threat_Model.md` (STRIDE across the frozen `OpenAPI.yaml` + `Schema.sql`), `sec-authn-engineer` reviews the auth/session design the contract implies before anyone codes against it. `arc-lead` will not freeze the Gate-3 bundle while the threat model carries an unmitigated High risk — the bundle waits on this room, not the other way around.
- **Gate 5 — Quality** (`gates.yaml id: 5`, owner `10-quality`). `sec-lead` runs as a squad partner to `qa-lead`, fanned out behind the merged `prj/<PRJ>` build. `gates.yaml`'s Gate-5 agent list names `sec-lead`, `sec-appsec-engineer`, `sec-pentester`, and `sec-authn-engineer`: `sec-appsec-engineer` reviews the shipped code for injection/authz/IDOR/SSRF, `sec-pentester` attacks the running, built system and produces `docs/<PRJ>_Pentest_Report.md` (reproductions + severity, normal prose), `sec-authn-engineer` re-checks the implemented auth/session/crypto against the Gate-3 design. `qa-lead` will not issue a PASS verdict while a Critical/High security finding stands unmitigated.
- **The veto (cross-gate, standing).** `sec-lead`, as `brd-cso`'s deputy, can block any gate, merge, deploy, or tunnel at any time on security grounds, regardless of which room owns that gate or how many other bars it has cleared (Article 07 §1). This is not a third gate assignment in `gates.yaml` — it is a standing authority that sits above the gate table. `sec-secrets-warden` (secret hygiene) and `sec-incident-responder` (containment) both operate cross-gate under this same authority, not tied to Gate 3 or Gate 5 specifically.

`brd-cto` (Ingrid Voss) is accountable for the Gate 3–4 span and `brd-cqo` (Otieno Wambua) for the Gate 5 verdict at the Boardroom level; neither overrides `sec-lead`'s veto — a security block outranks a schedule or a boardroom accountability check every time (Article 07 §1). `sec-lead` does not sign the Gate-3 or Gate-5 exit himself — `arc-lead` and `qa-lead` are the named owner-room signers — he signs and reports **this room's contribution**, and neither owner-room Lead will freeze/PASS around a missing or rejected `09-security` deliverable that gate depends on.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `sec-lead` directly):

| From | What |
|---|---|
| `04-architecture` via `arc-lead` | The frozen `OpenAPI.yaml` + `Schema.sql` — `sec-threat-modeler`'s only legitimate starting point for the STRIDE model. Not frozen → reject upward, don't threat-model a moving contract. |
| `08-data` via `dat-lead` | `dat-privacy-officer`'s `docs/<PRJ>_PII_Map.md` when the project touches personal data — `sec-threat-modeler` folds the classification into the threat model's Information Disclosure findings; `sec-compliance-auditor` maps it to regulatory obligation (GDPR/HIPAA/local law). |
| `05-backend`/`06-frontend`/`07-mobile` via their Leads (indirect, at Gate 5, forwarded through `qa-lead`) | The merged `prj/<PRJ>` build — `sec-appsec-engineer` and `sec-pentester`'s only legitimate target; never a summary of it, always the actual running system. |
| `03-design` via `dsn-lead` (indirect, forwarded through `arc-lead`'s bundle) | `Prototype_Spec.md` — the surfaces `sec-threat-modeler` must cover; a screen with no threat-model row is a gap, not a detail. |
| `00-boardroom` via `brd-cso` | Company-wide security policy, veto direction, and Deep-Audit-track determinations (money/credentials/auth/PII projects — full 9 gates, no exception). |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior incidents or findings (a past `IDOR`-shaped miss, a past secret-leak pattern) before a specialist starts from a blank page. |
| `11-devops` via `ops-lead` (indirect, cross-gate) | Notice of any public tunnel opened (`sofi tunnel up`) — `sec-secrets-warden` confirms seed-data-only before it stays open past its task. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `04-architecture` via `arc-lead` | The signed `docs/<PRJ>_Threat_Model.md` — the Gate-3 bundle does not freeze without it; an unmitigated High risk holds the freeze open. |
| `05-backend`/`06-frontend`/`07-mobile` via their Leads | Must-fix controls from the threat model (per-endpoint authz rules, secret handling, encryption requirements) that Build-room engineers implement in code; `sec-appsec-engineer`'s and `sec-authn-engineer`'s Gate-5 findings, each with a fix owner and a re-test. |
| `10-quality` via `qa-lead` | `docs/<PRJ>_Pentest_Report.md` (reproductions + severity, normal prose) — folded into `qa-lead`'s ONE aggregated PASS/BLOCK verdict; `qa-lead` will not PASS around an unmitigated Critical/High. |
| `00-boardroom` via `brd-cso` (veto/report) | Every veto exercised, with reason and remediation-with-evidence path or explicit CEO-override ADR; the Gate-3/Gate-5 security contribution report. |
| `12-observability` via `obs-lead` | Incident post-mortems (`sec-incident-responder`) that become Gate-1 re-entry tickets under Teaching V (Continuous Metamorphosis) when a live SLO/security breach demands it. |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for every security-consequential call (an accepted-risk exception, a CEO override of a veto); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket once the room's contribution carries its evidence block. |
| Any room, at any gate (via `sec-lead`, standing veto) | An immediate block ticket the moment a security finding warrants it — never queued behind the room's own gate sequencing. |

## Room bar (what `sec-lead` blocks on)

- No Gate-3 sign-off contribution without a signed `Threat_Model.md` — every asset and data flow STRIDE-covered, zero unmitigated High risks (`sec-threat-modeler`'s bar, mechanically scaffolded by `stride_scaffold.py`, never left with a blank mitigation row).
- No Gate-5 PASS contribution while a Critical/High finding from `sec-appsec-engineer` or `sec-pentester` stands unmitigated — every finding ships with a reproduction (request/response or file:line), not a guess.
- Authorization is always server-derived — never trusts client-sent identity or role; an endpoint with no authz rule is a blocker, not a note (`sec-appsec-engineer`'s and `sec-threat-modeler`'s shared bar).
- No secret ever reaches git, a Work Order, a ticket, a brain file, or chat — `sec-secrets-warden`'s standing scan is clean before any checkpoint the room signs off on; a secret that touched context is treated as exposed and rotated, not ignored.
- PII is classified before it is stored, and every money/credentials/auth/PII project runs the full Deep-Audit 9-gate track — no Fast-Track shortcut, ever, on this class of feature.
- Every offensive technique `sec-pentester` runs stays inside this project's own scope, authorized by the Work Order that named the target — no third party, no production without written authorization, full stop.
- Security findings, warnings, and remediation steps are always written in clear normal prose — caveman compression is off for this room's output, no exception, no dial overrides it.
- No specialist inside the room bypasses `sec-lead` to reach another room's Lead directly — every cross-room artifact and every veto leaves through the gateway, forwarded verbatim, never re-authored.
- The veto, once exercised, is lifted only by remediation with evidence (Article 03 V1) or an explicit CEO override recorded as an ADR — never by waiting it out or by schedule pressure.

## Playbook index

- `playbooks/gate-3-5-security-pass.md` — the room's core procedure: frozen Gate-3 input → STRIDE threat model + authz/auth design review → Build-room control handoff → Gate-5 appsec review + pentest → signed pass/block verdict, with real `sofi` commands end to end, run alongside the `04-architecture`/`08-data` and `10-quality` squads.
- `playbooks/pentest-execution.md` — `sec-pentester`'s sharpest recurring job: attacking the running, built system (auth flows, injection, IDOR/BOLA, API abuse) with reproduction-first findings, the adversarial self-verify pass, and the CVSS-ish severity rank.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/gate/stride_scaffold.py` (STRIDE skeleton generator, owned by `sec-threat-modeler`), `company/os/sofi_tools/guard.py` (`scan_secrets`, `check_script_header`, `assert_net_allowed` — the mechanical fail-closed guards `sec-secrets-warden` and `sec-appsec-engineer` lean on), `company/os/toolkit/core/sofi_scan.py` (`security` mode — the zero-token pre-flag pass every `09-security` review opens with).

## Skills index

See `skills/README.md`. Headline: `/sofi-secure` (owned by this room — threat/pentest/scan/verify modes, wires the cyber armory), plus `/sofi-boot`, `/sofi-delegate`, `/sofi-gate`, `/sofi-handoff` for the room's own Gate-3/5 cycle, and `/sofi-spec-review` (consumed, not owned — `04-architecture`'s `arc-review-architect` runs it; a security-shaped finding routes back here via the requesting Lead).

## Escalation path

`specialist → sec-lead → brd-cso → brd-ceo` — the **security spur**, which overrides the general chain (`nexus/bus/escalation.md` §2) and does not queue behind `gtw-conflict-resolver` or `brd-arbiter`. Inside the room:

- A specialist's finding is disputed by the room it's forwarded to (a Build-room Lead argues an authz gap is intentional) → `sec-lead` mediates one round, citing `file:line`; a security dispute unresolved after that round escalates straight to `brd-cso`, not to `gtw-conflict-resolver` — security never waits in the general queue.
- `sec-threat-modeler`'s STRIDE model surfaces an unmitigated High risk the frozen prototype can't design around → immediate block on `arc-lead`'s Gate-3 freeze, escalated to `sec-lead`/`brd-cso` if the affected room contests it.
- `sec-pentester` finds a Critical/High on the running build → immediate block on `qa-lead`'s Gate-5 PASS, reported with reproduction, escalated to `sec-lead`/`brd-cso` if remediation stalls past one correction round (circuit breaker still caps at 3 attempts before a HALT + crash dump).
- `sec-secrets-warden` finds a live secret in git history or a committed `.env` → immediate rotation order (Article 07 §2), `sec-incident-responder` engaged if the secret may already be exposed, both escalated to `sec-lead` the same turn — never queued for the next scheduled scan.
- A CEO override of a `sec-lead` veto → recorded as an ADR in `DECISIONS.md` before work resumes; the veto is never simply "waited out."
- A dispute above `brd-cso`'s authority → `brd-ceo`, the CEO speaking last per the Covenant; `sec-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
