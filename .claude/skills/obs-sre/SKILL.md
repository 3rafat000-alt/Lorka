---
name: obs-sre
description: "SLI/SLO definitions, error budgets per critical path."
---
# Observability - SRE

Calculate SLI from raw metric counts.

## Tool
`.claude/tools/obs/sre/sli-calc.sh`

## When to use
- SLI computation from monitoring data
- Error budget calculation
- Reliability reporting
- Service level attainment verification

## How to use
```bash
.claude/tools/obs/sre/sli-calc.sh --metric latency|error_rate|uptime|throughput --total <N> --good <N> [--window 5m]
```

## Input
Metric name, total events, good events, optional window. Computes SLI = (good / total) × 100.

## Output
SLI percentage with total/good/bad breakdown. Exit 0 if SLI ≥ SLO threshold.

## Related
- `engine/agents/obs/obs-sre.md`
- `.claude/tools/obs/sre/sli-calc.sh`
