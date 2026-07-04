# Advisor Mode: Strategic Use of Claude Models

**Source:** https://www.aiwithmo.com/prompts/advisor-mode

## Summary
"Advisor Mode" (`/model opus-plan` or `/advisor`) splits work between Opus (architecture/planning, ~5x Sonnet's per-token cost) and Sonnet (execution — writing code, applying changes), since execution consumes the majority of tokens in a coding session and doesn't need the expensive model.

## Key Techniques / Patterns
- Opus reasons through the plan; Sonnet inherits the full context and executes it.
- Review the Opus plan carefully before approving — correct misunderstandings in plain English before execution starts, not after.
- Use Haiku for purely mechanical tasks (renaming, quick edits).

## Concrete Examples From the Article
None beyond the model-split workflow itself — this is a technique article, not a case study.

## Relevance to SOFI
**Naming collision, not conceptual overlap**: SOFI's new "Advisor" role (per-tier cross-tier gateway) is unrelated to this article's "Advisor Mode" (a model-tiering workflow toggle). The underlying idea — expensive model for planning, cheap model for execution — is exactly SOFI's `routing.yaml` ladder (deep/gatekeeper/workhorse/mechanical), already applied per-role org-wide rather than as a session toggle.

## Actionable Takeaway
None — SOFI already implements this pattern more comprehensively (per-role fixed routing vs. a manual per-session toggle). Worth flagging the naming collision in team docs so nobody confuses SOFI's Advisor role with this article's Advisor Mode workflow.
