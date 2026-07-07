# Playbook — Gate-4 Build Procedure (Gate 4)

> Owner: `bck-lead` (Elif Kaya). The room's core recurring procedure — orient → confirm Gate 3 → worktree → fan out → in-room review → gate-merge → aggregate report — run once per project's Gate-4 pass, alongside `06-frontend`, `07-mobile`, and `08-data`'s own parallel builds behind the same frozen bundle, and again on any loop-back from `10-quality`'s coverage findings or `04-architecture`'s `arc-review-architect` `/sofi-spec-review` results.

## When to run this

Whenever `04-architecture` tags Gate 3 (`<PRJ>-gate3-done`) and `arc-lead`'s bundle is frozen, or whenever a Gate-5 loop-back names a specific backend gap that needs a fresh build ticket.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (note `branch` + `head_sha`) → `HANDOFFS.md` (my open Gate-4 ticket) → `CONTEXT.md`. Confirm `head_sha` matches the tree's HEAD before touching anything.

### 2. Confirm Gate 3 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 3
```
If this fails: **reject upward** to `arc-lead` with the specific missing artifact named (usually an unfrozen `OpenAPI.yaml` or an unsigned `Threat_Model.md`), stop. Do not build against a moving contract (Teaching II).

### 3. Open the room's worktree
```bash
sofi worktree PRJ-XXXX 4 backend    # creates worktrees/PRJ-XXXX-gate4-backend off prj/PRJ-XXXX
```
Export per-worktree build caches before anything builds (parallel squads sharing one physical root corrupt each other's `vendor/`/npm/composer caches):
```bash
export COMPOSER_CACHE_DIR="${PWD}/.composer_cache"
```
Claim any shared path before editing it:
```bash
sofi claim PRJ-XXXX "database/migrations/*"   # example — any path another room or specialist might also touch
```

### 4. Fan out the build work (mostly parallel, one pairing runs slightly staggered)
```bash
sofi dispatch PRJ-XXXX --agent bck-api-engineer --ticket TKT-NNN        # endpoint surface — needs domain interfaces, so hands off tightly with the next line
sofi dispatch PRJ-XXXX --agent bck-domain-engineer --ticket TKT-NNN     # services + money math — run first or in tight lockstep with the API engineer
sofi dispatch PRJ-XXXX --agent bck-blade-engineer --ticket TKT-NNN      # Blade views — needs entities/endpoints stable, runs slightly behind
```
Queue, integration, and refactoring run in parallel behind the same bundle once the domain interfaces exist:
```bash
sofi dispatch PRJ-XXXX --agent bck-queue-engineer --ticket TKT-NNN         # jobs/events/websockets
sofi dispatch PRJ-XXXX --agent bck-integration-engineer --ticket TKT-NNN   # third-party wiring
sofi dispatch PRJ-XXXX --agent bck-refactoring-surgeon --ticket TKT-NNN    # only where a specialist's draft surfaces debt worth paying down now
```

### 5. Mechanical checks before any diff is called ready
```bash
python3 company/os/agents/ceo/sofi_verify.py --prj PRJ-XXXX --only lint,view
python3 company/os/agents/ceo/sofi_scan.py wiring "" --prj PRJ-XXXX --md
python3 company/os/agents/ceo/sofi_scan.py security "" --prj PRJ-XXXX --md
python3 company/os/agents/uiux/uiux_pipeline.py gate --prj PRJ-XXXX --query <blade-scope>
```
Each specialist runs these on their own diff before handing it up; `bck-lead` re-confirms before routing to review. A failing exit code stops the pipeline — fix before proceeding, never route a red diff to review "to save a step."

### 6. Mandatory fresh-context review (in-room V2, before ANY merge eligibility)
```bash
sofi dispatch PRJ-XXXX --agent bck-code-reviewer --ticket TKT-NNN --target "<diff>"
```
`bck-code-reviewer` sees only the diff and the ticket's ORIGINAL criteria — never the implementer's reasoning. A PASS makes the diff merge-eligible; a BLOCK returns to the originating specialist with the SEV report attached, attempt-counted toward the circuit breaker; an UNKNOWN routes back to `bck-lead` for more evidence, never a default approval.

### 7. Gate-merge at close — never mid-build
```bash
sofi gate-merge PRJ-XXXX 4 backend    # --no-ff into prj/PRJ-XXXX, deletes the worktree
```
This is the ONE integration point for the room's whole Gate-4 pass. A specialist's individually-reviewed diff still waits for this step — merging piecemeal mid-build defeats the worktree isolation the whole squad depends on.

### 8. Coordinate the aggregate Gate-4 status (owner-room duty)
Confirm — don't assume — `06-frontend`, `07-mobile`, and `08-data` have each gate-merged their own worktrees:
```bash
sofi gate-check PRJ-XXXX --gate 4
```
This mechanical pass (V1) confirms all four rooms' artifacts exist with evidence blocks. If any room isn't ready, `bck-lead` reports the specific room and gap to `brd-ceo`/`brd-cto` — never folds an unready room into a convenient green report.

### 9. Sign, hand off, tag — the Gate-4 close
```bash
sofi checkpoint PRJ-XXXX "feat(backend): merge Gate-4 build — endpoints, services, views, jobs, integrations"
sofi gate-tag PRJ-XXXX 4
sofi dispatch PRJ-XXXX --agent qa-lead --ticket TKT-NNN+1 --intent "Gate-5 kickoff on merged build"
```
Append `CONTEXT.md` (+ `DECISIONS.md` if the build involved an irreversible implementation call — a broker choice, a large refactor), update `STATE.md` `head_sha`, write the next ticket in `HANDOFFS.md` addressed to `qa-lead`. Report the Gate-4 status to `brd-ceo`/`brd-cto`. `/sofi-handoff` runs this whole step.

## Self-check before closing the gate

1. Did every diff that merged carry `bck-code-reviewer`'s sign-off — never a self-graded pass?
2. Does the live endpoint surface actually byte-match `OpenAPI.yaml`, checked mechanically, not assumed from a careful read?
3. Does every Blade view carry all three states (empty/loading/error), not just the happy path?
4. Is every job's idempotency actually tested (a "runs twice" test present and green), not just designed on paper?
5. Was the aggregate `sofi gate-check --gate 4` run against all four Gate-4 rooms, and was any unready room reported by name rather than smoothed over?

## Rules

- No merge without `bck-code-reviewer`'s pass — a diff "too small to need review" is exactly the diff that slips a contract drift through.
- No gate-merge mid-build — the worktree exists precisely so parallel specialists can't collide; merging early defeats that isolation.
- `bck-lead` never reports the aggregate Gate-4 status green without actually running `sofi gate-check --gate 4` and confirming the other three rooms' worktrees are merged — a convenient assumption is not a confirmation.
- Pairs with `idempotent-job-design.md` (wraps step 4's queue-engineer dispatch), `/sofi-gate` (wraps step 8), and `/sofi-handoff` (wraps step 9).
