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

---

## Round 2 — GitHub research desk (13-agent sweep), 2026-07-07 · v6 mechanization

Source: `company/research/PATTERNS.md` — 13 parallel agents distilled 15 ranked patterns from the
most-recently-updated `claude` repositories. **Convergence finding:** independent projects
(cognitive-night, autonomous-work-harness, edict, molyanov, AgentHub, wshobson) all arrived at SOFI's
own `03-verification.md` / `04-reflection.md` doctrines. The v6 delta is therefore **mechanization**,
not new doctrine — turn prose laws into code that blocks, lints, budgets, and self-surfaces.

### ✅ Executed in the v6 rebuild
| Item | Where | Pattern |
|------|-------|---------|
| **Rooms replace tiers** — 15 self-contained departments, filesystem = org chart | `company/rooms/**`, `nexus/registry.yaml` | P1 (room-as-plugin), P15 |
| **Nexus staffed & addressable** — a Gateway room (6 operators) is the connecting layer, not prose | `company/rooms/14-gateway/`, `nexus/NEXUS.md` | P15, P3 |
| **Model tier stamped in every agent frontmatter** + single-source routing.yaml | `.claude/agents/*.md`, `nexus/routing.yaml` | P12 |
| **Least-privilege tool grants encode identity** — verifiers/reviewers get Read/Grep/Glob only | every `.claude/agents/*.md` | agent-def best practices |
| **Trigger-form descriptions as router keys** (progressive disclosure L1) | every agent/skill frontmatter | P2 |
| **Fresh-context gatekeeper owns gate advancement**, never the implementer | `gtw-gatekeeper`, `03-verification.md` | P5 |

### 🗺 Backlog — v6.1 mechanization (priority-ordered, each is a concrete room ticket)
1. **[HIGH] Deterministic scheduler — `sofi plan` → frozen DAG → `sofi run`.** One Fable call decomposes
   the plan into an inspectable DAG artifact in the brain; dispatch/gate-checks/merges run as plain
   Python. Zero model tokens on coordination — the single biggest lever at 105-agent scale. *(P4; owner
   gtw-dispatcher.)* First step: `sofi plan <PRJ>` emitting `_context/PLAN.dag.json`.
2. **[HIGH] Fail-closed gate hooks.** Convert the Stop hook to demand pasted `record-gates` proof at the
   exact working-tree hash before a turn ends when files changed; gate order as a `_VALID_TRANSITIONS`
   table in `sofi gate-check`. Doctrine → impossibility. *(P6; owner gtw-gatekeeper + sec-lead.)*
3. **[HIGH] Budgets enforced at the spawner.** `sofi dispatch`/`sofi squad` carry mandatory
   maxConcurrency / maxRounds / tokenCap / deadline; a heartbeat file per squad; escalation ladder as a
   nexus table. Runaway loops are the #1 failure at 100+ agents. *(P13; owner gtw-budget-warden.)*
4. **[HIGH] The harness remembers — capture→compress→inject brain pipeline over SQLite FTS5.** PostToolUse
   captures, SessionEnd compresses, SessionStart injects a ≤1k-token digest; topical `[LEARN]`
   auto-injection at UserPromptSubmit. Keep the LLM out of the write path. *(P10, P9; owner knw-memory-curator.)*
5. **[MED] LESSONS as a managed cache, not a log.** Confidence scores, injection cap (≤6 above 0.7),
   occurrence-threshold promotion (5+ across 2+ projects → global), 5%/week decay, vaccine auto-injection
   into an incoming Work Order's brief. *(P11; owner knw-reflector.)*
6. **[MED] Section-level indexed brain retrieval.** Index brain files by heading into stable IDs with byte
   offsets + SHA-256 drift hashes; `sofi brain-query` returns summaries, fetch exact sections
   (~12k→~400 tokens/lookup). *(P9; owner knw-brain-query.)*
7. **[MED] Zero-cost acceptance router.** `sofi route` tries the cheap tier, machine-scores the output
   (refusal/truncation/parse-fail vs 0.80), escalates on evidence — "escalate on evidence only" made
   mechanical; hard override rules for spec-review-class categories run BEFORE the classifier. *(P12; owner gtw-router.)*
8. **[MED] Breadcrumb-JSON resume.** Replace STATE.md prose `head_sha` with
   `breadcrumbs/<ticket>.json {branch,base_sha,head_sha,completed[],next_step}` + a FRESH/DEGRADED
   resolver in `sofi sync` (never resume silently on stale state). *(P14; owner gtw-dispatcher.)*
9. **[MED] Config lint in CI.** `claude plugin validate --strict` + an eval harness over the roster
   itself (static lint + LLM judge); SHA-256 content-pin agents/skills against drift. *(agent-def best
   practices; owner knw-lead + ops-cicd-engineer.)*
10. **[LOW] Fleet telemetry.** A `send_event.py` line in every room's hooks → one SQLite+WebSocket server
    feeding the dashboard's live swimlanes. At 105 agents, hooks must emit as well as guard. *(P15; owner obs-monitoring-engineer.)*

### 🚨 Anti-patterns the research flags (audit the org against these each gate-close)
LLM-as-coordinator · free-form inter-agent chat · self-graded completion · description-as-workflow-summary ·
whole-roster-in-context · transcript-passing handoffs · reactive auto-compaction · uncapped loops ·
budgets by self-discipline · trusting consensus among clones (multi-agent echo) · silent resume from stale
state · multiple writers to shared artifacts · untested agent configs · the frontier model routing itself ·
everything-persistent sessions.
