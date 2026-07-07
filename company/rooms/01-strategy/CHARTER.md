# 🧭 Room 01 — Strategy (الاستراتيجية)

> Gates: **0–1.** The Strategy room is where an idea becomes a bounded problem. Nothing downstream — no persona, no journey stage, no schema, no line of code — gets to exist until this room has named the user, the goal, the boundary, and the price of being wrong.

## Mission

Turn a raw idea into a project SOFI can actually build. Seven colleagues, one gateway: `str-lead` owns the Gate-0 exit and is the room's sole point of contact for every other room. Inside the boundary, the room produces a crisp Problem Statement with 5 deep clarifying questions, testable requirements and acceptance criteria, a market read, a sequenced two-track roadmap (Fast-Track vs Deep-Audit), a risk register with named kill criteria, and a monetization stance — the frozen bundle that `02-research` inherits at Gate 1 and that `brd-cpo` answers for at Gate 2. The room does not design, does not architect, does not write a line of product code — it decides, in writing, *whether this is worth building and exactly what "built" means.*

## Members

| id | persona | role | route |
|---|---|---|---|
| `str-lead` | ★ Dr. Amara Okafor | Room Lead / sole gateway — owns the Gate-0 exit | `inherit` · gatekeeper · high · full |
| `str-product-strategist` | Mateus Alencar | Problem Statement, business goals, scope boundary, 5 deep clarifying questions | `inherit` · gatekeeper · high · lite |
| `str-business-analyst` | Meera Chandrasekaran | Requirements, success metrics, acceptance criteria | `sonnet` · workhorse · medium · full |
| `str-market-analyst` | Min-jun Park | Market sizing, positioning, trends | `sonnet` · workhorse · medium · lite |
| `str-roadmap-planner` | Thandiwe Nkosi | Milestones, backlog grooming, two-track sizing (Fast-Track vs Deep-Audit) | `sonnet` · workhorse · medium · full |
| `str-risk-analyst` | Aleksander Nowak | Business risk register, kill criteria | `sonnet` · workhorse · medium · full |
| `str-monetization-strategist` | Valentina Ríos | Pricing, business model | `sonnet` · workhorse · medium · lite |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. All six specialists `reports_to: str-lead`; `str-lead` `reports_to: brd-ceo`.

## Gate ownership

`01-strategy` is the sole owner room of **Gate 0 — Inception** (`company/nexus/gates.yaml`, `id: 0`). `str-lead` and `str-roadmap-planner` carry a light Gate-1 touch (route `gate: "0-1"`) because the two-track sizing and the roadmap they hand off often need one adjustment once `02-research` starts surfacing evidence that contradicts an assumption — that adjustment is a **loop-back into the frozen Gate-0 bundle**, filed as a ticket, never a silent rewrite. `02-research` remains the sole owner room of Gate 1's artifacts (Personas + Journey_Map); Strategy's Gate-1 presence is advisory, not accountable.

`brd-cpo` (Isabelle Duarte) answers for the Gate 0–2 span at the Boardroom level; `str-lead` is the one who actually signs the Gate-0 exit ticket with an evidence block, and that signature is what `brd-cpo` checks.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `str-lead` directly):

| From | What |
|---|---|
| `00-boardroom` via `brd-ceo` / `brd-chief-of-staff` | The raw idea / stakeholder intent as a Work Order — the room's only legitimate starting point |
| `14-gateway` via `gtw-dispatcher` | The routed ticket that opens the Gate-0 sequence |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior projects; `brain-query` answers that sharpen a Problem Statement before it's written from scratch |
| `02-research` via `res-lead` | Loop-back evidence that contradicts a Gate-0 assumption (Discovery findings that require the room to re-open a roadmap or risk line) |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `00-boardroom` via `brd-ceo` (report) / `brd-cpo` (accountability check) | The Gate-0 exit bundle: Blueprint, Problem Statement (+5 answered/flagged questions), Risk Register, declared track (`fast_track`/`deep_audit`) |
| `02-research` via `res-lead` | The frozen Problem Statement + target-user framing that Discovery builds personas and the Journey Map from |
| `09-security` via `sec-lead` (only when the declared track is `deep_audit`) | The Deep-Audit trigger — money/credentials/auth/PII named in the Risk Register, forwarded for `brd-cso`'s posture |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for irreversible scope/track calls; `HANDOFFS.md` ticket queue entries |
| `14-gateway` via `gtw-router` | The next-gate ticket once the Gate-0 exit ticket carries its evidence block |

## Room bar (what `str-lead` blocks on)

- No Gate-0 sign-off without all three artifacts existing with evidence blocks: `Project_Blueprint.md`, `Problem_Statement.md` (5 deep questions included), `Risk_Register.md` (kill criteria named).
- The 5 deep clarifying questions are non-trivial and *answered or explicitly flagged pending* — never invented on the human's behalf (Article 02 §2, abstention over fabrication).
- Track declared explicitly: `fast_track` or `deep_audit`. Any doubt resolves to `deep_audit` — never guessed toward the cheaper path.
- `<slug>.local` registered and listed in `STATE.md` (`local_domain`/`local_port`) — no bare `127.0.0.1:PORT` ever reaches a stakeholder's eyes.
- Every business goal in the Blueprint carries a measurable success metric — a goal without a number is a wish, not a requirement (`str-business-analyst`'s bar).
- No specialist inside the room bypasses `str-lead` to reach another room's Lead directly — every cross-room artifact leaves through the gateway, forwarded verbatim, never re-authored.
- No Gate-0 sign-off carries a scope line that isn't traceable to the Problem Statement — anything else is Backlog, named as such, not silently dropped.

## Playbook index

- `playbooks/gate-0-inception.md` — the room's core procedure: raw idea → Blueprint + Problem Statement + Risk Register + track declaration → Gate-0 exit ticket, with real `sofi` commands end to end.
- `playbooks/two-track-sizing.md` — `str-roadmap-planner`'s sharpest recurring job: deciding Fast-Track vs Deep-Audit and what that decision actually collapses or expands downstream.

## Tools index

See `tools/README.md`. Headline: `company/templates/project-blueprint.template.md` (the Blueprint's frozen shape), `company/os/toolkit/core/ceo_toolkit.py`'s `ProjectInspector` (health-check the raw idea against an existing codebase when the project is a brownfield extension), `sofi domain register` (part of `new-project.sh`, the local-domain-first discipline).

## Skills index

See `skills/README.md`. Headline: `/sofi-boot`, `/sofi-delegate`, `/sofi-gate`, `/sofi-handoff`, plus `/sofi-team` and `/sofi-report` when the room needs to pick a downstream specialist by name or write the Gate-0 findings up for the brain.

## Escalation path

`specialist → str-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain). Inside the room:

- A specialist's draft is thin or contradicts another specialist's finding (e.g. `str-market-analyst`'s sizing conflicts with `str-monetization-strategist`'s pricing assumption) → `str-lead` mediates first, one round, citing both `file:line` positions; unresolved after that round → `gtw-conflict-resolver`.
- A raw idea has no bounded problem after `str-product-strategist`'s pass (the 5 questions can't even be asked meaningfully) → `str-lead` rejects upward to `brd-chief-of-staff`: this is not yet a project.
- A track call is contested (fast vs deep) → `str-roadmap-planner` and `str-risk-analyst` reconcile against the Risk Register first; still contested → `str-lead` escalates to `brd-cso` (Deep-Audit is the CSO's trigger to confirm, Article 07 §1) — never resolved by picking the cheaper path.
- Anything touching money/credentials/auth/PII discovered mid-room → immediate escalation to `brd-cso` via `str-lead`, no exception, regardless of what gate the room is nominally in.
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `str-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
