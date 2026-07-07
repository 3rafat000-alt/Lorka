# Playbook — Gate-2 Solution Design Procedure (Gate 2)

> Owner: `dsn-lead` (Daniel "Dan" Kim). The room's core recurring procedure — orient → fan out → integrate → a11y gate → freeze → handoff — run once per project's Gate-2 pass, and again on any loop-back from `12-observability` (Gate 8 → Gate 1 → Gate 2 re-open) or from `10-quality`'s `qa-design-auditor` flagging a built-vs-frozen fidelity gap.

## When to run this

Whenever `02-research` tags Gate 1 (`<PRJ>-gate1-done`) and `Journey_Map.md` is frozen, or whenever `obs-insights-analyst` re-opens Discovery-through-Design on an existing project after a Gate-8 SLO breach traced to a specific screen.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (note `branch` + `head_sha`) → `HANDOFFS.md` (my open Gate-2 ticket) → `CONTEXT.md`. Confirm `head_sha` matches the tree's HEAD before touching anything.

### 2. Confirm Gate 1 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 1
```
If this fails: **reject upward** to `res-lead` with the specific missing artifact named (usually a thin `Journey_Map.md` or an unresolved UNKNOWN claim), stop. Do not design against an unbounded journey (Teaching II).

### 3. Fan out the design work (mostly parallel, two must run in sequence)
```bash
sofi dispatch PRJ-XXXX --agent dsn-ux-architect --ticket TKT-NNN        # flows + IA — run first
sofi dispatch PRJ-XXXX --agent dsn-design-system --ticket TKT-NNN       # tokens + component library — parallel to ux-architect
sofi dispatch PRJ-XXXX --agent dsn-brand-designer --ticket TKT-NNN      # taste dials — needs the brief + emotional arc, can start immediately
```
`dsn-ui-designer` consumes `dsn-ux-architect`'s flow/IA and `dsn-design-system`'s token names, so she runs slightly behind, not fully parallel to either:
```bash
sofi dispatch PRJ-XXXX --agent dsn-ui-designer --ticket TKT-NNN
```
Once screens exist, dispatch the two specialists who consume them:
```bash
sofi dispatch PRJ-XXXX --agent dsn-content-strategist --ticket TKT-NNN  # final copy per screen/state
sofi dispatch PRJ-XXXX --agent dsn-motion-designer --ticket TKT-NNN     # motion spec per animated state
```

### 4. Accessibility gate (mandatory on the full bundle, not a spot-check)
```bash
sofi dispatch PRJ-XXXX --agent dsn-a11y-specialist --ticket TKT-NNN --target "screens+copy+dials+motion"
```
`dsn-a11y-specialist` consumes the finished screens, copy, taste-dial proposals, and motion spec together — not each piece in isolation — because narration order and focus order only make sense read as a whole flow. Any failing criterion returns to the producing specialist named by criterion, not a vague "fix accessibility." Re-run this step after every fix; do not treat a partial re-check as sufficient.

### 5. Room-level integration (dsn-lead, before signing)
Walk the bundle personally:
- Every screen in `Prototype_Spec.md` traces to a stage in `Journey_Map.md` — an orphan screen is deleted, not argued for.
- Every screen specifies all five states (empty/loading/error/offline/partial).
- `dsn-design-system`'s tokens are single-sourced — no duplicated component or divergent hex value survived `dsn-ui-designer`'s draft.
- `dsn-brand-designer`'s three dials and named brand preset are stated explicitly.
- `dsn-motion-designer`'s motion spec has a `prefers-reduced-motion` fallback for every animation.
- `dsn-a11y-specialist`'s matrix shows zero unresolved criteria.

### 6. Gate-check + adversarial verdict
```bash
sofi gate-check PRJ-XXXX --gate 2
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 2
```
Mechanical pass (V1) confirms all four artifacts exist with evidence blocks. The adversarial layer (V2), `gtw-gatekeeper`, sees only the diff + the ORIGINAL Gate-2 exit bar (`company/nexus/gates.yaml`) — never `dsn-lead`'s self-report. A matrix with even one unresolved criterion is a fail here, not a warning.

### 7. Sign, hand off, tag — THE FREEZE
```bash
sofi checkpoint PRJ-XXXX "feat(design): freeze Gate-2 Solution Design bundle"
sofi gate-tag PRJ-XXXX 2
sofi dispatch PRJ-XXXX --agent arc-lead --ticket TKT-NNN+1 --intent "Gate-3 kickoff on frozen Prototype Spec"
```
Append `CONTEXT.md` (+ `DECISIONS.md` if the freeze involved an irreversible taste or scope call), update `STATE.md` `head_sha`, write the next ticket in `HANDOFFS.md` addressed to `arc-lead`. Report the Gate-2 status to `brd-cpo`. `/sofi-handoff` runs this whole step. **After this checkpoint, the prototype IS truth** — no downstream room re-argues a frozen screen; a real problem with it goes through `dsn-lead` as a formal loop-back ticket, never a silent override.

## Self-check before closing the gate

1. Did every screen in the Prototype Spec trace to a real journey stage, with the orphan ones actually deleted rather than left in "for now"?
2. Does every screen specify all five states, not just the happy path?
3. Does `dsn-a11y-specialist`'s matrix show zero unresolved criteria — and was that verified against the whole bundle, not a partial re-check?
4. Are the taste dials and brand preset stated explicitly, with reasoning, not defaults left unexamined?
5. Was the mechanical gate-check AND the `gtw-gatekeeper` adversarial verdict both run — never one substituting for the other?

## Rules

- Read-only steps (orient, gate-check, integration walk) never write to the project tree. The freeze itself is exactly one checkpoint.
- `dsn-a11y-specialist`'s pass is never skipped and never partial — a taste-dial or motion change made after a fail requires a fresh full pass, not a spot-check of the one fixed item.
- Never skip the integration walk to save a turn under deadline pressure — a rejected bundle with a named gap is cheaper for the company than a freeze that has to be reopened at Gate 3 or later, after `arc-system-architect` has already built screen→component traceability against it.
- Pairs with `/sofi-design-taste` (wraps steps 3's brand-designer dispatch and step 4's a11y cross-check), `/sofi-gate` (wraps step 6), and `/sofi-handoff` (wraps step 7).
