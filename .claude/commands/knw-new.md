---
description: Create knowledge docs for new feature. /knw-new <feature>
agent: knw-lead
---

# 🆕 KNOWLEDGE — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. Doc Writer — @knw-doc-writer
🎭 **Role:** Doc Writer — guides
📂 **Context:** Feature built · gate-complete
🎯 **Command:** Write docs per Diataxis: reference, how-to, tutorial, explanation. README must answer first question in one screen
📐 **Format:** `README.md` · `docs/` guides

### 2. Historian — @knw-historian
🎭 **Role:** Historian — ADR
📂 **Context:** Feature delivery complete
🎯 **Command:** Record ADR: key decisions, date, rationale, alternatives considered. Link to frozen artifacts
📐 **Format:** Updated `docs/ADR.md`

### 3. Memory Curator — @knw-memory-curator
🎭 **Role:** Memory Curator — brain hygiene
📂 **Context:** All new docs + artifacts
🎯 **Command:** Update MEMORY.md routing map. Compress brain if above threshold. Enforce frontmatter discipline
📐 **Format:** Updated MEMORY.md · compressed brain

### 4. Reflector — @knw-reflector
🎭 **Role:** Reflector — lessons
📂 **Context:** Feature delivery complete
🎯 **Command:** Distil lessons from delivery. Patterns, anti-patterns, tooling gaps. Consolidate into procedural memory
📐 **Format:** `_context/LESSONS.md`

## Handoff
→ Librarian signs → `/gate-check knw`
