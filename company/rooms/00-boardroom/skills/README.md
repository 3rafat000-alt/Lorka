# Room 00-boardroom — Skills

> The Boardroom is the only room that plausibly wields all 13 `/sofi-*` skills — it owns the whole lifecycle, so it's the natural home for orchestration-shaped and cross-cutting commands. This is the room's own reading of when each one fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | any of the seven, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before anything else. No Boardroom officer acts on memory. |
| `/sofi-delegate` | `brd-chief-of-staff` (drafts), `brd-ceo` (dispatches) | Every raw intent that needs turning into a paste-ready four-field Work Order before a spawn. |
| `/sofi-team` | `brd-ceo`, `brd-chief-of-staff` | Deciding which of 105 agents, and which room's Lead, owns a given piece of work — before drafting the Work Order, not after. |
| `/sofi-gate` | `brd-cpo` / `brd-cto` / `brd-cqo` (their gate spans), `brd-ceo` (overall) | Every gate-advance decision: mechanical `sofi gate-check` pass plus `gtw-gatekeeper`'s fresh-context adversarial verdict — never a self-graded advance. |
| `/sofi-audit` | `brd-ceo` (commissioning), `brd-cso` (security-flavored sweeps) | A layered inspection is needed before committing a routing decision — e.g. confirming a project's actual state before assigning a fix. |
| `/sofi-spec-review` | `brd-cto` (Gate-3 accountability) | The hard gate for a feature crossing into Architecture — 4-pillar review + 7 steel rules, SEV report first, `arc-review-architect` → `gtw-gatekeeper` full handover. |
| `/sofi-feature` | `brd-ceo` (commissioning end-to-end work) | A whole feature needs the full loop — scan → review → fix → verify → report → gate → handoff — in one delegated arc rather than piecemeal routing. |
| `/sofi-secure` | `brd-cso` | Threat modeling, pentest, vuln scan, or fix-verify on any target — the CSO's operational lever into room 09-security via `sec-lead`. |
| `/sofi-fix` | `brd-cso` (routing findings), `brd-cto`/`brd-cpo` (routing non-security findings within their spans) | Turning an audit/security finding into an applied, checkpointed fix routed to the cheapest specialist that clears the bar. |
| `/sofi-report` | `brd-ceo` (weekly exec summary), `brd-cqo` (Gate-5 verdict writeups) | Any finding worth a durable, evidence-backed record in the brain rather than a chat-only summary. |
| `/sofi-reflect` | `brd-ceo` (schedules it), `knw-reflector` (executes it) | Scheduled dreaming — distilling `HANDOFFS.md` history into `LESSONS.md`. The Boardroom triggers the cadence; it doesn't hand-author the lessons. |
| `/sofi-design-taste` | `brd-cpo` (Gate-2 sign-off literacy) | Checking a Gate-2 freeze's anti-generic-UI dials and WCAG 2.2 AA matrix before signing — reading the output, not producing it (that's `03-design`'s job). |
| `/sofi-handoff` | all seven | Closing ritual on every unit of work: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Never skipped, never batched across multiple artifacts. |

## Rules

- The Boardroom **commissions** most of these skills; it rarely **executes** the underlying specialist work itself — `/sofi-secure` still runs through `sec-lead`'s room, `/sofi-spec-review`'s hard gate still runs through `arc-review-architect`. The Boardroom's role is deciding *that* the skill fires and *who* receives its output, consistent with "delegate, don't do."
- `/sofi-gate` is the one skill where a Boardroom officer's own signature is the deliverable (`brd-cpo`/`brd-cto`/`brd-cqo` per their span) — everywhere else, the officer routes and confirms, the room produces.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points and the sanitized-external-only rule (Article 07 §3) — the Boardroom doesn't get an exemption for being the top of the org chart.
