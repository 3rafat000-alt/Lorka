---
description: "Fix backend bug. /bck-fix <bug>"
argument-hint: "[description]"
---
> **Lead persona:** `bck-lead` — the main session *wears* this persona (`.claude/agents/bck-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 BACKEND — FIX: $ARGUMENTS

## Delegation
Select specialist per bug type:
- API bug → `@bck-api-engineer`
- Business logic → `@bck-domain-engineer`
- View bug → `@bck-blade-engineer`
- Queue bug → `@bck-queue-engineer`
- Integration bug → `@bck-integration-engineer`
- Tech debt → `@bck-refactoring-surgeon`

🎭 **Role:** Appropriate backend specialist
📂 **Context:** Bug: $ARGUMENTS · Gate 4
🎯 **Command:** Fix bug. Write regression test first (red → green). No behavior change without characterization test
📐 **Format:** Fix commit + regression test

## Code Review
`@bck-code-reviewer` — adversarial

## Handoff
→ Elif Kaya merges → `/qa-sweep "backend fix: $ARGUMENTS"`
