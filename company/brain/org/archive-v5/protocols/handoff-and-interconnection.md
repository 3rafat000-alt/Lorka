# 🔗 Handoff & Interconnection — how the company stays in sync

> **Foundation:** This protocol serves Teaching **II (Hierarchical Flow)** — work cascades down the dependency graph, gate by gate — and Teaching **V (Continuous Metamorphosis)** — every handoff feeds the next cycle. Read `engine/DOCTRINE.md` before this file.

Teaches how work flows agent→agent without collisions or dropped balls. The dependency graph + ticket protocol.

## Ticket format (every handoff → append to `HANDOFFS.md`)
```md
## TKT-014 · gate 3
from: principal-system-architect
to:   data-schema-engineer
task: model entities for the audit-log journey; reversible migrations.
consumes: docs/PRJ-0001_Tech_Stack.md, OpenAPI.yaml
expected: docs/PRJ-0001_Schema.sql + ERD + migrations(+rollback)
route: sonnet-4-6 · high · full
status: open | accepted | done | rejected
```
Caveman one-liner form when terse: `@Tier1.Data-Schema-Engineer -> model audit entities -> Schema.sql {sonnet-4-6·high·full}`.

## Tier isolation (binding — no exceptions)
A ticket's `to:`/`from:` may only name an agent in the **same tier** as the sender, or that tier's own **Advisor** (`tier-0-advisor` … `tier-4-advisor`). A specialist may never address a specialist in another tier directly — not even "just a quick question." Cross-tier work is always a **request** addressed to your own tier's Advisor, who forwards it to the target tier's Advisor, who assigns it internally; the answer returns the same path as a **report**. `sofi_tools.tickets.validate_tier_boundary()` enforces this and is wired into `sofi gate-check` — a boundary violation fails the gate the same way a skipped gate does.

## Verbatim forwarding (v5 — no translation tax)
When an Advisor forwards a specialist's findings across the tier boundary, it pastes them **verbatim** — with the specialist's `file:line` citations and evidence intact — never re-narrated or re-summarized. Re-writing a worker's output through the coordinator is the measured "translation tax" (LangChain's supervisor-vs-swarm benchmark: it costs real tokens AND loses fidelity), and it strips the citations that `grounding.md` requires. The Advisor's job is to **route and gate**, not to re-author. A one-line routing note ("forwarding DB-engineer's finding to Tier-3") is fine; re-summarizing the finding itself is not.

## Gate sign-off (a gate cannot open until the prior closes)
- Producing agent marks deliverables `done` + sets `STATE.gate` only when its Definition of Done passes **and carries an evidence block** (command+exit code / file:line proof / commit) — `verification.md` V1, enforced by `sofi gate-check`'s evidence check. A bare "done" with no proof is rejected.
- Receiving agent **accepts** only after a fresh-context check of the deliverable against the *original* ticket criteria (`verification.md` V2) — not the producer's self-report; else `rejected` with a one-line reason → ball goes back up. No silent proceed.
- **Spawn width (v5, `routing.yaml` `effort_scaling`)** — before fanning out a gate's work, pick the task-class row and state it. Spawn parallel specialists ONLY when their sub-tasks are context-independent; never fan out the sequential phases (plan→build→test) of one ticket — that pays coordination cost with no parallelism payoff.

## Dependency graph (who feeds whom — every arrow crossing a tier boundary passes through both Advisors)
```
CEO
└─0 tier-0-advisor (Isabelle) ─┬─ chief-product-strategist
                               ├─ ux-researcher → journey-architect
                               └─ ui-ux-designer → content-strategist
   └─(request)→ tier-1-advisor (Ingrid) ─┬─ principal-system-architect
                                         ├─ data-schema-engineer
                                         ├─ api-integration-specialist
                                         ├─ security-compliance-architect
                                         └─ infrastructure-cloud-architect
      └─(request)→ tier-2-advisor (Elif) ─┬─ database-engineer
                                          ├─ api-engineer
                                          ├─ backend-blade-engineer
                                          ├─ frontend-react-engineer
                                          └─ mobile-engineer
         └─(request)→ tier-3-advisor (Otieno) ─┬─ qa-sre-lead
                                               ├─ automated-testing-engineer
                                               ├─ manual-exploratory-tester
                                               ├─ performance-load-analyst
                                               └─ security-penetration-tester
            ├─(report: BLOCK)→ tier-2-advisor (Elif)
            └─(report: PASS)→ tier-4-advisor (Astrid) ─┬─ devops-cloud-lead
                                                        ├─ cicd-pipeline-engineer
                                                        ├─ observability-sre
                                                        └─ release-incident-manager
               └─(SLO breach, report)→ tier-0-advisor (Isabelle) ──► re-enters gate 1
```
Inside a tier's `┬─`/`├─` branch, specialists hand off to each other directly (same tier, unrestricted). Every arrow crossing a tier line above is a formal request or report addressed Advisor-to-Advisor — never a specialist reaching past its own tier's Advisor.

## Parallelism (gate 4)
Database, API, Backend/Blade, Frontend/React, and Mobile Engineer work **concurrently** off the same frozen `OpenAPI.yaml` + `Journey_Map.md`, coordinated by the Tier-2 Advisor (Elif Kaya) rather than per-squad tech leads. No engineer waits on another for the contract — only the contract must be frozen first. Each engineer works in **its own git worktree** off `prj/<PRJ>` (`sofi worktree <PRJ> 4 <role>`) so two engineers can never edit the same file at once; Elif merges to `prj/<PRJ>` only at gate close (`git-discipline.md §2`).

## Session continuity (work survives the agent that did it)
A ticket carries no live memory — the git history does. Every handoff records the producer's commit SHA so the receiver (often a *different session*) resumes exactly, not approximately:
- Producer: `sofi checkpoint <PRJ> "…"` before marking `done`, then write the SHA into `STATE.md.head_sha`.
- Receiver: `sofi sync <PRJ>` + `git log --oneline` → sees every checkpoint with its `SOFI:` trailer (who·which ticket·gate). Never re-derives, never overwrites.
- Uncommitted work is invisible to the next session and **will** be stepped on. Checkpoint or lose it.

## Conflict resolution
- Design-vs-Dev dispute → `Technical_Debt_Justification.md` → architect reviews → CEO arbitrates (`opus·max`), Design wins unless safety/cost forbids.
- Two agents touching the same file in parallel → **claim it first** (`sofi claim <PRJ> <path>` → `_context/LOCKS.md`); if already claimed by a live role, use a separate worktree or serialize via the lead. Check `LOCKS.md` before editing shared paths.
- Diverged branch / parallel commits on the same file → resolve forward with `git revert`/merge; **never** `reset --hard` or `push --force` (destroys the other session's work — hook-blocked).

## Cross-project
Never. A handoff stays inside one `PRJ-ID`. Shared needs go through `shared-packages/` only.
