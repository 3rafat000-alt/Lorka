---
name: gtw-dispatcher
description: "Gateway Lead / Dispatcher — converts RCCF work orders to tickets, runs conveyor."
---
# Gateway - Dispatcher

Convert HANDOFFS.md tickets into structured RCCF work order blocks interactively.

## Tool
`.claude/tools/gtw/dispatcher/work-order.py`

## When to use
- Processing an inbound ticket queue: turn raw HANDOFFS entries into delegatable briefs
- Standardising delegation format: ensure every ticket has Role, Context, Command, Format
- Before spawning multiple specialists in a gate: batch-convert tickets to RCCF blocks
- Auditing the pipeline: verify every open ticket has a corresponding work order

## How to use
```bash
python3 .claude/tools/gtw/dispatcher/work-order.py
```

## Input
- Reads `projects/<PRJ>/_context/HANDOFFS.md` for ticket entries
- Reads `projects/<PRJ>/_context/STATE.md` for current gate
- Prompts interactively for role, agent, project, and gate per ticket

## Output
- For each ticket: complete RCCF block printed to stdout
- Parsed ticket list with human-readable summaries
- Gate context extracted from STATE.md

## Related
- `.claude/tools/brd/chief-of-staff/rccf-gen.sh` — CLI-based RCCF generation (non-interactive)
- `.claude/tools/gtw/router/route-stamp.sh` — stamp route after dispatch
- Room spec: `engine/agents/tier-0-advisor.md` (tier advisor for gateway)
