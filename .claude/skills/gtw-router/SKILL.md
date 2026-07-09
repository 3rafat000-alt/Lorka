---
name: gtw-router
description: "Router — applies cost grid, stamps route before every model call."
---
# Gateway - Router

Log model·effort·caveman routing decision before every delegation to audit token economy.

## Tool
`.claude/tools/gtw/router/route-stamp.sh`

## When to use
- Before every subagent spawn: log the route dials to enforce Teaching IV (Token Economy)
- When choosing which model/effort/caveman level to use for a task
- Audit trail: record every delegation's cost profile for weekly waste review
- After a task completes: verify the route was appropriate (cheapest that cleared the bar)

## How to use
```bash
.claude/tools/gtw/router/route-stamp.sh <PRJ-ID> --role <agent-role> [--model <model>] [--effort <low|medium|high|max>] [--caveman <off|lite|full|ultra>]
```

## Input
- `PRJ-ID` — project identifier
- `--role` — agent role name (e.g. backend-blade-engineer)
- `--model`, `--effort`, `--caveman` — optional overrides
- Reads `engine/routing/routing.yaml` for per-role defaults

## Output
- Timestamped route entry appended to `projects/<PRJ>/_context/ROUTE_LOG.md`
- Calculated waste score if defaults are overridden above the cheapest viable level
- Exit code 0 if route logged

## Related
- `.claude/tools/gtw/budget-warden/token-audit.sh` — summarise all route stamps into waste report
- `engine/routing/routing.yaml` — master routing table
- `engine/DOCTRINE.md §Teaching IV` — Token Economy
