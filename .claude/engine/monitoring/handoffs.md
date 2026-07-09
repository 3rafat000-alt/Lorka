# Handoff Queue — Inter-Agent Workflow

Tracks tickets moving between rooms/agents. One entry per active work item.

## Format

| Ticket | PRJ | From | To | Gate | Status | Due |
|--------|-----|------|----|------|--------|-----|
| SOFI-001 | PRJ-XXXX | room-role | room-role | N | open/in_review/done | YYYY-MM-DD |

## Active Handoffs

| Ticket | PRJ | From | To | Gate | Status | Due |
|--------|-----|------|----|------|--------|-----|
| — | — | — | — | — | — | — |

## Rules

1. **Every spawn** creates a handoff ticket. No ticket = invisible work.
2. **Status flow:** open -> in_review (gatekeeper check) -> done -> archived
3. **Handoff = frozen RCCF block** — the receiver gets a sealed brief
4. **Done** only after gate bar is met AND evidence is pasted
5. **Stale tickets** (>7 days) auto-escalated to CEO
6. **Completed tickets** move to `.claude/engine/monitoring/evolution.md` as accomplishments
