# Self-Improving LLM Agents: Reflection, Skill Libraries, Procedural Memory

## State of the art (2025-2026)

The field converged on one idea: **don't fine-tune, write to memory**. Three lineages matter.

**Reflexion (Shinn et al., NeurIPS 2023, arXiv:2303.11366).** Actor/Evaluator/Self-Reflection loop: the actor attempts a task, an evaluator scores the trajectory (unit tests, scalar reward, or free-form critique), and a self-reflection model converts that feedback into a short natural-language lesson ("I failed because I assumed X; next time check Y first"). The lesson is appended to an **episodic memory buffer** and re-injected as context on the next trial of the *same* task. No weight updates. 91% pass@1 on HumanEval vs GPT-4's 80% baseline. Key limit: memory is per-task, unbounded growth, no cross-task generalization.

**Voyager (Wang et al., arXiv:2305.16291).** Three components: (1) automatic curriculum that proposes the next-hardest task from what the agent already knows, (2) an **ever-growing skill library** — each skill is executable JS code with a natural-language description, embedded and stored in a vector DB, retrieved by semantic similarity to the current situation, (3) iterative prompting: generate code → execute → catch environment/compiler errors → self-verify against sub-goals → refine, looping until the skill passes, then commit it to the library. Skills are *composable* (new skills call old ones), which is what avoids catastrophic forgetting — this is procedural memory as literal reusable code, not text.

**Procedural memory frameworks (2025).** Memp (arXiv:2508.06433) formalizes a **build → retrieve → update** cycle: distill successful trajectories into reusable procedure templates (not raw logs), retrieve the nearest procedure for a new task, and update/merge procedures as outcomes come in — explicitly separate from episodic (raw instance) and semantic (abstracted fact) memory. The "From Storage to Experience" survey (arXiv:2605.06716) gives the standard lifecycle: **acquisition → encoding → consolidation → retrieval → forgetting**, and stresses that *consolidation* (merging/abstracting episodes into semantic or procedural form) is what makes memory compound instead of just growing.

**A load-bearing counter-finding:** "Useful Memories Become Faulty When Continuously Updated by LLMs" (arXiv:2605.12978) and related work show naive "update memory after every interaction" designs degrade quality over time — agents given explicit retain/delete/consolidate actions and allowed to *default to keeping* raw episodes outperform forced-consolidation-every-turn designs. Reflection must be **scheduled and selective**, not continuous.

**Anthropic's own engineering guidance** (effective-context-engineering-for-ai-agents) formalizes "structured note-taking": persist state outside the context window (progress notes, maps, tallies), pull back in on resume; plus a shipped memory tool (file-based) for cross-session state, and "compaction" (summarize + discard redundant tool output, keep architectural decisions/unresolved bugs). Anthropic also documents Claude 4 being usable as its own prompt-engineer: given a failure trace, it can diagnose and rewrite the prompt that caused it — the mechanism behind automatic prompt optimization (APE: LLM proposes+scores candidate prompts; TextGrad: treats a text critique of a trajectory as a "gradient" back-propagated into the upstream prompt).

**Practitioner pattern (2026, widely replicated, e.g. jngiam's "self-improving Claude"):** a `learnings.md`/`memory.md` per skill, read at the top of every run and appended at the end — version-controlled, git-diffable, human-auditable. This is the git-native equivalent of Reflexion's episodic buffer, and it's the pattern closest to SOFI's existing brain files.

## Concrete techniques worth adopting

1. **Reflexion-style post-mortem note, not full transcript.** After each task/gate, generate one short natural-language "what went wrong / what to do differently" lesson from the outcome, not the raw log. Matters because raw traces don't compound — lessons do.
2. **Skill-library extraction (Voyager pattern).** When a delegation succeeds cleanly and is reusable, promote it to a named, retrievable artifact (template/RCCF block/checklist) rather than leaving it buried in one project's history. Matters because it turns one-off wins into org-wide capability.
3. **Build-retrieve-update cycle for procedures (Memp).** Explicitly separate "raw episode" from "distilled procedure": don't just append to a log, periodically compress N episodes into one reusable procedure entry keyed by task-type. Matters because unbounded raw history is unqueryable at scale.
4. **Scheduled consolidation, not per-turn.** Run reflection as a batch job over the last N sessions/tickets, not on every single write. Matters because continuous forced-consolidation measurably degrades memory quality (arXiv:2605.12978) — retain-by-default, consolidate-on-schedule.
5. **Retain/delete/consolidate as explicit actions**, each with its own trigger, not a single "update memory" step. Matters because it prevents silent lossy overwrites of still-useful episodes.
6. **Trace-driven prompt/instruction repair (TextGrad/APE style).** When a delegation fails, feed the failure + the RCCF block that produced it back to a model and ask for a revised RCCF/agent-prompt, applied as a diff to the source file, not just remembered informally. Matters because it closes the loop from "we noticed a failure" to "the artifact that caused it is fixed."
7. **Frontmatter/structured fields on memory entries.** Every taxonomy (Reflexion buffer, Memp, the survey) treats entries as structured records (task type, outcome, embedding key) not free prose, specifically to make retrieval and consolidation tractable. Matters for query-ability at scale.

## How it applies to SOFI

**Already right:** SOFI's 4-file brain (STATE/CONTEXT/DECISIONS/HANDOFFS.md) *is* a git-native episodic memory buffer — durable, diffable, human-auditable, closely matching the practitioner `learnings.md` pattern and Anthropic's "structured note-taking outside the context window." The RCCF delegation block is effectively a versioned procedure template already (procedural memory as a checked-in artifact, à la Voyager's skill-as-code, minus the auto-promotion). Tier isolation + gate bars act as the "retain by default, consolidate deliberately" discipline the 2605.12978 finding argues for — SOFI doesn't silently overwrite state.

**Genuinely missing (confirms the prior DEVELOPMENT-PLAN gaps):**
- **No scheduled reflection/consolidation job.** HANDOFFS.md accumulates raw episodes but nothing periodically distills them into a reusable lesson or procedure (the Reflexion/Memp step). This is the highest-leverage gap — a `/sofi-reflect` that runs on a cadence (e.g., every N checkpoints or gate exits), reads recent HANDOFFS+DECISIONS, and writes short structured lessons back (not full re-summaries) would close it cheaply on haiku/sonnet.
- **No extract-to-template promotion path.** When an RCCF delegation or fix pattern proves reusable across projects, nothing lifts it out of one PRJ's brain into `engine/agents/**` or `.claude/agents/` as a durable improvement — this is exactly Voyager's skill-library-commit step, and SOFI's registry.yaml/SUPERPOWERS.md "proposed → piloted → promoted" ladder already has the *slot* for it, just not the trigger.
- **No frontmatter on brain files**, so nothing can query "all lessons about X" without full-file reads — directly the structured-record gap the surveys flag as necessary for retrieval to scale past a handful of projects.
- **No failure-trace-to-prompt-repair loop.** When a delegation clearly fails a gate bar, there's no automated step that diffs the RCCF/agent spec that caused it (TextGrad/APE pattern) — currently that's manual CEO judgment only.

**Would be over-engineering for SOFI right now:** embedding-based vector retrieval over the skill library (Voyager needs it because it has hundreds of Minecraft skills; SOFI has ~30 agents and a handful of projects — grep-first, frontmatter-tagged markdown is sufficient and matches the "few token do trick" doctrine); per-turn memory updates (explicitly shown harmful, and SOFI's checkpoint-per-milestone cadence already avoids this); a separate vector DB or memory service (adds an infra dependency and ops surface disproportionate to the current corpus size — the existing git-backed files scale fine until there are dozens of concurrent projects).

## Sources
- https://arxiv.org/abs/2303.11366 (Reflexion)
- https://arxiv.org/abs/2305.16291 (Voyager)
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://arxiv.org/pdf/2508.06433 (Memp: Exploring Agent Procedural Memory)
- https://langchain-ai.github.io/langmem/
- https://arxiv.org/pdf/2603.10600 (Trajectory-Informed Memory Generation for Self-Improving Agent Systems)
- https://arxiv.org/pdf/2605.06716 (From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms)
- https://arxiv.org/pdf/2605.12978 (Useful Memories Become Faulty When Continuously Updated by LLMs)
- https://jngiam.bearblog.dev/the-instruction-that-turns-claude-into-a-self-improving-system/
