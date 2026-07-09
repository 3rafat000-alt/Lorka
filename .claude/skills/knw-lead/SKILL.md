---
name: knw-lead
description: "Knowledge Room Lead (The Librarian) — owns MEMORY.md routing map and brain governance."
---
# Knowledge - Room Lead (The Librarian)

Sync knowledge across memory files: check brain health and consistency.

## Tool
`.claude/tools/knw/lead/knowledge-sync.sh`

## When to use
- Session start — verify brain integrity before work
- After any brain mutation (STATE/CONTEXT/DECISIONS/HANDOFFS edits)
- Pre-handoff brain consistency check
- Multi-session continuity verification

## How to use
```bash
.claude/tools/knw/lead/knowledge-sync.sh --prj PRJ-XXXX [--check lessons|decisions|state|all] [--dry-run]
```

## Input
PRJ-ID. `--check` narrows to specific brain files or all. Validates STATE.md, CONTEXT.md, DECISIONS.md, HANDOFFS.md, LESSONS.md exist and have content.

## Output
Per-file health: present (lines count) or missing. Flags stale or empty files. Dry-run mode shows what would change.

## Related
- `engine/agents/knw/knw-lead.md`
- `.claude/tools/knw/lead/knowledge-sync.sh`
