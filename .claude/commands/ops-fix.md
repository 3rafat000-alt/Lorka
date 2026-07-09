---
description: "Fix deployment/infrastructure issue. /ops-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `ops-lead` — the main session *wears* this persona (`.claude/agents/ops-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 DEVOPS — FIX: $ARGUMENTS

## Delegation
Select specialist:
- Pipeline failure → `@ops-cicd-engineer`
- Infra issue → `@ops-cloud-engineer`
- Release rollback → `@ops-release-manager`
- Domain/DNS issue → `@ops-domain-warden`
- Migration issue → `@ops-migration-runner`
- Cost overrun → `@ops-cost-optimizer`

🎭 **Role:** Appropriate ops specialist
📂 **Context:** Issue: $ARGUMENTS · Gate 6–7
🎯 **Command:** Fix issue. Verify fix in staging first. Document root cause and resolution
📐 **Format:** Fix commit · incident note

## Verification
→ `@ops-lead` confirm fix in staging
→ If prod-impacting: `/ops-rollback "$ARGUMENTS"` first

## Handoff
→ `/gate-check 6` or `7` depending on scope
