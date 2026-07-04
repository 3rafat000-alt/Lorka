# Ultracode & Dynamic Workflows

**Source:** https://www.aiwithmo.com/prompts/ultracode-agent-orchestration

## Summary
Ultracode has Claude write a JavaScript orchestration script on the fly, specific to the task, rather than having the model itself coordinate sequentially. The script becomes the coordinator, freeing model reasoning for actual work. Supports up to 1,000 agents total, 16 concurrent.

## Key Techniques / Patterns
- **Understand → Change → Verify loop**: cluster 1 maps architecture, cluster 2 executes changes, cluster 3 verifies, loop until verification passes.
- **Adversarial validation**: a separate set of agents actively tries to refute findings from the first set, until results converge — distinguishes verified from merely-plausible output.
- Token-efficient coordination: 113 agents consumed 1.95M tokens while the JS coordination layer itself "spent nothing."

## Concrete Examples From the Article
Bun's creator ported 750,000 lines from Zig to Rust, 99.8% of the existing test suite passing, in 11 days — work traditionally measured in quarters.

## Relevance to SOFI
This is the exact mechanism SOFI's own `Workflow` tool implements (pipeline/parallel fan-out, agent-authored orchestration scripts, adversarial-verify pattern documented in the tool's own guidance). Direct convergent validation — SOFI independently arrived at the same architecture the field converged on.

## Actionable Takeaway
None needed — already implemented. Worth noting explicitly in SOFI doctrine (e.g. `engine/protocols/`) that the `Workflow` tool *is* SOFI's Ultracode-equivalent, so agents recognize when to reach for it (large, unclear-decomposition, quality-over-cost tasks) using the same decision criteria this article gives: task exceeds one context window, decomposition strategy unknown upfront, quality outweighs token economy.
