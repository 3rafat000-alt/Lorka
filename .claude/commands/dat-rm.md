---
description: "Remove feature data. /dat-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `dat-lead` — the main session *wears* this persona (`.claude/agents/dat-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ DATA — REMOVE: $ARGUMENTS

## Delegation

### 1. Database Engineer — @dat-db-engineer
🎭 **Role:** Database Engineer
📂 **Context:** Feature $ARGUMENTS data to remove
🎯 **Command:** Create reversible removal migration. Archive data per retention policy
📐 **Format:** Migration file · rollback script

### 2. Privacy Officer — @dat-privacy-officer
🎭 **Role:** Privacy Officer
📂 **Context:** Data removed
🎯 **Command:** Update privacy map. Confirm deletion meets regulatory requirements
📐 **Format:** Updated `docs/Privacy_Map.md`

### 3. Cache Engineer — @dat-cache-engineer
🎭 **Role:** Cache Engineer
📂 **Context:** Feature cache keys to remove
🎯 **Command:** Remove stale cache keys. Update invalidation logic
📐 **Format:** Cleaned cache config

## Handoff
→ Günther Weber merges → `/qa-sweep "data post-removal: $ARGUMENTS"`
