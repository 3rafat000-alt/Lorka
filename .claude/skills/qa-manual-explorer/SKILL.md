---
name: qa-manual-explorer
description: "Edge-case exploration by persona — empty/massive/offline/language/a11y."
---
# Quality - Manual Explorer

Generate edge-case checklist by persona.

## Tool
`.claude/tools/qa/manual-explorer/edge-cases.sh`

## When to use
- Pre-UAT exploratory testing session
- New feature manual QA prep
- Persona-based regression checklist
- Boundary/negative test scenario generation

## How to use
```bash
.claude/tools/qa/manual-explorer/edge-cases.sh --prj PRJ-XXXX --persona guest|member|admin|anonymous [--feature name]
```

## Input
PRJ-ID and persona. Optional feature filter. Generates persona-specific edge cases covering empty states, rate limits, concurrent sessions, network failure, invalid input, pagination bounds.

## Output
Checklist markdown printed to stdout with pass/fail boxes per edge case.

## Related
- `engine/agents/qa/qa-manual-explorer.md`
- `.claude/tools/qa/manual-explorer/edge-cases.sh`
