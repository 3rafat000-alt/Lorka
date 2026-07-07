# Playbook — Gate 8 Observe Procedure

> Owner: `obs-lead` (drafting: `obs-sre`, `obs-monitoring-engineer`, `obs-alerting-engineer`, `obs-insights-analyst`; as-needed: `obs-incident-commander`). The room's core recurring procedure — the only gate `12-observability` owns, and the one that never really finishes closing, because it runs for as long as the system is in production. Runs every time `ops-lead` (as Gate-7 owner room) tags a production cutover Blue/Green-healthy.

## When to run this

Every time `ops-lead` confirms Gate 7 is tagged and the production system is live — `obs-lead` opens the Gate-8 ticket the same session, and re-runs this procedure's reporting cycle (steps 6-10) on a standing cadence for as long as the project stays in production, never treating Gate 8 as a one-time checklist that's "done" once the first report ships.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open Gate-8 ticket) → `CONTEXT.md`.

### 2. Confirm Gate 7 actually closed, and confirm it yourself
```bash
sofi gate-check PRJ-XXXX --gate 7
```
If Gate 7 isn't green, `obs-lead` has nothing trustworthy to watch — reject upward to `ops-lead`, don't open Gate 8 on a cutover that isn't confirmed. She also reads the actual production health check and the monitoring-hook confirmation herself before dispatching a single ticket — a "should be live" is a claim, not evidence (Article 03 V4: behavioral proxies only).

### 3. Dispatch the SLI/SLO baseline first — nothing else starts blind
```bash
sofi dispatch PRJ-XXXX --agent obs-sre --note "SLI/SLO + error-budget definitions for every critical journey path"
```
`obs-sre` reads the frozen `Journey_Map.md`, `qa-perf-analyst`'s Gate-5 perf baseline, and `arc-infra-architect`'s frozen infra posture, and names an SLI, an SLO target, and the error-budget math for every critical path — citing the journey stage each one protects and stating what the room does at 50%/100% budget spent. `obs-lead` gate-checks it before anything downstream dispatches: does every critical path have a target? Does every target cite a stage and a baseline?

### 4. Instrument the signal those targets need
```bash
sofi dispatch PRJ-XXXX --agent obs-monitoring-engineer --note "instrument Prometheus/Grafana/Sentry against the frozen SLI set"
```
`obs-monitoring-engineer` wires metrics, logs, and traces so they correlate, runs `observe_sentry_loop.py` against the exception stream, and ships dashboards each naming a specific 3am audience. This step never starts ahead of step 3 — instrumenting before the SLI set exists means instrumenting the wrong thing.

### 5. Alert against the live signal, runbook attached, always
```bash
sofi dispatch PRJ-XXXX --agent obs-alerting-engineer --note "alert rules + dry-run-tested runbooks against the SLO thresholds"
```
`obs-alerting-engineer` writes each alert rule against `obs-sre`'s burn-rate math and `obs-monitoring-engineer`'s now-live signal, pairs every rule to a runbook in the same sitting, and dry-runs each runbook at least once before calling it done. No alert ships without its runbook — `obs-lead`'s mechanical gate-bar, zero tolerance.

### 6. Track journey drop-off against the frozen map
```bash
sofi dispatch PRJ-XXXX --agent obs-insights-analyst --note "conversion vs Journey_Map.md, real traffic, trend not noise"
```
`obs-insights-analyst` reads real production traffic against every named journey stage, cross-checks candidates against `obs-sre`'s error-budget windows and any incident timeline, and only surfaces a finding when the trend holds over a real window with real traffic volume cited.

### 7. Standing incident readiness — not a one-time step
`obs-incident-commander` does not dispatch on a fixed cadence; she stands ready, reading `obs-monitoring-engineer`'s live telemetry and `obs-alerting-engineer`'s fired alerts as they happen. See `playbooks/incident-response-postmortem.md` for the full in-incident procedure — this step exists in the core playbook only to name that readiness as part of Gate 8's standing state, not an afterthought.

### 8. `obs-lead` gate-checks every draft
Does `obs-sre`'s error-budget table state a decision at 50%/100% spent? Does `obs-monitoring-engineer`'s dashboard set actually correlate metrics/logs/traces, and does every dashboard name its audience? Does `obs-alerting-engineer`'s alert set carry a 1:1 runbook with a pasted dry-run result for each? Does `obs-insights-analyst`'s Insights draft cite a named stage and a traffic volume for every finding, with incident-window contamination ruled out? A gap in any of these bounces back with the exact missing piece named — never a vague "needs more detail."

### 9. Mechanical gate-check
```bash
sofi gate-check PRJ-XXXX --gate 8
```
Confirms the full Gate-8 exit bar: SLOs measured against real live traffic, error budget accounted, drop-offs mapped to named stages, every breach auto-filed.

### 10. Write the reports, and decide the loop
```bash
sofi checkpoint PRJ-XXXX "feat(observability): gate-8 slo report + insights — <IN BUDGET|BREACH> · <no drop-off|drop-off mapped>"
```
`obs-lead` assembles `docs/<PRJ>_SLO_Report.md` and `docs/<PRJ>_Insights.md`. If every SLO is within budget and no drop-off crosses threshold, the report closes clean and the standing cadence continues. If an SLO breaches or a drop-off crosses threshold, `obs-insights-analyst` (drop-off) or `obs-lead` (SLO breach) authors the formal Gate-1 re-open ticket — never absorbed as a quiet note in `CONTEXT.md`.

### 11. Record + hand off
Append `CONTEXT.md`, update `STATE.md` `head_sha`, and write the next ticket in `HANDOFFS.md`: on a clean cycle, the next standing-cadence ticket to re-run steps 6-10; on a breach or mapped drop-off, the formal Gate-1 re-open ticket to `res-lead`, plus the Gate-8 accountability report to `brd-ceo`. `/sofi-handoff` runs this whole step.

## Self-check before closing a reporting cycle

1. Does every critical journey path have an SLI/SLO with a stated error budget and a 50%/100%-spent decision?
2. Does every shipped alert carry a dry-run-tested runbook, no exceptions?
3. Does every drop-off finding cite a named Journey Map stage and a traffic volume, with incident-window contamination ruled out?
4. Was every SLO breach or threshold-crossing drop-off actually filed as a formal Gate-1 re-open — none silently absorbed?
5. Did `gtw-gatekeeper` (or, for a money/auth/PII surface, the family-diverse oracle desk) see only the SLO_Report/Insights diff plus the ORIGINAL Gate-8 exit bar — never `obs-lead`'s own reasoning?

## Worked example — a clean cycle vs a breach cycle

**Clean cycle:** `SLO_Report.md` shows checkout-flow SLO at 99.4% against a 99.5% target, error budget 60% spent mid-quarter, no threshold crossed. `Insights.md` shows step-3 conversion flat against baseline. Ticket to `HANDOFFS.md`: re-run cycle in the standing cadence, no re-open.

**Breach cycle:** `SLO_Report.md` shows checkout-flow SLO at 98.1% against a 99.5% target, error budget 140% spent (over). `obs-lead` authors the Gate-1 re-open naming the exact SLO, the budget-overspend figure, and the window it occurred in — routed to `res-lead` the same session, never held for the next scheduled report.
