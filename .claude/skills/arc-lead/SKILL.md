---
name: arc-lead
description: "Architecture Room Lead — assembles and signs frozen Gate 3 package."
---
# Architecture - Room Lead (Vikram Rao)

Assemble and sign Gate 3 architecture package. Verifies all upstream deliverables exist before freezing architecture.

## Tool
`.claude/tools/arc/lead/arch-signoff.sh`

## When to use
- Gate 3 signoff: confirm Project_Blueprint, Journey_Map, Prototype_Spec, component diagram, migrations, and API spec exist
- `--check-only` audit before a formal signoff attempt
- Architecture freeze milestone — no structural changes without ADR after this

## How to use
```bash
.claude/tools/arc/lead/arch-signoff.sh <PRJ-ID> [--check-only]
```

## Input
- `PRJ-ID` — project directory under `projects/`
- `--check-only` — audit only, don't write signoff file

## Output
- PASS/FAIL per required artifact (blueprint, journey map, prototype, component diagram, migrations, OpenAPI spec)
- Gate 3 signoff written to `_context/signoffs/gate3-signoff.md` on full pass
- Exit 0 on pass, 1 on failure

## Related
- `engine/agents/arc/lead.md`
- `.claude/tools/arc/lead/arch-signoff.sh`
