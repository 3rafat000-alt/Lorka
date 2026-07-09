---
description: "Fix frontend bug. /fnt-fix <bug>"
argument-hint: "[description]"
---
> **Lead persona:** `fnt-lead` — the main session *wears* this persona (`.claude/agents/fnt-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 FRONTEND — FIX: $ARGUMENTS

## Delegation
Select specialist per bug type:
- Component bug → `@fnt-vue-engineer` or `@fnt-react-engineer`
- CSS bug → `@fnt-css-artisan`
- Interaction bug → `@fnt-interaction-engineer`
- A11y bug → `@fnt-a11y-engineer`
- Performance issue → `@fnt-performance-engineer`

🎭 **Role:** Appropriate frontend specialist
📂 **Context:** Bug: $ARGUMENTS · Gate 4
🎯 **Command:** Fix bug. Add regression test. Verify a11y still passes. Verify responsive still works
📐 **Format:** Fix commit + test

## Code Review
`@fnt-code-reviewer` — adversarial

## Handoff
→ Grace Achieng merges → `/qa-sweep "frontend fix: $ARGUMENTS"`
