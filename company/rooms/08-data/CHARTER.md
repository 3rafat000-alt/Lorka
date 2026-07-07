# 🗄️ Room 08 — Data (البيانات)

> Gates: **3–4.** The Data room is where a designed schema and a frozen contract stop being paper and become a data layer that survives load, redelivery, and audit: reversible migrations physically built and run, indexes that match the journey's real read paths, a Redis caching layer that never stampedes, event pipelines a metric can actually be traced back to, ML/AI features that ship only behind an eval suite, idempotent batch syncs, and a PII map with a retention clock and an encryption-at-rest posture. `08-data` is not the owner room of either gate it touches — at Gate 3 it is a **squad partner** alongside `04-architecture` and `09-security`, all three fanned out behind the same frozen prototype; at Gate 4 it is a **support room** behind `05-backend`'s owner-room build window. Seven colleagues, one gateway: `dat-lead` sequences the six specialists, checks every artifact against the frozen upstream design, and signs — or rejects — the room's contribution at each gate it participates in.

## Mission

Turn `arc-data-architect`'s frozen schema design into a physically built, reversible, indexed, N+1-free database (Gate 3 validation → Gate 4 execution); build a Redis caching layer with stampede-safe invalidation over the hot read paths the built services actually exercise; stand up event pipelines and product-metrics models a dashboard number can be replayed back to a raw event; integrate ML/AI features that never ship without a passing eval suite against a stated baseline; run imports/exports/syncs as idempotent batch operations that survive being re-run on the same input; and classify every field that touches personal data, map its retention window, and state its encryption-at-rest posture before Gate 3 closes. `dat-lead` is the room's sole gateway — no specialist inside `08-data` reaches `arc-lead`, `bck-lead`, `sec-lead`, or any other room's Lead directly; every cross-room artifact leaves through him, forwarded verbatim, never re-authored.

## Members

| id | persona | role | route |
|---|---|---|---|
| `dat-lead` | ★ Günther Weber | Room Lead / sole gateway — promoted from Database Engineer; sequences the six specialists, validates against the frozen schema/contract, signs the room's Gate-3 and Gate-4 contributions | `sonnet` · workhorse · high · full |
| `dat-db-engineer` | Mai Trần | Executes the frozen schema as reversible migrations, runs `EXPLAIN` on hot queries, adds/tunes indexes, kills N+1 | `sonnet` · workhorse · high · full |
| `dat-cache-engineer` | Rafael Couto | Redis caching layer design — stampede-safe invalidation over the built services' real read paths | `sonnet` · workhorse · medium · full |
| `dat-analytics-engineer` | Yewande Coker | Event pipelines and product-metrics models — every dashboard number replayable to a raw event | `sonnet` · workhorse · medium · full |
| `dat-ml-engineer` | Daniel Suh | ML/AI feature integration — no model ships without a passing eval suite against a stated baseline | `sonnet` · workhorse · high · full |
| `dat-etl-engineer` | Zofia Kowalska | Imports/exports/syncs as idempotent batch operations — safe to re-run on the same input, always | `sonnet` · workhorse · medium · full |
| `dat-privacy-officer` | Joseph Mwangi | PII classification, retention map, encryption-at-rest posture | `sonnet` · workhorse · high · full |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The six specialists `reports_to: dat-lead`; `dat-lead` `reports_to: brd-ceo`.

## Gate ownership

`08-data` owns no gate outright in `company/nexus/gates.yaml`; it participates in two, with two different postures:

- **Gate 3 — Architecture** (`gates.yaml id: 3`, owner `04-architecture`). `dat-lead` runs as a **squad partner** to `arc-lead` and `sec-lead`, all three fanned out behind the *same* frozen `Prototype_Spec.md` + `Content_Strings.json` (`effort_scaling.cross-room`). `gates.yaml`'s Gate-3 agent list names `dat-lead`, `dat-db-engineer`, and `dat-privacy-officer` explicitly: `dat-db-engineer` gives `arc-data-architect`'s schema design physical migration-validation feedback (index cost, real read-pattern data from a brownfield brain, before the bundle freezes) — he does not design the schema, that stays `arc-data-architect`'s. `dat-privacy-officer` produces `docs/<PRJ>_PII_Map.md` whenever the frozen prototype touches personal data; its absence on a PII-bearing project blocks `arc-lead`'s Gate-3 freeze exactly like a missing threat model does.
- **Gate 4 — Build** (`gates.yaml id: 4`, owner `05-backend`). `08-data` is a named **support room**: `dat-db-engineer` physically executes the migrations `arc-data-architect` designed (with tested `down()`s, mechanically checked), `dat-cache-engineer` builds the caching layer the backend's services call into, and `dat-etl-engineer` builds the sync jobs a feature's scope requires. `gates.yaml`'s Gate-4 agent enumeration names these three plus `dat-lead` as the room's core build-time squad. `dat-analytics-engineer` and `dat-ml-engineer` are full room members whose own gate assignment (`routing.yaml`: gate 4) plugs into the same Build window — they are not blocking members of every Gate-4 pass, only of the projects whose frozen scope actually calls for an event pipeline or an ML feature; `dat-lead` dispatches them only when the ticket names that scope.

`brd-cto` (Ingrid Voss) is accountable for the Gate 3–4 span at the Boardroom level. `dat-lead` does not sign the Gate-3 or Gate-4 exit himself — `arc-lead` and `bck-lead` are the named owner-room signers — he signs and reports **this room's contribution**, and either owner-room Lead will not freeze/merge around a missing or rejected `08-data` deliverable that gate depends on.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `dat-lead` directly):

| From | What |
|---|---|
| `04-architecture` via `arc-lead` | `arc-data-architect`'s frozen schema design (`docs/<PRJ>_Schema.sql` + Mermaid ER + migration designs, each already paired with a rollback) — `dat-db-engineer`'s only legitimate starting point for the physical build. Not frozen → reject upward, don't build against a moving schema. |
| `04-architecture` via `arc-lead` | `arc-api-architect`'s frozen `OpenAPI.yaml` — the entity shapes `dat-analytics-engineer`'s event schema and `dat-etl-engineer`'s sync jobs must stay consistent with. |
| `03-design` via `dsn-lead` (indirect, forwarded through `arc-lead`'s bundle) | `Prototype_Spec.md` — the journey's actual read paths `dat-db-engineer` indexes for and the screens `dat-privacy-officer` scans for personal-data fields. |
| `05-backend` via `bck-lead` | Real read/write traffic shape from the built services, at Gate 4 — the evidence `dat-cache-engineer` validates the invalidation design against instead of a hypothetical access pattern; confirmation the physical migrations landed cleanly before services and models are written against them. |
| `09-security` via `sec-lead` | The signed `Threat_Model.md` — `dat-privacy-officer`'s encryption-at-rest posture and `dat-cache-engineer`'s cache design do not contradict an unmitigated High risk in it. |
| `00-boardroom` via `brd-cto` | Gate 3–4 accountability checks; binding constraints (a mandated retention ceiling, a regulatory data-residency rule) that bear on `dat-privacy-officer`'s map. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior data layers (a past `migration-double-index-hazard`-shaped mistake, a past cache-stampede incident) before a specialist designs from a blank page. |
| `04-architecture` via `arc-review-architect` (cross-gate, addressed through `dat-lead`) | A `/sofi-spec-review` verdict touching this room's data-layer surface — read-only, findings routed back through `dat-lead` to `/sofi-fix`. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `04-architecture` via `arc-lead` | Physical migration-validation feedback (Gate 3) — index cost, brownfield read-pattern data — that `arc-data-architect` folds into the schema design before the bundle freezes; the signed `PII_Map.md` when personal data is touched, a hard blocker on the Gate-3 freeze if missing. |
| `05-backend` via `bck-lead` | Executed, reversible migrations the domain services and models are written against (Gate 4); the caching layer's invalidation contract `bck-domain-engineer`'s services call into; sync jobs `bck-queue-engineer`'s jobs coordinate with. |
| `09-security` via `sec-lead` | `dat-privacy-officer`'s PII classification and encryption-at-rest posture, for `sec-appsec-engineer`'s secure-code review and `sec-compliance-auditor`'s regulatory mapping at Gate 5. |
| `10-quality` via `qa-lead` | `dat-ml-engineer`'s eval-suite results (baseline vs shipped model) and `dat-etl-engineer`'s idempotency test evidence, for `qa-automation-engineer`'s coverage pass. |
| `00-boardroom` via `brd-ceo` (report) / `brd-cto` (accountability check) | This room's signed contribution at each gate: Gate 3 migration-validation feedback + `PII_Map.md`; Gate 4 executed migrations + cache design + sync jobs (+ event pipelines / ML features when scoped in). |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for any expensive-to-reverse data call (a sharding decision, a retention-policy change, a model-serving architecture choice); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket once the room's contribution ticket carries its evidence block. |

## Room bar (what `dat-lead` blocks on)

- No migration merges without a passing `migration_check.py` result — no rollback = rejected, no exception (Teaching VI; `dat-db-engineer`'s bar, mechanically checked, not assumed).
- No index ships that doesn't cite the journey read pattern or hot query it serves — an index nobody reads from is a write-cost with no benefit (`dat-db-engineer`'s bar).
- No cache design ships without a named stampede-safe invalidation strategy (lock/jitter/stale-while-revalidate/versioned key — one of them, stated) and an explicit answer to "what happens when this key misses for a thousand requests at once" (`dat-cache-engineer`'s bar).
- No analytics metric ships that can't be replayed back to a raw event in the pipeline — a dashboard number nobody can trace is folklore, not data (`dat-analytics-engineer`'s bar).
- No ML/AI feature ships without a passing eval suite run against a stated baseline, evidence pasted (cmd + output), not self-reported (`dat-ml-engineer`'s bar; Article 03 V1).
- No batch job (import/export/sync) ships without a "runs twice on the same input" test proving idempotency — the same discipline `bck-queue-engineer` applies to jobs, owned here for data movement (`dat-etl-engineer`'s bar).
- No Gate-3 freeze proceeds on a PII-touching project without a signed `PII_Map.md` — classification, retention window, and encryption-at-rest posture for every field, no field left "we'll classify it later" (`dat-privacy-officer`'s bar).
- No specialist inside the room bypasses `dat-lead` to reach `arc-lead`, `bck-lead`, `sec-lead`, or any other room's Lead directly — every cross-room artifact leaves through the gateway, forwarded verbatim, never re-authored.

## Playbook index

- `playbooks/gate-3-4-data-layer.md` — the room's core procedure: frozen schema design → physical migration build + validation feedback (Gate 3) → executed migrations + cache + sync (Gate 4) → signed contribution at each gate, with real `sofi` commands end to end, coordinated alongside the `04-architecture`/`09-security` squad and the `05-backend` build window.
- `playbooks/stampede-safe-cache-invalidation.md` — `dat-cache-engineer`'s sharpest recurring job and the room's other standing procedure: designing a Redis caching layer whose invalidation survives a thundering-herd miss instead of amplifying it into an outage.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/gate/migration_check.py` (this room's own physical-build gate — registered in `company/nexus/registry.yaml` with `dat-db-engineer` as owner), `company/os/sofi_tools/gates.py` (`sofi gate-check`) for the mechanical Gate-3/Gate-4 validation this room's contribution feeds, `company/os/toolkit/core/sofi_scan.py` (`wiring`/`security` modes for locating a query seam or an N+1 pattern before `dat-db-engineer`'s pass), `company/os/toolkit/core/feature_scan.py` (Phase-1 scan behind any `/sofi-spec-review` touching this room's surface).

## Skills index

See `skills/README.md`. Headline: `/sofi-gate` (the Gate-3/Gate-4 contribution `dat-lead` signs each pass), plus `/sofi-boot`, `/sofi-delegate`, `/sofi-handoff` for the room's own cycle, `/sofi-audit`/`/sofi-fix` for the mechanical sweep-then-repair loop each specialist runs before handing work to `dat-lead`, and `/sofi-team`/`/sofi-report` for picking a downstream specialist or writing the room's findings up for the brain.

## Escalation path

`specialist → dat-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain). Inside the room:

- A specialist's draft contradicts the frozen upstream design (e.g. `dat-db-engineer`'s physical build needs an index `arc-data-architect`'s schema design didn't anticipate) → `dat-lead` mediates first, one round, citing both `file:line` positions; unresolved after that round, or the gap is in the frozen design itself → escalate to `arc-lead` via `dat-lead` (the design layer owns the fix, this room does not silently patch around a frozen artifact).
- A migration cannot be given a tested rollback after one correction round → `dat-lead` blocks the physical build and escalates to `arc-lead` (the design was frozen without a reversible path — that's a Gate-3 defect surfacing at Gate 4, not a Gate-4 one).
- `dat-cache-engineer`'s invalidation design can't answer the stampede question after one correction round → `dat-lead` blocks the merge and escalates to `bck-lead` if the ambiguity is in how the service actually reads the key, not in the cache design itself.
- `dat-ml-engineer`'s eval suite fails against the stated baseline → the feature does not ship; `dat-lead` escalates to `brd-cto` if the baseline itself is contested, never lowers the bar to pass a model through.
- `dat-etl-engineer` cannot make a batch job idempotent after one correction round (the source system offers no natural dedup key) → `dat-lead` escalates to `arc-integration-architect` via `arc-lead` — the integration plan may need a vendor-side change, not a workaround invented here.
- `dat-privacy-officer` finds a field the frozen prototype requires but that has no lawful retention/encryption answer yet → immediate escalation `sec-lead`/`brd-cso` via `dat-lead` (the security spur, Article 07 §1) — the Gate-3 freeze does not proceed around an unclassified PII field, regardless of schedule pressure.
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `dat-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
