---
description: "Remove security-critical feature. /sec-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `sec-lead` — the main session *wears* this persona (`.claude/agents/sec-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ SECURITY — REMOVE: $ARGUMENTS

## Delegation

### 1. Compliance Auditor — @sec-compliance-auditor
🎭 **Role:** Compliance Auditor
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Update compliance map. Confirm no regulatory gaps from removal
📐 **Format:** Updated `docs/Compliance_Map.md`

### 2. Secrets Warden — @sec-secrets-warden
🎭 **Role:** Secrets Warden
📂 **Context:** Feature removed
🎯 **Command:** Verify no orphaned secrets. Rotate any that were scoped to feature
📐 **Format:** Rotation log

## Handoff
→ CSO notes → `/gate-check 5`
