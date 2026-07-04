# Claude Orchestration: Parallel AI Agent Patterns

**Source:** https://www.aiwithmo.com/prompts/claude-orchestration-parallel

## Summary
The productivity leap in AI isn't a smarter model, it's smarter architecture — moving from sequential single-agent processing (which hits a context/quality ceiling) to parallel multi-agent operation, analogous to computing's single-core-to-multi-core shift.

## Key Techniques / Patterns
Three implementation tiers:
1. **Background Agents** — async sub-tasks (Ctrl+B), main session continues, checked via `/tasks`.
2. **Agent Teams** (experimental) — parallel agents on distinct domains, direct inter-agent communication, no coordinator overhead.
3. **Managed Agents** (production) — up to 20 parallel specialists, coordinator decomposes, specialists run independently, metered cost.

## Concrete Examples From the Article
- Netflix processes logs from hundreds of simultaneous builds, isolating recurring patterns rather than individual failures.
- Harvey (legal AI) achieved ~6x completion-rate increase on document tasks via orchestration with persistent memory.

## Relevance to SOFI
The 3-tier model maps loosely onto SOFI's structure: Background Agents ≈ `Agent` tool async dispatch; Managed Agents ≈ the tier/Advisor/CEO hierarchy with a coordinator. **Agent Teams' "direct inter-agent communication without coordinator overhead" is the opposite of what SOFI just built** — mandatory Advisor-gateway for every cross-tier handoff, prioritizing traceability/governance over this article's speed pattern.

## Actionable Takeaway
Deliberate tradeoff, not a bug — but worth being conscious it costs latency the field is optimizing away. If SOFI's Advisor-gateway model is ever measured as a real bottleneck (not just theoretical overhead), revisit whether same-tier direct comms could extend to *adjacent*-tier fast paths for low-stakes tickets while keeping the gateway mandatory for anything gate-crossing/high-stakes.
