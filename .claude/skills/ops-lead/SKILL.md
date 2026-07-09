---
name: ops-lead
description: "DevOps Room Lead — confirms PASS before any deploy, Gate 6–7 owner."
---
# Operations - Room Lead

Check CI/CD pipeline health across project workflows.

## Tool
`.claude/tools/ops/lead/ci-status.sh`

## When to use
- Pre-deployment CI health check
- Post-push pipeline verification
- Periodic CI infra audit
- Multi-project CI status overview

## How to use
```bash
.claude/tools/ops/lead/ci-status.sh [--prj PRJ-XXXX] [--workflow <name>] [--check lint|test|build|scan]
```

## Input
Optional PRJ-ID (all projects if omitted). Optional workflow name filter and check type.

## Output
Per-workflow pass/fail showing lint, test, build, scan step status. Non-zero exit if any workflow failing.

## Related
- `engine/agents/ops/ops-lead.md`
- `.claude/tools/ops/lead/ci-status.sh`
