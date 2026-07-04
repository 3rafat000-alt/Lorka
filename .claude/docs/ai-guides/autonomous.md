# Get Claude Code to Work Autonomously for Hours (GSD)

**Source:** https://www.aiwithmo.com/prompts/autonomous

## Summary
Using the GSD (Get Shit Done) framework's `/gsd-do` and `/gsd-autonomous` commands, Claude Code breaks a project into phases and then runs each phase — research, context updates, execution, summary — without manual intervention between steps.

## Key Techniques / Patterns
- Phase-based planning before any code is written (`/gsd-do`).
- Autonomous execution per phase (`/gsd-autonomous`), optionally starting at a specific phase (`--only 5`).
- `claude --dangerously-skip-permissions` to avoid repeated file-access interruptions on long runs.

## Concrete Examples From the Article
Restaurant POS dashboard: divided into sequential phases via `/gsd-do`, then autonomous mode launched from a specific phase, running for hours unattended.

## Relevance to SOFI
Matches SOFI's gate-sequenced lifecycle (0→8) closely — phases with a Definition of Done before advancing. The permission-bypass technique doesn't apply directly (SOFI's PreToolUse hook enforces security guardrails deliberately; bypassing it would violate SOFI's own git-discipline/security doctrine).

## Actionable Takeaway
None new — SOFI's gate model already implements phase-based autonomous execution more rigorously (with artifact validation via `gates.py`, not just a phase counter). Confirms the gate approach is sound.
