---
name: dat-cache-engineer
description: "Redis layer + stampede-safe invalidation."
---
# Data - Cache Engineer

Generate a Redis cache strategy document with key naming, TTL tiers, invalidation plan, and tag-based flushing. Optionally scan existing code for current Cache:: usage.

## Tool
`.claude/tools/dat/cache-engineer/cache-strategy.sh`

## When to use
- Gate 3–4 cache planning: document cache architecture before implementation
- Performance audit: analyze existing cache usage and recommend improvements
- New caching layer: generate strategy with key format, TTL, and invalidation rules

## How to use
```bash
.claude/tools/dat/cache-engineer/cache-strategy.sh <PRJ-ID> [--analyze]
```

## Input
- `PRJ-ID` — project directory
- `--analyze` — scan `app/` for existing `Cache::` or `cache()` calls first

## Output
- `docs/cache-strategy.md` with YAML frontmatter:
  - Redis configuration (host, port, prefix)
  - Cache key format (`{prefix}:{type}:{id}`)
  - TTL strategy: default (3600s), hot data (300s), cold data (86400s), session (7200s)
  - Invalidation triggers: on save, on bulk update, on schema change
  - Tag suggestions for grouped invalidation
- `--analyze`: current cache usage report with line-level references

## Related
- `engine/agents/dat/cache-engineer.md`
- `.claude/tools/dat/cache-engineer/cache-strategy.sh`
