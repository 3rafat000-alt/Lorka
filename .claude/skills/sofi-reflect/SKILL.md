---
name: sofi-reflect
description: Run SOFI's scheduled reflection loop ("dreaming") — mechanically locate NEW learning signals in a project's HANDOFFS history (escalations, circuit-breakers, recurring ticket patterns), distil each into one grounded lesson (situation · what-failed · rule), and write it to _context/LESSONS.md as durable procedural memory the org reads on future boots. Run at gate-close or on demand, never per-turn. Use to make the team learn from its own history instead of repeating mistakes. Triggers — "reflect", "what did we learn", "dreaming", "distil lessons", "post-mortem the project", "update lessons", "learn from handoffs", "coherence audit", "check for contradictions".
---

# /sofi-reflect — the org learns from itself

> Scheduled, never per-turn (per-turn memory updates degrade quality). Retain-by-default:
> only NEW signals are distilled; raw history is never rewritten. Continuous Metamorphosis (Teaching V).
> Doctrine: `company/constitution/04-reflection.md`. Owner: **`knw-reflector`** (Knowledge room).
> Engine: `company/os/toolkit/core/reflection_engine.py`.

**Usage:** `/sofi-reflect [PRJ-ID]` — defaults to the active project. Run this at a
gate close, at project wrap-up, or when you suspect a pattern is recurring.

## The loop (`knw-reflector` runs it; specialists never self-reflect mid-task)
1. **Locate — 0 model tokens.** Run the scan:
   ```bash
   python3 company/os/toolkit/core/reflection_engine.py scan --prj <PRJ>
   ```
   It prints only NEW candidates (escalations, circuit-breakers, recurring ≥3× patterns)
   not already in `LESSONS.md`. If it says "no new learning signals," stop — nothing to do.
2. **Distil — one grounded lesson per candidate.** For each, write:
   - **situation**: the context (what was being done)
   - **what-failed**: the actual failure/friction (cite the ticket — G1 · `company/constitution/02-grounding.md`)
   - **rule**: the durable rule that prevents recurrence (imperative, specific)
   Keep it to 1–2 lines. A lesson is a rule, not a re-summary of the ticket.
3. **Write** each lesson:
   ```bash
   python3 company/os/toolkit/core/reflection_engine.py write --prj <PRJ> \
     --sig "<sig-from-scan>" --situation "..." --failed "..." --rule "..." \
     --source "<TKT-ID>" --date "<today, from you — never invented in a tool>"
   ```
   Idempotent on `--sig` (won't double-write).
4. **Promote (optional).** If a candidate is a `recurring-pattern` or a delegation that
   needed 2+ correction rounds, propose lifting it into a durable artifact — an updated
   agent spec, an RCCF template, or a `company/superpowers/SUPERPOWERS.md` power
   (`proposed → piloted → promoted`). This is how capability compounds, not just caution.
   Reflection *proposes*; only the CEO amends the Constitution (recorded in
   `company/brain/org/DECISIONS.md`).
5. **Coherence audit — the silent-contradiction sweep (monthly or at gate-close).**
   Doctrine drifts apart quietly; you only notice when an agent produces a weird result.
   Ask ONE question across `CLAUDE.md` + `MEMORY.md` + `company/CONSTITUTION.md` +
   `company/constitution/*` + `company/nexus/*`: *"do the sections still agree with each
   other?"* — NOT "is the content correct?". Grep-first (0 model tokens where possible):
   duplicated rules stated twice with different wording, stale file paths, conflicting
   budgets/routes, a rule one file grants and another forbids. Each contradiction = a lesson
   candidate (situation · what-conflicts · which file wins) — then fix the LOSING file only,
   never both (one canonical owner per rule; the Constitution outranks all).
6. **Report** a one-line summary to the brain (`/sofi-handoff` or a `CONTEXT.md` note):
   how many lessons were distilled + any promotion proposed + contradictions found/fixed.
   Then `sofi checkpoint`.

## Rules
- Never run inside a working turn or mid-task — reflection is over *closed* work only.
- Never overwrite/delete a raw episode to "tidy up" — retain by default.
- Ground every rule (cite the ticket it came from · Article 02). An ungrounded lesson is folklore.
- Lessons are procedural memory — agents read `LESSONS.md` on `/sofi-boot`, so write rules an
  agent can actually act on next time, not vague reflections.
