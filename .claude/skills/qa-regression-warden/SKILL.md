---
name: qa-regression-warden
description: "Test suite health, flaky quarantine, flaky test stone."
---
# Quality - Regression Warden

Detect and quarantine flaky tests by running suite N times.

## Tool
`.claude/tools/qa/regression-warden/flaky-detect.sh`

## When to use
- CI suite showing intermittent failures
- Pre-release stability gate
- Test suite health monitoring
- After large refactors touching test fixtures

## How to use
```bash
.claude/tools/qa/regression-warden/flaky-detect.sh --prj PRJ-XXXX [--runs 5] [--threshold 2]
```

## Input
PRJ-ID. `--runs` (default 5) times to repeat suite. `--threshold` (default 2) failures to classify as flaky. Auto-detects PHPUnit/Pest/pytest/Jest.

## Output
Per-test pass/fail across runs. Lists flaky tests (passed fewer times than `--runs` minus `--threshold`). Exit non-zero if flaky tests found.

## Related
- `engine/agents/qa/qa-regression-warden.md`
- `.claude/tools/qa/regression-warden/flaky-detect.sh`
