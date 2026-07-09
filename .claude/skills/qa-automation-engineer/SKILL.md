---
name: qa-automation-engineer
description: "Unit/integration/E2E — coverage ≥90% or build fails."
---
# Quality - Automation Engineer

Check test coverage meets ≥90% threshold.

## Tool
`.claude/tools/qa/automation-engineer/coverage-report.sh`

## When to use
- Gate 5 quality verification
- CI post-merge coverage check
- Before release sign-off
- Coverage regression tracking

## How to use
```bash
.claude/tools/qa/automation-engineer/coverage-report.sh --prj PRJ-XXXX [--threshold 90] [--tool pest|phpunit|pytest|jest]
```

## Input
PRJ-ID. Optional threshold (default 90) and test tool. Auto-detects PHPUnit, Pest, pytest, or Jest from project files.

## Output
Coverage percentage vs threshold. PASS (green) or FAIL (red) with actual metrics.

## Related
- `engine/agents/qa/qa-automation-engineer.md`
- `.claude/tools/qa/automation-engineer/coverage-report.sh`
