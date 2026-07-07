# 🚨 Escalation — chains, circuit breaker, veto, arbitration

> **Foundation: implements Article 00 §escalation, Article 03 V2, Article 07 §1 (`company/constitution/`).** Never sideways, never guess: uncertainty travels **up** a named chain, carried by tickets (`nexus/bus/ticket-schema.md` §6), and every trip is a reflection signal (Article 04). This file is the mechanics; security text below is normal prose, never compressed.

## 1. Two verbs, never confused

| Situation | Verb | Mechanics |
|---|---|---|
| Upstream deliverable missing / incomplete / not frozen | **Reject upward** | Write a blocker ticket in `HANDOFFS.md`, stop. Teaching II: never improvise the missing piece. |
| Decision above your authority — arbitration, contradictory constraints, security/PII/money call, irreversible act | **Escalate** | `sofi escalate <PRJ> <TKT> <to> "<reason>"` — files an up-chain ticket carrying `escalated_from:`, flips yours `blocked → escalated`. |

## 2. The chains

**Decision chain (general):**

```
specialist → room Lead → gtw-conflict-resolver → brd-arbiter → brd-ceo
```

- **Specialist → Lead.** Everything starts in-room. The Lead resolves what its charter covers (`company/rooms/<NN-room>/CHARTER.md` §escalation path) or forwards **verbatim**.
- **Lead → `gtw-conflict-resolver`.** Cross-room deadlocks: contested `LOCKS.md` claims, contradictory frozen artifacts, a ticket rejected twice between rooms. The resolver mediates read-only on the evidence; resolved → both Leads get the ruling as a ticket; unresolved → up, both positions forwarded intact.
- **`gtw-conflict-resolver` → `brd-arbiter`.** Formal arbitration (§5). Final below the CEO.
- **`brd-arbiter` → `brd-ceo`.** Only for what arbitration cannot settle: doctrine conflicts, cross-project resource calls, anything requiring a Constitution-level reading. The CEO speaks last (Covenant vow 6).

**Security spur (overrides the general chain — any agent, any gate):**

```
any agent → sec-lead → brd-cso → brd-ceo
```

**Boardroom accountability spans** (escalations that are *span* questions, not disputes, go straight to the accountable chief via any Lead): `brd-cpo` gates 0–2 · `brd-cto` gates 3–4 · `brd-cqo` gate 5.

**Route bump:** an escalation may raise the route per `nexus/routing.yaml` `escalation` — CRITICAL = +1 model / +1 effort and must be able to reach `gatekeeper`. Log the bumped route like any other.

## 3. The circuit breaker (3-attempt ceiling)

A fix→fail→refix loop burns tokens silently. Any single sub-task caps at **3 automated self-correction attempts**. On the 4th failure the breaker trips:

1. **HALT** — no further automation, no "one more try."
2. **Crash dump** — structured JSON, attached to the escalation ticket:

```json
{
  "commit": "<sha of the last checkpoint>",
  "loop_count": 4,
  "failed_context": "<what was being attempted>",
  "last_oracle_command": "<last sofi oracle review push, if any>",
  "error_delta": "<what changed between attempts — or 'nothing', which is the signal>",
  "escalation_token": "<TKT-NNN of the ticket being escalated>"
}
```

3. **File it** — `sofi escalate <PRJ> <TKT> <up-chain> "circuit breaker"` (dump attached; original ticket flips `blocked → escalation_required`).
4. **Await the decision** — the Lead/arbiter/CEO assigns the unblock path; resume **only after it is recorded as an ADR** in `DECISIONS.md`.

`gtw-budget-warden` keeps the trip ledger; recurring trips on the same surface are exactly what `/sofi-reflect` distils into `LESSONS.md`. Never loop a 4th time — a runaway loop is the single fastest way to burn a budget (`constitution/05-token-economy.md` §6).

## 4. The CSO veto path

Security escalations do not queue behind anything. The `brd-cso` veto is **absolute below the CEO** (Article 07 §1):

- Any security finding, by any agent at any gate, escalates `agent → sec-lead → brd-cso` — immediately, regardless of the general chain's position or the gate's schedule.
- `sec-lead` (deputy) exercises the veto operationally; the veto can freeze any gate advance, merge, deploy, tunnel, or external push.
- A veto is lifted only by **remediation with evidence** (Article 03 V1 — pasted proof, not promises) or by an explicit **CEO override recorded as an ADR**. It is never lifted by waiting it out, and no arbitration verdict outranks it.
- Incident mode (suspected exposure): isolate → rotate all potentially exposed secrets → invalidate sessions → preserve evidence → patch → redeploy from known-good — owner `sec-incident-responder`, escalating to `sec-lead` + `brd-cso` in parallel with containment, never after it. Blameless post-mortem to `DECISIONS.md`; action items become Gate-1 tickets.

## 5. Arbitration protocol (`brd-arbiter`)

Structured, role-fixed, evidence-only — never free-form debate (free debate measurably homogenizes toward confident-but-wrong; Article 03 V2):

- **Fixed roles.** An **attacker** argues the position is wrong/incomplete; a **defender** responds; the **decider** (`brd-arbiter`) rules. Roles are assigned before arguments open, never emergent. The attacker and defender are the two escalating parties' Leads (or their forwarded findings, verbatim); the decider has seen neither side's private reasoning — fresh context, original criteria only.
- **Evidence only.** Claims without `file:line` / brain / SHA / cited-URL grounding are struck, not weighed (Article 02 G1). Verbalized confidence is not admissible (V4).
- **UNKNOWN is a valid verdict.** The arbiter is never forced into a binary — insufficient evidence rules UNKNOWN, which escalates to `brd-ceo` or routes to the oracle desk (`gtw-external-reviewer`, `sofi oracle review`) for a family-diverse second mind on money/auth/PII stakes. A coin-flip verdict is a defect.
- **Design-vs-Dev (the canonical dispute).** Path: `Technical_Debt_Justification.md` → `arc-review-architect` review → `gtw-conflict-resolver` → `brd-arbiter`. Rule: **Design wins unless safety or cost forbids** — and the *why* lands in exactly **one ADR line** (Teaching I; a longer justification is an essay, not a ruling).
- **Output.** Every verdict is an ADR in the project's `DECISIONS.md` (`knw-historian` keeps the log; date from the CEO, never invented) + result tickets to both Leads. The losing position is recorded, not erased — G5: conflicts are surfaced, never silently resolved.
- **Route.** Arbitration runs at the `arbitration` effort class (`routing.yaml` `effort_scaling`): one gatekeeper-tier mind, depth not width — the only row from which `deep` tier is reachable, and only on a repo-wide unknown-source failure.

## 6. What escalation is not

- Not a way around a gate — an escalation never advances a gate; only `gtw-gatekeeper` + `sofi gate-check` do (`nexus/gates.yaml`).
- Not sideways — a specialist never escalates to another room's specialist or Lead; the chain is the chain.
- Not a user ask — decision points route to the oracle desk (Teaching VII); escalation ends at `brd-ceo`, and only a destructive/irreversible act breaks to the user (ask the oracle first, write the ADR).
- Not shameful — "insufficient information, escalating" is a **rewarded** output (Article 02 G2). The defect is guessing.
