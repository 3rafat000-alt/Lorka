---
name: obs-lead
description: "Observability Room Lead — every SLO breach reopens Gate 1, Gate 8 owner."
---
# Observability - Room Lead

Generate SLI/SLO dashboard for a project.

## Tool
`.claude/tools/obs/lead/slo-dashboard.sh`

## When to use
- Gate 8 observability setup
- SLO definition and tracking initialization
- Service-level review meetings
- Post-incident reliability baseline

## How to use
```bash
.claude/tools/obs/lead/slo-dashboard.sh --prj PRJ-XXXX [--sli 'latency < 200ms:99.9%'] [--output dashboard.md]
```

## Input
PRJ-ID. Repeatable `--sli` flags define SLI name, target value, SLO percentage. Defaults: latency P99 < 200ms:99.9%, error rate < 1%:99.5%, uptime > 99.9%:99.95%.

## Output
Markdown table with SLI | Target | SLO | Status columns. Writes to stdout or file.

## Related
- `engine/agents/obs/obs-lead.md`
- `.claude/tools/obs/lead/slo-dashboard.sh`
