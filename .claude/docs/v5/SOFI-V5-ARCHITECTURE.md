# SOFI v5.0 — The Integrity & Intelligence Layer

## Executive summary
v4 built the **structure**: 30 agents, 5 tiers, Advisor gateways, a 9-gate lifecycle, a git-backed 4-file brain, economic routing. Six deep frontier-research sweeps (orchestration, context/memory, grounding, self-improvement, verification, spec-design — see `.claude/docs/ai-guides/research/`) independently **validate that structure as correct** for a compliance-oriented gated SDLC, and explicitly flag the alternatives (peer-to-peer mesh, vector-DB memory, 50-agent fan-out, trained verifier models) as over-engineering for SOFI's shape. So v5 does **not** rebuild the structure — that would destroy validated work. v5 adds the layer v4 lacks: agents that **can't hallucinate unchecked** (grounding), **can't self-report success** (verification), and an org that **learns from its own history** (reflection). Structure was the v4 achievement; integrity + intelligence is v5's.

## Design principles v5 adds
- **Ground or abstain.** Every factual claim cites a source or is marked unverified; "insufficient information" is a rewarded output, not a failure.
- **Outcome over self-report.** "Done / tests pass / migrated" is never trusted from the acting agent — the actual command output/exit code is the evidence.
- **Retain by default, consolidate on schedule.** Memory is distilled periodically (never per-turn — proven to degrade quality), and the org compounds lessons rather than re-reading raw logs.
- **Bounded autonomy beats unbounded.** Explicit effort/scope ceilings per delegation improve completion, not just safety.
- **Independent review, fixed-role.** Verification is a fresh-context adversarial pass against the original criteria — not the implementer grading itself, not free-form debate.

## Component catalog

### C1 — Grounding Protocol
- **What**: A five-rule anti-hallucination doctrine binding every agent, mapped to the agentic-hallucination taxonomy (reasoning/execution/perception/memory/communication).
- **Why more powerful**: Closes the #1 gap. Turns "sounds right" into "provably right or removed" across the whole org.
- **Files**: NEW `engine/protocols/grounding.md`; EDIT `engine/protocols/00-operating-system.md` (add Grounding to the universal contract); EDIT `engine/protocols/01-delegation-rccf.md` (grounding clause in Format).
- **Mechanism**: G1 source-or-silence (cite file:line/brain-file, else mark `[unverified]` and stop) · G2 abstention-rewarded (`insufficient information → escalate`) · G3 execution-truth (paste real command output+exit code, never assert) · G4 verified-vs-inferred tags · G5 conflict-surfacing.

### C2 — Reflection Engine ("dreaming")
- **What**: A scheduled, background consolidation job that reads recent HANDOFFS/DECISIONS, distills short structured lessons (Reflexion-style), and proposes template/doctrine improvements — never auto-applied.
- **Why more powerful**: The OODA "Reflection" layer was documentation only; this makes it real code. The org gets measurably better over time instead of repeating mistakes.
- **Files**: NEW `engine/tooling/agents/ceo/reflection_engine.py`; NEW `engine/protocols/reflection.md`; NEW `.claude/skills/sofi-reflect/SKILL.md`; writes to per-project `_context/LESSONS.md` (procedural memory).
- **Mechanism**: retain-by-default; consolidate on a cadence (per-gate-close or on demand), never per-turn; distill episode → lesson (`situation · what-failed · rule`), merge duplicates, prune stale; flag reusable patterns for promotion.

### C3 — Structured Queryable Brain
- **What**: Optional lightweight frontmatter on ticket/lesson blocks + a `brain query` capability.
- **Why more powerful**: Turns grep-only markdown into a queryable memory the reflection engine can consolidate by type without full-file reads.
- **Files**: EDIT `engine/tooling/sofi_tools/tickets.py` (parse `mem`/`type` fields — already parses `status`/`gate`); NEW query fn in `engine/tooling/sofi_tools/brain.py`; EDIT `engine/tooling/sofi_tools/cli.py` (`sofi brain-query`); EDIT `engine/protocols/context-and-memory.md` (memory-type doctrine: semantic=CONTEXT, episodic=HANDOFFS, procedural=DECISIONS/LESSONS).
- **Mechanism**: frontmatter keys `status·gate·type·mem·date`; `brain_query(prj, key=val)` filters ticket/lesson records; memory-type tag routes the reflection engine's consolidation.

### C4 — Verification Layer
- **What**: Codifies outcome-over-self-report + fixed-role adversarial self-verify + pass^k reliability + judge-bias awareness.
- **Why more powerful**: Catches plausible-but-wrong work before it advances a gate — the single highest-value agentic-QA lever per the research.
- **Files**: NEW `engine/protocols/verification.md`; EDIT `engine/tooling/sofi_tools/gates.py` (evidence-check: reject "done" tickets lacking pasted command output); EDIT `engine/protocols/spec-review.md` (add `UNKNOWN/insufficient-evidence` verdict + family-diversity note); EDIT `.claude/skills/sofi-secure/SKILL.md` (adversarial self-verify pass + per-finding execution plan).
- **Mechanism**: gate-bar `validate_evidence()` scans done-tickets for an evidence block; adversarial pass = fresh-context agent judges against original ticket criteria with an "Unknown" escape hatch; pass^k note for Gate 5/6.

### C5 — Budgeted Autonomy + Effort-Scaling
- **What**: A task-class → agent-count/call-budget table + hard scope ceilings per delegation.
- **Why more powerful**: Prevents both under- and over-spawning (Anthropic saw both failure directions until hardcoding the table); bounded agents complete more, not fewer, tasks.
- **Files**: EDIT `engine/routing/routing.yaml` (new `effort_scaling:` block); EDIT `engine/protocols/01-delegation-rccf.md` (effort hint + boundaries field + budget); EDIT `engine/protocols/handoff-and-interconnection.md` (context-boundary spawn rule + verbatim-forwarding).
- **Mechanism**: `effort_scaling` maps task classes (trivial-fix / single-role feature / cross-tier feature / audit-sweep / arbitration) to spawn width + call budget; RCCF carries an effort hint and a fail-safe stop condition.

### C6 — RCCF v2
- **What**: The delegation block gains a clarifying-question branch, frozen-brief enforcement, an explicit boundaries field, an effort hint, and the grounding clause.
- **Why more powerful**: Industry's answer (interview → freeze spec → implement) to the exact "solved the wrong problem because scope was inferred" failure the SDD papers + Anthropic both name.
- **Files**: EDIT `engine/protocols/01-delegation-rccf.md`; EDIT `.claude/skills/sofi-delegate/SKILL.md`.
- **Mechanism**: if Role/Context/Command/Format can't be filled with specifics → emit clarifying questions instead of a half-brief; once complete, the block is frozen (no instruction drip); boundaries + effort + grounding are first-class fields.

## Build order
1. C1 Grounding (pure doctrine, everything else references it)
2. C3 Structured Brain (tickets.py/brain.py — C2 depends on it)
3. C2 Reflection Engine (depends on C3's query + memory typing)
4. C4 Verification (depends on C1's execution-truth rule)
5. C5 Budgeted Autonomy (routing + handoff)
6. C6 RCCF v2 (integrates C1 grounding + C5 effort/boundaries)
7. Version bump v4.2→v5.0 in CLAUDE.md + SOFI_SYSTEM_PROMPT.md + routing.yaml + DECISIONS ADR

## Invariants that must not break
30-agent roster intact · `sofi doctor` stays PASS (30 subagents ↔ 30 specs) · PRJ-SAKK/PRJ-SYRH project code untouched (framework-only changes) · tier-isolation + `validate_tier_boundary()` preserved · git-discipline preserved · all new Python compiles + YAML valid · additive only — no existing agent/protocol deleted.

## Verification plan
`sofi doctor` PASS · `python3 -m py_compile` on all touched Python · YAML load on routing.yaml/registry.yaml · grep sweep for broken references · dry-run the reflection engine against PRJ-SAKK's real HANDOFFS.md · confirm `brain query` returns filtered records · adversarial-review the doctrine diffs for internal consistency.
