---
description: "Deploy feature to staging + prod. /ops-deploy <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `ops-lead` — the main session *wears* this persona (`.claude/agents/ops-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🚀 DEVOPS — DEPLOY: $ARGUMENTS

## Delegation

### 1. CI/CD Engineer — @ops-cicd-engineer
🎭 **Role:** CI/CD Engineer — pipeline
📂 **Context:** QA PASS · Gate 6–7
🎯 **Command:** Verify CI pipeline green. Lint → test → build → scan → deploy
📐 **Format:** CI status report · green check

### 2. Cloud Engineer — @ops-cloud-engineer
🎭 **Role:** Cloud Engineer — IaC
📂 **Context:** Feature deployment
🎯 **Command:** Confirm staging≈prod parity. IaC up-to-date. Teardown before provision
📐 **Format:** Infrastructure status

### 3. Migration Runner — @ops-migration-runner
🎭 **Role:** Migration Runner — DB migrations
📂 **Context:** Pending migrations
🎯 **Command:** Run migration with proven rollback on staging first. Then prod. Log before/after schema hash
📐 **Format:** Migration run log

### 4. Domain Warden — @ops-domain-warden
🎭 **Role:** Domain Warden — DNS/SSL
📂 **Context:** Feature on live domain
🎯 **Command:** Verify DNS, SSL, local domain. Tunnel if needed (seed data only)
📐 **Format:** Domain status report

### 5. Release Manager — @ops-release-manager
🎭 **Role:** Release Manager — Blue/Green
📂 **Context:** All pre-deploy checks pass
🎯 **Command:** Execute Blue/Green deploy. Tested rollback plan ready. Execute first in staging then prod
📐 **Format:** `docs/Release_Report.md` · deploy + rollback timestamps

## Post-deploy
→ `@obs-monitoring-engineer` verify signals
→ `@obs-alerting-engineer` confirm alerts fire

## Handoff
→ `/gate-check 6` (staging) → `/gate-check 7` (prod)
