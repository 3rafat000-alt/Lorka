# Playbook — brain-query retrieval

> Owner: `knw-brain-query` (dispatched via `knw-lead`). This is the room's sharpest recurring job: turning a human-shaped question — "where do I find X," "what did we decide about Y," "has this failure happened before" — into a cited answer, at the cheapest rung of the search ladder that actually answers it. Run any time an agent, in any room, is about to reach for a fresh re-search or a web query for something the company may have already written down. Every step names the real command; nothing here is aspirational.

## The ladder — stop at first hit, never skip a rung

1. **Rung 1 — `MEMORY.md` (the routing map itself).** Most "where do I find X" questions are answered here directly, at zero brain-file reads. Check this before touching the project brain at all.
   ```bash
   # read MEMORY.md, scan the relevant table row
   ```
2. **Rung 2 — the active project's brain (`_context/`).** For "what did we decide" / "what's the status" questions, read in the standard order: `STATE.md` → `HANDOFFS.md` → `CONTEXT.md` → `DECISIONS.md` → `LESSONS.md`.
   ```bash
   sofi brain <PRJ>
   ```
3. **Rung 3 — codebase (grep/glob).** For "where is X implemented / referenced" questions the brain doesn't hold, search the codebase directly — `.claudeignore` already trims vendor noise, so this stays cheap.
   ```bash
   # Grep / Glob against the relevant paths
   ```
4. **Rung 4 — `sofi brain-query` structured filters.** For questions that are really a filter in disguise ("all open gate-4 tickets to bck-lead," "every rejected ticket this project," "every lesson tagged procedural") — translate the human question into `key=value` filters before reading tickets one by one.
   ```bash
   sofi brain-query <PRJ> status=blocked type=feature
   sofi brain-query <PRJ> gate=4 to=bck-lead
   ```
5. **Rung 5 — web, last resort, and not this agent's own move.** `knw-brain-query` holds no Web tools by design — if all four rungs come up genuinely empty, the answer is "not found in the brain," returned plainly, and a web-shaped follow-up (if warranted) routes through the requesting room's own Web-tool-holding role, never fabricated here.

## Answer format — citation leads, prose is minimal

6. **Every row of the answer carries its citation first**: `file:line`, or `TKT-NNN`/`ADR-NNN`/`LES-NNN`, then a short one-line context — never a paragraph re-explaining what the citation already shows.
   ```
   projects/PRJ-0042/_context/DECISIONS.md:14  ADR-003 — chose Postgres over Mongo for PRJ-0042 (2026-03-02)
   projects/PRJ-0042/_context/HANDOFFS.md:88    TKT-021 — rejected: schema not frozen at Gate-3 dispatch
   ```
7. **A genuine miss is reported plainly**: `"not found in the brain — checked MEMORY.md, project brain, codebase grep, and sofi brain-query; recommend <requesting room> route this through its own Web-tool-holding role if a fresh source is needed."` Never upgraded to a guess, never silently dropped.

## Worked example

**Question:** "Did we already decide how to handle soft-deletes on the orders table for PRJ-0042?"

```bash
sofi brain-query PRJ-0042 type=decision
```
```
projects/PRJ-0042/_context/DECISIONS.md:22  ADR-006 (2026-04-11) — soft-delete via deleted_at
  timestamp, not a boolean flag; rollback: drop column, no data loss since nothing is
  hard-deleted downstream. By: dat-lead.
```
Answer returned: the citation above, one line of context, no re-narration.

## Rules

- The ladder is followed in strict order — a rung is skipped only because the prior rung already answered the question, never because it "felt faster" to jump ahead.
- No answer ships without a citation on every row it returns.
- "Not found in the brain" is a complete, valid answer — abstention is rewarded (G2), never treated as a failed query.
- A structural gap discovered mid-query (a `MEMORY.md` pointer to a file that no longer exists, a brain file with broken frontmatter) is reported to `knw-lead` immediately — it is a room-bar issue, not just a missed answer.
