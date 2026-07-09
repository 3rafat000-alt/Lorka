---
description: Fix monitoring/alerting/SLO issue. /obs-fix <issue>
agent: obs-lead
---

# 🔧 OBSERVABILITY — FIX: $ARGUMENTS

## Delegation
Select specialist:
- SLO breach → `@obs-sre`
- Missing/dim metrics → `@obs-monitoring-engineer`
- Alert noise/miss → `@obs-alerting-engineer`
- Incident mishandled → `@obs-incident-commander`
- Journey leak detected → `@obs-insights-analyst`

🎭 **Role:** Appropriate observability specialist
📂 **Context:** Issue: $ARGUMENTS · Gate 8
🎯 **Command:** Fix root cause. Update dashboards/runbooks/playbooks. Verify fix in staging
📐 **Format:** Fix commit · updated docs

## Handoff
→ Naomi Brooks signs fix
→ If SLO breach opened Gate 1 ticket → `/res-new "investigate: $ARGUMENTS"`
