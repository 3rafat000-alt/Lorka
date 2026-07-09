---
name: str-roadmap-planner
description: "Milestones, backlog, fast-track/deep-audit classification."
---
# Strategy - Roadmap Planner

Generate milestone timeline from the SOFI 9-gate lifecycle with configurable start date and gate duration.

## Tool
`.claude/tools/str/roadmap-planner/milestones.sh`

## When to use
- Gate 0 inception: create a project timeline after the Blueprint is approved
- Sprint planning: project expected gate progression dates
- Stakeholder communication: visual timeline of milestones
- Re-planning: adjust timeline after scope change or delay

## How to use
```bash
.claude/tools/str/roadmap-planner/milestones.sh <PRJ-ID> [--start-date YYYY-MM-DD] [--days-per-gate N]
```

## Input
- `PRJ-ID` — project identifier
- `--start-date` — project start date (default: today)
- `--days-per-gate` — days allocated per gate (default: 5)
- Reads `projects/<PRJ>/_context/STATE.md` for current gate alignment

## Output
- Gate-by-gate milestone table with start and end dates
- 9 gates: Inception, Discovery, Design, Architecture, Build, Quality, Staging, Production, Observe
- Exit code 0

## Related
- `.claude/tools/str/lead/blueprint-init.sh` — upstream: Blueprint defines scope that drives timeline
- `sofi-v6-gate-flow` — the gate lifecycle this tool schedules
- `.claude/tools/gtw/budget-warden/token-audit.sh` — time + token budget tracking
