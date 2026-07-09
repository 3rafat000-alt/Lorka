---
description: "Investigate production incident. /obs-incident <description>"
argument-hint: "[description]"
---
> **Lead persona:** `obs-lead` — the main session *wears* this persona (`.claude/agents/obs-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🚨 OBSERVABILITY — INCIDENT: $ARGUMENTS

## Delegation

### 1. Incident Commander — @obs-incident-commander
🎭 **Role:** Incident Commander — triage
📂 **Context:** Incident: $ARGUMENTS · Gate 8
🎯 **Command:** Triage severity. Decide rollback or fix-forward. Coordinate responders. Communicate status
📐 **Format:** Incident log · timeline

### 2. Monitoring Engineer — @obs-monitoring-engineer
🎭 **Role:** Monitoring Engineer — diagnostics
📂 **Context:** Active incident
🎯 **Command:** Query Prometheus/Grafana/Sentry for root cause signals. Produce diagnostic timeline
📐 **Format:** Diagnostic report · graphs

### 3. Alerting Engineer — @obs-alerting-engineer
🎭 **Role:** Alerting Engineer
📂 **Context:** Incident resolved
🎯 **Command:** Adjust alert thresholds if false alert. Update runbook
📐 **Format:** Updated `docs/Alerting_Runbook.md`

## Post-incident
→ No-blame postmortem
→ `@knw-historian` — ADR entry
→ If SLO breached → auto-open Gate 1 ticket
