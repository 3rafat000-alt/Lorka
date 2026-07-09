---
description: "Remove feature from mobile. /mob-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `mob-lead` — the main session *wears* this persona (`.claude/agents/mob-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ MOBILE — REMOVE: $ARGUMENTS

## Delegation

### 1. Flutter Engineer — @mob-flutter-engineer
🎭 **Role:** Flutter Engineer
📂 **Context:** Feature $ARGUMENTS to remove
🎯 **Command:** Remove feature directory. Update dependency injection. Remove routes/navigation
📐 **Format:** Cleaned codebase

### 2. State Engineer — @mob-state-engineer
🎭 **Role:** State Engineer
📂 **Context:** Feature blocs/stores removed
🎯 **Command:** Remove bloc files. Update Hydrated storage config
📐 **Format:** Cleaned state layer

## Handoff
→ João Silva merges → `/qa-sweep "mobile post-removal: $ARGUMENTS"`
