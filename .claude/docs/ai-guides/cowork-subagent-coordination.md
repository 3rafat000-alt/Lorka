# Claude Cowork Sub-Agents

**Source:** https://www.aiwithmo.com/prompts/cowork-subagent-coordination

## Summary
Claude Cowork automatically decomposes complex tasks into parallel workstreams with zero manual configuration. Each sub-agent gets its own isolated context window. Claude alone decides whether a task warrants parallelization — the user never names agents or assigns work.

## Key Techniques / Patterns
- Automatic complexity evaluation: parallelization triggers only past a size threshold, not on light tasks.
- Isolated context per worker prevents scope creep and cross-contamination between workstreams.
- No user-facing configuration — automation over control.

## Concrete Examples From the Article
- File processing: 5 sub-agents each handling 4 files instead of 1 agent processing 20 sequentially.
- Research: parallel streams investigating a company, pulling data, and scanning context simultaneously.

## Relevance to SOFI
Directly validates SOFI's tier/worktree isolation model — each specialist already gets its own scoped context and git worktree, matching Cowork's "isolated context per worker" principle. The automatic-complexity-threshold idea (only parallelize past a size bar) is not something SOFI's gate/ticket model currently encodes — squads are always sequenced through CEO/Advisor delegation regardless of task size.

## Actionable Takeaway
Consider: should trivial single-file tickets skip the full RCCF+Advisor-gateway ceremony and route direct-to-specialist? Worth a threshold rule if delegation overhead is ever measured as a bottleneck on small tasks. Not urgent — no evidence yet that it is one.
