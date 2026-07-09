---
name: qa-test-architect
description: "Risk classification, test pyramid, pass/k policy for Tier-A surfaces."
---
# Quality - Test Architect

Generate test plan from architecture spec.

## Tool
`.claude/tools/qa/test-architect/test-plan.py`

## When to use
- Gate 3 handoff to Gate 4 — test strategy needed
- New API endpoint or feature spec finalized
- Pre-refactoring regression test inventory
- Coverage gap analysis

## How to use
```bash
.claude/tools/qa/test-architect/test-plan.py --spec spec.yaml [--output test-plan.json]
```

## Input
Architecture spec (YAML). Parses endpoints, methods, classes, functions. Maps each to a test suite + test case + type (unit, integration, e2e).

## Output
Structured test plan JSON with test name, type, coverage target, and priority per spec element.

## Related
- `engine/agents/qa/qa-test-architect.md`
- `.claude/tools/qa/test-architect/test-plan.py`
