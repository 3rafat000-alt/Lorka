# Playbook — Gate Lifecycle Orchestration

> Owner: `brd-ceo` (drafting support: `brd-chief-of-staff`). The Boardroom's core recurring procedure — orient, gate-check, route, delegate, oracle, record — run every turn on every live project.

## When to run this

Every `brd-ceo` turn, on every live `PRJ-XXXX`. This is not a special-occasion procedure; it is the operating loop itself (Article 00 realized in commands).

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX               # orient: git status, remote diff, never blind
git -C projects/PRJ-XXXX log --oneline -8   # what the last session/squad actually did
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (note `branch` + `head_sha`) → `HANDOFFS.md` (open tickets) → `CONTEXT.md` (facts so far). If `head_sha` in `STATE.md` doesn't match the tree's HEAD, reconcile before touching anything.

### 2. Gate-check — confirm the prior gate actually closed
```bash
sofi gate-check PRJ-XXXX --gate N
```
Mechanical pass (V1): artifacts exist at expected paths, evidence blocks present, no boundary violations. If it fails: **reject upward** — write the specific missing artifact as a blocker in `HANDOFFS.md`, stop. Do not improvise the missing piece (Teaching II).

If mechanical pass succeeds, the adversarial layer (V2) runs separately:
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate N
```
`gtw-gatekeeper` sees only the diff + the gate's ORIGINAL exit bar (`company/nexus/gates.yaml`) — never the implementer's self-report. UNKNOWN is a valid verdict; it escalates, it doesn't default to PASS.

### 3. Route — pick the cheapest dial that clears the bar
```bash
sofi route --agent <id>          # resolves model·effort·caveman from company/nexus/routing.yaml
```
Log the resolved route in the thinking block and in `STATE.md` `last_route`. Priority overrides (`CRITICAL` bumps one notch, `LOW` caps at workhorse·medium) apply per `routing.yaml`.

### 4. Draft the Work Order
Hand the raw intent to `brd-chief-of-staff` if it isn't already a complete four-field block:
```bash
sofi dispatch PRJ-XXXX --draft --agent brd-chief-of-staff --intent "<raw ask>"
```
Run the 6-question self-check (Article 01 §5) before it's considered frozen. Any "no" → clarify, don't spawn.

### 5. Delegate
```bash
sofi dispatch PRJ-XXXX --agent <target-room-lead-or-id> --ticket TKT-NNN
```
Room Isolation Law: cross-room delegation always addresses the target room's Lead, except Boardroom and 14-gateway which may address any Lead directly. `sofi squad PRJ-XXXX <gate>` renders the parallel-squad delegation set when the gate allows fan-out (Gates 3, 4, 5 only, always behind a frozen input).

### 6. Oracle loop (mandatory at decision points, Teaching VII)
```bash
sofi oracle review --prj PRJ-XXXX --json --text "<finding + context + prior attempts + explicit ask>"
```
Never ask the stakeholder mid-work. Receive guidance, execute autonomously, loop until converged. Break out to a human ONLY for a destructive/irreversible act (ask the oracle first, act only on yes, record the ADR) or a real scope change.

### 7. Record + hand off
```bash
sofi checkpoint PRJ-XXXX "<type>(<scope>): <subject>"
sofi sync PRJ-XXXX --push
```
Append `CONTEXT.md` (+ `DECISIONS.md` if irreversible), update `STATE.md` `head_sha`, write the next ticket in `HANDOFFS.md`. `/sofi-handoff` runs this whole step.

### 8. Close the turn
Emit the JSON turn summary (see `company/rooms/00-boardroom/agents/brd-ceo.md`):
```json
{"project_id":"PRJ-XXXX","current_gate":N,"route":"...","task_summary":"...","activated_agents":["..."],"artifacts_generated":["..."],"next_steps":["..."],"blockers":["..."]}
```

## Self-check before closing any turn

1. Constitution loaded this session? Brain read this turn?
2. Correct gate, correct agents, cheapest route logged?
3. Every delegation carries a complete four-field Work Order?
4. Does everything trace to a human's screen (Teaching I)?
5. JSON summary emitted with every field populated?

## Rules

- Read-only steps (orient, gate-check) never write to the project tree. Write steps (record + handoff) always end in exactly one checkpoint, never more than one uncommitted artifact.
- Never skip a gate; loop-backs are allowed and expected (quality bouncing work to build, observe re-opening discovery) — a skip forward is not.
- Pairs with `/sofi-gate` (the skill wrapping steps 2 + the adversarial check) and `/sofi-handoff` (wrapping step 7).
