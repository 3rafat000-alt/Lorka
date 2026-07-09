---
name: knw-historian
description: "Decision log / ADR keeper — history from work orders, never fabricated."
---
# Knowledge - Historian

Generate ADR index from DECISIONS.md.

## Tool
`.claude/tools/knw/historian/adr-log.sh`

## When to use
- Pre-handoff ADR inventory
- Architecture review — decision traceability
- New team member onboarding — past decisions
- Post-mortem — decision timeline reconstruction

## How to use
```bash
.claude/tools/knw/historian/adr-log.sh --prj PRJ-XXXX [--output adr-index.md] [--format table|json]
```

## Input
PRJ-ID. Parses DECISIONS.md for ADR entries (numbered decisions with date, title, status). Creates empty DECISIONS.md if missing.

## Output
Index of all ADRs (table or JSON) with number, date, description, status. Writes to stdout or file.

## Related
- `engine/agents/knw/knw-historian.md`
- `.claude/tools/knw/historian/adr-log.sh`
