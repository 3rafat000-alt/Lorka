# Playbook — Gate 5 Quality Procedure

> Owner: `qa-lead` (drafting: `qa-test-architect`, `qa-automation-engineer`, `qa-manual-explorer`, `qa-perf-analyst`, `qa-regression-warden`, `qa-design-auditor`; squad partner: `sec-lead` via `09-security`). The room's core recurring procedure — the only gate `10-quality` owns outright. Runs every time `05-backend`/`06-frontend`/`07-mobile`/`08-data` finish their Gate-4 merges into `prj/<PRJ>`.

## When to run this

Every time `bck-lead` (as Gate-4 owner room) confirms all four Gate-4 rooms' worktrees are merged and reports the aggregate `sofi gate-check --gate 4` green — `qa-lead` opens the Gate-5 ticket the same session, never on a delay that lets the merged build drift further from what triggered the check.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open Gate-5 ticket) → `CONTEXT.md`.

### 2. Confirm Gate 4 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 4
```
If Gate 4 isn't green, `qa-lead` has nothing trustworthy to test — reject upward to `bck-lead`, don't test a build that's still moving (Teaching II).

### 3. Dispatch the strategy first — nothing else starts blind
```bash
sofi dispatch PRJ-XXXX --agent qa-test-architect --note "risk-tier + pyramid + pass^k plan"
```
`qa-test-architect` reads the merged build, the frozen `OpenAPI.yaml`/`Schema.sql`/`Threat_Model.md`, classifies every surface Tier-A or standard, and writes `docs/PRJ-XXXX_Test_Strategy.md` naming a pass^k plan for every Tier-A surface. `qa-lead` gate-checks it before anything downstream dispatches: does every surface have a classification with reasoning? Does every Tier-A surface name a run count, pass threshold, and executing specialist?

### 4. Fan out the four execution dimensions in parallel behind the frozen strategy
```bash
sofi dispatch PRJ-XXXX --agent qa-automation-engineer --note "unit/integration/E2E + pass^k automated legs"
sofi dispatch PRJ-XXXX --agent qa-manual-explorer --note "persona edge-probing + pass^k manual legs"
sofi dispatch PRJ-XXXX --agent qa-perf-analyst --note "load test + CWV audit"
sofi dispatch PRJ-XXXX --agent qa-design-auditor --note "Design Audit vs frozen prototype"
```
All four read the same frozen `Test_Strategy.md` and merged build — a genuine `effort_scaling.cross-room` fan-out, not a sequential drip. `qa-regression-warden` runs alongside them (see step 5), not after.

### 5. Run the regression warden's standing check in the same window
```bash
sofi dispatch PRJ-XXXX --agent qa-regression-warden --note "standing suite health + quarantine"
```
Tracks pass rate and flake history across the *combined* suite (pre-existing + `qa-automation-engineer`'s new tests as they land); quarantines any test showing a second unexplained red immediately, never waits for the whole pass to finish first.

### 6. Confirm `09-security`'s squad-partner contribution lands
```bash
sofi gate-check PRJ-XXXX --gate 5 --room 09-security
```
`sec-lead`'s appsec review, `sec-pentester`'s pentest report, and `sec-authn-engineer`'s re-check run on the same merged build, in parallel with this room's own four dimensions — `qa-lead` does not wait for `09-security` to finish before starting her own room's work, but she does not issue a verdict without their contribution present.

### 7. `qa-lead` gate-checks every draft
Does `qa-automation-engineer`'s coverage report show `coverage_gate.py` exit `0`? Did every assigned Tier-A pass^k leg (automated and manual) actually execute, with the real pass rate reported — not assumed? Does `qa-perf-analyst`'s `perf_budget.py` run show exit `0`, and does every breach carry a root cause? Does `qa-design-auditor`'s audit cover every frozen screen/state with zero left unchecked? Is `qa-regression-warden`'s quarantine list current, every entry with a named owner? A gap in any of these bounces back with the exact missing piece named — never a vague "needs more detail."

### 8. Fold in `09-security`'s findings — verbatim, never re-authored
`qa-lead` reads `sec-lead`'s signed contribution and folds it into the aggregate as-is; she does not summarize, soften, or reinterpret a Critical/High finding on the way into her own report.

### 9. Mechanical gate-check
```bash
sofi gate-check PRJ-XXXX --gate 5
```
Confirms the full Gate-5 exit bar: coverage >90%, perf budget clean, pass^k green on every Tier-A surface, zero unmitigated Critical/High from either room, design deviations resolved or accepted.

### 10. Adversarial verify (never self-graded)
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 5
```
Sees only the merged diff/artifacts + the ORIGINAL Gate-5 exit bar (`company/nexus/gates.yaml`) — never `qa-lead`'s own reasoning. Given the money/auth/PII stakes typical of Tier-A surfaces at this gate, prefer a family-diverse judge for the Tier-A slice specifically (Article 03 judge-bias guard).

### 11. Issue the ONE verdict
`qa-lead` compresses every dimension — her own six plus `09-security`'s squad contribution — into exactly one PASS or one BLOCK. PASS carries the full evidence block; BLOCK names the specific gap and the specific room that owns the fix, never a vague "quality issues found."

### 12. Record + hand off
```bash
sofi checkpoint PRJ-XXXX "feat(quality): gate-5 verdict — <PASS|BLOCK> — coverage/perf/pass-k/design-audit"
```
Append `CONTEXT.md`, update `STATE.md` `head_sha`, and write the next ticket in `HANDOFFS.md`: on PASS, to `ops-lead` (staging deploy can proceed); on BLOCK, one ticket per gap to the owning Build room's Lead. `/sofi-handoff` runs this whole step.

## Self-check before closing

1. Does `Test_Strategy.md` classify every surface, with every Tier-A surface carrying a named pass^k plan?
2. Did every assigned pass^k leg — automated and manual — actually execute, with the real pass rate reported?
3. Is coverage >90% with `coverage_gate.py` exit `0` pasted as evidence?
4. Is the perf budget clean with `perf_budget.py` exit `0` pasted, and every breach root-caused?
5. Does the Design Audit cover every frozen screen/state with zero unchecked?
6. Is `09-security`'s contribution folded in verbatim, with zero unmitigated Critical/High from either room?
7. Was the mechanical gate-check AND the `gtw-gatekeeper` adversarial verdict both run — never one substituting for the other?
8. Is the final verdict exactly ONE — PASS or BLOCK — never a fragmented per-dimension scoreboard?

## Rules

- No specialist inside the room reaches `bck-lead`, `fnt-lead`, `mob-lead`, `dat-lead`, or `sec-lead` directly — everything routes through `qa-lead`.
- `qa-lead` does not mediate a security dispute from `09-security`'s squad-partner review — that stays inside `09-security`'s own escalation path (the security spur).
- No execution specialist dispatches before `qa-test-architect`'s strategy is gate-checked — testing without a sized strategy is exactly the uniform-depth waste Teaching IV forbids.
- Pairs with `/sofi-gate` (wraps steps 9-10) and `/sofi-handoff` (wraps step 12).
