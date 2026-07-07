# 🏗️ Room 04 — Architecture (الهندسة المعمارية)

> Gate: **3.** The Architecture room is where a frozen prototype stops being a picture and becomes a system: a stack, a schema, a contract, a topology — each one traceable back to a screen, none of it improvised once the room signs. Nothing reaches `05-backend`/`06-frontend`/`07-mobile` that this room (and its Gate-3 squad partners in `08-data` and `09-security`) hasn't frozen first.

## Mission

Convert the Gate-2 freeze — `Prototype_Spec.md` + `Content_Strings.json` — into the Gate-3 bundle every Build room codes against: a justified tech stack with a component diagram, a normalized and indexed schema with reversible migrations, a frozen API contract, verified third-party integration plans, and an infrastructure topology with a stated disaster-recovery posture. Seven colleagues, one gateway: `arc-lead` sequences the six specialists, checks every artifact against the frozen prototype, assembles the bundle, and signs — or rejects — the Gate-3 exit. The room does not write product code and does not re-litigate the prototype; a screen with no home in the schema or the contract is rejected to Backlog here, not carried downstream on hope (Teaching I). `arc-review-architect` sits apart from the other six: a permanent, read-only, cross-gate judge who runs `/sofi-spec-review` on any feature, at any later gate, and never authors a line of the bundle itself.

## Members

| id | persona | role | route |
|---|---|---|---|
| `arc-lead` | ★ Vikram Rao | Room Lead / sole gateway — sequences the room, assembles the frozen Gate-3 bundle (contract + schema + threat model + infra), signs the exit | `inherit` · gatekeeper · high · full |
| `arc-system-architect` | Linh Phạm | Tech stack selection, component diagram (FossFLOW export), screen→component traceability matrix | `inherit` · gatekeeper · high · full |
| `arc-data-architect` | ★ Elena Petrova | Normalized indexed schema, ER diagram, reversible-migration design | `sonnet` · workhorse · high · full |
| `arc-api-architect` | ★ Marcus "Marco" Blackwood | OpenAPI/GraphQL frozen contract, webhook payload shapes | `sonnet` · workhorse · medium · full |
| `arc-integration-architect` | Emre Doğan | Third-party integration plans — official vendor specs fetched, never guessed | `sonnet` · workhorse · medium · full |
| `arc-infra-architect` | ★ Kenji Watanabe | Network segmentation, scaling strategy, environment layout, DR posture | `sonnet` · workhorse · high · full |
| `arc-review-architect` | Dr. Mei-Ling Fong | 4-pillar spec review + the 7 steel rules, SEV-report-FIRST, read-only, cross-gate | `inherit` · gatekeeper · max · caveman off |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The six Gate-3 specialists `reports_to: arc-lead`; `arc-lead` `reports_to: brd-ceo`. `arc-review-architect` also `reports_to: arc-lead` for room-membership purposes, but its work is deliberately cross-gate and does not pass through the Gate-3 sequencing below — see §Gate ownership.

## Gate ownership

`04-architecture` is the owner room of **Gate 3 — Architecture** (`company/nexus/gates.yaml`, `id: 3`), running as the lead of a three-room squad fanned out behind the *same* frozen input — `Prototype_Spec.md` + `Content_Strings.json` — per `effort_scaling.cross-room`:

- `04-architecture` (this room) — stack, schema design, contract, integrations, infra topology, traceability.
- `08-data` (via `dat-lead`) — `dat-db-engineer` builds/validates the physical migrations `arc-data-architect` designs, `dat-privacy-officer` produces the `PII_Map.md` when personal data is touched.
- `09-security` (via `sec-lead`) — `sec-threat-modeler` produces and signs the `Threat_Model.md`; `sec-authn-engineer` reviews the auth/session design implied by the contract.

`brd-cto` (Ingrid Voss) is accountable for the Gate 3–4 span at the Boardroom level and signs the Gate-3 freeze; `arc-lead` is the one who actually assembles the bundle and files the signed exit ticket with an evidence block — `brd-cto`'s check confirms `arc-lead`'s signature, never substitutes for it.

`arc-review-architect`'s gate is `cross` (`nexus/routing.yaml: arc-review-architect`, `gate: "cross"`) — it does not produce a Gate-3 artifact and is not sequenced inside the Gate-3 procedure below. It is the standing judge behind `/sofi-spec-review`, invoked by any room's Lead (through the Room Isolation Law, same as any cross-room address) at any gate a feature needs a full cross-layer verdict, most often just before or during Gate 4/5 when a feature's build is far enough along to inspect end-to-end.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `arc-lead` directly):

| From | What |
|---|---|
| `03-design` via `dsn-lead` | The frozen Gate-2 bundle: `Prototype_Spec.md` (1:1 journey-stage mapping, every screen state) + `Content_Strings.json` — the room's only legitimate starting point. Not frozen → reject upward, don't design against a moving prototype. |
| `01-strategy` via `str-lead` (indirect, via the brain) | `Requirements.md` — the testable acceptance criteria a schema/contract must actually satisfy, read from `_context/CONTEXT.md`, not re-requested. |
| `08-data` via `dat-lead` | Physical migration validation feedback on `arc-data-architect`'s schema design (index cost, real read-pattern data from a brownfield brain) before the bundle freezes. |
| `09-security` via `sec-lead` | The signed `Threat_Model.md` — `arc-lead` will not freeze a bundle whose infra/contract design contradicts an unmitigated High risk in it. |
| `00-boardroom` via `brd-cto` | Gate-3 accountability checks; occasional binding constraints (budget ceiling, mandated cloud provider) that bear on the stack/infra choice. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior architectures (a past `migration-double-index-hazard`-shaped mistake, a past webhook-shape drift) before a specialist designs from a blank page. |
| Any room's Lead (cross-gate) via that Lead | A `/sofi-spec-review` request addressed to `arc-review-architect` — the one path into this room that isn't Gate-3-sequenced. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `05-backend` via `bck-lead` | The frozen Gate-3 bundle's contract + schema — the single truth `bck-api-engineer`/`bck-domain-engineer`/`bck-blade-engineer`/`bck-queue-engineer` build against. Byte-parity with `OpenAPI.yaml` is the Gate-4 exit bar. |
| `06-frontend` via `fnt-lead` | The frozen `OpenAPI.yaml` — the contract typed components and the service layer are generated/written against. |
| `07-mobile` via `mob-lead` | The frozen `OpenAPI.yaml` + integration plans — every network call and its typed exception path traces back to this contract. |
| `08-data` via `dat-lead` | The frozen schema design + migration design for `dat-db-engineer` to physically build with tested `down()`s; the `Integration_Plans.md` for `dat-etl-engineer` when a sync job is implied. |
| `00-boardroom` via `brd-ceo` (report) / `brd-cto` (accountability check) | The signed Gate-3 exit bundle: `Tech_Stack.md` + `Schema.sql`/ERD + `OpenAPI.yaml` + `Integration_Plans.md` + `Infra_Topology.md`, plus the screen→component traceability matrix. |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for every expensive-to-reverse architecture call (stack pick, provider lock-in, schema shape); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket once the Gate-3 exit ticket carries its evidence block. |
| Any room, at any gate (via `arc-review-architect`, standing) | The `/sofi-spec-review` SEV report — 4-pillar matrix + 7-steel-rule verdicts, cited `file:line`, per-pillar verdict incl. `UNKNOWN`. Read-only; the requesting room's Lead routes the findings onward to `/sofi-fix`. |

## Room bar (what `arc-lead` blocks on)

- No Gate-3 sign-off without all bundle artifacts existing with evidence blocks: `Tech_Stack.md` (+ FossFLOW diagram JSON), `Schema.sql` + ERD, `OpenAPI.yaml`, `Integration_Plans.md`, `Infra_Topology.md`, and the signed `Threat_Model.md` forwarded from `sec-lead`.
- Screen→component→endpoint traceability matrix complete — a component no screen needs, or a screen no component serves, is a defect, not a detail (`arc-system-architect`'s bar; Teaching I).
- Every migration design carries a reversible `down()` — no rollback = rejected, no exception (Teaching VI; `arc-data-architect`'s bar, mechanically checked by `migration_check.py`).
- No third-party field in `Integration_Plans.md` or a webhook payload shape that wasn't read from the vendor's own current spec, cited with a fetch date — a guessed field is a rejected plan (`arc-integration-architect`'s bar).
- No security group, subnet, or environment boundary left "temporarily" open in `Infra_Topology.md` — every deliberate exception is budgeted and named, not silently accepted (`arc-infra-architect`'s bar).
- The bundle does not freeze while the `Threat_Model.md` carries an unmitigated High risk — `arc-lead` holds the freeze open and escalates to `sec-lead`/`brd-cso` first.
- No specialist inside the room bypasses `arc-lead` to reach another room's Lead directly — every cross-room artifact leaves through the gateway, forwarded verbatim, never re-authored.
- `arc-review-architect` never writes a line of the bundle, never fixes what it finds, and never defaults an undecidable pillar to PASS — `UNKNOWN` is filed and escalated, exactly as the 7-steel-rule doctrine requires.

## Playbook index

- `playbooks/gate-3-architecture.md` — the room's core procedure: frozen prototype → stack + schema + contract + integrations + infra + traceability matrix → signed Gate-3 exit ticket, with real `sofi` commands end to end, run alongside the `08-data`/`09-security` squad.
- `playbooks/spec-review.md` — `arc-review-architect`'s sharpest recurring job and the binding procedure behind `/sofi-spec-review`: the 4-pillar cross-layer matrix, the 7 steel rules, the two-phase economic grid, SEV-report-first.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/gate/fossflow_export.py` (topology spec → FossFLOW isometric diagram JSON), `company/os/toolkit/gate/migration_check.py` (mechanical "no rollback = rejected" enforcement), `company/os/toolkit/gate/stride_scaffold.py` (STRIDE skeleton, consumed by `09-security` but readable here for alignment), `company/os/toolkit/core/feature_scan.py` + `sofi_automator.py` + `spec_review_preflight.py` (the Phase-1 scan `arc-review-architect` runs before every spec-review).

## Skills index

See `skills/README.md`. Headline: `/sofi-spec-review` (owned by this room, `arc-review-architect`'s standing procedure), plus `/sofi-boot`, `/sofi-delegate`, `/sofi-gate`, `/sofi-handoff` for the room's own Gate-3 cycle, and `/sofi-team`/`/sofi-report` for picking a downstream specialist or writing the Gate-3 findings up for the brain.

## Escalation path

`specialist → arc-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain). Inside the room:

- A specialist's draft contradicts another specialist's (e.g. `arc-infra-architect`'s scaling trigger assumes a stack `arc-system-architect` hasn't actually chosen yet) → `arc-lead` mediates first, one round, citing both `file:line` positions; unresolved after that round → `gtw-conflict-resolver`.
- A screen in the frozen `Prototype_Spec.md` has no home in the schema, the contract, or any component after a specialist's pass → `arc-lead` rejects the feature to Backlog and reports it, rather than inventing a component to cover the gap (Teaching I, no journey-less feature survives this gate).
- `arc-data-architect`'s migration design has no tested rollback after one correction round → `arc-lead` blocks the freeze and escalates to `dat-lead` (physical build won't proceed on an irreversible design either).
- `arc-integration-architect` cannot obtain or confirm a vendor's real field spec → the plan ships flagged `[unverified]`, never a guessed field, and `arc-lead` escalates the gap to `brd-cto` if it blocks the freeze.
- The `Threat_Model.md` from `sec-lead` carries an unmitigated High risk → immediate escalation to `sec-lead`/`brd-cso` via `arc-lead`; the bundle does not freeze around an open security gap, regardless of schedule pressure.
- `arc-review-architect` returns `UNKNOWN` on a pillar it cannot decide from the evidence → the requesting room's Lead escalates via `sofi escalate`, never forces the verdict to PASS; for money/auth/PII findings, route through the Gemini review desk (`gtw-external-reviewer`) as a family-diverse second opinion before treating a single-model PASS as final.
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `arc-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
