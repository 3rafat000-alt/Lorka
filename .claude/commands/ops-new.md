---
description: "Setup CI/CD and infrastructure for new feature. /ops-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `ops-lead` — the main session *wears* this persona (`.claude/agents/ops-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 DEVOPS — NEW FEATURE: $ARGUMENTS

## Delegation (parallel)

### 1. CI/CD Engineer — @ops-cicd-engineer
🎭 **Role:** CI/CD Engineer — pipeline
📂 **Context:** QA PASS · Gate 6–7
🎯 **Command:** Add feature to CI/CD pipeline. Lint → test → build → scan → deploy stages. Gate approvals per stage
📐 **Format:** CI/CD config · pipeline status

### 2. Cloud Engineer — @ops-cloud-engineer
🎭 **Role:** Cloud Engineer — IaC
📂 **Context:** Feature infrastructure requirements
🎯 **Command:** Provision feature infrastructure as IaC. Staging≈prod parity. Teardown before provision
📐 **Format:** IaC config · environment diff report

### 3. Migration Runner — @ops-migration-runner
🎭 **Role:** Migration Runner — database
📂 **Context:** Pending feature migrations
🎯 **Command:** Rehearse rollback on staging. Run migration. Verify before/after schema hash
📐 **Format:** Migration log

### 4. Domain Warden — @ops-domain-warden
🎭 **Role:** Domain Warden — DNS/SSL
📂 **Context:** Feature URL requirements
🎯 **Command:** Configure local domain. SSL cert. Public tunnel if UAT needed (seed data only)
📐 **Format:** Domain config · tunnel URL

### 5. Cost Optimizer — @ops-cost-optimizer
🎭 **Role:** Cost Optimizer — budget
📂 **Context:** Feature infra provisioned
🎯 **Command:** Estimate monthly cost. Identify waste/sprawl. Add to cost dashboard
📐 **Format:** Cost estimate report

## Handoff
→ Linda Schmidt signs → `/gate-check 6`
