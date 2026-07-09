---
name: gtw-conflict-resolver
description: "Conflict Resolver — inter-room deadlock in one round, then escalate to Arbiter."
---
# Gateway - Conflict Resolver

Resolve inter-room deadlocks by documenting positions, escalating to arbitration, and suggesting resolution paths.

## Tool
`.claude/tools/gtw/conflict-resolver/deadlock-break.sh`

## When to use
- Two rooms disagree on a shared boundary (e.g. API contract between backend and frontend)
- A handoff is blocked because the receiving room rejects upstream work
- Room isolation law has been violated (specialist talked directly to another room)
- Pre-arbitration triage: log the deadlock before escalating to brd-arbiter

## How to use
```bash
.claude/tools/gtw/conflict-resolver/deadlock-break.sh <PRJ-ID> --room-a <room> --room-b <room> --issue "<desc>"
```

## Input
- `PRJ-ID` — project identifier
- `--room-a`, `--room-b` — room names in conflict
- `--issue` — description of the disagreement
- Reads `projects/<PRJ>/_context/HANDOFFS.md` for current ticket state

## Output
- Deadlock entry appended to HANDOFFS.md with DL-ID, date, room positions, and issue
- Escalation note if resolution is above this role's authority
- Exit code 0 if deadlock logged

## Related
- `.claude/tools/brd/arbiter/conflict-log.sh` — escalate here if deadlock cannot be resolved at gateway level
- `engine/ORG.md §Room Isolation Law` — protocol that governs room boundaries
- `engine/ROSTER.md §Escalation chain`
