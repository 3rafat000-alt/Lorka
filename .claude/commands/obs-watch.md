---
description: "Setup observability for new feature. /obs-watch <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `obs-lead` — the main session *wears* this persona (`.claude/agents/obs-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 👁️ OBSERVABILITY — WATCH: $ARGUMENTS

## Delegation

### 1. SRE — @obs-sre
🎭 **Role:** SRE — SLI/SLO definitions
📂 **Context:** Feature deployed · Gate 8
🎯 **Command:** Define SLIs and SLOs for every critical path in feature. Compute error budgets. 50%+ consumption → alert
📐 **Format:** `docs/SLO_Definition.md` · per-critical-path

### 2. Monitoring Engineer — @obs-monitoring-engineer
🎭 **Role:** Monitoring Engineer — dashboards
📂 **Context:** SLOs defined
🎯 **Command:** Set up Prometheus metrics, Grafana dashboards, Sentry error tracking. Every SLI = live signal
📐 **Format:** Grafana dashboards · Sentry project config

### 3. Alerting Engineer — @obs-alerting-engineer
🎭 **Role:** Alerting Engineer — rules + runbooks
📂 **Context:** Monitoring live
🎯 **Command:** Define alert rules. Dry-test in staging. Every alert has 1:1 runbook (what/check/fix/escalate)
📐 **Format:** `docs/Alerting_Runbook.md` · alert rules config

### 4. Incident Commander — @obs-incident-commander
🎭 **Role:** Incident Commander — playbooks
📂 **Context:** Feature live, monitored
🎯 **Command:** Write incident response playbook for feature. Triage → rollback/fix-forward → postmortem flow
📐 **Format:** `docs/Incident_Playbook.md`

### 5. Insights Analyst — @obs-insights-analyst
🎭 **Role:** Insights Analyst — journey tracking
📂 **Context:** Feature live with users
🎯 **Command:** Monitor user behavior. Detect journey leaks. Leak → formal Gate 1 reopen
📐 **Format:** `docs/Journey_Leak_Report.md` (weekly)

## Handoff
→ SLO breach → Gate 1 reopen ticket
→ `/gate-check 8`
