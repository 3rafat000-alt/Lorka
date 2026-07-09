---
name: dat-lead
description: "Data Room Lead — Gate 3 partner and Gate 4 support."
---
# Data - Room Lead (Günther Weber)

Generate a data plan from Gate 3 architecture artifacts. Produces a comprehensive plan covering database, cache strategy, analytics events, data retention, and backup schedule.

## Tool
`.claude/tools/dat/lead/data-plan.sh`

## When to use
- Gate 3–4 transition: generate data plan from architecture artifacts
- New project setup: document database engine, caching, analytics pipeline
- Architecture review: assess existing data strategy for gaps

## How to use
```bash
.claude/tools/dat/lead/data-plan.sh <PRJ-ID>
```

## Input
- `PRJ-ID` — project directory (reads migrations, models, OpenAPI spec)

## Output
- `docs/data-plan.md` with sections:
  - Database: engine, migration/model counts, relationships
  - Cache Strategy: Redis config, TTL defaults
  - Analytics Events: tracking approach and pipeline
  - Data Retention: active/soft-delete/log rotation policies
  - Backup Schedule: daily/weekly/DR frequency
  - Security: encryption method, PII casting recommendation

## Related
- `engine/agents/dat/lead.md`
- `.claude/tools/dat/lead/data-plan.sh`
