# Vibe Coding Done Right: Why Context Engineering Beats a Powerful Model Every Time

**Source:** https://www.aiwithmo.com/prompts/context-engineering-vibe-coding

## Summary
The article (Arabic, "Prompts" category) argues that AI-assisted coding ("vibe coding") fails not because models are weak but because developers give vague, unstructured requests, forcing the AI to invent undefined architecture and produce internally inconsistent projects. The fix is **context engineering**: preparing structured project files up front so the AI always works from a stable source of truth instead of guessing. This reframes the developer's role from casual prompter to project architect directing an AI worker, and the method is claimed to work across Claude Code, Codex, Gemini, Cursor, and Lovable.

## Key Techniques / Patterns
- Maintain four standing files as the project's source of truth: **ROADMAP.md** (goal, stack, phased plan with outcomes/tasks, explicit out-of-scope items), **ARCHITECTURE.md** (folder structure, data models, rationale, naming conventions), **CONTEXT.md** (behavior rules: read files first, plan before coding, stay in scope, work one phase at a time), **PROGRESS.md** (current phase, done/in-progress/next, known issues).
- Session workflow: start each session by having the AI read all four files → request a plan for the current phase only → wait for human approval → execute a single phase → update PROGRESS.md → start a fresh session for the next phase.
- Never let the AI design and build simultaneously; reviewing the plan before code is claimed to catch most errors early.
- Split oversized phases into sub-tasks inside ROADMAP.md rather than letting scope creep into one session.

## Concrete Examples From the Article
Sample prompts given: "Read ROADMAP.md, ARCHITECTURE.md and CONTEXT.md"; "We are on Phase 1. Write a plan for it and wait for my approval"; "Update PROGRESS.md". No case studies, benchmarks, or before/after metrics are provided for the method itself (a "75%" figure and a "$0 MVP" reference appear only in unrelated related-articles links, not as evidence for this technique).

## Relevance to SOFI
Directly applicable — this is essentially a lightweight version of SOFI's own architecture. The article's four-file discipline (ROADMAP/ARCHITECTURE/CONTEXT/PROGRESS + read-first, plan-then-approve, one-phase-per-session) maps almost 1:1 onto SOFI's existing brain (`STATE.md`/`CONTEXT.md`/`DECISIONS.md`/`HANDOFFS.md`) and the universal contract (sync → read brain → ticket → act → checkpoint → update brain → next ticket). It validates SOFI's design choice rather than introducing something new, and confirms the pattern generalizes across AI coding tools, not just Claude.

## Actionable Takeaway
Reinforce (don't change) the existing discipline: keep enforcing "no blind start / no uncommitted handoff" and consider explicitly requiring agents to state a per-phase plan and await gate/human approval before multi-file builds — the article's single strongest claim (plan-review catches most errors) is a cheap addition to `/sofi-gate` checks that SOFI doesn't yet formalize as a distinct pre-build step.
