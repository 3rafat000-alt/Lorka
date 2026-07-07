# SOFI EVOLUTION — framework improvement roadmap

> Teaching V (Continuous Metamorphosis). Improvements to the framework itself, triaged from
> external-review-desk critiques. Executed items link the commit; backlog items carry a priority +
> concrete first step. Large architectural changes are NOT auto-applied — they land here for
> deliberate staging (the review-desk loop's "break out for real scope change" exception).

## Round 1 — external review desk (Gemini), 2026-07-02

Pushed a full SOFI system description (team · gates · commands · routing · engine · brain · tooling ·
behaviors) and asked for a prioritized plan toward **frugal · economic · flexible**. Reply distilled
below. Source ask: `sofi gemini review` loop.

### ✅ Executed now (cheap, safe, reversible)

| Item | Where | Why |
|------|-------|-----|
| **Self-correction hard ceiling (3 attempts → escalate)** | `00-operating-system.md` §Escalation | fix→fail→refix loops burn tokens silently; hard cap is the single biggest cost leak plug |
| **Task-sizing: Fast-Track vs Deep-Audit** | `00-operating-system.md` §Escalation | trivial changes shouldn't traverse all 9 gates; money surfaces still take the full 9. Flexibility without weakening Tier-A |
| **Per-worktree build-cache isolation** | `git-discipline.md` §2 | parallel squads on one physical root corrupt shared `vendor/`/`.pub-cache`; export per-worktree cache dirs |

### 🗺 Backlog — deliberate implementation (priority-ordered)

1. **[HIGH] Differential context injection** — `lean_ctx_injector.py` at SessionStart builds a compact,
   target-scoped context per agent instead of passing whole `_context/*.md`. Est. −60% inter-agent
   context tokens. First step: prototype the injector reading the inbound ticket + only the DECISIONS
   entries tagged to the current feature.
2. **[HIGH] AST function-level truncation** — `sofi_scan.py` returns the target function body (via
   Python AST) not just `file:line`, so the model never reads the whole file. First step: add an
   `--extract` mode that emits the enclosing function/class for each hit.
3. **[HIGH] Self-correction & drift guards (partly done)** — the 3-attempt ceiling is live; still open:
   a **Context Lock** on `_context/` (require `git pull --rebase` + `sofi_verify` before any brain
   write) to kill the recurring shared-index race, and **brain divergence** protection at merge.
4. **[MED] Routing refinement** — shift file-reading/structure-scan from Sonnet→Haiku; render RCCF via
   Python templating + Haiku tone-pass instead of a Sonnet CEO call. Re-evaluate Fable→Sonnet+strict
   guards for spec-review gate (measure quality delta before committing — Fable gate exists for a
   reason; do NOT drop it blind).
5. **[MED] Runtime state in SQLite** — `.engine/state.db` as the fast read/write runtime; regenerate the
   human-readable `_context/*.md` only on checkpoint/close. Big change — needs a migration + a
   fallback; stage behind a flag. Note tension: markdown brain is the audit trail; DB must stay a
   cache, not the source of truth.
6. **[MED] Command consolidation** — desk proposes collapsing the 10 palette + ~25 dispatcher commands
   (e.g. `/sofi-pipeline`, `/sofi-squad`, `/sofi-close`). CAUTION: the tight 10-command palette was a
   deliberate anti-clutter decision; consolidate only where it removes real friction, measure
   wrong-command/arg-mismatch debug loops first.
7. **[MED] Cyclomatic-complexity / maintainability guard** — `sofi_scan.py` blocks merges that raise
   complexity even when tests pass (kills "green but spaghetti" debt).
8. **[MED, careful] Fail-CLOSED for Tier-1 security/money hooks** — desk flags fail-open as a risk on
   money surfaces. Tension: fail-open was chosen so a broken scanner never bricks a session. Proposed
   compromise: keep fail-open globally, but for edits under money/credential paths, a broken security
   scanner aborts THAT edit (not the session) + alerts. Needs careful scoping — do not flip globally.
9. **[STRUCTURAL] Cascading delegation** — CEO delegates to Tier-Heads, who generate sub-RCCF for their
   tier, shrinking CEO context. Large behavioral change to the org model; prototype with one tier
   (Tier-1) before rolling out.

### 🚨 Top risks the desk surfaced (all now tracked above)
- Infinite self-correction loops → **ceiling live** (#3).
- Context drift / brain divergence under parallel worktrees → Context Lock (#3).
- Silent technical-debt accumulation (green tests, bad code) → complexity guard (#7).

## Round 2 — Claude OSS frontier audit, 2026-07-07

Two grounded research leaves mined the top Claude ecosystem repos (claude-mem,
oh-my-claudecode, SuperClaude, claude-task-master, claude-code-router, VoltAgent subagents,
anthropics/skills + plugins, Thinking-Claude, learn-claude-code, awesome-claude-code,
best-practice). Method: fetch REAL READMEs, cite, map each pattern against what SOFI already
has, adopt only genuine deltas. **Finding: SOFI's spec shape (RCCF + Operating Contract) and
its memory layer (brain + REGISTRY + read/execute split) already beat or match most of the
ecosystem — the real gaps were AUTOMATED ROUTING TRIGGERS and DEPENDENCY-AWARE FLOW.** Star
counts ignored (several in the source list were wrong). Full mining data lives in the session
transcript; distillate below.

### ✅ Executed now (cheap, safe, reversible)

| Item | Where | Source pattern · why |
|------|-------|-----|
| **Adaptive routing block** — longContext auto-floor (≥60k ctx → ≥fable), haiku difficulty-triage (advisory), complexity-score → spawn-width, `model: inherit` value | `routing.yaml` §adaptive_routing | claude-code-router + claude-task-master. Routing was 100% human-judged; these add deterministic floors + a cheap scoring pre-step. Sizing scores ≠ confidence scores (V4/G4 stay behavioral). |
| **`remediate` mode** — named bounded delegate→verify-until-green loop | `routing.yaml` §adaptive_routing | oh-my-claudecode Ralph/UltraQA. Reuses the existing 3-strike circuit breaker as its hard stop; NOT unbounded "keep trying". |
| **Dependency-aware tickets + resolver** — `depends_on:` field + `next_ticket.py` (unblocked frontier / `--check`) | `handoff-and-interconnection.md`, `new-project.sh`, `agents/ceo/next_ticket.py` (registered) | claude-task-master `next`. Turns HANDOFFS from a hand-eyeballed queue into a machine DAG for parallel worktree squads. Gate-order no-skip still binds. Tested end-to-end (frontier + exit codes 0/1/2). |
| **Dogfood benchmark gate on Superpowers promotion** | `SUPERPOWERS.md` rule 1 | awesome-claude-code. Promotion now needs a measured delta in `DECISIONS.md`, not a vibe. |
| **Context-budget rule** — checkpoint/compact before degradation | `00-operating-system.md` §Escalation | claude-code-best-practice. Keeps the brain layer lean, complementing the read/execute split that already keeps leaves lean. |
| **Trigger-optimized agent descriptions** — pushy, keyword-front-loaded `description:` across all 30 specs | `.claude/agents/sofi-*.md` | anthropics/skills skill-creator: "Claude UNDERtriggers." The description IS the router's trigger; rewritten for accurate firing (scope kept truthful — grounding). |
| **Protocol-table drift fix** — add `02-intake-orchestration` + `04-coordination-registry` to the umbrella table | `00-operating-system.md` | internal: both core protocols were missing from the §8-protocols index. |

### ❌ Rejected — with grounded reason (the doctrine working as designed)
- **Numeric/verbalized confidence scoring** (SuperClaude 0.6-floor/0.8-target). SOFI already
  *deliberately* forbids this: `grounding.md` G4 + `verification.md` V4 route correctness
  through behavioral proxies, not self-rated certainty (miscalibration — AbstentionBench
  arXiv:2506.09038). Adopting it would be a regression. Non-adoption is the correct call.
- **Slash-command layer** (SuperClaude `/sc:*`). SOFI removed slash-commands on purpose (the
  team works directly, `02-intake-orchestration.md`). Not re-adding.
- **Hidden-code-block "thinking" scaffold** (Thinking-Claude). Obsoleted by native extended
  thinking + `effort_scaling`. Only "≥2 hypotheses before committing" is worth a note on the
  opus repo-wide-debug path — folded into backlog.
- **Vector/semantic brain search** (claude-mem Chroma). Heavy dependency for a modest gain over
  `sofi_scan.py` grep + REGISTRY. Not worth the install surface.

### 🗺 Backlog — deliberate implementation (priority-ordered)
1. **[HIGH] Triggering-eval harness for agent descriptions** — port skill-creator's eval loop
   (test prompts → measure which agent fires → description-improver) so description quality is
   *measured*, not hand-tuned. First step: a `description_lint.py` that flags specs whose
   trigger keywords don't cover their in-bounds scope.
2. **[MED] Path-scoped lazy-loaded rules** (`.claude/rules/*.md` glob-frontmatter). Move
   path-specific doctrine (stack defaults, git law, tooling-matrix) out of the always-on
   CLAUDE.md into rules loaded only on matching globs. First step: VERIFY the harness
   auto-loads `.claude/rules/*.md` before migrating anything (inert if unsupported).
3. **[MED] Progressive-disclosure conformance for heavy protocols** — restructure the largest
   protocols into thin body + `references/` loaded on demand (already the pattern for the cyber
   KB). Official Agent-Skills 3-level model.
4. **[LOW] Wrap SOFI as a versioned plugin** (`.claude-plugin/plugin.json` + `marketplace.json`,
   immutable `sofi` slug, pinned sha) for reproducible team onboarding. Only if portability is wanted.
5. **[LOW] ≥2-hypotheses-before-committing** on the opus repo-wide-debug path (Thinking-Claude).

### 🧹 Drift flagged (not fixed here — needs its own careful pass)
- **`02-` filename collision:** both `02-autonomous-gemini-loop.md` and
  `02-intake-orchestration.md` carry the `02` prefix. Renaming churns every cross-reference —
  resolve deliberately (pick one canonical `02`, renumber the other) in a dedicated commit, not
  bundled with feature work.
