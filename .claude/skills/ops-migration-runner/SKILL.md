---
name: ops-migration-runner
description: "Deploy-time migrations only after proven rollback rehearsal on staging data."
---
# Operations - Migration Runner

Test migration rollback on staging data.

## Tool
`.claude/tools/ops/migration-runner/rollback-test.sh`

## When to use
- Before prod migration execution
- Verifying rollback procedure works
- Doctrine Teaching VI — Reversibility Principle
- Schema change with data transformation

## How to use
```bash
.claude/tools/ops/migration-runner/rollback-test.sh --prj PRJ-XXXX [--db staging_db_name] [--migration <name>] [--all]
```

## Input
PRJ-ID. Optional DB name, specific migration class, or `--all` to test full cycle. For Laravel projects, uses artisan migrate + migrate:rollback.

## Output
Pre/rollback schema diff report. Shows backup taken, rollback executed, and verification that DB returned to pre-migration state.

## Related
- `engine/agents/ops/ops-migration-runner.md`
- `.claude/tools/ops/migration-runner/rollback-test.sh`
