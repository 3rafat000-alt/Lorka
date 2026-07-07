# Playbook — Gate 3-4 Data Layer

> Owner: `dat-lead` (drafting: `dat-db-engineer`, `dat-privacy-officer` at Gate 3; `dat-db-engineer`, `dat-cache-engineer`, `dat-etl-engineer`, and `dat-analytics-engineer`/`dat-ml-engineer` when scoped, at Gate 4). The room's core recurring procedure — a two-posture pass, since `08-data` owns no gate outright: at Gate 3 it runs as a **squad partner** to `04-architecture`/`09-security` behind the same frozen prototype; at Gate 4 it runs as a **support room** behind `05-backend`'s owner-room build window.

## When to run this

**Gate 3 leg:** every time `03-design` tags Gate 2 and `arc-lead` fans out the three-room squad (`sofi squad <PRJ> 3`) — `08-data` reads the same frozen prototype `04-architecture` and `09-security` do.
**Gate 4 leg:** every time `arc-lead` freezes the Gate-3 bundle and `bck-lead` opens the Build window — `08-data` picks up support work behind the same frozen bundle.

## Steps — Gate 3 leg

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open Gate-3 ticket addressed to `dat-lead`) → `CONTEXT.md`.

### 2. Confirm the squad is actually fanned out
```bash
sofi gate-check PRJ-XXXX --gate 2
```
If Gate 2 isn't closed, `dat-lead` has nothing to read yet — reject upward to `dsn-lead` via `arc-lead`, don't act on a partial prototype (Teaching II).

### 3. Read the frozen prototype and, once it lands, the schema design in progress
```bash
sofi dispatch PRJ-XXXX --agent dat-db-engineer --note "migration-validation feedback"
sofi dispatch PRJ-XXXX --agent dat-privacy-officer --note "PII_Map.md"
```
`dat-db-engineer` reads `arc-data-architect`'s in-progress/frozen schema design (via `arc-lead`) and gives index-cost and brownfield read-pattern feedback — she does not design the schema, only validates it against physical reality. `dat-privacy-officer` walks the frozen `Prototype_Spec.md`'s screens/forms and classifies every field that could be personal data, independent of the schema draft's timing.

### 4. `dat-lead` gate-checks both drafts
Does the migration-validation feedback cite specific `file:line` positions in the schema design? Does the `PII_Map.md` cover every screen/form field in the frozen prototype, with zero left unclassified? A gap in either bounces back with the exact missing piece named — never a vague "needs more detail."

### 5. Confirm no unmitigated High risk blocks the freeze
```bash
sofi gate-check PRJ-XXXX --gate 3 --room 09-security
```
`dat-lead` does not sign this room's Gate-3 contribution around an unmitigated High risk in `sec-lead`'s threat model that touches PII or the data layer — the freeze holds, escalate via the security spur if it does.

### 6. Hand the room's Gate-3 contribution to `arc-lead`
Migration-validation feedback flows into `arc-data-architect`'s final schema design; the signed `PII_Map.md` becomes part of the Gate-3 bundle `arc-lead` assembles. `dat-lead` does not assemble or sign the bundle itself — that stays `arc-lead`'s job; `dat-lead` signs this room's *contribution* to it.
```bash
sofi checkpoint PRJ-XXXX "feat(data): gate-3 contribution — migration-validation feedback + PII_Map"
```

## Steps — Gate 4 leg

### 7. Orient again — the bundle has frozen since step 1
```bash
sofi sync PRJ-XXXX
sofi gate-check PRJ-XXXX --gate 3
```
Confirm the Gate-3 bundle is actually frozen (`arc-lead`'s signature, `<PRJ>-gate3-done` tag) before executing anything against it — never build against a schema that might still move.

### 8. Claim shared paths, then execute migrations
```bash
sofi claim PRJ-XXXX database/migrations --agent dat-db-engineer
sofi dispatch PRJ-XXXX --agent dat-db-engineer --note "execute frozen migrations"
```
`dat-db-engineer` writes and runs the migrations from the now-final schema design, each paired with a tested `down()`, and runs the mechanical check:
```bash
python3 company/os/toolkit/tier-1-architecture/data-schema-engineer/migration_check.py database/migrations/
```
Exit `0` required before anything else in this leg proceeds — a non-reversible migration blocks the room's entire Gate-4 contribution, not just this one file.

### 9. Fan out cache and sync work once real service patterns exist
```bash
sofi dispatch PRJ-XXXX --agent dat-cache-engineer   # once bck-domain-engineer's services have real read patterns
sofi dispatch PRJ-XXXX --agent dat-etl-engineer     # if the scope includes any import/export/sync
```
`dat-cache-engineer` waits on real traffic shape from `05-backend` (via `bck-lead`) rather than designing against an assumed access pattern — dispatch slightly behind the backend's own fan-out. `dat-etl-engineer` can start as soon as `arc-integration-architect`'s frozen integration plans exist.

### 10. Fan out analytics/ML only when the ticket names that scope
```bash
sofi dispatch PRJ-XXXX --agent dat-analytics-engineer   # only if the project's frozen scope calls for event pipelines
sofi dispatch PRJ-XXXX --agent dat-ml-engineer           # only if the project's frozen scope calls for an ML/AI feature
```
Neither is a blocking member of every Gate-4 pass — `dat-lead` dispatches them only when `HANDOFFS.md`'s ticket explicitly names the scope; dispatching them on a project that doesn't need them is a token-economy defect (Teaching IV).

### 11. `dat-lead` gate-checks every draft
Every migration `migration_check.py`-clean? Every cache key names its invalidation trigger, stampede mechanism, and cold-start behavior? Every sync job has a passing "runs twice" test? Every analytics metric traces to a raw event, every ML feature to a passing eval against a stated baseline? One rejection round per gap, named specifically.

### 12. Mechanical gate-check (as part of the Gate-4 aggregate)
```bash
sofi gate-check PRJ-XXXX --gate 4 --room 08-data
```
Confirms this room's slice of the Gate-4 exit bar: migrations reversible, cache/sync/analytics/ML artifacts present with evidence where scoped in.

### 13. Adversarial verify (never self-graded)
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 4 --room 08-data
```
Sees only this room's diff/artifacts + the ORIGINAL Gate-4 exit bar (`company/nexus/gates.yaml`) — never `dat-lead`'s own reasoning. PASS/FAIL/UNKNOWN; UNKNOWN escalates.

### 14. Record + hand off to `bck-lead`
```bash
sofi checkpoint PRJ-XXXX "feat(data): gate-4 contribution — executed migrations, cache, sync"
```
Append `CONTEXT.md` (+ `DECISIONS.md` for any expensive-to-reverse call — a sharding decision, a retention-policy change), update `STATE.md` `head_sha`, and write the next ticket in `HANDOFFS.md` confirming to `bck-lead` that the physical data layer is ready for the services to build against. `bck-lead` — not `dat-lead` — runs the aggregate `sofi gate-check --gate 4` and the room's own worktree merge; `dat-lead` reports his room's slice as ready, he does not merge anyone else's worktree. `/sofi-handoff` runs this whole step.

## Self-check before closing either leg

1. Gate 3: does the `PII_Map.md` cover every screen/form field in the frozen prototype, zero left unclassified?
2. Gate 3: does the migration-validation feedback cite `file:line` against the schema design it reviews?
3. Gate 4: does every migration pass `migration_check.py`, exit `0`?
4. Gate 4: does every cache key have a named stampede mechanism, and every batch job a passing "runs twice" test?
5. Was the mechanical gate-check AND the `gtw-gatekeeper` adversarial verdict both run for each leg — never one substituting for the other?

## Rules

- No specialist inside the room reaches `arc-lead`, `bck-lead`, or `sec-lead` directly — everything routes through `dat-lead`.
- `dat-lead` signs this room's *contribution* at each gate; he does not sign the Gate-3 or Gate-4 exit itself — that stays `arc-lead`'s and `bck-lead`'s job respectively, as the named owner-room Leads in `gates.yaml`.
- `dat-analytics-engineer` and `dat-ml-engineer` are dispatched only when the ticket names their scope — dispatching them by default on every project wastes budget the room doesn't have (Teaching IV).
- Pairs with `/sofi-gate` (wraps steps 12-13, both legs) and `/sofi-handoff` (wraps step 14, and the Gate-3 leg's equivalent close).
