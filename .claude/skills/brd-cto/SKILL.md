---
name: brd-cto
description: "CTO — responsible for Gates 3–4 (Architecture + Build), signs architecture package."
---
# Boardroom - Chief Technology Officer (CTO)

Gate 3-4 signoff — verify architecture blueprints, ADRs, OpenAPI specs, and build readiness.

## Tool
`.claude/tools/brd/cto/gate34-signoff.sh`

## When to use
- Gate 3 → 4 transition: architecture is complete, build is about to start
- Gate 4 → 5 transition: build is complete, ready for QA
- Before parallel build squads are dispatched: verify architecture is frozen
- Mid-build check: verify code quality and schema docs are current

## How to use
```bash
.claude/tools/brd/cto/gate34-signoff.sh <PRJ-ID>
```

## Input
- `PRJ-ID` — project identifier
- Reads `projects/<PRJ>/docs/Architecture.md`, OpenAPI specs, ADRs, source tree

## Output
- Gate 3 checklist (Architecture Blueprint, ADRs, data flow diagrams, OpenAPI)
- Gate 4 checklist (build passing, schema docs, migration rollbacks)
- PASS/FAIL per gate with exit code

## Related
- `.claude/tools/brd/cqo/gate05-verify.sh` — next gate after build
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — adversarial re-check
- `.claude/tools/arc/...` — architecture room tools
