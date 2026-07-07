# MEMORY.md — routing map (where things live · v6)

> This file answers ONE question: **"where do I find X?"** — pointers only, never content.
> Behavior/rules live in `CLAUDE.md`; keep the two separate (routing ≠ behavior).
> Owner: `knw-lead` (13-knowledge room). Budget: under 200 lines. If an entry grows, push detail into the target file, not here.

## Search order (ladder — stop at first hit)
1. This map → the file it points to
2. Active project brain (`projects/<PRJ>/_context/`)
3. Codebase (grep/glob — `.claudeignore` already trims vendor noise)
4. Past-work memory (`sofi brain-query` / `mem-search` skill)
5. Web (only roles holding Web tools — `company/constitution/09-research-law.md`) — verify + cite

## Doctrine & law
| Question | Source |
|---|---|
| How do we behave / global rules | `CLAUDE.md` (root behavior contract) |
| Supreme law — 7 Teachings + articles | `company/CONSTITUTION.md` |
| Universal contract every agent obeys | `company/constitution/00-operating-system.md` |
| How to write a delegation (RCCF Work Order) | `company/constitution/01-work-order.md` · `/sofi-delegate` |
| Grounding (cite or abstain) | `company/constitution/02-grounding.md` |
| Verification (fresh-context, evidence) | `company/constitution/03-verification.md` |
| Reflection (LESSONS dreaming) | `company/constitution/04-reflection.md` · `/sofi-reflect` |
| Token economy (routes, caveman, budgets) | `company/constitution/05-token-economy.md` |
| Git law (branches, trailer, checkpoints) | `company/constitution/06-git-discipline.md` |
| Security law (veto, secrets, exposure) | `company/constitution/07-security-law.md` |
| Handoff & interconnection law | `company/constitution/08-handoff-law.md` |
| Research & internet law | `company/constitution/09-research-law.md` |
| Lifecycle gates law | `company/constitution/10-lifecycle-gates.md` |
| Why v6 is shaped this way (design record) | `company/BLUEPRINT.md` |
| Evidence base (GitHub research synthesis) | `company/research/PATTERNS.md` |

## Org, rooms & lifecycle
| Question | Source |
|---|---|
| Who is on the team / org chart | `company/ORG.md` · `/sofi-team` |
| Machine index rooms→agents→skills→tools | `company/nexus/registry.yaml` · `sofi registry` |
| How rooms talk (bus, leads-as-gateways) | `company/nexus/NEXUS.md` |
| A room's mission, members, bar | `company/rooms/<NN-room>/CHARTER.md` |
| Agent full spec (persona · contract) | `company/rooms/<NN-room>/agents/<id>.md` |
| Spawnable subagent definitions | `.claude/agents/<id>.md` (id = `<roomcode>-<role>`) |
| Ticket format on the bus | `company/nexus/bus/ticket-schema.md` |
| Escalation chain + circuit breaker | `company/nexus/bus/escalation.md` |
| Gate order + owners + exit bars (machine) | `company/nexus/gates.yaml` · `sofi gate-check` |
| Model routing + costs + effort_scaling | `company/nexus/routing.yaml` · `sofi route <id>` |
| How to drive a project end-to-end | `company/RUNBOOK.md` |
| Room playbooks / room tools | `company/rooms/<NN-room>/{playbooks,tools}/` |

## Live project state (per PRJ — read fresh, never cache here)
| Question | Source |
|---|---|
| Gate / branch / head_sha / domain / blockers | `projects/<PRJ>/_context/STATE.md` |
| What happened so far | `projects/<PRJ>/_context/CONTEXT.md` |
| Irreversible decisions (ADRs) | `projects/<PRJ>/_context/DECISIONS.md` |
| Next ticket / handoffs | `projects/<PRJ>/_context/HANDOFFS.md` |
| Lessons (procedural memory, read on boot) | `projects/<PRJ>/_context/LESSONS.md` |
| Path claims (parallel-squad locks) | `projects/<PRJ>/_context/LOCKS.md` |

## Brain & memory architecture
| Question | Source |
|---|---|
| Memory tiers (org vs project vs session) | `company/brain/BRAIN.md` |
| Brain-file templates (STATE/…/FOUNDATIONS) | `company/brain/templates/` |
| Org-level decisions / evolution / lessons | `company/brain/org/{DECISIONS,EVOLUTION,LESSONS}.md` |
| Personas history / team status | `company/brain/org/{PERSONAS,TEAM_STATUS}.md` |
| v5 law, verbatim (historical) | `company/brain/org/archive-v5/` |
| What did past sessions do | `mem-search` skill · `sofi brain-query` |
| Session breadcrumbs | `.claude/memory/sessions.jsonl` |

## Tooling & infra
| Question | Source |
|---|---|
| What tools already exist (discover before writing) | `company/nexus/registry.yaml` · `sofi tools` |
| Tooling law (10 rules) | `company/os/GOVERNANCE.md` |
| Dispatcher + all CLI verbs | `company/os/bin/sofi` |
| Shared Python library | `company/os/sofi_tools/` |
| Per-role toolkits (scanners) | `company/os/agents/` |
| OODA autonomous engine | `company/os/ooda/` |
| Local domains / public tunnels | `company/constitution/07-security-law.md` · `sofi domain` / `sofi tunnel` |
| Oracle desk (external review) | `company/os/oracle/` · `sofi oracle review` · owner `gtw-external-reviewer` |
| Autopilot / caveman / server-plane | `company/os/{autopilot,caveman,server-plane}/` |
| Superpowers registry | `company/superpowers/SUPERPOWERS.md` |
| Who holds Web tools | `company/nexus/registry.yaml` (grants) · `company/constitution/09-research-law.md` |
| Artifact templates (ADR, OpenAPI, journey map…) | `company/templates/` |
| Scaffold a new project | `company/os/bin/new-project.sh` |
| Observability console | `dashboard/` (registry-driven) |

## Ingest vs reach (context vs connections)
- **Ingest (evergreen → brain):** locked decisions, durable rules, lessons. Test: *"still worth having in a year?"*
- **Reach (volatile → fetch on demand, never ingest):** live app data, DB rows, logs, dashboards — via `sofi` tools/MCP as the LAST stop in the search order. Ingested volatile data = noise someone must weed later.

## Write triggers (who writes what, when)
- **«تذكّر» / "remember"** — the ONLY trigger for durable doctrine/preference writes (`CLAUDE.md`, this map, harness memory). A policy change touches its ONE owning file, never fanned across files.
- **Project brain** (`STATE/CONTEXT/DECISIONS/HANDOFFS`) — contract-driven, every acting turn (`company/constitution/00-operating-system.md` step 9); never waits for a trigger word.
- **LESSONS** — written only by the reflection loop (`/sofi-reflect`, `knw-reflector`), scheduled, never per-turn.
- **This map** — a new durable location earns one pointer row here; content stays in the target file.
