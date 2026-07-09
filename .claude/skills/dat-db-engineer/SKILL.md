---
name: dat-db-engineer
description: "Reversible migrations, EXPLAIN on hot paths, indexes, N+1 kill."
---
# Data - Database Engineer

Analyze migration files and suggest consolidation grouping by table. Identifies tables with multiple migration files that could be merged into one.

## Tool
`.claude/tools/dat/db-engineer/migration-consolidate.sh`

## When to use
- Migration cleanup: before Gate 5, consolidate fragmented migration history
- Large projects: hundreds of migrations on a single table signal consolidation need
- Dry-run first: review consolidation plan before any file modification

## How to use
```bash
.claude/tools/dat/db-engineer/migration-consolidate.sh <PRJ-ID> [--dry-run]
```

## Input
- `PRJ-ID` — project directory with `database/migrations/`
- `--dry-run` — show consolidation candidates without modifying files

## Output
- Per-table consolidation candidates: tables with >1 migration file
- Total migration count
- Consolidation summary: how many tables have merge candidates
- Dry-run mode: hints for manual merge and `migrate:fresh` command

## Related
- `engine/agents/dat/db-engineer.md`
- `.claude/tools/dat/db-engineer/migration-consolidate.sh`
