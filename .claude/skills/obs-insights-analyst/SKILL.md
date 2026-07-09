---
name: obs-insights-analyst
description: "Journey leak tracking → formal Gate 1 reopen."
---
# Observability - Insights Analyst

Detect journey leaks from telemetry and logs.

## Tool
`.claude/tools/obs/insights-analyst/journey-leak.sh`

## When to use
- Post-deploy funnel analysis
- UX drop-off root cause investigation
- Journey Map validation with real data
- Conversion funnel optimization

## How to use
```bash
.claude/tools/obs/insights-analyst/journey-leak.sh --prj PRJ-XXXX [--from-date 2026-07-01] [--journey-map docs/Journey_Map.md] [--logs dir]
```

## Input
PRJ-ID. Optional date range, Journey Map path, log directory. Parses Journey Map stages, then scans logs for transitions, errors, and drop-offs at each stage.

## Output
Per-stage leak report: transition count, error rate, drop-off rate. Stages with high drop-off flagged as leaks with recommended investigation.

## Related
- `engine/agents/obs/obs-insights-analyst.md`
- `.claude/tools/obs/insights-analyst/journey-leak.sh`
