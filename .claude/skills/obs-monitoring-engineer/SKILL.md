---
name: obs-monitoring-engineer
description: "Prometheus/Grafana/Sentry — every SLI is a live signal."
---
# Observability - Monitoring Engineer

Scaffold alert rule definition and runbook.

## Tool
`.claude/tools/obs/monitoring-engineer/alert-rule.sh`

## When to use
- New metric added — needs alert coverage
- Runbook creation for existing alert
- Alert review and standardization
- On-call onboarding documentation

## How to use
```bash
.claude/tools/obs/monitoring-engineer/alert-rule.sh --name error-rate --metric http_error_rate --condition '> 1%' --severity warning|critical [--runbook runbook.md]
```

## Input
Alert name, metric name, condition expression, severity. Generates structured runbook with symptoms, triage, mitigation, post-mortem sections.

## Output
Markdown runbook files in `projects/runbooks/`. Covers alert metadata, symptoms, triage checklist, mitigation steps, escalation path.

## Related
- `engine/agents/obs/obs-monitoring-engineer.md`
- `.claude/tools/obs/monitoring-engineer/alert-rule.sh`
