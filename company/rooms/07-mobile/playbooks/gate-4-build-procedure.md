# Playbook — Gate-4 Build Procedure (Gate 4)

> Owner: `mob-lead` (João Silva). The room's core recurring procedure — orient → confirm Gate 3 → worktree → fan out → João's own review pass (or `gtw-gatekeeper` escalation) → gate-merge → readiness signal to `bck-lead` — run once per project's Gate-4 pass, alongside `05-backend`'s (owner room) and `06-frontend`'s own parallel builds behind the same frozen bundle, and again on any loop-back from `10-quality`'s coverage findings or `04-architecture`'s `arc-review-architect` `/sofi-spec-review` results.

## When to run this

Whenever `04-architecture` tags Gate 3 (`<PRJ>-gate3-done`) and `arc-lead`'s bundle is frozen, or whenever a Gate-5 loop-back names a specific mobile gap that needs a fresh build ticket.

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
sofi worktree PRJ-XXXX 4 mobile    # creates worktrees/PRJ-XXXX-gate4-mobile off prj/PRJ-XXXX
```
Export a per-worktree Pub cache before anything builds (parallel squads sharing one physical root corrupt each other's package caches):
```bash
export PUB_CACHE="${PWD}/.pub_cache"
```
Claim any shared path before editing it:
```bash
sofi claim PRJ-XXXX "lib/core/network/*"   # example — any path another specialist might also touch
```

### 4. Fan out the build work (mostly sequenced, some parallel)
```bash
sofi dispatch PRJ-XXXX --agent mob-flutter-engineer --ticket TKT-NNN     # layer skeleton + DI — runs first, everything else depends on it
sofi dispatch PRJ-XXXX --agent mob-state-engineer --ticket TKT-NNN       # Bloc/Cubit — needs stable repository interfaces, runs once mob-flutter-engineer's data layer lands
sofi dispatch PRJ-XXXX --agent mob-platform-engineer --ticket TKT-NNN    # ApiException hierarchy + platform channels — runs in parallel once the datasource layer exists
```
Once screens are actually built and worth measuring:
```bash
sofi dispatch PRJ-XXXX --agent mob-perf-profiler --ticket TKT-NNN        # jank/leak profiling — runs against built screens, not scaffolding
```
Last, once the build is otherwise merge-ready:
```bash
sofi dispatch PRJ-XXXX --agent mob-release-engineer --ticket TKT-NNN     # signing, versioning, channel submission
```

### 5. Mechanical checks before any diff is called ready
```bash
flutter analyze
flutter test
dart format --set-exit-if-changed lib/
python3 company/os/toolkit/core/sofi_verify.py --prj PRJ-XXXX --only lint
python3 company/os/toolkit/core/sofi_scan.py wiring "" --prj PRJ-XXXX --md
python3 company/os/toolkit/core/sofi_scan.py security "" --prj PRJ-XXXX --md
```
Each specialist runs these on their own diff before handing it up; `mob-lead` re-confirms before his own review pass. A failing exit code stops the pipeline — fix before proceeding, never route a red diff to review "to save a step."

### 6. Review — the room's own substitute for a dedicated in-room reviewer (before ANY merge eligibility)
`07-mobile` carries no dedicated `mob-code-reviewer` agent (a deliberate roster gap, named explicitly rather than silently skipped). `mob-lead` covers it himself:
```bash
sofi dispatch PRJ-XXXX --agent mob-lead --ticket TKT-NNN --intent "Review diff against ticket's original criteria: layer direction, explicit Bloc states, typed ApiException mapping, benchmark evidence"
```
For anything touching money, auth, or a native-code platform-channel bridge — where João's own closeness to the assignment makes him a weaker judge — escalate to a genuine fresh-context pass instead:
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --ticket TKT-NNN --target "<diff>"
```
A PASS makes the diff merge-eligible; a BLOCK returns to the originating specialist with the specific gap named, attempt-counted toward the circuit breaker; an UNKNOWN routes back for more evidence, never a default approval.

### 7. Gate-merge at close — never mid-build
```bash
sofi gate-merge PRJ-XXXX 4 mobile    # --no-ff into prj/PRJ-XXXX, deletes the worktree
```
This is the ONE integration point for the room's whole Gate-4 pass. A specialist's individually-reviewed diff still waits for this step — merging piecemeal mid-build defeats the worktree isolation the whole squad depends on.

### 8. Signal readiness to the owner room — never claim the aggregate yourself
`bck-lead` is the named owner room for Gate 4 and runs the aggregate `sofi gate-check --gate 4` across all squad rooms. `mob-lead`'s job here is honest reporting of his own room, not a self-graded aggregate claim:
```bash
sofi dispatch PRJ-XXXX --agent bck-lead --ticket TKT-NNN+1 --intent "07-mobile Gate-4 readiness: worktree merged, review evidence attached, gap: <name any, or 'none'>"
```

### 9. Sign, hand off, tag — the Gate-4 close
```bash
sofi checkpoint PRJ-XXXX "feat(mobile): merge Gate-4 build — layers, state, platform, benchmarks"
```
Append `CONTEXT.md` (+ `DECISIONS.md` if the build involved an irreversible implementation call — a state-management boundary, a platform-channel design touching native code), update `STATE.md` `head_sha`, write the next ticket in `HANDOFFS.md` addressed to `bck-lead`. `sofi gate-tag` and the actual Gate-4 close happen once `bck-lead` confirms all squad rooms are in. `/sofi-handoff` runs this whole step for the room's own contribution.

## Self-check before signaling readiness

1. Did every diff that merged carry my own review sign-off or `gtw-gatekeeper`'s — never a specialist's own self-graded pass?
2. Do the layer boundaries actually hold (domain never imports data/presentation types), checked mechanically via `flutter analyze` and an import grep, not assumed from a careful read?
3. Does every Bloc/Cubit carry all five states (initial/loading/success/error/empty), not just the happy path?
4. Does every network catch actually map to a typed `ApiException` subtype — checked with a grep for bare `catch (e)` blocks, not assumed?
5. Does every claimed performance fix carry a pasted before/after benchmark, not just a "feels smoother" note?

## Rules

- No merge without a review pass — João's own, or `gtw-gatekeeper`'s for anything contested. A diff "too small to need review" is exactly the diff that slips a layer violation through.
- No gate-merge mid-build — the worktree exists precisely so parallel specialists can't collide; merging early defeats that isolation.
- `mob-lead` never signals readiness to `bck-lead` without actually confirming his own room's diffs are reviewed and evidence-backed — a convenient assumption is not a confirmation.
- Pairs with `typed-network-exception-design.md` (wraps step 4's platform-engineer dispatch), `/sofi-gate` (wraps step 8), and `/sofi-handoff` (wraps step 9).
