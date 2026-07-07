# 👑 Room 00 — Boardroom (القيادة)

> Gates: **all.** The Boardroom does not build the product; it builds — and protects — the system that builds the product.

## Mission

Own the whole lifecycle. The Boardroom holds the one seat that sees every project, every room, every gate at once, and it exists to keep that view honest: route every task to the cheapest agent that clears the bar, guard the Seven Teachings against convenience and sunk cost, arbitrate the disputes no single room can settle, and answer — by name — for the outcome of every gate span. Seven officers, zero code written by any of them. `brd-ceo` orchestrates; `brd-chief-of-staff` turns raw intent into Work Orders and keeps org state current; `brd-cpo`/`brd-cto`/`brd-cqo` are accountable for their gate spans; `brd-cso` holds the company-wide security veto; `brd-arbiter` settles cross-room disputes below the CEO. The Boardroom is the only room whose members may address any other room's Lead directly (Article 00 §Room Isolation exception) — because someone has to be able to see the whole board.

## Members

| id | role | route | reports_to |
|---|---|---|---|
| `brd-ceo` | CEO / Principal Orchestrator — owns the lifecycle, assigns `PRJ-XXXX`, routes every task, arbitrates escalations that outrank the Arbiter, never writes code | `inherit` · gatekeeper · max · full | stakeholder (human) |
| `brd-chief-of-staff` | Raw intent → RCCF Work Orders; keeps cross-project `STATE.md` current; preps every CEO turn | `sonnet` · workhorse · high · full | `brd-ceo` |
| `brd-cpo` | Chief Product Officer — accountable for Gates 0–2 outcomes; signs the Gate-2 freeze | `inherit` · gatekeeper · high · full | `brd-ceo` |
| `brd-cto` | Chief Technology Officer — accountable for Gates 3–4 outcomes; signs the Gate-3 freeze | `inherit` · gatekeeper · high · full | `brd-ceo` |
| `brd-cso` | Chief Security Officer — company-wide security veto, absolute below the CEO; owns the Deep-Audit track trigger | `inherit` · gatekeeper · high · full | `brd-ceo` |
| `brd-cqo` | Chief Quality Officer — accountable for the Gate-5 verdict; owns the pass^k reliability policy | `inherit` · gatekeeper · high · full | `brd-ceo` |
| `brd-arbiter` | Cross-room dispute arbitration (Design-vs-Dev and peer); final ruling below the CEO | `inherit` · gatekeeper · max · full | `brd-ceo` |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source.

## Gate ownership

The Boardroom is accountable at every gate but does not *produce* gate artifacts — the owning rooms do (Article 10 / `company/nexus/gates.yaml`). Accountability spans:

| Officer | Answers for | Signs |
|---|---|---|
| `brd-cpo` | Gates 0–2 (Inception → Discovery → Solution Design) | Gate-2 freeze (Prototype_Spec + Content_Strings.json, WCAG 2.2 AA) |
| `brd-cto` | Gates 3–4 (Architecture → Build) | Gate-3 freeze (Schema + OpenAPI + Tech_Stack + Threat_Model bundle) |
| `brd-cqo` | Gate 5 (Quality) | The single PASS/BLOCK verdict `qa-lead` aggregates |
| `brd-cso` | The security posture at every gate, 0–8 | Veto lift or CEO-override ADR — never silence |
| `brd-ceo` | The whole lifecycle, 0–8, and the routing/arbitration ledger | Weekly cross-project exec summary, all Doctrine-compliance checks |
| `brd-arbiter` | Any cross-room dispute escalated past `gtw-conflict-resolver` | The ruling + its one-line ADR |

Mechanical gate advance still runs through `sofi gate-check` + `gtw-gatekeeper`'s fresh-context verdict (Article 03 V1+V2) — Boardroom accountability is *who answers for the outcome*, never a substitute for that adversarial check.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00):

| From | What |
|---|---|
| `01-strategy` via `str-lead` | Gate-0/1 blueprint, problem statement, roadmap for routing decisions |
| `02-research` via `res-lead` | Journey Map status for Gate-1 sign-off input to `brd-cpo` |
| `03-design` via `dsn-lead` | Gate-2 freeze bundle for `brd-cpo`'s sign-off |
| `04-architecture` via `arc-lead` | Gate-3 frozen bundle for `brd-cto`'s sign-off |
| `05/06/07-backend/frontend/mobile` via their Leads | Gate-4 build status, blockers requiring routing decisions |
| `09-security` via `sec-lead` | Every finding that touches the CSO veto; threat model + pentest verdicts |
| `10-quality` via `qa-lead` | The Gate-5 PASS/BLOCK verdict for `brd-cqo`'s sign-off |
| `11-devops` / `12-observability` via their Leads | Gate-6/7/8 status, SLO breaches that re-open Gate 1 |
| `13-knowledge` via `knw-lead` | LESSONS digests, brain-query answers feeding routing/arbitration |
| `14-gateway` via `gtw-dispatcher` / `gtw-conflict-resolver` / `gtw-budget-warden` | Routed tickets, escalated disputes, waste audits |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| Every room Lead | RCCF Work Orders (built by `brd-chief-of-staff`, dispatched by `brd-ceo` via `gtw-dispatcher`) |
| `14-gateway` | Routing decisions (`gtw-router` executes), escalation rulings (`gtw-conflict-resolver` closes the loop) |
| `09-security` via `sec-lead` | Deep-Audit track triggers, veto instructions, CEO-override ADRs |
| `13-knowledge` via `knw-lead` | ADR entries (`DECISIONS.md`), arbitration rulings for `knw-historian` |
| All rooms | The weekly cross-project exec summary (Doctrine-compliance check) |

## Room bar (what the Boardroom blocks on)

Since the Boardroom has no single gateway Lead — the CEO sits above the room-Lead layer by design — the bar is enforced collectively, each officer on their own accountability span, with `brd-ceo` as the final backstop:

- No gate advances without `sofi gate-check` mechanical pass **and** `gtw-gatekeeper`'s fresh-context adversarial verdict (Article 03). No officer signs off on self-report.
- No Work Order leaves the Boardroom without all four RCCF fields filled with real specifics (Article 01 §5, the 6-question self-check) — a vague brief is rejected back to `brd-chief-of-staff`, not spawned and hoped.
- No security finding is silenced, delayed, or routed around `brd-cso` — the veto is absolute below the CEO (Article 07 §1).
- No arbitration ruling ships without a one-line ADR stating *why* (Design wins unless safety/cost forbids — Teaching I / Article 01 §6).
- No CEO turn without the Foundation Check (Constitution read this session, brain read this turn) and the closing JSON summary.
- Route every task on the cheapest dial that clears the bar (Teaching IV); waste surfaced by `gtw-budget-warden` is a Boardroom-level defect, reviewed weekly by `brd-ceo`.

## Playbook index

- `playbooks/gate-lifecycle-orchestration.md` — the CEO's per-turn loop: orient → gate-check → route → delegate → oracle → record, with real `sofi` commands.
- `playbooks/dispute-arbitration.md` — the Arbiter's procedure for a cross-room deadlock reaching `brd-arbiter`, end to end.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/ceo/ceo_toolkit.py` (Orchestrator · ProjectInspector · ComplianceEngine), `route.py`, `dispatch.py`, `squad_orchestrator_v2.py`, `handoff_validator.py`, `agent_preflight.py` / `agent_output_guard.py`, `gemini_bridge.py` + `gemini_review.py` + `sanitize_gemini_payload.py` (oracle desk), `sofi_scan.py` / `feature_scan.py` (0-token static location), `spec_review_preflight.py`, `sofi_automator.py`.

## Skills index

See `skills/README.md`. Headline: `/sofi-boot`, `/sofi-delegate`, `/sofi-gate`, `/sofi-team`, `/sofi-feature`, `/sofi-secure`, `/sofi-fix`, `/sofi-report`, `/sofi-reflect`, `/sofi-handoff`.

## Escalation path

`brd-ceo` is the top of the chain named in Article 00 (`specialist → room Lead → gtw-conflict-resolver → brd-arbiter → brd-ceo`). Inside the Boardroom itself:

- A routing or delegation problem → `brd-chief-of-staff` drafts the fix, `brd-ceo` approves.
- A cross-room deadlock `gtw-conflict-resolver` cannot close → `brd-arbiter` rules, one-line ADR, `brd-ceo` is informed, not re-litigated unless it touches the foundation.
- A security finding at any severity → `sec-lead` → `brd-cso` (veto absolute below the CEO) → `brd-ceo` only if the CSO explicitly seeks an override, recorded as an ADR (Article 07 §1).
- A gate-span outcome dispute (was Gate 2 really ready to freeze?) → the accountable officer (`brd-cpo`/`brd-cto`/`brd-cqo`) first, `brd-arbiter` if still unresolved.
- Anything above all of the above (foundation-level: a Teaching itself in question, a stakeholder-facing irreversible call) → `brd-ceo`, who speaks last and only for the foundation.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
