---
name: brd-chief-of-staff
description: "Chief of Staff — converts raw intent into frozen work orders, updates enterprise state."
---
# Boardroom - Chief of Staff

Generate complete RCCF (Role · Context · Command · Format) delegation work order blocks.

## Tool
`.claude/tools/brd/chief-of-staff/rccf-gen.sh`

## When to use
- Spawning a subagent: build the 4-part delegation block before calling any specialist
- Converting a HANDOFFS.md ticket into a structured brief
- Ensuring every delegation has persona, route, frozen artifact, and gate-bar
- Standardising delegation format across the enterprise

## How to use
```bash
.claude/tools/brd/chief-of-staff/rccf-gen.sh --role <name> --agent <agent> --project <PRJ-ID> --ticket <TKT> [--gate <N>] [--artifact <path>]
```

## Input
- `--role` — persona name (e.g. Aisha Rahman)
- `--agent` — agent role (e.g. backend-blade-engineer)
- `--project` — PRJ-ID
- `--ticket` — ticket number from HANDOFFS.md
- `--gate`, `--artifact` — optional gate number and frozen artifact path
- Reads `engine/ROSTER.md` for route defaults

## Output
- Complete RCCF block (🎭 Role · 📂 Context · 🎯 Command · 📐 Format) ready to insert into a spawn call

## Related
- Room spec: `engine/agents/ceo-sofi.md` (CEO is the delegator, Chief of Staff crafts the brief)
- `.claude/tools/gtw/dispatcher/work-order.py` — automated ticket→RCCF conversion
