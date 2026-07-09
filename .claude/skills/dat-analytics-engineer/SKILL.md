---
name: dat-analytics-engineer
description: "Exported event pipelines + reproducible product metric models."
---
# Data - Analytics Engineer

Scaffold an analytics event model, migration, and fillable fields. Creates an Eloquent model under `Analytics` namespace and a timestamped migration for the analytics table.

## Tool
`.claude/tools/dat/analytics-engineer/event-pipeline.sh`

## When to use
- New analytics event: track page views, button clicks, API calls
- Gate 4 data layer: set up structured event tracking
- Product metrics: instrument user actions for funnel analysis

## How to use
```bash
.claude/tools/dat/analytics-engineer/event-pipeline.sh <PRJ-ID> <event-name> [fields...]
```

## Input
- `PRJ-ID` — project directory
- `event-name` — snake_case event name (e.g. `page_view`, `button_click`)
- `fields` — comma-separated field names (e.g. `user_id,page,referrer`)

## Output
- `app/Models/Analytics/{Pascal}.php` — Eloquent model with fillable, casts, and table name
- `database/migrations/{timestamp}_create_analytics_{name}_table.php` — migration with id, field columns, occurred_at, timestamps
- Rollback: `Schema::dropIfExists('analytics_{name}')`

## Related
- `engine/agents/dat/analytics-engineer.md`
- `.claude/tools/dat/analytics-engineer/event-pipeline.sh`
