---
name: arc-system-architect
description: "Stack, component diagram, screen→component→endpoint traceability."
---
# Architecture - System Architect

Generate Mermaid component diagrams from JSON component definitions. Visualize system architecture with dependencies and subcomponent grouping.

## Tool
`.claude/tools/arc/system-architect/component-diagram.py`

## When to use
- Gate 3: produce system architecture diagram for architecture package
- Design review: visualize component relationships and data flow
- Onboarding: give new team members a bird's-eye view of the system

## How to use
```bash
.claude/tools/arc/system-architect/component-diagram.py [input.json] --title "Title" -o output.md
```

## Input
- JSON file (or stdin) with component list — each with `id`, `label`, `color`, `deps[]`, `subcomponents[]`
- `--title` — diagram title (default: "System Architecture")
- `-o` — output file path

## Output
- Mermaid `graph TB` diagram written to file or stdout
- Node styles, dependency arrows, subgraph grouping

## Related
- `engine/agents/arc/system-architect.md`
- `.claude/tools/arc/system-architect/component-diagram.py`
