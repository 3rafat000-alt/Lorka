---
name: bck-queue-engineer
description: "Idempotent tasks, retry/backoff/DLQ, events, WebSocket channels."
---
# Backend - Queue Engineer

Generate a queued Laravel job class with retry/backoff configuration. Includes dispatchable interface, queue assignment, tags, and failure handler.

## Tool
`.claude/tools/bck/queue-engineer/job-scaffold.sh`

## When to use
- New async job: scaffold a ShouldQueue job with retry logic
- Gate 4 queue workers: create jobs for email, notifications, webhook dispatch
- Prototyping delayed processing: job scaffold with configurable tries and backoff

## How to use
```bash
.claude/tools/bck/queue-engineer/job-scaffold.sh <PRJ-ID> <JobName> [queue-name] [tries]
```

## Input
- `PRJ-ID` — project directory
- `JobName` — PascalCase job name (e.g. `ProcessPayment`)
- `queue-name` — queue channel (default: `default`)
- `tries` — max attempts (default: `3`)

## Output
- `app/Jobs/{JobName}.php` — job with `ShouldQueue`, `$tries`, `$backoff`, `tags()`, `handle()`, `failed()`
- Dispatch hint: `{JobName}::dispatch($data)`

## Related
- `engine/agents/bck/queue-engineer.md`
- `.claude/tools/bck/queue-engineer/job-scaffold.sh`
