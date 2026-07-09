---
description: "Fix/update knowledge docs. /knw-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `knw-lead` — the main session *wears* this persona (`.claude/agents/knw-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 KNOWLEDGE — FIX: $ARGUMENTS

## Delegation
Select specialist:
- Doc outdated/wrong → `@knw-doc-writer`
- ADR missing key decision → `@knw-historian`
- Brain stale/messy → `@knw-memory-curator`
- Lessons not captured → `@knw-reflector`

🎭 **Role:** Appropriate knowledge specialist
📂 **Context:** Issue: $ARGUMENTS · cross-gate
🎯 **Command:** Fix/update docs. Cite what changed, why, when. Compress if above threshold
📐 **Format:** Updated file · change log

## Handoff
→ Librarian reviews → `/gate-check knw`
