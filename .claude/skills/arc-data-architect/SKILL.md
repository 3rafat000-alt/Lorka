---
name: arc-data-architect
description: "Printed schema, ER diagram, every migration reversible."
---
# Architecture - Data Architect

Parse database migration files and output structured table/column/index mapping. Validate schema design against conventions.

## Tool
`.claude/tools/arc/data-architect/schema-map.sh`

## When to use
- Gate 3: produce schema map as part of architecture deliverables
- Migration review: verify columns, types, and indexes are correct
- Schema audit before Gate 5: check for missing indexes or wide tables

## How to use
```bash
.claude/tools/arc/data-architect/schema-map.sh <PRJ-ID> [--json]
```

## Input
- `PRJ-ID` — project directory with `database/migrations/`
- `--json` — output structured JSON instead of formatted table

## Output
- Per-migration: table name, columns with types, and index indicators
- JSON mode: machine-readable array of `{migration, table, columns}`
- Exit 0 on success, 1 if no migrations found

## Related
- `engine/agents/arc/data-architect.md`
- `.claude/tools/arc/data-architect/schema-map.sh`
