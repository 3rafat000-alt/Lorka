---
name: knw-brain-query
description: "Retrieval: brain-query + grep-first file:line table."
---
# Knowledge - Brain Query

Grep + brain-query hybrid search across brain files.

## Tool
`.claude/tools/knw/brain-query/brain-search.sh`

## When to use
- Looking for past decision or reasoning
- "Did we discuss X before?" — quick brain lookup
- Finding who made a decision or ticket reference
- Context gathering before new work on familiar area

## How to use
```bash
.claude/tools/knw/brain-query/brain-search.sh --prj PRJ-XXXX --query 'search terms' [--mode grep|brain|hybrid] [--max 10]
```

## Input
PRJ-ID and search query. `--mode` selects search strategy: grep (regex in brain files), brain (cached index), hybrid (both merged). `--context` includes surrounding lines.

## Output
Matching lines from STATE.md, CONTEXT.md, DECISIONS.md, HANDOFFS.md, LESSONS.md grouped by file. Each result shows line number and context.

## Related
- `engine/agents/knw/knw-brain-query.md`
- `.claude/tools/knw/brain-query/brain-search.sh`
