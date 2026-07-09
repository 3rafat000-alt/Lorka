---
description: Document new feature across knowledge room. /knw-doc <feature>
agent: knw-lead
---

# 📚 KNOWLEDGE — DOCUMENT: $ARGUMENTS

## Delegation

### 1. Doc Writer — @knw-doc-writer
🎭 **Role:** Doc Writer — README + guides
📂 **Context:** Feature complete · cross-gate
🎯 **Command:** Write docs: README answering first question in one screen. Follow Diataxis (reference/how-to/tutorial/explanation). Never duplicate
📐 **Format:** `docs/README.md` · `docs/guides/`

### 2. Historian — @knw-historian
🎭 **Role:** Historian — ADR + decision log
📂 **Context:** All decisions made during $ARGUMENTS lifecycle
🎯 **Command:** Record ADR entries: what, why, alternatives considered, rollback plan. Trace to work orders
📐 **Format:** Updated `docs/ADL.md` · `docs/DECISIONS.md`

### 3. Memory Curator — @knw-memory-curator
🎭 **Role:** Memory Curator — brain hygiene
📂 **Context:** All $ARGUMENTS artifacts
🎯 **Command:** Compress oversized context files. Enforce frontmatter. Archive stale artifacts
📐 **Format:** Cleaned brain files

### 4. Reflector — @knw-reflector
🎭 **Role:** Reflector — lessons distilled
📂 **Context:** Feature delivery complete
🎯 **Command:** Run reflection pass: what worked, what failed, what to change. Max 3 lessons
📐 **Format:** Updated `docs/LESSONS.md`

### 5. Brain Query — @knw-brain-query
🎭 **Role:** Brain Query — search index
📂 **Context:** New documentation created
🎯 **Command:** Index new docs. Ensure grep+brain-query can find them
📐 **Format:** Searchability verification