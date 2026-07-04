# Claude Agent Teams

**Source:** https://www.aiwithmo.com/prompts/claude-agent-teams

## Summary
A lead Claude instance decomposes a complex goal into parallel workstreams, spawning specialized teammate instances with dedicated context and tools. Teammates communicate directly with each other and the lead — no human coordinates handoffs.

## Key Techniques / Patterns
- **Lead-and-teammate structure**: lead decomposes/synthesizes, teammates work simultaneously on minimally-dependent streams.
- **Governance through architecture**: quality gates embedded in the initial prompt's criteria, not manual oversight; teammates submit plans to the lead for approval before executing.
- **"Dreaming" (added May 7, 2026)**: a scheduled process where agents review past sessions, extract behavioral patterns, and update memory automatically — creates compounding improvement over time, with measurable gaps between freshly-configured and month-old agents.

## Concrete Examples From the Article
- Anthropic's own compiler project: 16 agents built a 100,000-line Rust C compiler across ~2,000 sessions, capable of compiling the Linux kernel for x86/ARM/RISC-V.
- Netflix already runs multiagent orchestration in production for platform-team operations.

## Relevance to SOFI
Lead-and-teammate = CEO + tier structure, already present. Plan-approval-before-execution = SOFI's gate-check + Definition-of-Done pattern, already present. **"Dreaming" is a genuine gap** — SOFI's OODA has a conceptual "Reflection" layer but no actual scheduled process reviewing `HANDOFFS.md`/session history to auto-extract patterns and update doctrine/memory.

## Actionable Takeaway
Design a "dreaming" pass: a periodic (per-gate-close or nightly) job that reads recent `HANDOFFS.md`/`DECISIONS.md` entries across projects, extracts recurring friction points or successful patterns, and proposes doctrine updates (e.g. to `engine/protocols/` or a role's spec) for human review — not auto-applied, since SOFI's CEO-no-write-app-code doctrine implies doctrine changes need the same discipline.
