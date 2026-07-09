---
name: knw-memory-curator
description: "Brain hygiene, caveman compression above threshold, frontmatter discipline."
---
# Knowledge - Memory Curator

Compress brain files (caveman format) to save tokens.

## Tool
`.claude/tools/knw/memory-curator/brain-compress.sh`

## When to use
- Brain file growing beyond efficient token budget
- Monthly brain maintenance
- Before session with large context load
- After many small decisions accumulated

## How to use
```bash
.claude/tools/knw/memory-curator/brain-compress.sh --prj PRJ-XXXX [--file CONTEXT.md|STATE.md|DECISIONS.md] [--backup]
```

## Input
PRJ-ID. Optional file filter (default all brain files). `--backup` preserves original as `.bak`. Strips filler, preserves frontmatter, compresses verbosity while keeping all facts and decisions.

## Output
Compressed file written in place (or backed up). Reports lines before/after and savings percentage.

## Related
- `engine/agents/knw/knw-memory-curator.md`
- `.claude/tools/knw/memory-curator/brain-compress.sh`
