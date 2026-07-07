---
name: sofi-handoff
description: Close a unit of SOFI work the disciplined way — write the artifact, checkpoint to git, append CONTEXT (+DECISIONS if irreversible), update STATE (head_sha), and write the next ticket in HANDOFFS. The "after acting" half of the universal contract. Use when finishing a task, before ending a session, or when handing work to the next agent. Triggers — "handoff", "wrap up", "checkpoint and record", "close this out", "hand to next agent", "save progress".
---

# /sofi-handoff — record work so the next session can see it

> **Uncommitted session = invisible to the next one.** This skill is the
> "after acting" half of the universal contract (`company/constitution/00-operating-system.md`)
> and the handoff law (`company/constitution/08-handoff-law.md`). Run it at every
> milestone, not just session end. نقطة after نقطة — checkpoint early, checkpoint often.

## Steps (in order)

1. **Write the artifact.** The deliverable lives under `projects/<PRJ>/` (a doc,
   code, report). One-off scripts go in `projects/<PRJ>/_scratch/` (ephemeral,
   never a deliverable, purged at gate exit).

2. **Checkpoint to git** — commit early/often with a compliant, traceable message:
   ```bash
   sofi checkpoint <PRJ> "<type>(<scope>): <subject>"
   ```
   `<type>` ∈ feat|fix|chore|docs|refactor|test|perf|ci|build|style|revert. The
   pre-commit hook hard-blocks non-conforming subjects, a missing `SOFI:` trailer,
   and forbidden paths (secrets, `_scratch/`). Never `reset --hard` / `--force`
   (hook-blocked · Teaching VI · Reversibility).

3. **Append `CONTEXT.md`** (append-only durable facts) — what changed and why,
   in one tight entry. Add a row to **`DECISIONS.md`** only if the choice is
   irreversible (use `company/templates/adr.template.md`; ADR log kept by `knw-historian`).

4. **Update `STATE.md`** — set `head_sha` to the new commit, refresh `gate`,
   `active`, `status`, `blockers`, `updated_by`. The recorded `head_sha` is the
   spine the next session orients on.

5. **Write the next ticket in `HANDOFFS.md`** — the single next action for whoever
   picks this up (an agent id like `bck-blade-engineer`). Be specific: inputs,
   expected output, route. Follow the bus schema `company/nexus/bus/ticket-schema.md`.
   Room Isolation Law (Article 08): a cross-room ticket travels
   `specialist → own Lead → target Lead → target specialist` — Leads forward VERBATIM.

## Report

```
HANDOFF <PRJ>
artifact: <path>
commit: <sha> <type>(<scope>): <subject>
STATE: gate <N> · head_sha <sha> · active <id> · blockers <none|...>
NEXT TICKET → <agent id>: <action>
```

## Rules
- Commit message must pass git discipline (`company/constitution/06-git-discipline.md`) —
  conventional type + `SOFI:` trailer. Code, commits, and security warnings are written
  in **normal prose, never caveman** (Article 05).
- Project work on `prj/<ID>` (parallel squads in worktrees); doctrine on `main`.
- No secrets and no `_scratch/` in history (Article 07 · Security Law).
- Mirror of `/sofi-boot` — that opens a session the same way this closes one.
