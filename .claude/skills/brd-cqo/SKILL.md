---
name: brd-cqo
description: "CQO — responsible for Gate 5 (Quality) pass/k policy and verdict."
---
# Boardroom - Chief Quality Officer (CQO)

Gate 5 quality pass/kill — verify tests, coverage, lint, and TTI against the quality bar.

## Tool
`.claude/tools/brd/cqo/gate05-verify.sh`

## When to use
- Gate 5 transition: QA is complete, voting PASS or BLOCK
- Re-verify after fixes: confirm quality bar is met before staging deploy
- Periodic quality audit: check trending metrics
- Before any production release: quality gate must pass

## How to use
```bash
.claude/tools/brd/cqo/gate05-verify.sh <PRJ-ID> [--min-coverage <N>] [--max-tti <N>]
```

## Input
- `PRJ-ID` — project identifier
- `--min-coverage` — minimum test coverage percentage (default: 90)
- `--max-tti` — maximum time-to-interactive in seconds (default: 2.0)
- Reads `projects/<PRJ>/` for tests, coverage reports, and lint output

## Output
- Gate 5 checklist: test directory, coverage, lint pass, TTI threshold
- PASS/BLOCK verdict with score tally
- Exit code 0 if all checks pass

## Related
- `.claude/tools/brd/ceo/sofi-exec.sh --check-gate 5` — combined exec + quality check
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — adversarial re-check before staging
- `engine/DOCTRINE.md §6` — reversibility principle: coverage <90% rejected
