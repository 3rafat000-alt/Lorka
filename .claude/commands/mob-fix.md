---
description: "Fix mobile bug. /mob-fix <bug>"
argument-hint: "[description]"
---
> **Lead persona:** `mob-lead` — the main session *wears* this persona (`.claude/agents/mob-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 MOBILE — FIX: $ARGUMENTS

## Delegation
Select specialist per bug type:
- Widget/feature bug → `@mob-flutter-engineer`
- State bug → `@mob-state-engineer`
- Platform bug → `@mob-platform-engineer`
- Performance issue → `@mob-perf-profiler`

🎭 **Role:** Appropriate mobile specialist
📂 **Context:** Bug: $ARGUMENTS · Gate 4
🎯 **Command:** Fix bug. Regression test. Profile before/after if perf impact
📐 **Format:** Fix commit + test + perf delta

## Handoff
→ João Silva merges → `/qa-sweep "mobile fix: $ARGUMENTS"`
