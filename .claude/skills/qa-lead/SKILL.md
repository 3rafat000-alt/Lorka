---
name: qa-lead
description: "QA Room Lead — single unambiguous PASS/BLOCK verdict, Gate 5 owner."
---
# Quality - Room Lead

Generate PASS/BLOCK gate verdict with mechanical evidence.

## Tool
`.claude/tools/qa/lead/qa-verdict.sh`

## When to use
- Gate advance decision point
- Pre-deployment quality sign-off
- Release readiness check
- CI pipeline final gate

## How to use
```bash
.claude/tools/qa/lead/qa-verdict.sh --prj PRJ-XXXX --gate <N> [--coverage <pct>] [--tests <pass/total>] [--tti <ms>] [--output verdict.md]
```

## Input
PRJ-ID, gate number. Optional coverage percentage, test pass count, TTI. Checks brain artifacts exist, runs coverage + test + TTI validation.

## Output
PASS/BLOCK per check with stdout and optional markdown report. Exit 0 = all gates pass.

## Related
- `engine/agents/qa/qa-lead.md`
- `.claude/tools/qa/lead/qa-verdict.sh`
