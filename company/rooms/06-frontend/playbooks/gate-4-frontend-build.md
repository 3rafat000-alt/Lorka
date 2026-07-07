# Playbook — Gate 4 Frontend Build

> Owner: `fnt-lead` (drafting: `fnt-vue-engineer`/`fnt-react-engineer`, `fnt-css-artisan`, `fnt-interaction-engineer`, `fnt-a11y-engineer`, `fnt-performance-engineer`, `fnt-code-reviewer`; squad partners `bck-lead` and `mob-lead` in `05-backend`/`07-mobile`). The room's core recurring procedure — frozen bundle → framework pick → component build → styling/motion → a11y/performance hardening → fresh-context review → signed Gate-4 merge, run as one of three parallel squads behind one frozen input.

## When to run this

Every time `04-architecture` tags Gate 3 (`<PRJ>-gate3-done`) and the bundle — `OpenAPI.yaml` + `Tech_Stack.md` + `Threat_Model.md` — is frozen. This room also needs the frozen Gate-2 record (`Prototype_Spec.md` + `Content_Strings.json` + `Design_Tokens.md` + `A11y_Matrix.md`), already committed in `docs/` since Gate 2 closed.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open Gate-4 frontend ticket) → `CONTEXT.md`. Confirm `head_sha` matches the tree's HEAD before touching anything.

### 2. Confirm Gate 3 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 3
```
If this fails: **reject upward** to `arc-lead` with the specific missing bundle artifact named (usually an unfrozen `OpenAPI.yaml` or a missing `Threat_Model.md` signature), stop. Do not build against an unfrozen contract (Teaching II).

### 3. Fan out the three-squad worktree wave behind the frozen bundle
```bash
sofi squad PRJ-XXXX 4
sofi worktree PRJ-XXXX 4 frontend
```
`05-backend`, `06-frontend`, `07-mobile` all read the *same* frozen `OpenAPI.yaml`/`Tech_Stack.md`/`Threat_Model.md` — none waits on another squad's output to start (`effort_scaling.cross-room`). Claim shared paths first if `src/frontend/` already has conflicting file names from a prior pass:
```bash
sofi claim PRJ-XXXX src/frontend/components/**  --agent fnt-lead
```

### 4. `fnt-lead` picks the framework and dispatches the matching component engineer
```bash
grep -i "frontend framework" projects/PRJ-XXXX/docs/PRJ-XXXX_Tech_Stack.md
sofi dispatch PRJ-XXXX --agent fnt-vue-engineer      # if Tech_Stack.md names Vue
# or
sofi dispatch PRJ-XXXX --agent fnt-react-engineer    # if Tech_Stack.md names React
```
Never dispatch both — the frozen stack decision is exclusive. Everything else in the room leans on the resulting component skeleton.

### 5. Fan out styling and motion behind the component skeleton
```bash
sofi dispatch PRJ-XXXX --agent fnt-css-artisan
sofi dispatch PRJ-XXXX --agent fnt-interaction-engineer
```
`fnt-css-artisan` styles from `Design_Tokens.md` once the skeleton exists; `fnt-interaction-engineer` layers motion once styling has landed enough to know what's actually animating. Both check in with `fnt-lead` before finalizing anything that would fail an a11y criterion.

### 6. Run the a11y + performance hardening pass
```bash
sofi dispatch PRJ-XXXX --agent fnt-a11y-engineer
sofi dispatch PRJ-XXXX --agent fnt-performance-engineer
```
Both run against the assembled diff — see `playbooks/a11y-performance-hardening.md` for the detailed procedure. `fnt-lead` will not send anything to review with an open finding from either.

### 7. `fnt-lead` gate-checks every draft
For each specialist's artifact: does it cite `file:line` back to the frozen contract or prototype it derives from? Are all three states (empty/loading/error) built? Does every fetch have a handled error branch? Is every style value sourced from a token? Does every interaction have a working reduced-motion fallback? One rejection round per gap, named specifically — never a vague "needs work."

### 8. Fresh-context adversarial review (never self-graded)
```bash
sofi dispatch PRJ-XXXX --agent fnt-code-reviewer
```
`fnt-code-reviewer` sees only the diff + the ORIGINAL frozen `OpenAPI.yaml`/`Prototype_Spec.md`/`A11y_Matrix.md` — never the implementer's own reasoning. PASS/FAIL/UNKNOWN; UNKNOWN escalates, it never defaults to PASS. A FAIL routes back to the owning specialist through `fnt-lead`, attempt-counted toward the circuit breaker.

### 9. Confirm the squad partners are tracking
```bash
sofi gate-check PRJ-XXXX --gate 4 --room 05-backend
sofi gate-check PRJ-XXXX --gate 4 --room 07-mobile
```
`fnt-lead` doesn't block its own merge on the other squads finishing — each squad merges its own worktree independently — but flags a contract drift immediately if `05-backend`'s markup structure has changed underneath this room's mounting points.

### 10. Mechanical gate-check
```bash
sofi gate-check PRJ-XXXX --gate 4 --room 06-frontend
```
Confirms: `src/frontend/**` + tests exist; OpenAPI byte-parity; all three states built; `fnt-code-reviewer`'s PASS verdict attached; a11y audit and perf baseline both clean. Fails → the specific missing artifact is filed as a blocker in `HANDOFFS.md`, this room's slice stays open.

### 11. Gate-merge the worktree
```bash
sofi gate-merge PRJ-XXXX 4 frontend
```
Only after step 8's PASS and step 10's clean mechanical check — never before, never with a manual fast-forward that skips `--no-ff`.

### 12. Record + tag + hand off
```bash
sofi checkpoint PRJ-XXXX "feat(frontend): merge Gate-4 frontend build — components, styling, motion, a11y, perf"
```
Append `CONTEXT.md` (+ `DECISIONS.md` for the Vue/React confirmation and any irreversible state-management call), update `STATE.md` `head_sha`, and write the next ticket in `HANDOFFS.md` addressed to `bck-lead` (who owns the aggregate Gate-4 close once all three squads land) and to `qa-lead` for Gate 5. Report status to `brd-ceo`/`brd-cto`. `/sofi-handoff` runs this whole step. `bck-lead` runs `sofi gate-tag PRJ-XXXX 4` once all three squads have merged — this room does not tag Gate 4 alone.

## Self-check before closing this room's slice

1. Was exactly one of `fnt-vue-engineer`/`fnt-react-engineer` dispatched, matching `Tech_Stack.md`?
2. Does every screen this room touched have all three states (empty/loading/error) built per the frozen prototype?
3. Does every network call have a typed, handled error branch — zero silent catches?
4. Is `docs/PRJ-XXXX_Frontend_A11y_Audit.md` clean, zero unresolved criteria?
5. Is `docs/PRJ-XXXX_Frontend_Perf_Baseline.md` clean, zero CWV or bundle-budget regression?
6. Did `fnt-code-reviewer` return PASS, on the ORIGINAL frozen criteria, before `sofi gate-merge` ran?

## Rules

- No specialist inside the room reaches `bck-lead`/`mob-lead`/`dsn-lead`/`arc-lead` directly — everything routes through `fnt-lead`.
- The three-squad worktree wave (`05-backend`/`06-frontend`/`07-mobile`) fans out only because all three read the *same* frozen bundle independently — never fan out sequential phases of one ticket.
- `fnt-lead` never gate-merges around an open a11y or performance finding, regardless of schedule pressure — both are hard gates, not formalities.
- Pairs with `/sofi-gate` (wraps steps 10-11) and `/sofi-handoff` (wraps step 12).
