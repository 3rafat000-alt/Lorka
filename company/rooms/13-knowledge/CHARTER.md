# 📚 Room 13 — Knowledge (المعرفة)

> Gate: **cross-gate — standing service, no gate of its own.** `13-knowledge` is the room every other room reads from before it acts and writes through when it's done, and it never once appears as the "owner" column in `company/nexus/gates.yaml`. That is by design: memory is not a phase of the lifecycle, it is the substrate every phase stands on. Six colleagues keep the company's brain — org-level and per-project — honest, queryable, and small enough to actually read: `knw-lead` owns `MEMORY.md`'s routing map and the brain's overall governance; `knw-memory-curator` keeps every brain file from bloating past what a boot can afford; `knw-reflector` turns raw episodic history into the durable lessons that stop the same mistake from filing twice; `knw-doc-writer` keeps the company's own documentation legible, bilingual-ready, to a human who just landed; `knw-historian` keeps the ADR ledger honest with dates that came from the record, never invented; and `knw-brain-query` answers "where do I find X" in one grep-first pass instead of a blind re-search. The room's whole reason for existing is a single line in `company/brain/BRAIN.md`: **"not in the brain = not true."**

## Mission

Be the company's memory, not its diary. `13-knowledge` does not produce features, contracts, or code — it produces the infrastructure that makes every other room's "read the brain before you act" (Article 00 §1) actually mean something: a `MEMORY.md` routing map any agent can scan in seconds (`knw-lead`); brain files kept under their token ceilings via caveman-compression that never destroys meaning, with the pre-compression original always preserved (`knw-memory-curator`); `LESSONS.md` entries distilled from closed episodes, never from a mid-task guess (`knw-reflector`); READMEs and guides that read cleanly in English and are bilingual-ready in Arabic without a translation tax (`knw-doc-writer`); an ADR/decision ledger where every date is the one the CEO actually gave, never one an agent invented to look tidy (`knw-historian`); and grep-first structured retrieval that answers a brain question with a file:line table instead of a re-read of everything (`knw-brain-query`). `knw-lead` is the room's sole gateway and its escalation point — she is the one name that signs off when a brain-governance question crosses into another room's territory, and the one name `brd-ceo` calls when the org brain itself (`company/brain/org/`) needs a ruling.

## Members

| id | persona | role | route |
|---|---|---|---|
| `knw-lead` | Dalia Haddad | Librarian / sole gateway — owns `MEMORY.md`'s routing map + overall brain governance (org + project layers); the one signature on any cross-room memory-architecture ruling | `sonnet` · workhorse · medium · full · `3k-6k` |
| `knw-memory-curator` | Bartek Nowak | Memory Curator — brain hygiene: caveman-compresses grown files at gate-close or the ~300-line threshold, always keeping a `.original.md` backup; frontmatter discipline across every brain file | `haiku` · mechanical · low · ultra · `1k-3k` |
| `knw-reflector` | Yuki Almeida | Reflector — LESSONS distillation, scheduled dreaming at gate-close or on demand, **never per-turn**; one candidate → one grounded `situation · what-failed · rule` lesson | `sonnet` · workhorse · medium · full · `3k-6k` |
| `knw-doc-writer` | Youssef El-Sayed | Doc Writer — READMEs and guides, bilingual-ready EN/AR, written to be scanned in seconds not studied | `haiku` · mechanical · low · full · `1k-3k` |
| `knw-historian` | Rosario Quispe | Historian — DECISIONS/ADR log keeper; the date always comes from the CEO's Work Order, never invented | `haiku` · mechanical · low · full · `1k-3k` |
| `knw-brain-query` | Duc Pham | Brain Query — retrieval specialist: `sofi brain-query`, grep-first search ladder, returns file:line tables, never a re-summary | `haiku` · mechanical · low · ultra · `1k-3k` |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The five specialists `reports_to: knw-lead`; `knw-lead` `reports_to: brd-ceo`.

## Gate ownership

`13-knowledge` owns **no numbered gate** in `company/nexus/gates.yaml` — it is a cross-gate standing service, the same shape as `14-gateway`, and its "exit bar" is continuous rather than a single ceremony:

- **Trigger:** every gate-close (a lesson-distillation pass becomes due), every brain-file write across every project (curation/frontmatter discipline applies), every ADR the CEO dates (the historian's ledger entry becomes due), and every session boot (`MEMORY.md` + `LESSONS.md` get read, per Article 00 §1) — this room's work has no single ceremony because memory has no single moment.
- **Entry:** a closed episode exists to reflect on (never an in-flight ticket — Article 04 rule 1, scheduled not per-turn); a brain file has actually crossed its compression threshold or a gate has actually closed (never speculative "let's tidy early"); a decision has an actual date from the CEO (never `knw-historian`'s own clock).
- **Artifacts:** `MEMORY.md` (root routing map, under 200 lines — `knw-lead`'s bar), `projects/<PRJ>/_context/LESSONS.md` + `company/brain/org/LESSONS.md` (`knw-reflector`), `.original.md` backups beside every compressed brain file (`knw-memory-curator`), `company/rooms/*/README`-shaped docs and any guide `knw-doc-writer` is asked for, `DECISIONS.md`/ADR entries project + org (`knw-historian`), brain-query result tables (`knw-brain-query`, ephemeral — returned to the asking agent, not stored).
- **Exit bar:** `MEMORY.md` stays under 200 lines and every pointer it carries resolves to a real file (`sofi doctor` and `knw-lead`'s own periodic self-check); no brain file with a `.original.md` sibling lost meaning in compression (spot-checked, Article 03 V5-style); no `LESSONS.md` entry lacks a `sig:` or a cited source ticket; no ADR entry carries a date `knw-historian` invented; every doc `knw-doc-writer` ships is legible without a follow-up question.
- **On fail:** a bloated `MEMORY.md`, a lost citation, an undated ADR, or a per-turn reflection attempt is a room-bar violation `knw-lead` blocks on directly — this room does not "gate-check" the way `qa-lead` does, but its own standing bar is enforced with the same seriousness, because a corrupted brain corrupts every downstream gate silently.

`brd-ceo` carries this room's accountability line directly (no dedicated C-level intermediary, the same shape as `12-observability`'s Gate-8 accountability) — a broken brain is a company-wide risk, not a departmental one.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `knw-lead` directly):

| From | What |
|---|---|
| every room, via its own Lead | Closed `HANDOFFS.md` tickets (escalations, circuit-breaker trips, rejections, ≥3× recurring patterns to the same target) — the raw signal `knw-reflector` mechanically locates candidates from, at zero model tokens, per project. |
| `00-boardroom` via `brd-ceo` | The dated Work Order behind every ADR `knw-historian` logs — she never invents a date, she only ever transcribes the one the CEO gave. |
| `14-gateway` via `gtw-dispatcher` / `gtw-conflict-resolver` | Escalation and dispute records worth a `LESSONS.md` candidate — a circuit breaker `gtw-conflict-resolver` had to mediate is exactly the kind of recurring-pattern signal `knw-reflector`'s scan surfaces. |
| `09-security` via `sec-lead` | Post-mortem action items and incident patterns — `knw-historian` logs the ADR, `knw-reflector` distils the durable rule once the incident is closed. |
| `12-observability` via `obs-lead` | Blameless post-mortem summaries and journey drop-off findings — `knw-historian`'s ADR ledger and `knw-reflector`'s lesson candidates both draw on these once an incident or a Gate-1 re-open is closed. |
| any room, via its own Lead | A request to draft or refresh a README/guide (`knw-doc-writer`), a request to compress a grown brain file (`knw-memory-curator`), or a structured retrieval question (`knw-brain-query`) — the room's four specialist services, requested the same way any cross-room service is: through the requesting room's own Lead to `knw-lead`. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| every room, at boot, directly (read, not delegated) | `MEMORY.md` (root routing map) and `LESSONS.md` (project + org) — every agent reads these at Article 00 §1, they are not "delivered" so much as always-open for reading; `knw-lead` and `knw-reflector` are the ones who keep them worth reading. |
| `00-boardroom` via `brd-ceo` | Org-level `DECISIONS.md` ADR entries (`knw-historian`), `PERSONAS.md` updates (`knw-doc-writer`), `TEAM_STATUS.md` health-snapshot inputs, and promotion proposals surfaced by recurring `LESSONS.md` patterns — reflection *proposes*, the CEO decides (Article 04). |
| `14-gateway` via `gtw-router` / `gtw-budget-warden` | `sofi brain-query` retrieval results feeding a routing or budget decision, and `MEMORY.md` pointer confirmations before a registry sync. |
| any room, via its own Lead | Requested README/guide drafts, a compressed brain file with its `.original.md` sibling intact, or a brain-query result table — returned to the requesting Lead, never delivered sideways to a specialist directly. |

## Room bar (what `knw-lead` blocks on)

- No `MEMORY.md` entry points to a file that doesn't exist, and the file itself never exceeds ~200 lines — grown detail moves into the target file, never piles up here.
- No brain-file compression ships without a `.original.md` backup sitting beside it — reversibility (Teaching VI) applies to memory hygiene exactly as it applies to a migration.
- No compression ever touches code, commits, security warnings, ADR rationale + rollback plans, evidence blocks, or `LESSONS.md` rules — these are the audit trail, full prose, forever (`company/brain/BRAIN.md` §8).
- No `LESSONS.md` entry ships without a `sig:` key and a cited source ticket — an ungrounded "lesson" is an opinion, not procedural memory.
- No reflection pass runs mid-task or per-turn — gate-close or on-demand only (Article 04 rule 1); `knw-reflector` scans *closed* episodes, never a specialist's live working turn.
- No ADR date is invented — `knw-historian` transcribes the CEO's Work Order date, full stop; a missing date blocks the entry, it does not get backfilled with "today."
- No doc `knw-doc-writer` ships needs a follow-up meeting to explain itself — if it does, it gets rewritten before it's called done.
- No specialist inside the room bypasses `knw-lead` to reach another room's Lead directly — every cross-room memory-governance ruling and every requested service response leaves through the gateway.
- No `knw-brain-query` answer skips the grep-first ladder (map → project brain → codebase → `sofi brain-query` → web) to jump straight to a web search — the ladder exists precisely so the company stops re-discovering what it already wrote down.
- Reflection never rewrites doctrine or a frozen spec silently — it proposes, `brd-ceo` decides, and the decision itself becomes an `knw-historian` ADR entry.

## Playbook index

- `playbooks/gate-close-reflection-and-hygiene.md` — the room's core cross-gate procedure: how `knw-lead` sequences `knw-reflector`'s scheduled dreaming pass, `knw-memory-curator`'s compression sweep, and `knw-historian`'s ADR logging at every gate close, with real `sofi` commands end to end.
- `playbooks/brain-query-retrieval.md` — the room's sharpest recurring job: `knw-brain-query`'s grep-first retrieval ladder, from a raw human-shaped question to a cited file:line table, before anyone reaches for a fresh search.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/ceo/reflection_engine.py` (`knw-reflector`'s standing backbone — mechanical `scan`/`write` over `HANDOFFS.md`, dedup by `sig:`, ported forward from v5's `ceo/`-housed reflection engine and re-owned by this room), `company/os/sofi_tools/brain.py` (`sofi brain`, `read_state`/`append_context`/`append_decision` — `knw-historian`'s and `knw-lead`'s primary console), `company/os/sofi_tools/tickets.py` (`query`/`lesson_signatures`/`append_lesson` — the mechanical backbone under both `sofi brain-query` and the reflection engine's dedup), `company/os/sofi_tools/guard.py` (`check_script_header` — the header-discipline check `knw-memory-curator` runs on any script this room writes), `company/os/caveman/integration.md` (the `caveman-compress` contract `knw-memory-curator` follows verbatim, including the `.original.md`-backup guarantee).

## Skills index

See `skills/README.md`. Headline: `/sofi-reflect` (this room's owned command — `knw-reflector` runs it, scheduled, never per-turn), `/sofi-boot` (every agent's first read of `MEMORY.md` + `LESSONS.md`, which this room keeps worth reading), `/sofi-handoff` (the write-order half of the brain contract this room polices), plus `/sofi-report`/`/sofi-team` for the room's own accountability check-ins and roster lookups.

## Escalation path

`specialist → knw-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain), with two shortcuts specific to this room:

- A brain-governance ruling that another room's Lead disputes (e.g. `bck-lead` wants a compression `knw-memory-curator` declines to run because it would touch code or an evidence block) → `knw-lead` mediates one round citing `company/brain/BRAIN.md` §8's compressible/never-compressed split; unresolved after that round → `gtw-conflict-resolver`.
- A `LESSONS.md` promotion candidate (a recurring pattern `knw-reflector` flagged 2+ times) that would touch doctrine or a frozen spec → routes directly to `brd-ceo` via `knw-lead`, never auto-applied — reflection proposes, the CEO decides, and the ruling becomes `knw-historian`'s next ADR entry.
- A specialist's task trips the circuit breaker (3 failed attempts — a compression that keeps losing meaning, a lesson that keeps failing its own `sig:` dedup check) → `knw-lead` halts that specialist's contribution and escalates with the structured crash dump, rather than accepting a fourth unverified "done."
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `knw-lead` informed and the ruling forwarded verbatim to whichever specialist is affected — and logged by `knw-historian` the same turn it's decided.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
