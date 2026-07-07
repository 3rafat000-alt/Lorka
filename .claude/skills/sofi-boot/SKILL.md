---
name: sofi-boot
description: Orient before any SOFI work — git sync, load the active project's live brain (STATE/CONTEXT/HANDOFFS), and report gate, branch, head_sha, and the next ticket. Use at the start of a session or before touching a project. Triggers — "boot", "orient", "sync project", "what's the state", "pick up where we left off", "where were we".
---

# /sofi-boot — orient, never start blind

The universal contract (`company/constitution/00-operating-system.md`, Article 00):
**no blind start.** Before acting on any SOFI project you orient with git, then read
the live brain. This skill runs that sequence and reports back tersely (doctrine:
*big brain, small mouth*).

## Steps

1. **Pick the project.** If the user named a `PRJ-ID` use it. Otherwise the active
   project is the one whose `projects/<PRJ>/_context/STATE.md` is newest:
   ```bash
   ls -t projects/*/_context/STATE.md | head -1
   ```

2. **Git-orient (never blind).**
   ```bash
   sofi sync <PRJ>     # or: git status --short && git log -1 --format='%h %s'
   ```
   Note the current `branch` and `head_sha`.

3. **Read the brain — in this order:**
   - `projects/<PRJ>/_context/STATE.md` — branch, `head_sha`, `gate`, `active`, `local_domain`, `status`, `blockers`.
   - `projects/<PRJ>/_context/HANDOFFS.md` — **your ticket** (the next action; bus schema `company/nexus/bus/ticket-schema.md`).
   - `projects/<PRJ>/_context/CONTEXT.md` — durable facts (read the tail; it's append-only).
   - `projects/<PRJ>/_context/DECISIONS.md` — only if a choice is in play.
   - `projects/<PRJ>/_context/LESSONS.md` — procedural memory the org distilled (`/sofi-reflect`); read the rules before repeating a mistake.

4. **Cross-check** the recorded `head_sha` in STATE.md against the real git HEAD.
   If they diverge, surface it — the brain is stale or someone committed out of band.

## Report (terse)

```
PROJECT <PRJ> — <title>
gate <N> · branch <branch> · HEAD <sha> (matches STATE: yes/no)
active room/agent: <id>   local: <local_domain>
blockers: <none|...>
NEXT TICKET: <first actionable line from HANDOFFS.md>
```

Then state the one next action and proceed (or ask if the ticket is ambiguous).

## Rules
- Read-only. This skill **orients**; it does not change code or commit.
- One brain per project, isolated by `PRJ-ID` — never bleed context across projects (Teaching III · Radical Isolation).
- Pair with `/sofi-handoff` to *close* work the same way this *opens* it (Article 08).
- **Standing loop reminder:** every report/verdict-producing command (`/sofi-spec-review`, `/sofi-audit`, `/sofi-secure`, `/sofi-feature`, `/sofi-fix`, `/sofi-report`) routes its output through the **oracle desk** before handoff — `sofi oracle review --prj <PRJ> --json --text "…"` → analyze + EXECUTE the reply, loop till done (Teaching VII · Autonomous Oracle Loop; operator `gtw-external-reviewer`; loop architecture `company/os/oracle/GEMINI_LOOP_ARCHITECTURE.md`). Boot only orients, so it doesn't fire the desk; surface it as the next step.
- See `company/CONSTITUTION.md` (supreme law), `company/constitution/00-operating-system.md` (the universal contract), and `CLAUDE.md`.
