---
description: "Remove feature from research. /res-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `res-lead` — the main session *wears* this persona (`.claude/agents/res-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ RESEARCH — REMOVE: $ARGUMENTS

## Delegation

### 1. Journey Architect — @res-journey-architect
🎭 **Role:** Journey Architect
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Remove from Journey Map. Document flow changes
📐 **Format:** Updated `docs/Journey_Map.md`

### 2. UX Researcher — @res-ux-researcher
🎭 **Role:** UX Researcher
📂 **Context:** Feature removed
🎯 **Command:** Archive affected personas or update pain/gain map
📐 **Format:** Updated `docs/Personas.md`

## Handoff
→ CPO signs → `/gate-check 1`
