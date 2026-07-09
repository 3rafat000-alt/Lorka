---
name: dat-etl-engineer
description: "Import/export/sync as idempotent resumable batch operations."
---
# Data - ETL Engineer

Generate an idempotent ETL sync command with upsert logic. Creates a Laravel Artisan command that fetches from a source (api/db/csv) and upserts into a local table.

## Tool
`.claude/tools/dat/etl-engineer/idempotent-sync.sh`

## When to use
- New ETL pipeline: sync data from external API, database, or CSV into local storage
- Gate 4 data integration: set up idempotent sync with progress bar
- Scheduled sync: generate command ready for cron or Laravel scheduler

## How to use
```bash
.claude/tools/dat/etl-engineer/idempotent-sync.sh <PRJ-ID> <sync-name> [source]
```

## Input
- `PRJ-ID` — project directory
- `sync-name` — snake_case sync name (e.g. `orders`, `products`)
- `source` — `api` (default), `db`, or `csv`

## Output
- `app/Console/Commands/Sync{Name}.php` — Artisan command with:
  - `--force` flag to re-sync all records
  - `updateOrInsert` upsert logic keyed on `external_id`
  - Progress bar for visibility
  - Synced/skipped/failed counters
  - `fetchSource()` stub for source implementation
- Schedule hint: `$schedule->command('sync:{name}')->hourly()`

## Related
- `engine/agents/dat/etl-engineer.md`
- `.claude/tools/dat/etl-engineer/idempotent-sync.sh`
