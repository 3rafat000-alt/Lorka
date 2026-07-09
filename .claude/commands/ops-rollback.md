---
description: Rollback a deployment. /ops-rollback <version>
agent: ops-lead
---

# ⏮️ DEVOPS — ROLLBACK: $ARGUMENTS

## Delegation

### 1. Release Manager — @ops-release-manager
🎭 **Role:** Release Manager — rollback
📂 **Context:** Rollback to $ARGUMENTS required
🎯 **Command:** Execute tested rollback plan. Blue/Green flip or restore previous version. Confirm success
📐 **Format:** Rollback report · timestamp + health

### 2. Migration Runner — @ops-migration-runner
🎭 **Role:** Migration Runner — revert
📂 **Context:** Rollback includes DB migrations
🎯 **Command:** Run rollback migration scripts. Verify schema at expected hash
📐 **Format:** Rollback migration log

### 3. Monitoring Engineer — @obs-monitoring-engineer
🎭 **Role:** Monitoring Engineer
📂 **Context:** Post-rollback
🎯 **Command:** Verify all signals green. Dashboards healthy
📐 **Format:** Health check report

## Handoff
→ `@obs-incident-commander` — postmortem
→ `@knw-historian` — ADR entry