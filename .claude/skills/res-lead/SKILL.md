---
name: res-lead
description: "Research Room Lead — owns Gate 1 exit, Room gateway."
---
# Research - Lead

Synthesise research findings (personas, interview notes, competitive analyses) into a draft Journey Map.

## Tool
`.claude/tools/res/lead/research-synth.sh`

## When to use
- Gate 1 complete: all research artifacts are ready, synthesise into the Journey Map
- After a batch of user interviews: distill findings into journey stages
- Competitive teardown completed: integrate competitor insights into the map
- Before Gate 2 handoff: the Journey Map must be ready for Design

## How to use
```bash
.claude/tools/res/lead/research-synth.sh <PRJ-ID> [--findings "<file>"]
```

## Input
- `PRJ-ID` — project identifier
- `--findings` — path to research notes file (default: `projects/<PRJ>/_context/RESEARCH_NOTES.md`)
- Reads research artifacts from `_context/RESEARCH_NOTES.md` or custom path

## Output
- Draft Journey Map appended to `projects/<PRJ>/docs/Journey_Map.md`
- Stages extracted from research data with rough emotion/touchpoint annotations
- Exit code 0

## Related
- `.claude/tools/res/ux-researcher/persona-gen.sh` — upstream: personas feed into synthesis
- `.claude/tools/res/competitor-analyst/teardown.sh` — upstream: competitor insights
- `.claude/tools/res/journey-architect/journey-map.py` — downstream: structured map generation
