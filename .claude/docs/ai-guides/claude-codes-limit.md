# Anthropic Postmortem: The Cause of Claude Code's Limit Drain and the Official Fix

**Source:** https://www.aiwithmo.com/prompts/claude-codes-limit

## Summary
On April 23, Anthropic published an official postmortem explaining a period of degraded Claude Code quality and abnormally fast consumption of account usage limits. Root cause: a bug in a prompt-caching optimization that cleared reasoning/context history on *every* turn instead of only on idle sessions, forcing continuous cache misses and full token retransmission on each request. Anthropic shipped a fix and reset all subscriber usage limits as compensation; users are told to update to v2.1.116+ via `claude update`.

## Key Techniques / Patterns
- Prompt-caching optimization and reasoning-history management (the subsystem that broke).
- Session-based memory clearing — should trigger only on idle, not every turn.
- Cache-miss mitigation as a first-class reliability concern, not just a cost concern.
- Transparent incident postmortems + compensating usage-limit resets as a trust-repair pattern.

## Concrete Examples From the Article
- The fix requires updating to Claude Code v2.1.116 or later via `claude update`.
- Anthropic's compensation: a full reset of usage limits for all affected subscribers.
- No other numbers, benchmarks, or code samples are given beyond the bug description and fix command.

## Relevance to SOFI
This is an incident postmortem/product-fix announcement, not a prompt-engineering or orchestration technique — there is no new pattern to adopt for agent design. The one operationally relevant point: SOFI's routing doctrine ("few token do trick," cost map in `engine/routing/routing.yaml`) implicitly assumes prompt caching works as expected across long agent sessions (STATE/CONTEXT/HANDOFFS reads, RCCF blocks, multi-turn delegations). A silent caching regression like the one described would inflate token cost and degrade context continuity without any code change on SOFI's side — the failure mode is invisible until limits/cost spike.

## Actionable Takeaway
Add a lightweight cache-health check to SOFI's tooling (e.g. in `engine/tooling/bin/sofi doctor` or a routing-cost log) that flags abnormal token-consumption growth per session as a leading indicator of upstream caching regressions like this one — not a new technique, just a defensive monitoring hook.
