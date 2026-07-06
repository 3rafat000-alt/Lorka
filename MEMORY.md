# MEMORY.md — routing map (where things live)

> This file answers ONE question: **"where do I find X?"** — pointers only, never content.
> Behavior/rules live in `CLAUDE.md`; keep the two separate (routing ≠ behavior).
> Budget: under 200 lines. If an entry grows, push detail into the target file, not here.

## Search order (ladder — stop at first hit)
1. This map → the file it points to
2. Active project brain (`projects/<PRJ>/_context/`)
3. Codebase (grep/glob — `.claudeignore` already trims vendor noise)
4. Past-work memory (`mem-search` skill / `sofi brain-query`)
5. Web (only roles holding Web tools) — verify + cite

## Doctrine & identity
| Question | Source |
|---|---|
| How do we behave / global rules | `CLAUDE.md` (root behavior contract) |
| Constitution v5 | `.claude/SOFI_SYSTEM_PROMPT.md` |
| Universal contract every agent obeys | `engine/protocols/00-operating-system.md` |
| Grounding / verification / reflection | `engine/protocols/{grounding,verification,reflection}.md` |
| v5 architecture record | `.claude/docs/v5/SOFI-V5-ARCHITECTURE.md` |
| Frontier research the v5 layer is built on | `.claude/docs/ai-guides/research/` |

## Org & lifecycle
| Question | Source |
|---|---|
| Who is on the team / who does X | `engine/ROSTER.md` |
| Agent role spec (persona · contract) | `engine/agents/**` |
| Spawnable subagent definitions | `.claude/agents/sofi-*.md` |
| Gate order + exit bars | `engine/lifecycle/gates.md` |
| Model routing + costs | `engine/routing/routing.yaml` |
| How to delegate (RCCF) | `engine/protocols/01-delegation-rccf.md` |
| How to drive a project end-to-end | `engine/RUNBOOK.md` |
| Git law | `engine/protocols/git-discipline.md` |

## Live project state (per PRJ — read fresh, never cache here)
| Question | Source |
|---|---|
| Gate / branch / head_sha / domain / blockers | `projects/<PRJ>/_context/STATE.md` |
| What happened so far | `projects/<PRJ>/_context/CONTEXT.md` |
| Irreversible decisions | `projects/<PRJ>/_context/DECISIONS.md` |
| Next ticket / handoffs | `projects/<PRJ>/_context/HANDOFFS.md` |
| Lessons (procedural memory, read on boot) | `projects/<PRJ>/_context/LESSONS.md` |

## Tooling & infra
| Question | Source |
|---|---|
| What tools already exist (discover before writing) | `engine/tooling/registry.yaml` |
| Tooling law | `engine/tooling/GOVERNANCE.md` |
| Dispatcher commands | `engine/tooling/bin/sofi` |
| Local domains / public tunnels | `engine/protocols/{local-domains,public-tunnels}.md` |
| External review desk (Gemini) | `engine/protocols/external-review-desk.md` |
| Superpowers registry | `engine/SUPERPOWERS.md` |
| Who holds Web tools | `engine/protocols/tooling-matrix.md` |

## Session memory
| Question | Source |
|---|---|
| What did past sessions do | `mem-search` skill / `get_observations` (claude-mem) |
| Session breadcrumbs | `.claude/memory/sessions.jsonl` |
| Structured queryable brain | `sofi brain-query` |

## Ingest vs reach (context vs connections)
- **Ingest (evergreen → brain):** locked decisions, durable rules, lessons. Test: *"still worth having in a year?"*
- **Reach (volatile → fetch on demand, never ingest):** live app data, DB rows, logs, dashboards — via `sofi` tools/MCP as the LAST stop in the search order. Ingested volatile data = noise someone must weed later.
