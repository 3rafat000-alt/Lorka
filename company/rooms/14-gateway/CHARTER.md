# 🕸️ Room 14 — Gateway (النقطة)

> Gates: **cross-gate.** Every other room owns a slice of the lifecycle; `14-gateway` owns the wires between them. It routes the Work Order that enters the org or crosses a room wall (`gtw-dispatcher`), stamps the cheapest model/effort/caveman that clears the bar on every spawn (`gtw-router`), runs the fresh-context adversarial check no gate advances without (`gtw-gatekeeper`), operates the external oracle desk for decisions that need a genuinely different mind (`gtw-external-reviewer`), mediates the deadlock two rooms can't settle between themselves (`gtw-conflict-resolver`), and keeps the company's token spend honest against `routing.yaml`'s budget bands (`gtw-budget-warden`). `14-gateway` produces no product artifact — Prototype_Spec, Schema.sql, and Blade components are not this room's job. Its deliverable is that the other fourteen rooms' work reaches the right desk, at the right price, verified by someone who wasn't the one who wrote it.

`gtw-dispatcher` is the room's Lead exactly as every other room has one — but because this room's entire mandate is cross-room routing, all six operators (dispatcher included) hold a standing exception the Room Isolation Law grants explicitly (`company/nexus/NEXUS.md` §3): **the boardroom and the gateway room may address any room's Lead directly.** No other room's specialists get that reach; this room exists to have it.

## Mission

Be the Nexus made staff: turn intent into routed tickets, turn every spawn into a logged cheapest-clearing route, turn a "done" claim into a verified one, turn a sensitive decision into a sanitized ask to a second mind, turn a stuck cross-room dispute into a mediated ruling or a clean escalation, and turn the company's weekly token spend into an audited number instead of a felt sense. None of the six agents in this room write product code, design a schema, or draft a Prototype_Spec — every artifact in `14-gateway`'s remit is about the *connective tissue*: tickets, routes, verdicts, sanitized reports, rulings, and budget ledgers.

## Members

| id | persona | role | route |
|---|---|---|---|
| `gtw-dispatcher` | ★ Astrid Lindqvist | Room Lead / gateway — turns a Work Order into bus tickets, addresses the right room Leads (may address any Lead), sequences multi-room work, runs `sofi dispatch`/`sofi squad` | `sonnet` · workhorse · high · full |
| `gtw-router` | Linh Pham | Model/cost routing for every spawn — looks up `routes.<id>` in `routing.yaml`, applies overrides, stamps and logs the route before anyone acts | `haiku` · mechanical · low · ultra |
| `gtw-gatekeeper` | Tomasz Wójcik | Fresh-context adversarial gate verification (Article 03 V2) — sees only the deliverable + the ORIGINAL exit bar, never the implementer's reasoning; runs `sofi gate-check` | `inherit` (gatekeeper-tier) · high · full |
| `gtw-external-reviewer` | Farah Bassil | Oracle desk operator — sanitize → condense → push → capture → parse → ingest digest via `sofi gemini review`/`capture`/`status` | `sonnet` · workhorse · medium · full |
| `gtw-conflict-resolver` | Diego Salgado | Cross-room deadlock mediation, read-only on the evidence; unresolved → `brd-arbiter` | `sonnet` · workhorse · medium · full |
| `gtw-budget-warden` | Bram Oosterhuis | Token-budget audits against `routing.yaml` bands, circuit-breaker trip ledger, weekly waste report | `haiku` · mechanical · low · ultra |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The five specialists `reports_to: gtw-dispatcher`; `gtw-dispatcher` `reports_to: brd-ceo`.

## Gate ownership

`14-gateway` owns no gate in `company/nexus/gates.yaml` — no `owner_room: 14-gateway` line exists, and correctly so: a gate needs an owner who produces a deliverable, and this room produces routing/verification/mediation/budget artifacts instead. Its footprint is different — **it operates the mechanism every gate advances through**, at all nine:

- **Every gate's advancement** runs the two-layer flow `NEXUS.md` §6 fixes: mechanical `sofi gate-check` (owned by `sofi_tools.gates`, invoked by whichever Lead is closing the gate) → `gtw-gatekeeper`'s fresh-context adversarial verdict against the gate's `exit_bar` in `gates.yaml` → `sofi gate-tag`. No gate anywhere in the company skips this — Gate 0's charter sign-off and Gate 8's SLO-breach re-open both run through the same verifier.
- **Every ticket that crosses a room wall** is dispatched by `gtw-dispatcher`; every spawn behind it is routed by `gtw-router` before the first token is spent.
- **Every money/auth/PII verdict** and every Teaching-VII decision point routes through `gtw-external-reviewer`'s oracle desk, regardless of which gate the decision sits in.
- **Every unresolved cross-room deadlock**, at any gate, reaches `gtw-conflict-resolver` before `brd-arbiter`.
- **Every gate's token spend** is audited by `gtw-budget-warden` against the bands in `routing.yaml`, weekly and on demand — not scoped to one gate, all of them.

`brd-ceo` (Magnus Holt) is the accountable chief for `gate: "all"` per `gates.yaml`'s accountability table — the same span this room's mechanism serves. `gtw-dispatcher` does not sign any gate's exit herself; `gtw-gatekeeper`'s verdict feeds the owner-room Lead's signature, and the owner-room Lead (not this room) is the one who runs `sofi gate-tag`.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; this room's own standing exception lets it *reach* any Lead, but what it consumes from that Lead is still that Lead's own signed, forwarded-verbatim output, never a specialist's raw draft):

| From | What |
|---|---|
| `00-boardroom` via `brd-ceo`/`brd-chief-of-staff` | Raw Work Orders that need turning into bus tickets and routed across rooms — `gtw-dispatcher`'s starting input on anything that isn't already a single in-room ticket. |
| Any room's Lead | A ticket ready to close (`status: done` + evidence block) awaiting `gtw-gatekeeper`'s fresh-context verdict before the owner-room Lead can tag the gate. |
| Any room's Lead | A report, spec, or high-stakes verdict (money/auth/PII, a Teaching-VII decision point) that needs a second, genuinely different mind — `gtw-external-reviewer`'s oracle-desk input. |
| Two rooms' Leads (both sides) | A contested `LOCKS.md` claim, contradictory frozen artifacts, or a ticket rejected twice between rooms — `gtw-conflict-resolver`'s mediation input, both positions forwarded verbatim, never re-argued in transit. |
| `company/nexus/routing.yaml` (the file itself, not a room) | The single source of every `routes.<id>` entry, `effort_scaling` class, `priority_override` rule, and budget band — `gtw-router` and `gtw-budget-warden`'s ground truth; neither ever invents a route or a budget number. |
| `company/nexus/gates.yaml` (the file itself) | The `exit_bar` per gate — `gtw-gatekeeper`'s ONLY criteria source; consuming anything else (a Slack summary, the implementer's own account) is exactly the self-report failure Article 03 V2 exists to prevent. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior disputes or circuit-breaker trips — `gtw-conflict-resolver`'s and `gtw-budget-warden`'s evidence base before ruling on a pattern that has recurred before. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| Any room's Lead | Bus tickets addressed and sequenced (`gtw-dispatcher`), each carrying a stamped route (`gtw-router`) — the room's most common outbound artifact, dozens of times a gate. |
| The owner-room Lead of the gate closing | `gtw-gatekeeper`'s verdict — PASS / FAIL / **UNKNOWN** — against the gate's `exit_bar`; UNKNOWN routes to `sofi escalate`, never a coin-flip. |
| The requesting room's Lead | `gtw-external-reviewer`'s ingested oracle-desk digest, appended to the requesting project's `HANDOFFS.md` — analyzed and actioned autonomously per Teaching VII, not left for a human to read. |
| Both disputing rooms' Leads | `gtw-conflict-resolver`'s ruling (resolved) or both positions forwarded intact to `brd-arbiter` (unresolved) — never a silently-picked winner. |
| `00-boardroom` via `brd-ceo` | `gtw-budget-warden`'s weekly waste audit — unlogged routes, deep-tier spend on routine work, orphaned report files — filed as defects, not observations. |
| `13-knowledge` via `knw-lead` | Circuit-breaker trip ledger entries and mediation rulings — raw signal `knw-reflector`'s scheduled dreaming pass distils into `LESSONS.md`; this room doesn't distil it itself. |
| `00-boardroom` via `brd-arbiter` | Unresolved cross-room disputes, both positions intact, for formal arbitration (`bus/escalation.md` §5). |

## Room bar (what `gtw-dispatcher` blocks on)

- No ticket leaves this room addressed to a specialist directly — every dispatch targets a room's Lead (or, same-room, stays inside `14-gateway`); the Room Isolation Law binds this room's outbound traffic exactly as it binds everyone else's (`gtw-dispatcher`'s bar).
- No spawn happens with an unlogged route — `gtw-router` stamps `model · effort · caveman` into the ticket and `STATE.md`'s `last_route` before the first token is spent, every time, no exceptions for "it's obviously mechanical" (`gtw-router`'s bar; Teaching IV).
- No gate advances on the implementer's self-report — `gtw-gatekeeper` sees only the deliverable and the gate's ORIGINAL `exit_bar` from `gates.yaml`, never the chat log that produced it, and UNKNOWN is filed as UNKNOWN, never rounded to a pass (`gtw-gatekeeper`'s bar; Article 03 V2).
- No payload reaches the oracle desk unsanitized — `gtw-external-reviewer` redacts keys/secrets/.env before a byte leaves the machine, every send, and never treats the desk's reply as an approval rather than advice (`gtw-external-reviewer`'s bar; Article 07 §3).
- No cross-room dispute gets a silently-picked winner — `gtw-conflict-resolver` mediates on cited evidence only, one round, and either both Leads get a ruling or both positions travel to `brd-arbiter` intact (`gtw-conflict-resolver`'s bar; G5, conflicts surfaced not resolved-away).
- No circuit-breaker trip goes unlogged — `gtw-budget-warden` keeps the ledger and reports a route that skipped mechanical tier without evidence of an escalation trigger as a defect, same weight as any other waste finding (`gtw-budget-warden`'s bar; Teaching IV, "waste is a defect").
- No specialist inside this room addresses a specialist in another room — even holding the standing Lead-reach exception, that exception is Lead-to-Lead, never specialist-to-specialist; `gtw-dispatcher` is the one who exercises it, not any of the other five.

## Playbook index

- `playbooks/gate-advancement.md` — the room's core, always-on procedure: `sofi gate-check` (mechanical) → `gtw-gatekeeper`'s fresh-context adversarial verdict against the ORIGINAL `exit_bar` → `sofi gate-tag`, with the UNKNOWN-verdict path, the money/auth/PII oracle-desk escalation, and real `sofi` commands end to end. Every gate in the company advances through this, not just one.
- `playbooks/oracle-desk-review.md` — `gtw-external-reviewer`'s sharpest recurring job and the room's other standing procedure: sanitize → condense → push → capture → parse → ingest, the full Teaching-VII loop from a raw report to an autonomously-actioned digest in `HANDOFFS.md`.

## Tools index

See `tools/README.md`. Headline: `company/os/sofi_tools/gates.py` (`sofi gate-check`, this room's mechanical verification layer), `company/os/toolkit/ceo/gemini_review.py` + `gemini_bridge.py` + `sanitize_gemini_payload.py` (the oracle desk's full driver stack, all three owned by `gtw-external-reviewer` in `registry.yaml`), `company/os/toolkit/ceo/dispatch.py` (`gtw-dispatcher`'s ticket-render tool), `company/os/toolkit/ceo/handoff_validator.py` (`gtw-gatekeeper`'s evidence-validation support), `company/os/sofi_tools/routing.py` (`sofi route`, `gtw-router`'s ground truth reader).

## Skills index

See `skills/README.md`. Headline: `/sofi-gate` (this room's core mechanism, wielded by `gtw-gatekeeper`), `/sofi-delegate` (every Work Order `gtw-dispatcher` renders), `/sofi-team` (the who-does-what lookup `gtw-dispatcher` runs before addressing a Lead), plus `/sofi-boot`/`/sofi-handoff` for the room's own cycle and `/sofi-reflect` as a consumer of this room's circuit-breaker and mediation signal.

## Escalation path

`specialist → gtw-dispatcher → brd-arbiter → brd-ceo` for anything internal to this room's own operation — but because four of the six agents here (`gtw-gatekeeper`, `gtw-external-reviewer`, `gtw-conflict-resolver`, `gtw-budget-warden`) are themselves *links* in every other room's standard chain (`specialist → room Lead → gtw-conflict-resolver → brd-arbiter → brd-ceo`), this room's own escalation path is short by design — it is rarely the room asking for help, more often the room others ask through:

- `gtw-router` mis-stamps a route (wrong tier for the task) → `gtw-dispatcher` corrects it directly, one round; no formal escalation needed for a mechanical lookup error.
- `gtw-gatekeeper` returns UNKNOWN and the requesting room's Lead disputes it → `gtw-dispatcher` mediates one round citing the exact `exit_bar` clause in question; unresolved → `brd-arbiter` (the verdict itself is never overridden by mediation, only the *interpretation* of an ambiguous bar clause is).
- `gtw-external-reviewer` cannot get a reply from the oracle desk within `--timeout` → `sofi gemini capture` resumes once, then `sofi gemini status` to probe; if the desk is down, `gtw-dispatcher` proceeds the decision through `brd-arbiter`'s human-role-fixed protocol instead — the loop does not stall the company waiting on an external service.
- `gtw-conflict-resolver`'s mediation itself becomes contested (a third room disputes the ruling's precedent) → `brd-arbiter`, same as any unresolved dispute — this room does not self-arbitrate a ruling it already made.
- `gtw-budget-warden`'s waste finding is disputed by the flagged room's Lead → `gtw-dispatcher` mediates once against the actual `routing.yaml` band cited; unresolved → `brd-ceo` directly (budget disputes are a boardroom-accountability matter, not an arbitration one, since `brd-ceo` already owns `gate: "all"`).
- A dispute above `gtw-dispatcher`'s own mediation authority → `brd-arbiter`, one-line ADR, `gtw-dispatcher` informed and the ruling forwarded verbatim to whichever room's Lead is affected.
- **Security spur, no exception:** any of the six agents surfacing a security finding mid-task routes it `→ sec-lead → brd-cso` immediately, same as any other room — this room holds no veto of its own and never queues a security finding behind routine dispatch traffic.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
