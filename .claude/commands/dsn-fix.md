---
description: "Fix design issue. /dsn-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `dsn-lead` — the main session *wears* this persona (`.claude/agents/dsn-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 DESIGN — FIX: $ARGUMENTS

## Delegation
Select relevant specialist per issue type:
- Flow bug → `@dsn-ux-architect`
- Screen bug → `@dsn-ui-designer`
- Copy bug → `@dsn-content-strategist`
- A11y violation → `@dsn-a11y-specialist`
- Motion issue → `@dsn-motion-designer`
- Brand issue → `@dsn-brand-designer`

🎭 **Role:** Appropriate design specialist
📂 **Context:** Issue: $ARGUMENTS · Gate 2
🎯 **Command:** Fix the specific design artifact. Document change. Re-check a11y matrix
📐 **Format:** Updated artifact + delta log

## Verification
`@dsn-a11y-specialist` — confirm WCAG still passes
`@dsn-lead` — sign fix

## Handoff
→ `/gate-check 2`
