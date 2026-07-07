# 🌙 Reflection Protocol — the org that learns from itself (SOFI v5)

> **Foundation:** Serves Teaching **V (Continuous Metamorphosis)** — the loop must feed the next cycle — made real. The OODA docs (`engine/ooda/REFLECTION.md`) described this layer; v5 ships it as running code. Read `engine/DOCTRINE.md` and `context-and-memory.md` (memory-types) first.

An org that files the same escalation twice has a memory problem, not a skill problem. Reflection is how SOFI turns raw episodic history (`HANDOFFS.md`) into durable procedural lessons (`LESSONS.md`) that change future behavior — Reflexion's episodic-buffer idea (arXiv:2303.11366), git-native.

## The three hard rules (from the research, not opinion)
1. **Scheduled, never per-turn.** Continuous "update memory after every interaction" measurably *degrades* memory quality (arXiv:2605.12978). Reflection runs at **gate-close** or **on demand** (`/sofi-reflect`), never inside a working turn. Specialists do not self-reflect mid-task — the CEO runs the loop over closed work.
2. **Retain by default, consolidate deliberately.** Never overwrite or delete a raw episode to "tidy up." The engine only *adds* distilled lessons for signals it hasn't already distilled (dedup by signature). Raw HANDOFFS history stays intact.
3. **Distil to a lesson, not a re-summary.** A lesson is `situation · what-failed · rule` in one or two lines — the durable rule that prevents recurrence — not a paragraph re-narrating the ticket. Logs don't compound; rules do.

## The loop (`/sofi-reflect`, run by the CEO)
1. **Locate (0 model tokens)** — `python3 engine/tooling/agents/ceo/reflection_engine.py scan --prj <PRJ>` mechanically finds NEW learning candidates: every escalation / circuit-breaker / rejected ticket, and any ticket-type that recurred ≥3× against the same target (a candidate for a reusable template). It excludes anything already in `LESSONS.md`.
2. **Distil (model judgment)** — for each candidate, the CEO writes ONE grounded lesson: what the situation was, what actually failed, and the rule that would prevent it. Cite the ticket (G1, `grounding.md`).
3. **Write** — `reflection_engine.py write --prj <PRJ> --sig <sig> --situation ... --failed ... --rule ... --source <TKT> --date <YYYY-MM-DD>` appends it to `_context/LESSONS.md`. Idempotent on `--sig`.
4. **Promote (optional)** — if a lesson is a reusable *pattern* (a recurring-pattern candidate, or a delegation that needed 2+ correction rounds), propose lifting it into a durable artifact: an updated agent spec, an RCCF template, or a `registry.yaml` power (`proposed → piloted → promoted`). This is Voyager's skill-library-commit step — the org's capability compounds, not just its caution.
5. **Feed forward** — `LESSONS.md` is procedural memory: agents read it on boot alongside the rest of the brain, so a distilled rule actually changes the next delegation. A lesson nobody reads is a log.

## What reflection does NOT do
- It does not auto-apply lessons to doctrine or specs — that stays CEO judgment (CEO-no-write-code discipline extends to no-silent-doctrine-rewrite). Reflection *proposes*; a human/CEO decides.
- It does not build a vector store or embedding index — grep + frontmatter over `LESSONS.md` is sufficient at SOFI's scale (research verdict). Reconsider only at dozens of concurrent projects.
- It does not run continuously or inside a specialist's turn — see rule 1.
