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
