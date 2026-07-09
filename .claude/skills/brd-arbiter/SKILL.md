---
name: brd-arbiter
description: "Arbiter — resolves design-vs-development disputes, final word under CEO."
---
# Boardroom - Arbiter

Log design-vs-development disputes and emit ADRs to DECISIONS.md.

## Tool
`.claude/tools/brd/arbiter/conflict-log.sh`

## When to use
- Design and Development disagree on implementation (Design wins unless safety forbids)
- An irreversible decision needs arbitration and ADR documentation
- A room deadlock has been escalated from gtw-conflict-resolver
- A designer and developer cannot agree on a layout/behaviour trade-off

## How to use
```bash
.claude/tools/brd/arbiter/conflict-log.sh <PRJ-ID> --title "<desc>" --design "<viewpoint>" --dev "<viewpoint>" [--resolution "<decision>"]
```

## Input
- `PRJ-ID` — project identifier
- `--title` — short dispute description
- `--design` — design's position
- `--dev` — development's position
- `--resolution` — optional: the arbiter's decision
- Reads `projects/<PRJ>/_context/DECISIONS.md` for existing ADRs

## Output
- New ADR entry in DECISIONS.md with TID, date, both positions, and resolution
- Escalation ticket written to HANDOFFS.md if unresolved
- Exit code 0 if ADR logged

## Related
- `.claude/tools/gtw/conflict-resolver/deadlock-break.sh` — first-line deadlock before escalation
- `engine/DOCTRINE.md §2` — Design wins unless safety or cost forbids
- `engine/protocols/00-operating-system.md §Escalation chain`
