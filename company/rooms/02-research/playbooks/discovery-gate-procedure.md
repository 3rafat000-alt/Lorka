# Playbook — Discovery Gate Procedure (Gate 1)

> Owner: `res-lead` (Hiroshi Tanaka). The room's core recurring procedure — orient → fan out → journey map → fact-check → freeze → handoff — run once per project's Gate-1 pass, and again on any loop-back from `12-observability` (Gate 8 → Gate 1 re-open).

## When to run this

Whenever `01-strategy` tags Gate 0 (`<PRJ>-gate0-done`) and the `Problem_Statement.md` is frozen, or whenever `obs-insights-analyst` re-opens Discovery on an existing project after a Gate-8 SLO breach.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (note `branch` + `head_sha`) → `HANDOFFS.md` (my open Gate-1 ticket) → `CONTEXT.md`. Confirm `head_sha` matches the tree's HEAD before touching anything.

### 2. Confirm Gate 0 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 0
```
If this fails: **reject upward** to `str-lead` with the specific missing artifact named (usually a thin or unanswered `Problem_Statement.md`), stop. Do not research against an unbounded problem (Teaching II).

### 3. Fan out the research (parallel, behind the frozen Problem Statement)
```bash
sofi dispatch PRJ-XXXX --agent res-ux-researcher --ticket TKT-NNN
sofi dispatch PRJ-XXXX --agent res-data-researcher --ticket TKT-NNN   # if telemetry/survey grounding is available
sofi dispatch PRJ-XXXX --agent res-competitor-analyst --ticket TKT-NNN  # only if market-facing
```
`res-ux-researcher` produces personas + pain/gain first — the other two consume her draft, so they run slightly behind, not fully parallel to her. Any of the three may request `res-web-scout` for a bounded search:
```bash
sofi dispatch PRJ-XXXX --agent res-web-scout --ticket TKT-NNN-scout --intent "<bounded question>"
```

### 4. Journey mapping (gatekeeper tier, after personas exist)
```bash
sofi dispatch PRJ-XXXX --agent res-journey-architect --ticket TKT-NNN
```
`res-journey-architect` consumes the frozen personas, not a draft — confirm `res-ux-researcher`'s ticket is `done` with an evidence block before dispatching this one.

### 5. Adversarial fact-check pass (mandatory on every artifact)
```bash
sofi dispatch PRJ-XXXX --agent res-fact-checker --ticket TKT-NNN --target Personas.md
sofi dispatch PRJ-XXXX --agent res-fact-checker --ticket TKT-NNN --target Journey_Map.md
sofi dispatch PRJ-XXXX --agent res-fact-checker --ticket TKT-NNN --target Competitor_Teardown.md   # if produced
```
Each pass returns a claim-by-claim CONFIRMED/CONTRADICTED/UNKNOWN table. Any CONTRADICTED goes back to the producing specialist for a fix — do not proceed with a known-wrong claim. Any UNKNOWN must appear, visibly flagged, in the final artifact — never silently dropped and never silently kept as if confirmed.

### 6. Room-level evidence audit (res-lead, before signing)
Walk the fact-checker's tables personally:
- Every persona has a JTBD + at least one CONFIRMED or explicitly-flagged trait.
- Every journey stage has emotion + friction, friction table ranked by pain × frequency.
- No CONTRADICTED claim remains unresolved.
- Every UNKNOWN is visible in the artifact text, not buried in a footnote.

### 7. Gate-check + adversarial verdict
```bash
sofi gate-check PRJ-XXXX --gate 1
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 1
```
Mechanical pass (V1) confirms artifacts exist with evidence blocks. The adversarial layer (V2), `gtw-gatekeeper`, sees only the diff + the ORIGINAL Gate-1 exit bar (`company/nexus/gates.yaml`) — never `res-lead`'s self-report. UNKNOWN is a valid verdict here too; it escalates, it does not default to PASS.

### 8. Sign, hand off, tag
```bash
sofi checkpoint PRJ-XXXX "feat(research): freeze Gate-1 Discovery bundle"
sofi gate-tag PRJ-XXXX 1
sofi dispatch PRJ-XXXX --agent dsn-lead --ticket TKT-NNN+1 --intent "Gate-2 kickoff on frozen Journey Map"
```
Append `CONTEXT.md` (+ `DECISIONS.md` if the freeze involved an irreversible scoping call), update `STATE.md` `head_sha`, write the next ticket in `HANDOFFS.md` addressed to `dsn-lead`. Report the Gate-1 status to `brd-cpo`. `/sofi-handoff` runs this whole step.

## Self-check before closing the gate

1. Did every claim in every Gate-1 artifact pass through `res-fact-checker`?
2. Is every UNKNOWN claim visible in the shipped artifact, not silently dropped or silently trusted?
3. Does every journey stage have both an emotion and a friction entry, including unhappy paths?
4. Is the freeze evidence block citing real sources, not self-report ("I did the research" is not evidence)?
5. Was the mechanical gate-check AND the `gtw-gatekeeper` adversarial verdict both run — never one substituting for the other?

## Rules

- Read-only steps (orient, gate-check, audit) never write to the project tree. The freeze itself is exactly one checkpoint.
- `res-competitor-analyst` runs only when the project is market-facing — don't force a teardown on an internal tool.
- Never skip the fact-checker pass to save a turn under deadline pressure — a rejected draft with a named gap is cheaper for the company than a freeze that has to be reopened at Gate 3 or later.
- Pairs with `/sofi-gate` (wraps step 7) and `/sofi-handoff` (wraps step 8).
