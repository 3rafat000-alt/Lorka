---
name: res-ux-researcher
description: "Evidence-based personas (JTBD), pain/gain map."
---
# Research - UX Researcher

Generate evidence-based persona documents from interview notes or structured input.

## Tool
`.claude/tools/res/ux-researcher/persona-gen.sh`

## When to use
- Gate 1 Discovery: after user interviews, generate primary and secondary personas
- Before any design work: ensure the team has a clear, documented target user
- Product pivot or scope change: update personas to reflect new target audience
- Stakeholder alignment: share evidence-based user profiles (not assumptions)

## How to use
```bash
.claude/tools/res/ux-researcher/persona-gen.sh <PRJ-ID> --name "<Persona Name>" --role "<role>" --goal "<JTBD>" [--pain "<pains>"] [--output <file>]
```

## Input
- `PRJ-ID` — project identifier
- `--name` — persona name
- `--role` — job role / user category
- `--goal` — Jobs To Be Done statement
- `--pain` — optional pain points (auto-extracts from INTERVIEW_NOTES.md if omitted)
- `--output` — optional output path (default: `projects/<PRJ>/docs/personas/`)

## Output
- Persona document with demographics, goals, pain points, behaviours, and quote
- Exit code 0

## Related
- `.claude/tools/res/lead/research-synth.sh` — downstream: personas feed journey synthesis
- `.claude/tools/res/web-scout/fetch-cite.sh` — supporting research for persona evidence
- `.claude/tools/res/fact-checker/ground-check.sh` — verify persona claims against sources
