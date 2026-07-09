---
description: "Remove feature from infrastructure. /ops-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `ops-lead` — the main session *wears* this persona (`.claude/agents/ops-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ DEVOPS — REMOVE: $ARGUMENTS

## Delegation

### 1. Cloud Engineer — @ops-cloud-engineer
🎭 **Role:** Cloud Engineer
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Teardown feature infrastructure. Update IaC. Document removed resources
📐 **Format:** Updated IaC · cleanup log

### 2. Domain Warden — @ops-domain-warden
🎭 **Role:** Domain Warden
📂 **Context:** Feature domain/routes removed
🎯 **Command:** Update DNS/domain config if feature had dedicated domain
📐 **Format:** Updated domain config

### 3. Cost Optimizer — @ops-cost-optimizer
🎭 **Role:** Cost Optimizer
📂 **Context:** Infrastructure removed
🎯 **Command:** Audit cost savings from removal. Report monthly savings
📐 **Format:** Cost savings report

## Handoff
→ `/gate-check 7`
