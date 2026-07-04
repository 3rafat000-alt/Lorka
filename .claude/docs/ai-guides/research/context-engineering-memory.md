# Context Engineering for Agents (2025-2026): Context Rot, Compaction, Structured Memory

## State of the art (2025-2026)

**Context rot is measured, not folklore.** Chroma's 2025 study tested 18 frontier models (GPT-4.1, Claude Opus 4, Gemini 2.5) and found monotonically decreasing F1 as input length grows, with steepest drop in the 100K-500K token range — even when the needed info is present ("needle in haystack" isn't enough). Three compounding mechanisms: (1) lost-in-the-middle attention bias (U-shaped when <50% context full, recency-biased when >50% full), (2) quadratic attention dilution, (3) distractor interference — semantically-similar-but-wrong content actively misleads. Counterintuitively, *coherent, logically structured* context degrades performance more than shuffled content in some tests. Follow-on work (Slipstream, arXiv 2605.08580) reports 13.9-85% degradation and argues agents need active context management **well before** the nominal window is exhausted, not just at the limit.

**Anthropic's canonical framing** ("Effective context engineering for AI agents," Sept 2025): context is a finite, expensive resource with diminishing marginal return per token ("attention budget"); the job is finding the smallest high-signal token set, not maximizing recall. Their concrete architecture, also detailed in "Effective harnesses for long-running agents":
- **Compaction**: summarize near the context limit, reinit with a compressed summary that preserves architectural decisions/unresolved issues, discards redundant tool outputs. Tune the summarization prompt on real agent traces — start high-recall, then tighten precision. Clearing stale tool results is called out as "the safest, lightest-touch form of compaction."
- **Structured note-taking / agentic memory**: agent periodically writes to a persistent file (progress log, NOTES.md, feature-list JSON with `passes` booleans) *outside* the context window, re-reads it on the next turn/session. Demonstrated at extreme scale by their Pokémon-playing agent maintaining strategy notes across thousands of steps without being told to.
- **Sub-agent architecture with clean contexts**: a lead agent spawns focused sub-agents that may burn 10K+ tokens exploring, but return only a condensed distillate to the parent — isolates noisy search from the orchestrating context. This is the direct analog of SOFI's Advisor→specialist delegation.
- **Memory tool (file-based, public beta)**: first-class Anthropic API primitive for agents to read/write a persistent knowledge store across sessions, separate from RAG.
- **Just-in-time retrieval / progressive disclosure**: keep lightweight references (file paths, IDs) in context; load full content only when needed via tool calls, using naming/timestamps as retrieval signals — vs. eagerly stuffing everything up front.
- **System prompt "right altitude"**: neither hardcoded brittle if-else logic nor vague generalities — specific enough to steer, flexible enough to generalize; organized with clear section headers (XML/Markdown).

**Memory taxonomy converges across frameworks.** LangMem (LangChain) and Claude Code's own memory model (per practitioner writeups) both land on the same triad, now standard in 2026 agent literature:
- **Semantic memory**: durable facts/preferences (CLAUDE.md hierarchy; LangMem "profiles"/"collections").
- **Episodic memory**: records of specific past interactions distilled into reusable examples (LangMem: "the situation, reasoning, and why it worked" — not raw transcript).
- **Procedural memory**: memory that changes *behavior*, not just facts — agents rewriting their own system instructions/skills from accumulated feedback (LangMem procedural memory; Claude Code's `.claude/skills/` with progressive disclosure — ~100-token index always loaded, full body loaded on demand).
- Formation timing splits into **hot-path** (in-conversation, adds latency, immediate) vs **background/subconscious** (post-hoc, no latency cost, higher recall) — LangMem explicitly supports both; background extraction is the dominant 2026 pattern for cost reasons.
- **Memory distillation** = reconciliation, not append-only logging: new info updates/invalidates/consolidates existing memory entries rather than growing a document forever (LangMem "enrichment"; Claude Code "Dreams" — a consolidation job that merges duplicates and prunes stale entries).

**Working memory is explicitly named as the volatile layer** (the live context window) and treated as categorically different from the three persistent memory types above — losing it is fine, losing persistent memory is not.

## Concrete techniques worth adopting

1. **Compaction with a tuned summarization prompt, not `/clear`** — trigger before hitting the limit (30% threshold cited in recent papers), preserve decisions/open issues, discard resolved tool output verbatim. Why: prevents context rot from ever reaching the danger zone instead of reacting to it.
2. **Structured note-taking outside the context window** — a running progress/scratch file the agent re-reads each turn, distinct from the final deliverable. Why: gives long-horizon tasks a memory that survives compaction and session boundaries without re-deriving state.
3. **Sub-agent distillation contract** — sub-agent may burn a large budget internally but returns a fixed-shape condensed summary to the parent. Why: isolates exploration noise from the orchestrator's context, the single biggest lever against context rot in multi-agent systems.
4. **Tri-partite memory typing (semantic/episodic/procedural) with different write paths** — facts vs. past-episode lessons vs. self-modifying behavior, each with its own store and update rule. Why: conflating them into one undifferentiated memory file is why memory files rot into unusable logs.
5. **Background (post-hoc) memory formation over hot-path** — extract/distill memory after the unit of work closes, not mid-task. Why: avoids latency tax and lets the distillation model see the whole episode before deciding what's durable.
6. **Memory consolidation/"dreams" pass** — a periodic job that merges duplicate entries and prunes stale ones in persistent memory. Why: without this, append-only memory files degrade into their own context-rot problem.
7. **Progressive disclosure for procedural knowledge** — tiny always-loaded index + full instructions loaded only on trigger (Claude Skills pattern). Why: keeps the "menu" of available capabilities cheap while capability count scales.
8. **Structured frontmatter/metadata on memory artifacts** for targeted retrieval instead of full-file reads. Why: directly attacks context rot by letting the next session load only the relevant slice.
9. **Just-in-time retrieval with light-weight references** (paths/IDs in context, full content fetched on demand) over eager context stuffing. Why: matches Chroma's finding that presence of information isn't enough — position and volume both cost accuracy.

## How it applies to SOFI

**Already right:** SOFI's Advisor→specialist tier isolation *is* the sub-agent distillation pattern Anthropic describes — RCCF blocks force a bounded, condensed handoff instead of raw context leakage across tiers. The 4-file brain (STATE/CONTEXT/DECISIONS/HANDOFFS) is a legitimate persistent-memory substrate, and `sofi checkpoint`/`sofi sync` already enforce a git-backed "never blind start, never silent handoff" discipline that most agent frameworks lack entirely. `_scratch/` purged at gate exit is a correct working-memory boundary.

**Genuinely missing, worth adopting:**
- **No compaction discipline for RCCF/delegation payloads.** Nothing in the current design tunes what gets summarized vs. dropped when a project's CONTEXT.md/HANDOFFS.md history grows long — it will hit context rot as projects mature past dozens of tickets. A compaction pass (background, triggered at a size threshold, condensing resolved tickets into a distilled paragraph) belongs in `sofi_tools`.
- **No memory-type separation.** STATE/CONTEXT/DECISIONS/HANDOFFS are functionally organized (what/why/who's-next) but not memory-type organized — DECISIONS.md is closest to procedural memory (should feed back into agent behavior, not just be a log), HANDOFFS is episodic, CONTEXT is semantic. This matches the DEVELOPMENT-PLAN gap #6 (no structured frontmatter) — frontmatter should encode memory-type + staleness so a future consolidation job (SOFI's "dreams" equivalent) can prune/merge without full-file reads. This directly supports DEVELOPMENT-PLAN gap #2 (no scheduled reflection loop): the reflection loop's actual job should be exactly LangMem's background memory formation — read HANDOFFS history, distill episodic lessons into DECISIONS (procedural), not just re-read raw logs each boot.
- **No structured note-taking during long single-agent runs.** A specialist working a multi-hour ticket has no equivalent of Anthropic's "write progress notes outside the window" — only the final handoff. Worth a lightweight per-ticket scratch note convention feeding the eventual handoff, not a new subsystem.

**Would be over-engineering for SOFI right now:** a vector-DB/RAG memory layer, LangMem-style hot-path memory formation (SOFI's per-ticket cadence is already coarser-grained than chat turns, so latency isn't the constraint), or a general-purpose episodic-memory query API — SOFI's unit of work is a ticket/gate, not a conversation turn, so most memory papers' turn-level machinery is the wrong grain. The right move is compaction + frontmatter + a background distillation pass bolted onto the existing 4-file brain, not a new memory architecture.

## Sources
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- https://www.trychroma.com/research/context-rot
- https://langchain-ai.github.io/langmem/concepts/conceptual_guide/
- https://alexop.dev/posts/four-types-memory-coding-agents-claude-code/
- https://arxiv.org/pdf/2605.08580 (Slipstream: Trajectory-Grounded Compaction Validation for Long-Horizon Agents)
- https://arxiv.org/abs/2605.23296 (Parallel Context Compaction for Long-Horizon LLM Agent Serving)
- https://arxiv.org/pdf/2606.23525 (Self-Compacting Language Model Agents)
