---
description: Fix architecture issue. /arc-fix <issue>
agent: arc-lead
---

# 🔧 ARCHITECTURE — FIX: $ARGUMENTS

## Delegation
Select relevant specialist:
- System flaw → `@arc-system-architect`
- Schema flaw → `@arc-data-architect`
- API flaw → `@arc-api-architect`
- Integration flaw → `@arc-integration-architect`
- Infra flaw → `@arc-infra-architect`

🎭 **Role:** Appropriate architect
📂 **Context:** Issue: $ARGUMENTS · Gate 3
🎯 **Command:** Fix architecture artifact. Update ADR. Ensure rollback plan exists
📐 **Format:** Updated artifact + ADR entry

## Verification
`@arc-review-architect` — adversarial re-review

## Handoff
→ Vikram Rao signs → `/gate-check 3`