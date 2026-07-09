---
name: dsn-lead
description: "Design Room Lead — owns Gate 2 freeze, Room gateway."
---
# Design - Lead

Freeze all design artifacts and sign Gate 2 — the point of no return for visual decisions.

## Tool
`.claude/tools/dsn/lead/design-freeze.sh`

## When to use
- Gate 2 → 3 transition: all design work is complete, freeze for architecture
- After prototype signoff: stamp DESIGN-FREEZE in HANDOFFS.md and STATE.md
- Before parallel build squads are dispatched: no design changes after freeze
- Enforce Teaching I (Design is Truth): after freeze, no visual change without new Gate 2

## How to use
```bash
.claude/tools/dsn/lead/design-freeze.sh <PRJ-ID> [--force]
```

## Input
- `PRJ-ID` — project identifier
- `--force` — freeze even if some files are missing (use when re-freezing an existing project)
- Checks for: Prototype_Spec.md, Journey_Map.md, Design_System.md, screen specs

## Output
- Pass/Fail checklist of required design artifacts
- DESIGN-FREEZE timestamp stamped into HANDOFFS.md
- STATE.md gate advanced to 3
- Exit code 0 if all required files exist (or --force), non-zero otherwise

## Related
- `.claude/tools/brd/cpo/gate02-signoff.sh` — CPO verifies freeze quality
- `.claude/tools/gtw/gatekeeper/gate-check.sh --gate 2` — adversarial re-check
- Room agents: .claude/tools/dsn/ui-designer, ux-architect, design-system, brand-designer, a11y-specialist
