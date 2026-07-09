---
description: "Remove feature from architecture. /arc-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `arc-lead` — the main session *wears* this persona (`.claude/agents/arc-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ ARCHITECTURE — REMOVE: $ARGUMENTS

## Delegation

### 1. System Architect — @arc-system-architect
🎭 **Role:** System Architect
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Update component diagram. Remove components. Document architectural impact
📐 **Format:** Updated `docs/System_Architecture.md` · ADR

### 2. API Architect — @arc-api-architect
🎭 **Role:** API Architect — deprecation
📂 **Context:** Feature endpoints to remove
🎯 **Command:** Produce API deprecation plan (soft deprecate → migrate → hard remove). Timeline + headers
📐 **Format:** Updated `docs/API_Contract.yaml` · deprecation schedule

### 3. Data Architect — @arc-data-architect
🎭 **Role:** Data Architect — data removal
📂 **Context:** Feature data to archive/delete
🎯 **Command:** Design data migration/archival plan. Reversible
📐 **Format:** Updated `docs/Data_Architecture.md` · rollback script

## Handoff
→ Vikram Rao signs → `/gate-check 3`
