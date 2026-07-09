# Decision Log (ADR)

Architectural Decision Records. Every irreversible change requires an entry.

## Format

| Date | Decision | Rationale | Author | Status |
|------|----------|-----------|--------|--------|
| YYYY-MM-DD | Short title | Why this path vs alternatives | Agent name | Proposed / Accepted / Deprecated |

## Active Decisions

| Date | Decision | Rationale | Author | Status |
|------|----------|-----------|--------|--------|
| 2026-07-09 | .claude/engine/ 8-section arch | Old engine was flat copy, no clear separation. New: identity, operations, agents, lifecycle, monitoring, governance, hooks, tooling. | Magnus Holt | Accepted |
| 2026-07-09 | All model refs unified to big-pickle | Remove haiku/sonnet/opus/fable/claude routing. Single model for all agents. Simpler, zero confusion. | Magnus Holt | Accepted |
| 2026-07-09 | .claude/ deleted → .claude/ | All SOFI infra under .claude/. Claude-specific files removed. sofi-run + memory preserved. | Magnus Holt | Accepted |

## Rules

1. **When to write:** any change that is irreversible, changes protocol, or costs >30 min to undo
2. **Status lifecycle:** Proposed (needs CEO sign) -> Accepted (frozen) -> Deprecated (replaced)
3. **Every entry must carry:** source tags for factual premises [verified: file:line]
4. **ADR is binding** — implementation must match the frozen decision
5. **Overriding an ADR** requires a new ADR that references and supersedes the old one
