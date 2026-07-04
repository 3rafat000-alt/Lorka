# AI Updates You Probably Missed: New Features in Claude Code, Codex, and Gemini

**Source:** https://www.aiwithmo.com/prompts/ai-updates-roundup-may-2026

## Summary
A roundup of quietly-shipped updates (no major fanfare) across Anthropic's Claude Code, OpenAI's Codex, and Google's Gemini App. Claude Code gains a Fast Mode, background tasks, and clearer usage billing; Codex gains a Fast Mode, Computer Use, and long-horizon autonomous "Goal Mode"; Gemini App gets NotebookLM integration, usage transparency, personal-data grounding, and native desktop support.

## Key Techniques / Patterns
- Fast/low-latency inference paths dedicated to rapid iteration loops, separate from default deep-reasoning mode
- Background task execution decoupled from the interactive session (Claude Code `Ctrl+B`)
- Side-channel Q&A during a running task without derailing it (`/btw`)
- Per-session model switching instead of global config changes
- Autonomous multi-step/multi-day goal pursuit (Codex Goal Mode)
- Instant visual/textual app-state capture to seed agent context (Codex Appshots)
- Cross-session memory recall of prior task context
- Usage transparency dashboards replacing opaque quota limits
- Personal-data grounding — connecting an assistant to a user's own service ecosystem (Gemini Personal Intelligence)

## Concrete Examples From the Article
- Claude Code Fast Mode: ~2.5x higher output speed, running on Opus 4.7 by default; PR status in terminal footer refreshes every 60 seconds
- Codex Fast Mode uses GPT-5.3-Codex-Spark; Goal Mode runs autonomously for "hours or even days"
- Gemini: free music generation via Lyria 3 Pro (max 3 minutes), file generation across 10 formats, 55+ curated plugins

## Relevance to SOFI
Partially applicable. This is mostly a product-update digest, not a technique article, but two patterns transfer directly to SOFI's own use of Claude Code as its execution substrate: (1) background task execution (`Ctrl+B`) maps to SOFI's parallel-squad worktree model — long-running agent work shouldn't block the orchestrating session; (2) per-session model switching reinforces SOFI's existing economic routing ladder (haiku→sonnet→fable→opus) — operators can drop to Fast Mode for cheap iteration and escalate only on evidence, same doctrine already codified in `engine/routing/routing.yaml`. The Codex/Gemini feature lists (Goal Mode, Appshots, Personal Intelligence) are competitor product features with no direct architectural technique to extract for a multi-agent dev org.

## Actionable Takeaway
Confirm whether Claude Code's Fast Mode (`/fast`) is usable inside SOFI subagent spawns for the 🟢 haiku-tier "80% of routine ops" — if so, document it in `engine/routing/routing.yaml` as a speed lever alongside the existing model-cost ladder.
