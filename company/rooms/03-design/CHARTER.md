# 🎨 Room 03 — Design (التصميم)

> Gate: **2 (Solution Design).** The Design room is where a journey stage becomes a screen a human can actually use — and, at the moment `dsn-lead` signs the freeze, becomes the one thing every downstream room is no longer allowed to argue with. After the freeze, the prototype **is** truth (Teaching I, made literal a second time — first by `res-journey-architect`'s map, now by this room's screens).

## Mission

Turn the frozen `<PRJ>_Journey_Map.md` into a textual hi-fi Prototype Spec that maps 1:1 to every journey stage, a reusable design-token/component-library spec, final UX copy as keyed strings in one voice, explicit taste dials that keep the result from looking like generic AI-UI, a motion spec that respects `prefers-reduced-motion`, and a WCAG 2.2 AA matrix that wins over every one of those dials without exception. Eight colleagues, one gateway: `dsn-lead` owns the Gate-2 exit and is the room's sole point of contact for every other room. The room does not invent journeys (that's `02-research`), does not choose a stack (that's `04-architecture`), and does not write a line of production code — it decides, screen by screen and state by state, *exactly what "built" has to look, read, move, and feel like.*

## Members

| id | persona | role | route |
|---|---|---|---|
| `dsn-lead` | ★ Daniel "Dan" Kim | Room Lead / gateway — owns the Gate-2 FREEZE; after it, the prototype is truth | `sonnet` · workhorse · high · full |
| `dsn-ui-designer` | Léa Fontaine | Textual hi-fi prototype spec, 1:1 journey-stage mapping, every component state | `sonnet` · workhorse · medium · lite |
| `dsn-ux-architect` | Tomasz Kowalski | Flows, information architecture, interaction models | `sonnet` · workhorse · medium · lite |
| `dsn-design-system` | Chidinma Eze | Design tokens, component library spec | `sonnet` · workhorse · medium · full |
| `dsn-content-strategist` | ★ Margaret "Peg" O'Sullivan | Final UX copy + microcopy as keyed JSON, one tone of voice, actionable errors | `haiku` · mechanical · low · full |
| `dsn-brand-designer` | Rafael Andrade | Taste dials (`DESIGN_VARIANCE`·`MOTION_INTENSITY`·`VISUAL_DENSITY`) + brand presets, anti-generic UI | `sonnet` · workhorse · medium · lite |
| `dsn-motion-designer` | Ji-woo Baek | Motion & micro-interaction specs — durations, easings, reduced-motion fallbacks | `haiku` · mechanical · low · full |
| `dsn-a11y-specialist` | Marcus Webb | WCAG 2.2 AA matrix — accessibility ALWAYS wins over any taste dial | `sonnet` · workhorse · medium · full |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. All seven specialists `reports_to: dsn-lead`; `dsn-lead` `reports_to: brd-ceo`.

## Gate ownership

`03-design` is the sole owner room of **Gate 2 — Solution Design** (`company/nexus/gates.yaml`, `id: 2`, `owner_room: 03-design`). `brd-cpo` (Isabelle Duarte) answers for the Gate 0–2 span at the Boardroom level; `dsn-lead` is the one who actually signs the Gate-2 exit ticket with an evidence block, and that signature is what `brd-cpo` checks before her own sign-off.

- **Entry:** `docs/<PRJ>_Journey_Map.md` frozen (gate-1 tag `<PRJ>-gate1-done` exists).
- **Artifacts:** `docs/<PRJ>_Prototype_Spec.md` (textual hi-fi, 1:1 journey-stage mapping, all component states) · `docs/<PRJ>_Content_Strings.json` (keyed UX copy + microcopy, one tone of voice, actionable errors) · `docs/<PRJ>_Design_Tokens.md` (+ taste dials: `DESIGN_VARIANCE`·`MOTION_INTENSITY`·`VISUAL_DENSITY`) · `docs/<PRJ>_A11y_Matrix.md` (WCAG 2.2 AA).
- **Exit bar:** WCAG 2.2 AA matrix passes — accessibility wins over any taste dial (`/sofi-design-taste`) · every screen traces 1:1 to a Journey Map stage; every state (empty/loading/error/offline/partial) specified · all UI strings live in `Content_Strings.json` — none invented downstream · **THE FREEZE:** `dsn-lead` signs — after this ticket, the prototype IS truth for everything downstream (Teaching I).
- **On fail:** bounced inside the room until AA passes; a screen with no journey stage is deleted, not argued for (Teaching II — reject, don't improvise around a missing parent).

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `dsn-lead` directly):

| From | What |
|---|---|
| `02-research` via `res-lead` | The frozen `Personas.md` + `Journey_Map.md` — the Gate-1 bundle every screen and every string must trace back to |
| `00-boardroom` via `brd-cpo` | Gate 0-2 accountability questions, Deep-Audit triggers when the project touches money/credentials/auth/PII (extra a11y and copy rigor on those flows) |
| `14-gateway` via `gtw-dispatcher` | Routed Work Orders opening the Gate-2 ticket |
| `12-observability` via `obs-lead` (loop-back, Gate 8 → 1 → 2) | `obs-insights-analyst`'s journey drop-off findings that re-open a specific screen for redesign on the next cycle |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `04-architecture` via `arc-lead` | The frozen Gate-2 bundle — `arc-system-architect` builds screen→component traceability directly against it; not-frozen input is rejected back |
| `06-frontend` via `fnt-lead` | `Design_Tokens.md` + taste dials + `Content_Strings.json` + `A11y_Matrix.md`, applied literally at Gate 4 by `fnt-css-artisan`, `fnt-interaction-engineer`, `fnt-a11y-engineer` |
| `05-backend` via `bck-lead` | `Content_Strings.json` + every prototyped state, for `bck-blade-engineer`'s Blade layouts/components/pages |
| `00-boardroom` via `brd-cpo` | The Gate-2 status report and, at freeze, the signed bundle for her sign-off |
| `13-knowledge` via `knw-lead` | Cited design decisions worth ingesting into the durable brain (a brand-preset choice, an a11y exception rationale) |
| `10-quality` via `qa-lead` (Gate 5) | The frozen Prototype Spec as the reference `qa-design-auditor` checks built-vs-frozen fidelity against |

## Room bar (what `dsn-lead` blocks on)

- No screen ships without mapping 1:1 to a stage on `res-journey-architect`'s frozen Journey Map — an orphan screen is deleted, not argued for.
- No screen ships with only its happy state — empty, loading, error, offline, and partial states are all specified, per Teaching I as `dsn-ui-designer` practices it.
- `dsn-a11y-specialist`'s WCAG 2.2 AA matrix passes before anything else is signed — accessibility wins over every taste dial, no exception, no override by `dsn-brand-designer` or anyone else.
- All UI strings live in `dsn-content-strategist`'s `Content_Strings.json` as keyed JSON, one tone of voice, every error stating what happened and how to fix it — nothing invented downstream by a Build-room engineer.
- `dsn-design-system`'s tokens are single-sourced — a color, spacing value, or component used twice resolves to one token, never two divergent hex values or two competing component specs.
- Taste dials (`DESIGN_VARIANCE`·`MOTION_INTENSITY`·`VISUAL_DENSITY`) are stated explicitly with a named brand preset — no default-template look ships unexamined.
- `dsn-motion-designer`'s motion spec states a `prefers-reduced-motion` fallback for every animation — a motion spec with no reduced-motion path is incomplete, not optional polish.
- No specialist inside the room bypasses `dsn-lead` to reach another room's Lead directly — every cross-room artifact leaves through the gateway, forwarded verbatim.
- Gate-2 does not advance on `dsn-lead`'s self-report alone — mechanical `sofi gate-check` plus `gtw-gatekeeper`'s fresh-context adversarial verdict, same as every gate (Article 03 V1+V2).

## Playbook index

- `playbooks/gate-2-solution-design-procedure.md` — the room's core Gate-2 procedure end to end: orient → fan out → integrate → a11y gate → freeze → handoff, with real `sofi` commands.
- `playbooks/anti-generic-taste-application.md` — `dsn-brand-designer`'s specialty procedure: setting the three taste dials against a brand preset and running the anti-generic-UI checklist without ever overriding the a11y bar.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/uiux/uiux_pipeline.py` (owner `dsn-lead`, the UI/UX static pipeline feeding `/sofi-audit ui` and this room's own Gate-2 pre-checks), plus the shared `sofi_scan.py design`/`flow` modes and the `sofi_tools` library every room leans on.

## Skills index

See `skills/README.md`. Headline: `/sofi-boot`, `/sofi-delegate`, `/sofi-design-taste` (this room's own dial-and-checklist skill, owned by `dsn-brand-designer`), `/sofi-gate`, `/sofi-handoff`, plus `/sofi-audit ui` for a pre-freeze static sweep.

## Escalation path

`specialist → dsn-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00 chain), with these room-specific triggers:

- A taste-dial choice from `dsn-brand-designer` conflicts with a WCAG 2.2 AA requirement from `dsn-a11y-specialist` → accessibility wins, always, no exception; if `dsn-brand-designer` disputes the read, `dsn-lead` decides, not a vote.
- A screen proposed by `dsn-ui-designer` or a flow proposed by `dsn-ux-architect` cannot find its parent stage on the frozen Journey Map → rejected upward to `res-lead` as a thin or ambiguous map, never invented around.
- A copy/voice conflict between `dsn-content-strategist`'s draft and `res-ux-researcher`'s persona voice notes → `dsn-lead` mediates first, citing both sources; unresolved after one round → `gtw-conflict-resolver`.
- Anything the room's work touches that reads as money/credentials/auth/PII-adjacent (an error message revealing account state, a screen showing a balance) → `dsn-lead` escalates immediately to `brd-cpo`, who triggers the Deep-Audit track via `brd-cso` — Room 03 does not make that call alone.
- A Design-vs-Dev dispute about whether a token, component, or motion spec is technically infeasible → `dsn-lead` first, `gtw-conflict-resolver` if unresolved at the room-Lead level, `brd-arbiter` only past that (Design wins unless safety/cost forbids it — the "why" gets one ADR line either way).
- Circuit breaker: 3 failed self-correction attempts on any Gate-2 artifact → HALT, structured crash-dump JSON, escalation ticket, `dsn-lead` decides the next route (Article 00 §"Escalation & parallelism").

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
