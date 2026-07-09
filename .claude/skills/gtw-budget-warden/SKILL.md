---
name: gtw-budget-warden
description: "Budget Warden — token budgets, circuit breakers, waste audit."
---
# Gateway - Budget Warden

Audit token efficiency — read route stamps, calculate waste score, and identify overspend.

## Tool
`.claude/tools/gtw/budget-warden/token-audit.sh`

## When to use
- Weekly token waste audit: summarise all delegations and their cost profiles
- Before a gate pass: verify the route economy is within budget for the gate
- When a project has unusually high token consumption: find the waste hot-spots
- CEO requests waste report: produce evidence of Teaching IV compliance

## How to use
```bash
.claude/tools/gtw/budget-warden/token-audit.sh <PRJ-ID> [--verbose]
```

## Input
- `PRJ-ID` — project identifier
- `--verbose` — detailed per-delegation breakdown
- Reads `projects/<PRJ>/_context/ROUTE_LOG.md` for route stamps
- Reads `projects/<PRJ>/_context/STATE.md` for current gate

## Output
- Token waste score with PASS/WARN/FAIL
- Per-delegation route audit (model used vs cheapest viable)
- Total routes logged, wasteful routes flagged
- Recommendations for economy improvement
- Exit code 0 if waste is within threshold

## Related
- `.claude/tools/gtw/router/route-stamp.sh` — produces the route stamps this tool audits
- `engine/routing/routing.yaml` — reference table for cheapest viable routes
- `engine/DOCTRINE.md §Teaching IV` — Token Economy
