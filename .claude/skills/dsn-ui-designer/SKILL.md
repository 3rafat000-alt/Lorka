---
name: dsn-ui-designer
description: "High-fidelity text spec, one screen per journey stage, all states."
---
# Design - UI Designer

Generate a text-format UI screen spec from a journey stage — the artifact that traces code to a human's screen.

## Tool
`.claude/tools/dsn/ui-designer/screen-spec.sh`

## When to use
- Gate 2 Design: after the Journey Map is frozen, generate specs for each screen
- New feature: every journey stage needs one screen spec minimum
- Before handoff to development: the screen spec freezes layout, elements, and states
- Design audit: verify that existing screens match their spec

## How to use
```bash
.claude/tools/dsn/ui-designer/screen-spec.sh <PRJ-ID> --screen "<name>" --stage "<stage>" [--elements "<h1,p,button>"] [--states "<loading,empty,error>"]
```

## Input
- `PRJ-ID` — project identifier
- `--screen` — screen name
- `--stage` — corresponding journey stage
- `--elements` — comma-separated UI elements (h1, p, form, button, etc.)
- `--states` — comma-separated states to handle (loading, empty, error, edge cases)

## Output
- Screen spec at `projects/<PRJ>/docs/screens/<name>.md`
- Sections: elements list, states matrix, layout notes, behaviour rules
- Each element has: type, purpose, behaviour notes
- Exit code 0

## Related
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: freeze all screen specs
- `.claude/tools/dsn/ux-architect/flow-diagram.py` — sister tool: flow between screens
- `engine/DOCTRINE.md §Teaching I` — Design is Truth: code traces to this spec
