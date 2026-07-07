# 🔗 Article 08 — Handoff Law (tickets, boundaries, sign-off)

> **Foundation: serves Teaching II (Hierarchical Flow)** — work cascades down the dependency graph, gate by gate — **and Teaching V (Continuous Metamorphosis)** — every handoff feeds the next cycle. Read `company/CONSTITUTION.md` (Room Isolation Law) and Article 06 (the git spine) first. Bus schema: `company/nexus/bus/ticket-schema.md`; escalation mechanics: `company/nexus/bus/escalation.md`.

How work flows agent → agent across 15 rooms without collisions or dropped balls. The bus is not middleware — it is tickets in the project brain's `HANDOFFS.md`, validated mechanically, spine'd by git.

## 1. The ticket (every handoff appends one)

```md
## TKT-014 · gate 3
from: arc-system-architect
to:   dat-db-engineer
task: model entities for the audit-log journey; reversible migrations.
consumes: docs/PRJ-0001_Tech_Stack.md, docs/PRJ-0001_OpenAPI.yaml
expected: docs/PRJ-0001_Schema.sql + ERD + migrations(+rollback)
route: workhorse · high · full
status: open
```

- **Lifecycle: `open → accepted → done | rejected`.** `open` = filed, unclaimed. `accepted` = the receiver has read the ticket, verified its inputs exist and are frozen, and taken it. `done` = Definition of Done passed **with an evidence block**. `rejected` = bounced with a one-line reason; the ball goes back up. Escalations flip a ticket `blocked → escalated` and file an up-chain ticket carrying `escalated_from:` (traceable, `sofi escalate`).
- Optional fields: `type:` / `mem:` (memory-type frontmatter for `sofi brain-query`) / `date:` / `escalated_from:`. `sofi handoff <op> <ID>` and `sofi dispatch` operate the queue.
- Compact one-liner when terse: `@08-data.dat-db-engineer -> model audit entities -> Schema.sql {workhorse·high·full}`.

## 2. Room-boundary validation (the Isolation Law, wired)

A ticket's `from:`/`to:` may only pair agents of the **same room**, an agent with its **own Lead**, **Lead with Lead**, or the **boardroom/gateway with any Lead**. A specialist never addresses a specialist in another room directly — not even "just a quick question." Cross-room work is a **request** to your own Lead, forwarded Lead-to-Lead, assigned internally; the answer returns the same path as a **report**. `sofi_tools.tickets.validate_room_boundary()` (room map loaded from `company/nexus/registry.yaml`, fail-open on unknown agents) is wired into `sofi gate-check` — a boundary violation fails the gate the same way a skipped gate does.

## 3. Verbatim forwarding (no translation tax)

When a Lead forwards a specialist's findings across a room boundary, it pastes them **verbatim** — `file:line` citations and evidence blocks intact — never re-narrated. Re-writing a worker's output through the coordinator is the measured "translation tax": it costs real tokens AND loses fidelity, and it strips the citations Article 02 requires. The Lead's job is to **route and gate**, not to re-author. A one-line routing note ("forwarding dat-db-engineer's finding to 04-architecture") is fine; re-summarizing the finding itself is not.

## 4. Gate sign-off (a gate cannot open until the prior closes)

- **Producer:** marks `done` and updates `STATE.gate` only when the Definition of Done passes **and the ticket carries an evidence block** — command + exit code, `file:line` proof, or diff/SHA (Article 03 V1; `validate_evidence` in `sofi gate-check` rejects bare "done"s, fail-closed).
- **Receiver:** `accepted` only after a **fresh-context check of the deliverable against the ORIGINAL ticket criteria** (Article 03 V2) — never the producer's self-report. Fails the check → `rejected` + one-line reason. No silent proceed.
- **Gate advance:** on top of per-ticket sign-off, the gate itself advances only through `gtw-gatekeeper`'s adversarial fresh-context verdict + `sofi gate-check` mechanical pass, then `sofi gate-tag` (Article 10).
- **Spawn width:** before fanning out a gate's work, state the effort-scaling class (`01-work-order.md` §4). Parallel specialists ONLY for context-independent sub-tasks behind a frozen input — never the sequential phases of one ticket.

## 5. Claims & LOCKS (two agents, one file — never)

- Before editing shared paths: `sofi claim <PRJ> <path-glob>` → recorded in `_context/LOCKS.md` (path → agent → timestamp). Release with `sofi release` when done.
- Path already claimed by a live agent → use a worktree or serialize via the Lead. Check `LOCKS.md` before editing anything shared.
- Diverged parallel commits on the same file → resolve forward (`git revert` / merge); never `reset --hard` / `push --force` (hook-blocked, Article 06).
- Design-vs-Dev dispute → `Technical_Debt_Justification.md` → `arc-review-architect` reviews → `gtw-conflict-resolver` → `brd-arbiter` (CEO last). Design wins unless safety or cost forbids; the why lands in one ADR line.

## 6. Session continuity (work survives the agent that did it)

A ticket carries no live memory — the git history does. Every handoff records the producer's commit SHA so the receiver, often a *different session*, resumes exactly, not approximately:

- Producer: `sofi checkpoint <PRJ> "…"` before marking `done`, then the SHA into `STATE.md` `head_sha`.
- Receiver: `sofi sync <PRJ>` + `git log --oneline` → every checkpoint with its `SOFI:` trailer (who · which ticket · gate). Never re-derives, never overwrites.
- Uncommitted work is invisible to the next session and **will** be stepped on. Checkpoint or lose it. `/sofi-handoff` closes the ritual; `/sofi-boot` opens the next one.

## 7. Cross-project

**Never.** A handoff stays inside one `PRJ-ID` (Teaching III). Shared needs go through `shared-packages/` only — extracted deliberately, versioned, never copy-pasted between trees. A ticket naming two projects is invalid on its face; `validate_room_boundary` has nothing to say about it because it never gets that far.
