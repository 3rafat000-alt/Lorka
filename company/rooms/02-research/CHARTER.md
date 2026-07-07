# 🔬 Room 02 — Research (البحث)

> Gate: **1 (Discovery)**, plus `res-web-scout` cross-gate as the company's dedicated search/fetch/verify scout. Research does not decide what to build; it decides what is **true** about the human who will use it — and hands that truth to Design as a fact, never a guess.

## Mission

Answer, with evidence, what the user wants and what blocks them. Room 02 takes the frozen `<PRJ>_Problem_Statement.md` from `01-strategy` and turns it into evidence-grounded personas, a pain/gain map, a Customer Journey Map (Mermaid, with emotional arc and ranked friction log — **the Design Truth**, Teaching I), and — when the project is market-facing — a competitor teardown. Every claim in every artifact this room produces traces to a source: a brain file, a codebase line, or a cited URL with a fetch date. An uncited "fact" is a guess wearing a suit (Article 09), and `res-fact-checker` exists specifically to catch it before it ships. `res-lead` owns the Gate-1 exit: nothing leaves this room for `03-design` unless it answers WHAT the user wants and WHAT blocks them, cited, with `res-fact-checker`'s adversarial pass done.

## Members

| id | role | route | reports_to |
|---|---|---|---|
| `res-lead` | Room Lead / gateway — owns the Gate-1 exit; the only member who may address another room's Lead | `sonnet` · workhorse · high · full | `brd-ceo` |
| `res-ux-researcher` | Evidence-grounded personas, pain/gain map, JTBD inventory | `sonnet` · workhorse · medium · lite | `res-lead` |
| `res-journey-architect` | Customer Journey Map (Mermaid) + emotional arc + ranked friction log — THE Design Truth | `inherit` · gatekeeper · high · lite | `res-lead` |
| `res-web-scout` | Search → fetch → verify → cite ladder for the whole company; Ingest-vs-Reach discipline | `haiku` · mechanical · low · full | `res-lead` |
| `res-competitor-analyst` | Competitor teardowns — feature, pricing, positioning, and the honesty of their error states | `sonnet` · workhorse · medium · lite | `res-lead` |
| `res-data-researcher` | Quantitative evidence — surveys, telemetry mining, benchmark numbers with sample sizes attached | `sonnet` · workhorse · medium · full | `res-lead` |
| `res-fact-checker` | Adversarial claim verification — enforces G1-G5 on every research output; UNKNOWN is a valid verdict | `sonnet` · workhorse · medium · full | `res-lead` |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source.

## Gate ownership

Room 02 owns **Gate 1 (Discovery)** end to end (`company/nexus/gates.yaml`, `owner_room: 02-research`). `brd-cpo` is accountable for the Gate-0/1 span but does not produce the artifacts — this room does.

- **Entry:** `docs/<PRJ>_Problem_Statement.md` frozen (gate-0 tag `<PRJ>-gate0-done` exists).
- **Artifacts:** `docs/<PRJ>_Personas.md` (evidence-grounded, cited) · `docs/<PRJ>_Journey_Map.md` (Mermaid + emotional arc + friction log) · `docs/<PRJ>_Competitor_Teardown.md` (when market-facing).
- **Exit bar:** answers WHAT the user wants and WHAT blocks them, every claim cited (source URL + fetch date, or brain file, per Article 02) · `res-fact-checker`'s adversarial pass done, G1-G5 enforced, UNKNOWN claims flagged and never shipped · every persona traces to evidence · every journey stage carries an emotional state + a friction entry.
- **On fail:** rejected upward to `01-strategy` if the problem statement was too thin to research against, or re-researched inside the room; unverifiable claims are dropped, never kept "for now."

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00):

| From | What |
|---|---|
| `01-strategy` via `str-lead` | The frozen `Problem_Statement.md`, `Blueprint.md`, and the two-track sizing call (fast_track vs deep_audit) that scopes how deep this room's research needs to go |
| `00-boardroom` via `brd-cpo` | Gate-0/1 accountability questions, Deep-Audit triggers when the project touches money/credentials/auth/PII |
| `14-gateway` via `gtw-dispatcher` | Routed Work Orders opening a Gate-1 ticket |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `03-design` via `dsn-lead` | `Personas.md` + `Journey_Map.md` (the frozen Gate-1 bundle) — `dsn-ui-designer` maps one screen per journey stage, `dsn-content-strategist` writes copy that matches the personas' voice |
| `00-boardroom` via `brd-cpo` | Gate-1 status for the Gate-0/1 accountability check-in |
| `01-strategy` via `str-lead` | Rejection-upward when the problem statement is too thin to research against (Teaching II — reject, don't improvise) |
| `13-knowledge` via `knw-lead` | Cited research facts worth ingesting into the durable brain (Ingest, not Reach — Article 09 §5) |
| `12-observability` via `obs-lead` (loop-back, Gate 8 → 1) | `obs-insights-analyst`'s journey drop-off findings re-open this room's Discovery work on the next cycle |

## Room bar (what `res-lead` blocks on)

- No persona ships without a JTBD and at least one traceable evidence source — an invented trait is rejected back to `res-ux-researcher`, named.
- No Journey Map ships happy-path-only — every stage needs an emotional state and a friction entry, including offline/error/recovery branches; `res-journey-architect`'s freeze is what makes it the Design Truth downstream (Teaching I).
- No claim crosses into `Personas.md`, `Journey_Map.md`, or `Competitor_Teardown.md` without `res-fact-checker`'s pass — a claim marked UNKNOWN is flagged in the artifact, never silently dropped or silently kept.
- No web-derived fact is missing its `[source: <url>, fetched <date>]` citation (Article 09 §4) — the fetch date always comes from the orchestrator, never invented.
- No volatile fact (a price, a version number, a rank) gets written into the brain as if it were evergreen — Reach facts are recorded as dated decisions, not standing truth (Article 09 §5).
- Gate-1 does not advance on `res-lead`'s self-report alone — mechanical `sofi gate-check` plus `gtw-gatekeeper`'s fresh-context adversarial verdict, same as every gate (Article 03 V1+V2).

## Playbook index

- `playbooks/discovery-gate-procedure.md` — the room's core Gate-1 procedure end to end: orient → research fan-out → journey map → fact-check → freeze → handoff, with real `sofi` commands.
- `playbooks/competitor-teardown.md` — `res-competitor-analyst`'s specialty procedure for a market-facing project: how to structure a teardown that judges by user value, not feature checklists.

## Tools index

See `tools/README.md`. This room currently has no dedicated Python scanners of its own (v5 carried none for the strategy/research tier) — it leans on the shared `company/os/sofi_tools` library and the general-purpose `sofi_scan.py`/`feature_scan.py` for any mechanical pre-pass, and on `res-web-scout` for everything requiring live web access.

## Skills index

See `skills/README.md`. Headline: `/sofi-boot`, `/sofi-gate`, `/sofi-handoff`, `/sofi-delegate`, `/sofi-report`, `/sofi-fix` (routing a rejected/UNKNOWN claim), `/sofi-audit` (research-quality sweep).

## Escalation path

`specialist → res-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00 chain), with these room-specific triggers:

- A persona or journey claim `res-fact-checker` cannot resolve to CONFIRMED or CONTRADICTED (i.e. genuinely UNKNOWN after a second-source check) → flagged in the artifact, `res-lead` decides whether it blocks the Gate-1 freeze or ships as a labeled assumption.
- A `Problem_Statement.md` too thin to research against → rejected upward to `str-lead`, not improvised around.
- Anything the room's research surfaces that touches money/credentials/auth/PII → `res-lead` escalates immediately to `brd-cpo`, who triggers the Deep-Audit track via `brd-cso` — Room 02 does not make that call alone.
- A Design-vs-Research dispute about whether a journey stage is real or invented → `res-lead` first, `gtw-conflict-resolver` if unresolved at the room-Lead level, `brd-arbiter` only past that.
- Circuit breaker: 3 failed self-correction attempts on any Gate-1 artifact → HALT, structured crash-dump JSON, escalation ticket, `res-lead` decides the next route (Article 00 §"Escalation & parallelism").

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
