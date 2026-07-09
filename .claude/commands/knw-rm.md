---
description: "Record knowledge after feature removal. /knw-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `knw-lead` — the main session *wears* this persona (`.claude/agents/knw-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ KNOWLEDGE — REMOVE: $ARGUMENTS

## Delegation

### 1. Historian — @knw-historian
🎭 **Role:** Historian — removal ADR
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Record ADR: what removed, when, why, rollback plan if reversal needed
📐 **Format:** Updated `docs/ADL.md`

### 2. Memory Curator — @knw-memory-curator
🎭 **Role:** Memory Curator — archive
📂 **Context:** Feature artifacts to archive
🎯 **Command:** Archive feature docs. Compress brain. Ensure no orphaned references
📐 **Format:** Archived docs · cleaned brain
