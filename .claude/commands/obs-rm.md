---
description: Remove observability for deprecated feature. /obs-rm <feature>
agent: obs-lead
---

# 🗑️ OBSERVABILITY — REMOVE: $ARGUMENTS

## Delegation

### 1. Monitoring Engineer — @obs-monitoring-engineer
🎭 **Role:** Monitoring Engineer
📂 **Context:** Feature $ARGUMENTS deprecated
🎯 **Command:** Remove feature dashboards from Grafana. Archive queries
📐 **Format:** Cleaned Grafana config

### 2. Alerting Engineer — @obs-alerting-engineer
🎭 **Role:** Alerting Engineer
📂 **Context:** Feature alerts to remove
🎯 **Command:** Remove alert rules. Archive runbooks
📐 **Format:** Cleaned alert config

### 3. Insights Analyst — @obs-insights-analyst
🎭 **Role:** Insights Analyst
📂 **Context:** Feature journey removed
🎯 **Command:** Archive journey leak tracking for removed feature
📐 **Format:** Archived report

## Handoff
→ `/gate-check 8`