# The Two-Terminal Strategy: How to Save Millions of Tokens in Autonomous AI Coding

**Source:** https://www.aiwithmo.com/prompts/claude-code-glm

## Summary
The article tackles the "token burn" problem in AI-assisted coding: using a single powerful, expensive model for every phase of development wastes budget and degrades quality as context grows (models forget instructions, hallucinate code). The author reports monthly usage of ~30M tokens that could have ballooned to 100M+ without a fix. The proposed fix splits work across two models/terminals running in parallel on the same project — one purely for planning, one purely for execution.

## Key Techniques / Patterns
- **Architect/Executor split**: a premium model (Claude Opus 4.7) only plans — it never writes executable code, only a detailed `implementation_plan.md`.
- **Plan decomposition**: the plan breaks the project into micro-tasks, each with explicit verification steps and success criteria.
- **Cheaper executor model**: a capable-but-cheap model (GLM-5.1) reads the plan and autonomously executes tasks, relying on the plan's precision instead of its own judgment.
- **Checklist-driven execution** to prevent hallucination — instructions must be unambiguous, not open-ended.
- **Cost-tiered model routing**: reserve the expensive model for deep analysis/architecture only; route mechanical execution to the cheaper model.

## Concrete Examples From the Article
- Monthly token usage cited: ~30 million tokens actually used, vs. a potential 100M+ without this strategy.
- Named models: Claude Opus 4.7 (architect/planner) and GLM-5.1 (executor), with GLM-5.1 pitched as a "significantly cheaper" alternative starting at ~$18/month.
- A performance claim that GLM-5.1 alone can handle roughly "5x" the workload of using Claude Code by itself (source's exact framing was ambiguous but directionally about capacity/cost ratio).

## Relevance to SOFI
This is directly applicable — it's essentially a two-tier version of the routing ladder SOFI already codifies (🟢 haiku → 🔵 sonnet → 🔮 fable → 🟣 opus, "always pick cheapest that clears bar"). The article's Architect/Executor split maps closely onto SOFI's gate-sequenced delegation: an architect-tier agent (Fable/Opus) produces a frozen plan/spec artifact, and cheaper agents (Haiku/Sonnet) execute against it via RCCF blocks — which SOFI already does structurally through `/sofi-delegate` and the gate lifecycle. The reinforcing idea worth adopting explicitly: treat the plan artifact itself (not just the model tier) as the mechanism that lets a cheap executor run long unsupervised stretches without drifting — i.e., plan quality is what buys token savings, not just model choice.

## Actionable Takeaway
When routing Build-gate (Gate 4) work, ensure the upstream architecture/spec artifact (from Fable/Opus at Gate 3) is broken into micro-tasks with explicit verification/success criteria before handoff — this is what should let Haiku/Sonnet executors run longer autonomous stretches without escalation, not just the model-tier choice alone.
