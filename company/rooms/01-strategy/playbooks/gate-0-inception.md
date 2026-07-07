# Playbook — Gate 0 Inception

> Owner: `str-lead` (drafting: `str-product-strategist`, `str-business-analyst`, `str-market-analyst`, `str-roadmap-planner`, `str-risk-analyst`, `str-monetization-strategist`). The room's core recurring procedure — raw idea → Blueprint + Problem Statement + Risk Register + declared track → signed Gate-0 exit ticket.

## When to run this

Every time a raw idea reaches `01-strategy` as a Work Order — the first thing that happens to any new `PRJ-XXXX` before a single downstream room touches it.

## Steps

### 1. Scaffold the project (if it doesn't exist yet)
```bash
bash company/os/bin/new-project.sh PRJ-XXXX "project title" PRIORITY <date>
```
This creates `projects/PRJ-XXXX/` (brain scaffolded: `STATE.md`/`CONTEXT.md`/`DECISIONS.md`/`HANDOFFS.md`), the `prj/PRJ-XXXX` branch, and auto-runs `sofi domain register` for `<slug>.local` — never a bare `127.0.0.1:PORT`. Confirm the domain landed:
```bash
sofi domain list | grep PRJ-XXXX
```

### 2. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open ticket) → `CONTEXT.md`. If this is genuinely a fresh project, these files exist but are near-empty — that's expected, not a blocker.

### 3. `str-lead` assigns the Problem Statement
```bash
sofi dispatch PRJ-XXXX --agent str-product-strategist --intent "<raw idea, verbatim>"
```
`str-product-strategist` reads the raw idea, researches the market only if it sharpens the problem (cites every fact), and writes `docs/PRJ-XXXX_Problem_Statement.md` — problem, user, top-3 JTBD, goals + metrics, constraints/assumptions, scope boundary, 5 deep questions. If the idea genuinely won't bound into a problem, `str-lead` rejects upward to `brd-chief-of-staff` here — stop, don't force a shape onto nothing.

### 4. Fan out the room's specialists behind the frozen Problem Statement
Once the Problem Statement is frozen, `str-lead` dispatches the remaining five specialists — each reads the same frozen artifact, none waits on another except where noted:
```bash
sofi dispatch PRJ-XXXX --agent str-business-analyst    # requirements + acceptance criteria
sofi dispatch PRJ-XXXX --agent str-market-analyst       # sizing + positioning + trend
sofi dispatch PRJ-XXXX --agent str-risk-analyst          # risk register + kill criteria
```
`str-monetization-strategist` runs after `str-market-analyst` lands (needs the Market Brief for pricing context); `str-roadmap-planner` runs last, after Requirements *and* the Risk Register both land (sequencing needs both):
```bash
sofi dispatch PRJ-XXXX --agent str-monetization-strategist
sofi dispatch PRJ-XXXX --agent str-roadmap-planner
```

### 5. `str-lead` gate-checks every draft
For each specialist's artifact: does it cite `file:line` back to the frozen Problem Statement? Does every goal carry a measurable metric? Does every requirement carry a testable acceptance criterion? Does every risk carry a named kill criterion? Does the roadmap tag every milestone with its track? One rejection round per gap, named specifically — never a vague "needs work."

### 6. Assemble the Blueprint and declare the track
`str-lead` assembles `docs/PRJ-XXXX_Blueprint.md` (using `company/templates/project-blueprint.template.md` as the frozen shape) from the Problem Statement + business goals, and confirms the track `str-roadmap-planner` declared — `fast_track` or `deep_audit`. Any doubt resolves to `deep_audit`. If any risk touches money/credentials/auth/PII, forward the Deep-Audit trigger:
```bash
sofi dispatch PRJ-XXXX --agent sec-lead --intent "Deep-Audit trigger: <named risk, file:line>"
```

### 7. Mechanical gate-check
```bash
sofi gate-check PRJ-XXXX --gate 0
```
Confirms: `docs/PRJ-XXXX_Blueprint.md`, `docs/PRJ-XXXX_Problem_Statement.md`, `docs/PRJ-XXXX_Risk_Register.md` all exist with evidence blocks; `<slug>.local` listed in `STATE.md`; track declared. Fails → the specific missing artifact is filed as a blocker in `HANDOFFS.md`, gate stays at 0.

### 8. Adversarial verify (never self-graded)
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 0
```
`gtw-gatekeeper` sees only the three artifacts + the ORIGINAL Gate-0 exit bar (`company/nexus/gates.yaml`) — never `str-lead`'s own reasoning. PASS/FAIL/UNKNOWN; UNKNOWN escalates, it never defaults to PASS.

### 9. Record + tag + hand off
```bash
sofi checkpoint PRJ-XXXX "feat(strategy): freeze Gate-0 bundle — blueprint, problem statement, risk register, track"
sofi gate-tag PRJ-XXXX 0
```
Append `CONTEXT.md` (+ `DECISIONS.md` if the track call was itself irreversible), update `STATE.md` `head_sha`, and write the next ticket in `HANDOFFS.md` addressed to `res-lead` for Gate 1. `/sofi-handoff` runs this whole step.

## Self-check before closing the gate

1. Are all 5 deep questions answered, or explicitly flagged pending for the human — never invented?
2. Does every business goal carry a measurable metric?
3. Does every requirement carry a testable acceptance criterion, and every risk a named kill criterion?
4. Is the track explicitly declared, defaulting to `deep_audit` on any doubt?
5. Is `<slug>.local` live and listed in `STATE.md`?

## Rules

- No specialist inside the room reaches `res-lead` or any other room's Lead directly — everything routes through `str-lead`.
- Never fan out sequential phases of one ticket; the specialists above fan out only because they read the same frozen Problem Statement independently, not because the work is chopped mid-thought.
- Pairs with `/sofi-gate` (wraps steps 7-8) and `/sofi-handoff` (wraps step 9).
