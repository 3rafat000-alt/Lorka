# Playbook — Pass^k Reliability on Tier-A Surfaces

> Owner: `qa-test-architect` (planning), executed by `qa-automation-engineer` (automated legs) and `qa-manual-explorer` (manual legs), enforced by `qa-lead`. The room's sharpest recurring job: money/auth/PII surfaces don't get to ship reliable on a single green run (Article 03 V3) — a flaky test on a payment path or an auth flow is a blocker, not a retry-until-green.

## When to run this

Every Gate-5 pass, as soon as `qa-test-architect`'s `Test_Strategy.md` names at least one Tier-A surface in the merged build — which, per the Deep-Audit track, is every project touching money, credentials, auth, or PII, without exception.

## Steps

### 1. Classify the surface — before any test executes
`qa-test-architect` reads the merged build against the frozen `Threat_Model.md` and `OpenAPI.yaml`/`Schema.sql` and asks: does this surface handle money movement, authentication/authorization state, or personal data? A "maybe" defaults to Tier-A — the cost of over-testing a borderline surface is far cheaper than the cost of a flaky auth bypass shipping as "probably fine."

### 2. Name the plan explicitly
For every Tier-A surface, `qa-test-architect` states in `docs/PRJ-XXXX_Test_Strategy.md`:
- **Run count `k`** — the number of independent executions required (typical: 10-20 for a fast automated path; fewer for an expensive manual leg, but never fewer than 3).
- **Pass threshold** — typically 100% of `k` runs green; a lower threshold requires an explicit reasoned exception, never a default softening.
- **Executing specialist(s)** — `qa-automation-engineer` for anything a script can drive independently across runs (payment calculation, token issuance/expiry, permission checks); `qa-manual-explorer` for anything that needs a human variation across runs (a race-condition-prone UI flow, a confusing-but-technically-correct auth error state).

### 3. Automated legs — independent runs, not one script looped blindly
```bash
qa-automation-engineer: for i in $(seq 1 k); do <test command>; done   # or the framework's native repeat-run flag
```
Each run must be genuinely independent — fresh test data or state reset between runs, not a cached fixture that guarantees the same result every time and defeats the point of running `k` times. A pass^k claim built on `k` runs against identical cached state is not evidence; it is one run wearing a multiplier.

### 4. Manual legs — real variation across repeats
`qa-manual-explorer` runs her assigned Tier-A surface `k` times as different personas or with different realistic input variations each time — not the identical click-path repeated verbatim. The goal is surfacing a race condition, a timing-dependent bug, or a state-dependent auth gap that a single careful pass would never trigger.

### 5. Report the actual result — never round up
Both specialists report the literal pass count out of `k`, not a rounded "reliable" or "mostly passing." `9/10` on a Tier-A surface with a 100% threshold is a BLOCK, full stop, however close it looks.

### 6. `qa-test-architect` reconciles plan vs. execution
Did the executed run count match the planned `k`? Was each run genuinely independent (fresh state), or did a specialist take a shortcut that invalidates the multiplier? A shortcut discovered here restarts the pass^k run from a clean state — it does not get graded on the compromised runs already completed.

### 7. `qa-lead` enforces the bar
```bash
sofi gate-check PRJ-XXXX --gate 5
```
No PASS verdict issues while any Tier-A surface sits below its stated pass threshold. A flaky result on a Tier-A surface routes to the owning Build room's Lead as a blocking finding, with the specific failing run(s) cited — not "the tests are flaky sometimes."

### 8. Record
```bash
sofi checkpoint PRJ-XXXX "test(quality): pass^k results — <surface> — <pass_count>/<k> @ threshold <t>"
```
Append the pass^k results into the same `docs/PRJ-XXXX_Test_Report.md` this room already produces for Gate 5 — never a separate, easy-to-miss side document.

## Self-check before closing

1. Is every Tier-A surface's classification traceable to a specific `Threat_Model.md` or `Schema.sql` row?
2. Does every Tier-A surface's plan name `k`, the pass threshold, and the executing specialist explicitly?
3. Was each run in the `k` genuinely independent — fresh state, real variation — not a cached or identical repeat?
4. Is the reported result the literal pass count out of `k`, never rounded up?
5. Did any surface's flaky result get treated as a blocker, not a retry-until-green?

## Rules

- A "maybe Tier-A" surface defaults to Tier-A — the token cost of over-testing is cheap next to the cost of a missed auth/money flake (Teaching IV, weighed against Teaching VI's irreversibility principle for money/auth surfaces specifically).
- No pass^k claim counts on identical cached state across runs — independence is the entire point of running more than once.
- No threshold below 100% without an explicit, reasoned exception recorded by `qa-test-architect` — a silently softened bar is a bar that was never really there.
- Pairs with `playbooks/gate-5-quality-procedure.md` (this is the deep-dive on that playbook's step 4/7) and `/sofi-gate`.
