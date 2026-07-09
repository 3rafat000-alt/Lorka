---
name: res-journey-architect
description: "Customer Journey Map (Mermaid) — the Design truth every feature traces to."
---
# Research - Journey Architect

Generate a Mermaid.js journey map diagram from structured CSV data.

## Tool
`.claude/tools/res/journey-architect/journey-map.py`

## When to use
- Gate 1 Discovery: after research synthesis, create the visual Journey Map
- Before Design (Gate 2): the journey map must be frozen for screen specs
- Service blueprinting: document human-centred flow across touchpoints
- Stakeholder presentation: visual map of the user's end-to-end experience

## How to use
```bash
python3 .claude/tools/res/journey-architect/journey-map.py <csv-path> <PRJ-ID>
```

## Input
- CSV file with columns: stage, goal, touchpoint, emotion (auto-detected by header matching)
- `PRJ-ID` — project identifier
- Column names containing: stage, goal, touch/channel, emotion/mood

## Output
- Mermaid.js journey map markdown (--- delimited, flowchart TD)
- Sections: title, stages, goals, touchpoints, emotion arcs
- Output printed to stdout
- Exit code 0

## Related
- `.claude/tools/res/lead/research-synth.sh` — upstream: synthesised research feeds this tool
- `.claude/tools/dsn/ui-designer/screen-spec.sh` — downstream: each journey stage becomes a screen spec
- `.claude/tools/dsn/ux-architect/flow-diagram.py` — sister tool: detailed flow diagrams from CSV
