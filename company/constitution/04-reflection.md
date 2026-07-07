# 🌙 Article 04 — Reflection (scheduled dreaming)

> **Foundation: serves Teaching V (Continuous Metamorphosis)** — the loop must feed the next cycle, made real. Read `company/CONSTITUTION.md` and `company/brain/BRAIN.md` (memory types) first.

A company that files the same escalation twice has a memory problem, not a skill problem. Reflection is how SOFI turns raw episodic history (`HANDOFFS.md`) into durable procedural lessons (`LESSONS.md`) that change future behavior. In v6 the loop is owned by the knowledge room: **`knw-reflector`** runs it, `knw-memory-curator` keeps the output queryable, and the boardroom decides what gets promoted. Skill: `/sofi-reflect`.

## The three hard rules (from the research, not opinion)

1. **Scheduled, never per-turn.** Continuous "update memory after every interaction" measurably *degrades* memory quality. Reflection runs at **gate-close** or **on demand** (`/sofi-reflect`), never inside a working turn. Specialists do not self-reflect mid-task — `knw-reflector` runs the loop over *closed* work.
2. **Retain by default, consolidate deliberately.** Never overwrite or delete a raw episode to "tidy up." The engine only *adds* distilled lessons for signals it hasn't already distilled (dedup by `sig:`). Raw `HANDOFFS.md` history stays intact — it is the audit trail and the future training ground.
3. **Distil to a lesson, not a re-summary.** A lesson is `situation · what-failed · rule` in one or two lines — the durable rule that prevents recurrence — not a paragraph re-narrating the ticket. Logs don't compound; rules do.

## The loop (5 steps)

1. **Locate — 0 model tokens.** Python mechanically finds NEW learning candidates in the project's history: every escalation, circuit-breaker trip, and `rejected` ticket, plus any ticket pattern that recurred ≥3× against the same target (a candidate for a reusable template). Already-distilled signals are excluded by signature against `LESSONS.md`. Python-locates-model-judges (Article 05) — the model never greps its own history.
2. **Distil — model judgment.** For each candidate, write ONE grounded lesson: what the situation was, what actually failed, and the rule that would prevent it. Cite the source ticket (G1, `02-grounding.md`). One candidate, one lesson — no essays.
3. **Write — idempotent on `sig`.** Append to `projects/<PRJ>/_context/LESSONS.md` as `## LES-NNN` with `sig` / `mem` / `situation` / `what_failed` / `rule` / `source` frontmatter fields (schema: `company/brain/templates/`). Re-running the loop never duplicates a lesson.
4. **Promote — optional, gated.** If a lesson is a reusable *pattern* (a recurring-pattern candidate, or a delegation that needed 2+ correction rounds), propose lifting it into a durable artifact: an updated agent spec in `company/rooms/`, a Work Order template, or a power in `company/nexus/registry.yaml` (`proposed → piloted → promoted`, with a `DECISIONS.md` row). This is the skill-library step — the company's capability compounds, not just its caution.
5. **Feed forward.** `LESSONS.md` is procedural memory: agents read it on boot alongside the rest of the brain (step 1 of the universal contract), so a distilled rule actually changes the next delegation. A lesson nobody reads is a log. Org-wide lessons roll up to `company/brain/org/LESSONS.md` via `knw-lead`.

## What reflection does NOT do

- **It does not auto-rewrite doctrine or specs.** Reflection *proposes*; the CEO decides — recorded in `DECISIONS.md`. The CEO-never-writes-code discipline extends to no-silent-doctrine-rewrite. Constitution amendments follow the amendment clause, full stop.
- **It does not build a vector store.** Grep + frontmatter over `LESSONS.md` (`sofi brain-query`) is sufficient at SOFI's scale — a deliberate decision, revisit only at dozens of concurrent projects.
- **It does not run continuously or inside a specialist's turn** — rule 1. A specialist that hits a failure escalates or trips the circuit breaker; the *signal* is recorded, the *dreaming* happens later.
- **It does not summarize.** Coherence audits (contradiction hunting between brain files) are part of the same scheduled pass — conflicts found are surfaced per G5, never silently merged.
