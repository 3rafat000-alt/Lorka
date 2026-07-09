---
name: knw-reflector
description: "Distil lessons from deliveries (scheduled reflection, not per-turn)."
---
# Knowledge - Reflector

Distil HANDOFFS history into LESSONS.md.

## Tool
`.claude/tools/knw/reflector/distil-lessons.sh`

## When to use
- After a batch of tickets completed
- Pre-retro lesson extraction
- Knowledge transfer between squads
- Handoff closure — capture what was learned

## How to use
```bash
.claude/tools/knw/reflector/distil-lessons.sh --prj PRJ-XXXX [--output LESSONS.md] [--max 10]
```

## Input
PRJ-ID. Parses HANDOFFS.md for blocker, failure, error, fix, resolved, and workaround patterns. `--max` caps lesson count.

## Output
LESSONS.md with sections: Blockers, Fixes, Workarounds, Patterns. Each lesson tagged with source ticket reference.

## Related
- `engine/agents/knw/knw-reflector.md`
- `.claude/tools/knw/reflector/distil-lessons.sh`
