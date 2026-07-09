---
name: sec-incident-responder
description: "Incident playbooks, containment, no-blame postmortem opens Gate 1 ticket."
---
# Security - Incident Responder

Generate structured incident playbook from scenario template.

## Tool
`.claude/tools/sec/incident-responder/playbook.sh`

## When to use
- Security incident readiness drilling
- Post-incident playbook creation
- SOC runbook generation
- Tabletop exercise prep

## How to use
```bash
.claude/tools/sec/incident-responder/playbook.sh --scenario breach|dos|leak|insider|ransomware [--output playbook.md]
```

## Input
Scenario name. Optionally `--output` to write playbook file. Each scenario covers detection, triage, containment, eradication, recovery, post-mortem.

## Output
Structured markdown playbook with actionable checklist per phase. Writes to stdout or file.

## Related
- `engine/agents/sec/sec-incident-responder.md`
- `.claude/tools/sec/incident-responder/playbook.sh`
