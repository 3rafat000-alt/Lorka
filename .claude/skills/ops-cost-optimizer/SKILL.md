---
name: ops-cost-optimizer
description: "Infrastructure economics — waste and over-provisioning by evidence."
---
# Operations - Cost Optimizer

Infrastructure cost analysis by provider.

## Tool
`.claude/tools/ops/cost-optimizer/cost-report.sh`

## When to use
- Monthly infrastructure cost review
- Provider cost comparison
- Budget vs actual tracking
- Right-sizing analysis

## How to use
```bash
.claude/tools/ops/cost-optimizer/cost-report.sh [--prj PRJ-XXXX] [--provider aws|gcp|do|all] [--budget monthly_usd] [--output report.md]
```

## Input
PRJ-ID optional. Provider filter. Budget cap. Analyzes docker-compose/k8s/terraform for resource hints and estimates cost.

## Output
Per-provider cost table with compute/storage/network estimates. Budget comparison with overspend flag. Optional markdown report.

## Related
- `engine/agents/ops/ops-cost-optimizer.md`
- `.claude/tools/ops/cost-optimizer/cost-report.sh`
