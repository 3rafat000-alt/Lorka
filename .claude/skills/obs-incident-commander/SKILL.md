---
name: obs-incident-commander
description: "Triage → rollback-or-fix-forward → no-blame postmortem."
---
# Observability - Incident Commander

Triage incident → rollback or fix-forward decision.

## Tool
`.claude/tools/obs/incident-commander/incident-triage.sh`

## When to use
- Production incident response
- Severity classification drill
- Post-incident runbook validation
- On-call incident simulation training

## How to use
```bash
.claude/tools/obs/incident-commander/incident-triage.sh --alert 'description' --severity sev1|sev2|sev3 [--prj PRJ-XXXX] [--auto]
```

## Input
Alert description, severity (sev1=5min, sev2=15min, sev3=1hr SLA). Optional project and auto mode.

## Output
Structured triage output: SLA, recommended action (rollback/fix-forward), checklist (acknowledge, blast radius, tag version, notify, log).

## Related
- `engine/agents/obs/obs-incident-commander.md`
- `.claude/tools/obs/incident-commander/incident-triage.sh`
