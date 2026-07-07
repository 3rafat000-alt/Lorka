# Playbook — Gate Advancement (the two-layer verify, every gate, every time)

> Owner: `gtw-gatekeeper` (mechanical layer run by whichever owner-room Lead is closing the gate). The room's core, always-on procedure — every one of the company's 9 gates advances through this and no other path (`company/nexus/NEXUS.md` §6, Article 03 V1+V2). Unlike every other room's core playbook, this one isn't scoped to a gate span — it runs identically whether the gate closing is 0 (Inception) or 8 (Observe).

## When to run this

Every time an owner-room Lead believes their gate's exit conditions are met and wants to tag it — `arc-lead` closing Gate 3, `bck-lead`/`fnt-lead`/`mob-lead` closing Gate 4, `qa-lead` closing Gate 5, and so on through `obs-lead` at Gate 8. Also runs standalone (outside a full gate close) whenever a high-stakes ticket wants `accepted` and the requesting Lead wants a fresh-context check before proceeding.

## Steps

### 1. Owner-room Lead confirms the deliverable carries an evidence block
```bash
sofi brain-query PRJ-XXXX status=done gate=<N>
```
Article 03 V1: a `done` ticket without a pasted cmd+exit-code, `file:line` proof, or diff/SHA is not eligible to be gate-checked at all — `validate_evidence()` rejects it fail-closed. If the evidence block is missing, the owner-room Lead bounces it back to the specialist before this playbook even starts; `gtw-gatekeeper` never rules on an ungrounded claim.

### 2. Mechanical layer — `sofi gate-check`
```bash
sofi gate-check PRJ-XXXX
```
Reads back:
```
━━ gate-check PRJ-XXXX ━━
  sequence : 0 1 2 3
  no-skip  : ✓
  artifacts: ✓ all 6 present
  tiers    : ✓ no boundary violations
  evidence : ✓ done-tickets carry proof
  VERDICT  : PASS
```
Four checks, all fail-closed: no-skip (`validate_no_skip` — gates move monotonically, loop-backs reported not penalized), artifacts (`validate_artifacts` — every path `gates.yaml` names for this gate exists), room-boundary (`validate_room_boundary` — no `from:`/`to:` pair violates the Isolation Law), evidence (`validate_evidence` — every `done` ticket carries proof). **A mechanical FAIL stops here** — `gtw-gatekeeper` does not spend a token on the adversarial layer against a bundle that fails its own mechanical check; the owner-room Lead fixes the mechanical gap first.

### 3. `gtw-router` stamps the verification request
```bash
sofi route gtw-gatekeeper
```
Gatekeeper tier, high effort, full caveman, as-needed budget — logged into the ticket before `gtw-gatekeeper` reads anything.

### 4. `gtw-gatekeeper` pulls the ORIGINAL exit_bar — nothing else
Read `company/nexus/gates.yaml`'s `exit_bar` list for this exact gate number, verbatim. This is the ONLY criteria source. Do not read the ticket's `task:` narrative, the implementer's chat log, or any status update claiming success — Article 03 V2's whole point is that the verifier never sees how the work got done, only whether it arrived.

### 5. Rule each `exit_bar` line item independently
For each line in the gate's `exit_bar`:
- Locate the specific artifact/deliverable that should satisfy it.
- Check it directly — read the file, run the pasted command again if reasonable, confirm the `file:line` cited actually says what the evidence block claims.
- Rule PASS / FAIL / **UNKNOWN** for that line, citing the exact clause + the exact evidence.

Fixed roles when the stakes warrant a structured adversarial pass rather than a solo read (a contested or ambiguous clause): an **attacker** pass argues the deliverable is wrong/incomplete, a **defender** pass responds citing the deliverable itself, `gtw-gatekeeper` **decides**. Never free-form debate — free debate homogenizes toward confident-but-wrong.

### 6. Money/auth/PII stakes — defer, don't rule solo
If any `exit_bar` line touches money, authentication, or PII (a `deep_audit`-track project per `gates.yaml` `tracks`, or the gate's artifact set includes a payment/credential/PII surface), do not rule solo:
```bash
sofi dispatch PRJ-XXXX --agent gtw-external-reviewer --note "family-diverse judge — gate <N> exit_bar §<clause>"
```
A same-family judge (Claude checking Claude) carries a documented self-enhancement bias; the oracle desk is a genuinely different model family. The desk's read feeds `gtw-gatekeeper`'s final ruling — it doesn't replace it.

### 7. Roll up the verdict
- All lines PASS → overall **PASS**.
- Any line FAIL → overall **FAIL**, reported with the exact failing clause(s) and gap(s) — not "needs work," the specific missing piece.
- Any line UNKNOWN and no line FAIL → overall **UNKNOWN** — never rounded up to PASS to keep a schedule moving.

### 8. UNKNOWN → escalate, never guess
```bash
sofi escalate PRJ-XXXX TKT-NNN <owner-room-lead> "gate <N> exit_bar §<clause> — insufficient evidence to rule"
```
Files an up-chain ticket carrying `escalated_from:`; the original ticket flips `blocked → escalated`. `brd-ceo` or a family-diverse oracle-desk pass (already run in step 6 for money/auth/PII) resolves it. UNKNOWN is a rewarded output (Article 02 G2) — it is never treated as a soft failure of nerve.

### 9. PASS → owner-room Lead tags the gate
`gtw-gatekeeper` does not run `sofi gate-tag` — the verdict feeds the *owner-room* Lead's own signature:
```bash
sofi gate-tag PRJ-XXXX <N>
```
Produces `<PRJ>-gate<N>-done`, an immutable restore point. The owner-room Lead reports the closed gate to the accountable boardroom chief (`brd-cpo` gates 0-2, `brd-cto` gates 3-4, `brd-cqo` gate 5, `brd-ceo` all).

### 10. FAIL → bounce, cite the exact gap, no proceed
The owner-room Lead routes the specific FAIL clause back to the owning specialist via the normal in-room chain — never a silent partial-proceed to the next gate. `gtw-gatekeeper` re-runs this playbook from step 1 once the specialist's fix carries its own evidence block.

### 11. Checkpoint the verdict itself
```bash
sofi checkpoint PRJ-XXXX "chore(gate): gate-<N> verdict — <PASS|FAIL|UNKNOWN>, gtw-gatekeeper"
```
The verdict is part of the project's recorded history whether it passed or not — a rejected gate attempt is exactly the kind of signal `/sofi-reflect` needs later.

## Worked example — a FAIL with a cited gap

```
exit_bar §"coverage >= 90% or the build FAILS"
evidence pasted: `php artisan test --coverage` → 84.2%
VERDICT: FAIL — clause requires ≥90%, evidence shows 84.2%. Bounced to qa-automation-engineer via qa-lead.
```

No essay, no "close but needs polish" — the exact clause, the exact number, the exact next hop.
