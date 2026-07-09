---
name: ops-cloud-engineer
description: "Environments as IaC, staging≈prod parity, teardown before provision."
---
# Operations - Cloud Engineer

Compare staging/prod environment parity.

## Tool
`.claude/tools/ops/cloud-engineer/env-sync.sh`

## When to use
- Staging → prod deploy prep
- Debugging env-specific failures
- Onboarding new environment
- Post-migration parity verification

## How to use
```bash
.claude/tools/ops/cloud-engineer/env-sync.sh --prj PRJ-XXXX [--staging .env.staging] [--production .env.production] [--ignore APP_KEY,DB_PASSWORD]
```

## Input
PRJ-ID. Points to staging and production env files. Can ignore value-different-but-should-be fields.

## Output
Per-variable diff: missing vars, different values, extra vars. Shows which values differ beyond ignored keys.

## Related
- `engine/agents/ops/ops-cloud-engineer.md`
- `.claude/tools/ops/cloud-engineer/env-sync.sh`
