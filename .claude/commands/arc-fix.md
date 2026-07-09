---
description: "Fix architecture issue. /arc-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `arc-lead` — the main session *wears* this persona (`.claude/agents/arc-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

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
