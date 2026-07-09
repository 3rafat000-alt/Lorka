---
name: obs-alerting-engineer
description: "Dry-tested alert rules — every alert paired 1:1 with a runbook."
---
# Observability - Alerting Engineer

Dry-test alert rule against metric history.

## Tool
`.claude/tools/obs/alerting-engineer/alert-test.sh`

## When to use
- Before deploying new alert rule
- Threshold tuning based on historical data
- Alert rule validation after metric changes
- SLO breach drill simulation

## How to use
```bash
.claude/tools/obs/alerting-engineer/alert-test.sh --rule runbook.md [--metric-values '99.5 98.0 99.9'] [--threshold 99.0]
```

## Input
Runbook file (reads condition) or explicit threshold + metric values. Simulates each value against threshold.

## Output
Per-value pass/fail with breach count. Shows alert fire rate = fired/total as percentage.

## Related
- `engine/agents/obs/obs-alerting-engineer.md`
- `.claude/tools/obs/alerting-engineer/alert-test.sh`
