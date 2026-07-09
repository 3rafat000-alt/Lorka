---
name: dsn-ux-architect
description: "Flows, information architecture, interaction models — no dead ends."
---
# Design - UX Architect

Generate Mermaid.js flow diagrams from structured CSV data — the paths between screens.

## Tool
`.claude/tools/dsn/ux-architect/flow-diagram.py`

## When to use
- Gate 2 Design: document the flow between all screens in the product
- After screen specs are done: connect them into navigation paths
- Before handoff to development: clarify branching logic, conditional paths, error flows
- UX audit: verify the implemented flow matches the diagram

## How to use
```bash
python3 .claude/tools/dsn/ux-architect/flow-diagram.py <csv-path> [--title "<title>"]
```

## Input
- CSV file with columns: id/step, label/description/action, next/goto/transition (auto-detected by header matching)
- Optional: branch/condition column for decision nodes
- `--title` — diagram title (default: "User Flow")

## Output
- Mermaid.js flowchart TD diagram with named nodes, labelled edges, and decision branches
- Printed to stdout
- Exit code 0

## Related
- `.claude/tools/dsn/ui-designer/screen-spec.sh` — upstream: screen specs define nodes
- `.claude/tools/res/journey-architect/journey-map.py` — sister tool: higher-level journey map
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: freeze the flow diagrams
