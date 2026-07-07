# Playbook — Incident Response & Blameless Post-Mortem

> Owner: `obs-incident-commander` (drafting/support: `obs-monitoring-engineer`, `obs-alerting-engineer`; execution partner: `ops-release-manager`, via `obs-lead` → `ops-lead`; security spur: `sec-lead`). The room's sharpest recurring job — the moment an alert stops being a line on a dashboard and becomes a live decision with real consequences. This procedure runs the instant a production incident is confirmed, independent of the standing Gate-8 reporting cadence, and does not wait for a convenient point in that cycle.

## When to run this

The instant `obs-alerting-engineer`'s alert fires on a signal `obs-monitoring-engineer`'s instrumentation confirms is real — not a flapping false-positive, an actual live production condition. `obs-incident-commander` does not wait for `obs-lead`'s sign-off to begin; incident command authority is hers from the moment the incident is confirmed.

## Steps

### 1. Confirm the signal is real, not a false-positive
```bash
sofi dispatch PRJ-XXXX --agent obs-monitoring-engineer --note "confirm fired alert against live telemetry — real or false-positive"
```
`obs-monitoring-engineer` checks the fired alert against the actual live dashboard and trace data. A confirmed false-positive routes back to `obs-alerting-engineer` for threshold tuning — no incident is declared. A confirmed real signal moves to step 2 immediately.

### 2. Declare command
`obs-incident-commander` states, out loud, in the incident channel: *"I have command."* This happens before any tactical discussion — no one proposes a fix, no one debates root cause, until command is declared and the fixed-order triage begins.

### 3. Triage in fixed order — never reordered
1. **Is it worsening?** Read `obs-monitoring-engineer`'s live telemetry trend, not a single snapshot.
2. **Is it customer-facing?** Cross-check against `obs-insights-analyst`'s baseline conversion data if the incident's shape suggests a journey-stage impact.
3. **Is it security-shaped?** Cross-check against `sec-lead`'s incident-response runbooks and the threat model's known attack surfaces (via `obs-lead`).

If step 3 answers yes at any point, stop here — go immediately to step 4a. Otherwise continue to step 5.

### 4a. Security-shaped → hand off immediately
```bash
sofi escalate PRJ-XXXX TKT-XXX sec-lead "incident triage flagged security-shaped: <one-line signal>"
```
`obs-incident-commander` hands triage authority to `sec-lead`'s chain the instant this is recognized — she does not keep running point, does not attempt her own remediation first, does not wait for a cleaner handoff moment. The security spur bypasses this room's own chain entirely (per `09-security`'s charter).

### 5. Decide: rollback or forward-fix — alone, on his own authority
`obs-incident-commander` states the decision in one line with its reason: e.g. *"Rollback — the regression traces to the last deploy, no fast forward-fix path exists, executing via ops-release-manager."* This decision is never a mid-incident consensus vote; the room's standard escalation chain (`specialist → lead → gtw-conflict-resolver → brd-arbiter → brd-ceo`) does not apply while an incident is live.

### 6. Hand execution to `ops-release-manager` — never execute it yourself
```bash
sofi dispatch PRJ-XXXX --agent obs-lead --note "relay rollback decision to ops-lead → ops-release-manager for execution"
```
`obs-incident-commander` does not touch the rollback mechanism herself — she decides, `ops-release-manager` executes, exactly the boundary Article 03 V4 exists to enforce (behavioral proxies only: the executed rollback's exit code and health-check result are the evidence, not her verbal confidence in the call).

### 7. Confirm recovery
Read the post-rollback (or post-forward-fix) health check and telemetry trend directly — recovery is confirmed by the same instrumentation that flagged the incident, never by an "it should be fixed now" from whoever applied the fix.

### 8. Run the blameless post-mortem — inside the recovery window, not weeks later
```bash
sofi dispatch PRJ-XXXX --agent obs-incident-commander --note "blameless post-mortem: timeline, failure mode, action items"
```
Reconstruct the timeline from `obs-monitoring-engineer`'s actual telemetry, not memory. Name the **failure mode** — "the deploy pipeline shipped a migration with no feature flag, so the regression was live for every user simultaneously" — never the person who ran the deploy. Every action item gets a named owner and a concrete next step; "we should look into this" is not an accepted action item.

### 9. Route action items into Gate 1
```bash
sofi checkpoint PRJ-XXXX "fix(observability): incident postmortem — <one-line failure mode> — N action items → gate-1"
```
`obs-incident-commander` hands the finished post-mortem to `obs-lead`, who writes it into `DECISIONS.md` (the ADR line: what happened, why, the rollback/forward-fix reason) and opens one Gate-1 ticket per action item — routed to `02-research` via `res-lead` if the item is a real product/journey change, or to the specific room whose surface failed if the item is a scoped technical fix.

### 10. Record + hand off
Append `CONTEXT.md` with the incident summary, update `STATE.md` `head_sha`, and confirm every action-item ticket exists in `HANDOFFS.md` before closing. `/sofi-handoff` runs this whole step. The standing Gate-8 reporting cadence (`playbooks/gate-8-observe-procedure.md`) resumes on its normal schedule — this playbook does not pause it longer than the incident itself required.

## Self-check before closing an incident

1. Was command declared before any tactical discussion started?
2. Was triage run in the fixed order — worsening, customer-facing, security-shaped — with no step skipped or reordered?
3. If security-shaped, was the handoff to `sec-lead` immediate, with no attempted remediation first?
4. Was the rollback-or-forward-fix decision made by `obs-incident-commander` alone, stated with its reason, and executed by `ops-release-manager` — never the reverse?
5. Was recovery confirmed by instrumentation, not by a self-report?
6. Does the post-mortem name a failure mode, never a person, with every action item carrying a named owner?
7. Does every action item exist as a real Gate-1 (or scoped-fix) ticket in `HANDOFFS.md` — none left living only in the post-mortem doc?

## Worked example

Alert fires: checkout error rate crosses burn-rate threshold. `obs-monitoring-engineer` confirms real (not a false-positive — traffic volume and error count both climbing). `obs-incident-commander` declares command, triages: worsening (yes, climbing 3 minutes running), customer-facing (yes, checkout), security-shaped (no — traced to a schema migration, not an intrusion signal). Decides rollback, one line: *"Rollback to pre-migration tag — the error correlates exactly with the migration's deploy timestamp, no safe forward-fix exists in the window."* Hands to `ops-release-manager` via `obs-lead`/`ops-lead`. Recovery confirmed 4 minutes later via the same error-rate dashboard. Post-mortem: failure mode named as "the migration shipped without a staged rollout, so 100% of checkout traffic hit the new schema before the incompatibility was caught" — two action items, both with named owners, both filed as Gate-1 tickets to `08-data` (via `dat-lead`, for the staged-rollout process gap) and `10-quality` (via `qa-lead`, for the missing migration-compatibility test).
