---
name: brd-cpo
description: "CPO — responsible for Gates 0–2 (Inception, Discovery, Design), signs off on design freeze."
---
# Boardroom - Chief Product Officer (CPO)

Gate 2 (Design) signoff checklist — verify design deliverables exist and are frozen before build.

## Tool
`.claude/tools/brd/cpo/gate02-signoff.sh`

## When to use
- Gate 2 → 3 transition: confirm Prototype_Spec, Journey_Map, Design_System are complete
- Before any architecture work begins: verify design is frozen
- Re-verification after a design revision: confirm all artifacts updated
- Quality audit: check upstream deliverables exist

## How to use
```bash
.claude/tools/brd/cpo/gate02-signoff.sh <PRJ-ID>
```

## Input
- `PRJ-ID` — project identifier
- Reads `projects/<PRJ>/docs/` for design artifacts

## Output
- Checklist with ✓/✗ per deliverable
- Score summary (e.g. "3/4 deliverables present")
- Exit code 0 if all pass, non-zero if missing

## Related
- `.claude/tools/dsn/lead/design-freeze.sh` — counterpart to freeze artifacts before this check
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — adversarial re-check
- `.claude/tools/brd/ceo/sofi-exec.sh --check-gate 2` — combined exec + gate check
