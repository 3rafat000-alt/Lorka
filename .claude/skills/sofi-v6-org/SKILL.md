---
name: sofi-v6-org
description: SOFI v6 company charter — full enterprise org chart with 105 agents, 15 rooms, room isolation law, escalation chain, routing ladder, and gate order. Use when user asks about company structure, org chart, team layout, room hierarchy, SOFI v6, or how agents connect.
---

# SOFI v6 — Company of Rooms

105 agents across 15 rooms + boardroom + gateway + knowledge room. Every agent is an opencode subagent in `.claude/agents/<room>/`.

## Agent invocation

Each agent file at `.claude/agents/<room>/<agent-name>.md` is registered as an opencode subagent. Invoke with: `@agent-name` (e.g., `@str-product-strategist`) in any session.

Agents have `mode: subagent` so they can be spawned for focused tasks, or `mode: all` for standalone use.

## Quick reference

| Prefix | Room | Agents | Gate |
|--------|------|--------|------|
| `brd-*` | Boardroom | 7 | all |
| `gtw-*` | Gateway/Nexus | 6 | cross |
| `str-*` | Strategy | 7 | 0 |
| `res-*` | Research | 7 | 1 |
| `dsn-*` | Design | 8 | 2 |
| `arc-*` | Architecture | 7 | 3 |
| `bck-*` | Backend | 8 | 4 |
| `fnt-*` | Frontend | 8 | 4 |
| `mob-*` | Mobile | 6 | 4 |
| `dat-*` | Data | 7 | 3–4 |
| `sec-*` | Security | 8 | 3+5·veto |
| `qa-*` | Quality | 7 | 5 |
| `ops-*` | DevOps | 7 | 6–7 |
| `obs-*` | Observability | 6 | 8 |
| `knw-*` | Knowledge | 6 | all |

## Delegation rules

1. **Room Isolation:** call a room lead first (`@str-lead`), never a specialist directly except from within the same room
2. **Escalation:** specialist → room lead → `@gtw-conflict-resolver` → `@brd-arbiter` → `@brd-ceo`
3. **Gatekeeper:** every gate pass requires `@gtw-gatekeeper` adversarial check
4. **Routing:** model unified to inherit. Vary caveman level + effort only.

See `engine/ORG.md` for the full charter.