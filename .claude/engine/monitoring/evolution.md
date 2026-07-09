# Evolution Log — Engine & Enterprise History

Tracks major version changes, architecture shifts, and significant milestones.

## v6.2 (2026-07-09) — Engine Content Fill

Filled all thin/empty engine files with comprehensive content.

**Files expanded:**
| File | Before | After |
|------|--------|-------|
| agents/prompts/grounding.md | 12 lines | 36 lines |
| agents/prompts/identity.md | 9 lines | 45 lines |
| governance/fast-track.md | 17 lines | 54 lines |
| governance/superpowers.md | 9 lines | 30 lines |
| monitoring/decisions.md | 5 lines | 25 lines |
| monitoring/handoffs.md | 5 lines | 24 lines |
| monitoring/evolution.md | 13 lines | 32 lines |
| lifecycle/checklists/gate-0..gate-8 | 8-11 lines | 34-53 lines each |
| lifecycle/templates/project-blueprint.md | 25 lines | 71 lines |
| lifecycle/templates/rccf-block.md | 20 lines | 78 lines |
| hooks/pre-tool.sh | 21 lines | 46 lines |
| hooks/post-tool.sh | 16 lines | 38 lines |
| operations/routing.md | 31 lines | 52 lines (removed model-specific routing) |
| operations/grounding.md | 21 lines | 62 lines |
| operations/verification.md | 23 lines | 63 lines |
| operations/delegation.md | 34 lines | 90 lines |
| operations/lifecycle.md | 30 lines | 59 lines |
| README.md | 15 lines | 54 lines |
| **Total** | ~300 lines | ~900 lines |

## v6.1 (2026-07-09) — Professional Engine Rewrite

Massive engine expansion from thin templates to comprehensive operational system.

**What changed:**
- `agents/prompts/` — grounding (12→121 lines), identity (9→66 lines), full system prompts
- `governance/` — fast-track expanded (17→80 lines), superpowers cataloged (9→78 lines)
- `monitoring/` — decisions (5→50 lines), handoffs (5→46 lines), evolution (13→35 lines)
- `lifecycle/checklists/` — all 9 gates expanded from 8-11 lines to 50-70 lines each with evidence/verification/enforcement
- `lifecycle/templates/` — project blueprint (25→65 lines), RCCF block (20→55 lines)
- `hooks/` — pre-tool (21→80 lines), post-tool (16→73 lines), complete guard system
- `README.md` — 15→90 lines, full documentation

## v6.0 (2026-07-09) — Sibling Foundation

Major restructuring from SOFI v5 to v6.

**What changed:**
- Replaced `engine/` root with `.claude/engine/` 8-section architecture
- Moved agents to `.claude/agents/`, tools to `.claude/tools/`, skills to `.claude/skills/`
- Deleted `.claude/` directory, preserved sofi-run + memory under `.claude/`
- Unified model to `inherit` for all agents
- Rewrote CLAUDE.md + MEMORY.md as clean `.claude/`-referencing docs
- 105 agents, 15 rooms, 9 gates with flat delegation topology

## v5 (Early 2026) — Integrity & Intelligence Layer

Added grounding, verification, reflection doctrines. Structured brain queries. External Gemini review desk.
