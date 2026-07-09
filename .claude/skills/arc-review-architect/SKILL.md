---
name: arc-review-architect
description: "4-pillar spec review + 7 steel rules (SEV first)."
---
# Architecture - Review Architect

Run 7 steel rules + 4-pillar spec review against a project. Gate-keeping gate: ensures every spec meets the minimum bar before implementation.

## Tool
`.claude/tools/arc/review-architect/spec-review.sh`

## When to use
- Gate 3 entry check: before architecture work begins
- Spec review: validate R1-R7 (frozen upstream, bounded, traceable, testable, security-vetted, rollback plan)
- Before Gate 4 handoff: confirmation that architecture package is reviewable

## How to use
```bash
.claude/tools/arc/review-architect/spec-review.sh <PRJ-ID>
```

## Input
- `PRJ-ID` — project with `docs/` directory containing upstream artifacts

## Output
- PASS/FAIL for each steel rule and each pillar
- `7 Steel Rules`: R1 (frozen upstream), R2 (one scope), R3 (bounded), R4 (traceable to journey), R5 (testable), R6 (security vet), R7 (rollback plan)
- `4 Pillars`: completeness, consistency, feasibility, reviewability
- Aggregate score with PASS/FAIL verdict (threshold: 80%)

## Related
- `engine/agents/arc/review-architect.md`
- `.claude/tools/arc/review-architect/spec-review.sh`
- `engine/protocols/spec-review.md`
