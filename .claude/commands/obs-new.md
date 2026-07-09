---
description: "Setup observability for new feature. /obs-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `obs-lead` — the main session *wears* this persona (`.claude/agents/obs-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 OBSERVABILITY — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. SRE — @obs-sre
🎭 **Role:** SRE — SLI/SLO
📂 **Context:** Feature deployed · Gate 8
🎯 **Command:** Define SLIs + SLOs per critical path. Error budget. 50% budget consumed → alert
📐 **Format:** `docs/SLO_Definition.md`

### 2. Monitoring Engineer — @obs-monitoring-engineer
🎭 **Role:** Monitoring Engineer — dashboards
📂 **Context:** SLOs defined
🎯 **Command:** Prometheus metrics, Grafana dashboard, Sentry project. Every SLI = live signal
📐 **Format:** Grafana dashboard · Sentry config

### 3. Alerting Engineer — @obs-alerting-engineer
🎭 **Role:** Alerting Engineer — rules + runbooks
📂 **Context:** Monitoring live
🎯 **Command:** Alert rules. Dry-test in staging. Every alert → 1:1 runbook
📐 **Format:** `docs/Alerting_Runbook.md`

### 4. Incident Commander — @obs-incident-commander
🎭 **Role:** Incident Commander — playbook
📂 **Context:** Feature monitored
🎯 **Command:** Incident response playbook: triage → fix-forward/rollback → postmortem
📐 **Format:** `docs/Incident_Playbook.md`

### 5. Insights Analyst — @obs-insights-analyst
🎭 **Role:** Insights Analyst — journey tracking
📂 **Context:** Feature live with users
🎯 **Command:** Track user behavior. Detect journey leaks. Leak → Gate 1 reopen
📐 **Format:** `docs/Journey_Leak_Report.md`

## Handoff
→ Naomi Brooks signs → `/gate-check 8`
