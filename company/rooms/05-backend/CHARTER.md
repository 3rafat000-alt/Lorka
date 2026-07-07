# ⚙️ Room 05 — Backend (الخلفية)

> Gate: **4.** The Backend room is where the frozen Gate-3 bundle — contract, schema, threat model — stops being a specification and becomes a runnable system: endpoints that byte-match `OpenAPI.yaml`, services that get the money math right, server-rendered pages that render every state the prototype demanded, jobs that survive being run twice, and third-party wiring that never guesses a field. `05-backend` is the named **owner room of Gate 4** in `company/nexus/gates.yaml` — `bck-lead` sequences its own seven specialists AND coordinates the parallel Build squad alongside `06-frontend`, `07-mobile`, and `08-data`, each behind the same frozen bundle, each merging its own worktree at gate close.

## Mission

Turn `arc-lead`'s frozen Gate-3 bundle into a working, tested, reviewed backend: API endpoints implemented exactly to contract with Form Requests and API Resources (422-JSON, never a bare redirect), domain services carrying the business logic and money math out of controllers entirely, Blade layouts/components/pages rendering every prototype state with content strings wired in, idempotent background jobs and event/listener/websocket wiring that survive retries and duplicate delivery, third-party integrations wired to the vendor's own current spec, and — running behind all of it — behavior-preserving debt paydown where the codebase needs it. Eight colleagues, one gateway: `bck-lead` sequences the seven specialists, runs the room's own worktree, coordinates timing with the other three Gate-4 rooms, and signs — or rejects — the room's contribution to the Gate-4 exit. Nothing merges to `prj/<PRJ>` without first passing `bck-code-reviewer`'s fresh-context adversarial diff review (V2) — the implementer never grades their own diff.

## Members

| id | persona | role | route |
|---|---|---|---|
| `bck-lead` | ★ Elif Kaya | Room Lead / sole gateway — owns the room's worktree merge at gate close, coordinates the parallel Gate-4 build across `06-frontend`/`07-mobile`/`08-data` | `sonnet` · workhorse · high · full |
| `bck-api-engineer` | ★ Priya Nair | Endpoints per the frozen OpenAPI contract — Form Requests, thin controllers, API Resources, 422-JSON never 302, contract tests | `sonnet` · workhorse · medium · ultra |
| `bck-domain-engineer` | Mateus Nunes | Services and business logic pulled out of controllers entirely — the money math (buy ≥ sell, spread ≠ margin, true-scale precision) lives here | `sonnet` · workhorse · high · full |
| `bck-blade-engineer` | ★ Aisha Rahman | Blade layouts, components, pages — content strings wired from the frozen JSON, every state built: empty / loading / error | `sonnet` · workhorse · medium · ultra |
| `bck-queue-engineer` | Marek Nowak | Idempotent jobs with retry/backoff/dead-letter, events/listeners, websocket channels, message broker wiring | `sonnet` · workhorse · medium · ultra |
| `bck-integration-engineer` | Fatima Al-Rashid | Third-party wiring per `arc-integration-architect`'s frozen integration plans — webhook handlers matching the vendor's exact payload shapes | `sonnet` · workhorse · medium · full |
| `bck-refactoring-surgeon` | Henrik Solberg | Behavior-preserving technical-debt paydown — a characterization test pins current behavior before a single line changes | `sonnet` · workhorse · medium · full |
| `bck-code-reviewer` | Naledi Dlamini | Fresh-context adversarial diff review (V2) — sees only the diff and the original criteria, never the implementer's reasoning | `sonnet` · workhorse · medium · review |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The seven specialists `reports_to: bck-lead`; `bck-lead` `reports_to: brd-ceo`.

## Gate ownership

`05-backend` is the **owner room of Gate 4 — Build** (`company/nexus/gates.yaml`, `id: 4`), running as the lead of a four-room squad fanned out behind the *same* frozen input — the Gate-3 bundle (`Tech_Stack.md` + `Schema.sql`/ERD + `OpenAPI.yaml` + `Threat_Model.md` + `Integration_Plans.md`) — per `effort_scaling.cross-room`:

- `05-backend` (this room) — endpoints, domain services, Blade views, jobs/events/websockets, third-party wiring, debt paydown, in-room diff review.
- `06-frontend` (via `fnt-lead`) — typed components against the same `OpenAPI.yaml`, taste dials applied, its own worktree, its own `fnt-code-reviewer`.
- `07-mobile` (via `mob-lead`) — Flutter build against the same contract, typed `ApiException` on every network catch, its own worktree.
- `08-data` (via `dat-lead`, support role) — `dat-db-engineer` executes the physical migrations `arc-data-architect` designed (with tested `down()`s); `dat-cache-engineer` and `dat-etl-engineer` build the cache/sync layer this room's services call into.

`brd-cto` (Ingrid Voss) is accountable for the Gate 3–4 span at the Boardroom level. `bck-lead` is named the owner-room Lead in `gates.yaml`: she does not merge `06-frontend`'s or `07-mobile`'s worktrees — each Lead owns and merges its own — but she is the one who confirms all four rooms' worktrees are gate-merged (`sofi gate-merge --no-ff`, never before), runs the aggregate `sofi gate-check --gate 4`, and reports the Gate-4 status to `brd-ceo`/`brd-cto`. A room that isn't ready does not get folded into a green report on schedule pressure — `bck-lead` reports the specific room and gap.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `bck-lead` directly):

| From | What |
|---|---|
| `04-architecture` via `arc-lead` | The frozen Gate-3 bundle: `OpenAPI.yaml` (the contract every endpoint must byte-match), `Schema.sql`/ERD (the entities every service and model works against), `Integration_Plans.md` (the vendor specs `bck-integration-engineer` wires to), `Infra_Topology.md` (queue/broker/cache placement `bck-queue-engineer` wires against). Not frozen → reject upward, don't build against a moving contract. |
| `03-design` via `dsn-lead` (indirect, forwarded through `arc-lead`'s bundle) | `Prototype_Spec.md` (1:1 journey-stage mapping, every screen state) + `Content_Strings.json` — `bck-blade-engineer`'s only legitimate source for copy and states. |
| `09-security` via `sec-lead` | The signed `Threat_Model.md` — this room does not build an endpoint or a webhook handler that contradicts an unmitigated High risk in it. |
| `08-data` via `dat-lead` | Confirmation the physical migrations behind the frozen schema are executed and reversible before `bck-domain-engineer`'s services and `bck-api-engineer`'s models are written against them. |
| `00-boardroom` via `brd-cto` | Gate-4 accountability checks; occasional binding constraints (a scope cut, a schedule ceiling) that bear on sequencing across the four Gate-4 rooms. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior builds (a past idempotency miss, a past 302-instead-of-422 regression) before a specialist writes from a blank page. |
| `04-architecture` via `arc-review-architect` (cross-gate, addressed through `bck-lead`) | A `/sofi-spec-review` verdict on a feature this room has built far enough to inspect end-to-end — read-only, findings routed back through `bck-lead` to `/sofi-fix`. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `10-quality` via `qa-lead` | The merged `prj/<PRJ>` backend build — endpoints, services, Blade views, jobs, integrations — every diff already passed `bck-code-reviewer`, ready for `qa-automation-engineer`'s coverage pass and `qa-manual-explorer`'s edge probing. |
| `09-security` via `sec-lead` | The merged build's auth/webhook/admin surfaces for `sec-appsec-engineer`'s secure-code review and `sec-pentester`'s reproduction pass at Gate 5. |
| `06-frontend` via `fnt-lead` | Confirmation the live endpoint surface byte-matches `OpenAPI.yaml` — the contract `fnt-vue-engineer`/`fnt-react-engineer` build their service layer against; any drift bounces to `bck-api-engineer`, never silently absorbed by the client. |
| `07-mobile` via `mob-lead` | Same byte-parity confirmation for `mob-flutter-engineer`'s typed `ApiException` mapping. |
| `08-data` via `dat-lead` | Real read/write patterns from the built services — feedback `dat-cache-engineer` uses to validate the invalidation design against actual traffic shape, not a hypothetical one. |
| `00-boardroom` via `brd-ceo` (report) / `brd-cto` (accountability check) | The room's signed contribution to the Gate-4 exit: merged worktree, contract byte-parity confirmation, all-states confirmation for every Blade view, code-reviewer sign-off on every diff. |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for any expensive-to-reverse implementation call (a queue/broker choice, a refactor that touched a shared service); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket once the room's Gate-4 exit ticket carries its evidence block. |

## Room bar (what `bck-lead` blocks on)

- No worktree merge without `sofi gate-merge --no-ff` at gate close — never mid-build, never to save a step under schedule pressure.
- No endpoint merges without byte-parity against `OpenAPI.yaml` — a response shape that "almost" matches the contract is a defect, not a detail (Teaching I; `bck-api-engineer`'s bar).
- No error path returns a bare redirect — every validation failure is a structured `422`-class JSON body the client can render specifically (steel rule 1; mechanically checked, not assumed).
- No business logic or money math left inside a controller — `bck-domain-engineer`'s services own it, and every money-math path holds buy ≥ sell / spread ≠ margin / true-scale precision, checked before merge (steel rule 5).
- No Blade view merges missing a state — empty, loading, and error are as mandatory as the happy path, and no copy is hardcoded outside `Content_Strings.json` (`bck-blade-engineer`'s bar).
- No job merges without an idempotency key, a bounded retry with backoff, and a dead-letter path — "what happens if this runs twice" is answered before the code is, not after an incident (`bck-queue-engineer`'s bar).
- No integration field or webhook payload shape merges that wasn't read from the vendor's own current spec, cited with a fetch date — a guessed field is a rejected wire (`bck-integration-engineer`'s bar).
- No refactor merges without a characterization test proving behavior is unchanged — "cleaner" that also changes behavior is a silent regression, not a paydown (`bck-refactoring-surgeon`'s bar).
- No diff leaves the room without `bck-code-reviewer`'s fresh-context pass — the implementer's own self-report is never sufficient (Article 03 V2); a reviewer who has read the implementer's reasoning first is disqualified from that review.
- No specialist inside the room bypasses `bck-lead` to reach another room's Lead directly — every cross-room artifact leaves through the gateway, forwarded verbatim, never re-authored.

## Playbook index

- `playbooks/gate-4-build-procedure.md` — the room's core procedure: frozen Gate-3 bundle → worktree → fan-out across the seven specialists → in-room fresh-context review → gate-merge → signed Gate-4 contribution, with real `sofi` commands end to end, coordinated alongside the `06-frontend`/`07-mobile`/`08-data` squad.
- `playbooks/idempotent-job-design.md` — `bck-queue-engineer`'s sharpest recurring job and the room's other standing procedure: designing a background job, event, or webhook handler that survives running twice, arriving late, or never arriving — the discipline the whole async surface of the room leans on.

## Tools index

See `tools/README.md`. Headline: `company/os/toolkit/core/sofi_verify.py` (mechanical `php -l` / `artisan view:cache` / lint gate every merge passes through), `company/os/toolkit/gate/migration_check.py` (readable here for the "reversible migration" cross-check against `08-data`'s physical build), `company/os/toolkit/uiux/uiux_pipeline.py` (the `gate` mode `bck-blade-engineer` runs before a view is called done — blade compile, cache, lint), `company/os/toolkit/core/sofi_scan.py` (modes `search`/`wiring`/`security` for locating an endpoint, a route↔controller↔view seam, or an OWASP static pre-flag before `bck-code-reviewer`'s pass), `company/os/toolkit/core/feature_scan.py` + `spec_review_preflight.py` (the Phase-1 scan behind any `/sofi-spec-review` this room's work triggers).

## Skills index

See `skills/README.md`. Headline: `/sofi-gate` (the Gate-4 exit decision `bck-lead` runs as owner room), plus `/sofi-boot`, `/sofi-delegate`, `/sofi-handoff` for the room's own build cycle, `/sofi-audit` and `/sofi-fix` for the mechanical sweep-then-repair loop every specialist runs before handing a diff to `bck-code-reviewer`, and `/sofi-team`/`/sofi-report` for picking a downstream specialist or writing the Gate-4 findings up for the brain.

## Escalation path

`specialist → bck-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain). Inside the room:

- A specialist's implementation contradicts the frozen contract (e.g. `bck-domain-engineer`'s service returns a shape `bck-api-engineer`'s Resource can't map cleanly to `OpenAPI.yaml`) → `bck-lead` mediates first, one round, citing both `file:line` positions; unresolved after that round → `gtw-conflict-resolver`.
- An endpoint, job, or view has no home in the frozen bundle after a specialist's pass (a screen state the prototype specifies but no Blade partial covers) → `bck-lead` rejects the gap to Backlog and reports it, rather than inventing a state to cover it (Teaching I).
- `bck-refactoring-surgeon`'s characterization test can't be made to pass against the pre-refactor behavior after one correction round → `bck-lead` blocks the merge and escalates to `arc-review-architect` for a spec-review read if the ambiguity is in the original spec, not the refactor.
- `bck-integration-engineer` cannot obtain or confirm a vendor's real field spec → the wiring ships flagged `[unverified]`, never a guessed field, and `bck-lead` escalates the gap to `brd-cto` if it blocks the merge.
- `bck-code-reviewer` returns a 🔴 finding twice on the same diff after correction → third attempt trips the circuit breaker (Article 00 §Escalation); `bck-lead` halts the merge and escalates rather than accepting a third self-graded pass.
- The `Threat_Model.md` from `sec-lead` carries an unmitigated High risk touching this room's surface → immediate escalation to `sec-lead`/`brd-cso` via `bck-lead`; nothing merges around an open security gap, regardless of schedule pressure.
- A dispute above `gtw-conflict-resolver`'s mediation authority, or a cross-room timing conflict with `fnt-lead`/`mob-lead`/`dat-lead` that the four Leads can't resolve directly → `brd-arbiter`, one-line ADR, `bck-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
