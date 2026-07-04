# The GSD Framework (Get Shit Done)

**Source:** https://www.aiwithmo.com/prompts/gsd-framework

## Summary
A structured methodology for reliable autonomous coding with Claude Code, addressing "Context Rot" — degradation from LLMs losing track of architecture across extended sessions.

## Key Techniques / Patterns
Three pillars: (1) **Memory Segmentation** — Plan/Execute/Review phases, Plan mode restricted to markdown checklists only (no code), context resets between phases; (2) **Sub-Agent Ecosystem** — specialized roles (Architect for roadmaps, Coder for execution, Tester for verification), prevents task-jumping; (3) **Autonomous Self-Correction Loop** — verification required before marking done, AI runs tests/reads output/debugs independently, only proceeds after clean exit codes and a git commit.

## Concrete Examples From the Article
Prompt pattern: "You are operating under the GSD framework. Step 1: Analyze requirements and create a plan. Do not write code. Step 2: Await approval..." — transforms the user's role from programmer to manager of an autonomous team.

## Relevance to SOFI
Directly matches SOFI's existing architecture: gate-sequenced phases with context boundaries (each gate = a phase), tier specialization (Architect≈Tier-1, Coder≈Tier-2, Tester≈Tier-3), and Definition-of-Done gates requiring verification (`sofi gate-check`, `validate_artifacts`) before a ticket closes.

## Actionable Takeaway
None new — SOFI's gate model is a more rigorous, machine-validated version of this exact framework (GSD's "clean exit code + git commit" check is what `gates.py`'s artifact validation formalizes). Good confirmation.
