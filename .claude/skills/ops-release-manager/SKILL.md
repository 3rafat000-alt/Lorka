---
name: ops-release-manager
description: "Blue/Green transitions, tested rollback — owns the return path."
---
# Operations - Release Manager

Blue/Green or rolling release with rollback plan.

## Tool
`.claude/tools/ops/release-manager/release.sh`

## When to use
- Production deploy execution
- Staged rollout to mitigate blast radius
- Release dry-run for verification
- Rollback procedure documentation

## How to use
```bash
.claude/tools/ops/release-manager/release.sh --prj PRJ-XXXX [--strategy blue-green|rolling] [--version v1.0.0] [--dry-run]
```

## Input
PRJ-ID. Strategy (blue-green default, rolling). Optional version tag. `--dry-run` prints steps without executing.

## Output
Execution plan printed to stdout. Blue-green: deploy green → health check → switch LB → keep blue as rollback. Rolling: ramp from 20% → 50% → 100%.

## Related
- `engine/agents/ops/ops-release-manager.md`
- `.claude/tools/ops/release-manager/release.sh`
