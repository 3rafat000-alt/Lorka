---
name: dsn-brand-designer
description: "Taste metrics, anti-generic-UI guardrails."
---
# Design - Brand Designer

Evaluate design against anti-generic-UI taste dials — typography, colour, spacing, motion, personality.

## Tool
`.claude/tools/dsn/brand-designer/taste-meter.sh`

## When to use
- Gate 2 Design: establish or verify the brand personality before handoff
- After initial UI concepts: score against taste dials to avoid generic output
- Design review gate: every screen must score above threshold on taste meter
- Brand identity pivot: re-evaluate dials after a strategic direction change

## How to use
```bash
.claude/tools/dsn/brand-designer/taste-meter.sh <PRJ-ID> [--check]
```

## Input
- `PRJ-ID` — project identifier
- `--check` — run interactive scoring (default: print dials without scoring)
- Reads design artifacts in `projects/<PRJ>/docs/`

## Output
- Taste dials display: Typography, Color, Spacing, Motion, Personality, Border/Radius
- Each dial scored 1-10 (generic → distinctive)
- Qualitative notes per dial when --check is used
- Exit code 0

## Related
- `.claude/tools/dsn/design-system/token-export.py` — downstream: tokens implement the brand
- `.claude/tools/dsn/content-strategist/voice-check.sh` — sister tool: copy voice matches brand
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: brand identity frozen with design
- `engine/SUPERPOWERS.md §taste-skill` — designer power-up
