# 🔀 Git Discipline — how 30 agents share one repo across many sessions

> **Foundation:** This protocol serves Teaching **VI (Reversibility Principle)** — every checkpoint is a rollback point; `git reset --hard` destroys reversibility and is hook-blocked — and Teaching **II (Hierarchical Flow)** — branches mirror the gate cascade. Read `engine/DOCTRINE.md` before this file.

The collision-proof contract. Agents run in **parallel squads** and across **separate sessions** — one picks up where another left off. Git is the shared brain's *spine*: every state is a commit, every handoff a recorded SHA, every parallel squad a worktree. No blind starts. No silent overwrites. No lost work. **Doctrine: every milestone is a checkpoint (نقطة) — commit early, commit often, never lose a session's work.**

Pairs with `handoff-and-interconnection.md` (tickets) and `context-and-memory.md` (the brain files). Code/commits = **normal prose, never caveman.**

---

## 1. Branch model — `main` is doctrine, `prj/<ID>` is work

| Branch | Holds | Who commits |
|--------|-------|-------------|
| `main` | SOFI doctrine, protocols, tooling, agent specs — this enterprise's own evolution | CEO / whoever edits the SOFI system itself |
| `prj/<PRJ-ID>` | All work for one project. Integration branch. Created at Gate 0 scaffold. | every agent on that project (via its worktree) |
| `worktrees/<PRJ-ID>-gate<N>-<squad>` | A parallel squad's isolated tree at Gates 3 · 4 · 5 | one squad, never another |

- **Project isolation is a branch boundary.** Work for `PRJ-0001` lives only on `prj/PRJ-0001`. Never cross-commit (mirrors Rule: no cross-project bleed).
- A project branch never merges to `main`. `main` carries doctrine, not deliverables.

## 2. Worktree-per-squad — the parallelism that can't collide

Gates 3/4/5 run squads **concurrently** behind a frozen input (see `00-operating-system.md §Escalation & parallelism`). Each squad gets its **own working tree** so two agents physically cannot edit the same file at once:

```bash
sofi worktree <PRJ-ID> <gate> <squad>     # creates worktrees/<PRJ>-gate<N>-<squad> off prj/<PRJ>
# gate 4 example → three trees, three squads, zero contention:
#   worktrees/PRJ-0001-gate4-backend    (backend-blade-engineer + squad)
#   worktrees/PRJ-0001-gate4-frontend   (frontend-react-engineer + squad)
#   worktrees/PRJ-0001-gate4-mobile     (mobile-engineer + squad)
```

- Squad lead owns its worktree's commits. Members commit through the lead's tree or serialize via the lead.
- **Merge at gate close, not before.** Lead runs `sofi gate-merge <PRJ> <gate> <squad>` → fast-forward/merge into `prj/<PRJ>`, then deletes the worktree. Integration happens once, at Gate 5, off `prj/<PRJ>` — never mid-build.
- Worktrees live under `worktrees/` (git-ignored). Never a deliverable.
- **Isolate build caches per worktree** — parallel squads on one physical root share `vendor/`, `.pub-cache`, composer/npm caches → corrupt builds. Each worktree exports its own cache dirs before building: `export PUB_CACHE="${PWD}/.dart_tool/pub-cache"` · `export COMPOSER_CACHE_DIR="${PWD}/.composer_cache"` (mirror for npm/pip as needed). (External-review-desk recommendation, 2026-07-02.)

## 3. Checkpoints (نقاط) — commit cadence

A checkpoint is a commit that makes a moment recoverable. **The rule: you may never hold more than one artifact's worth of uncommitted work.**

- **At minimum: one commit per ticket** — when its Definition of Done passes, before you write the next ticket.
- **During long work:** checkpoint at each sub-milestone (`wip:` type) so a crash or a takeover by another session loses nothing.
- **Before any risky op** (migration, dependency bump, large refactor): checkpoint first — that commit is your rollback point.
- **Before handoff: always.** The receiving agent/session reads your last SHA.

## 4. Commit message — the traceable format (HARD RULE, hook-enforced)

```
<type>(<scope>): <subject ≤ 50 chars, imperative>

<body — the "why", wrapped, optional for trivial commits>

SOFI: <PRJ-ID> · <TKT-ID> · gate <N> · <role>
```

- **type** ∈ `feat fix chore docs refactor test perf ci build style revert wip`. Missing/invalid type → **commit blocked by the hook.**
- The `SOFI:` trailer ties every commit to its project, ticket, gate, and author agent — this is how a later session reconstructs *who did what, when, under which ticket*. Project-scoped commits without it are rejected at review.
- Example:
  ```
  feat(auth): add 2FA challenge endpoint

  Fulfils OpenAPI POST /auth/2fa; rate-limited per threat model T-07.

  SOFI: PRJ-0001 · TKT-031 · gate 4 · backend-blade-engineer
  ```

## 5. The git steps inside the Universal Contract

Bolted onto the agent loop (`00-operating-system.md`). Every agent, every turn:

**ORIENT (before acting) — never start blind:**
```bash
sofi sync <PRJ>        # git fetch + switch to your branch/worktree + show divergence
git log --oneline -8   # what the prior session/squad already did
```
Read `STATE.md` → `branch`, `head_sha`, `active`. If `head_sha` ≠ your tree's HEAD, a session moved ahead of you → reconcile before touching anything.

**CLAIM (before editing shared paths):**
```bash
sofi claim <PRJ> <path-glob>    # records path → role → ts in _context/LOCKS.md
```
Check `LOCKS.md` first. Path already claimed by a live role → use a worktree or serialize via the lead. Release with `sofi release <PRJ> <path-glob>` when done.

**CHECKPOINT (during + after work):**
```bash
sofi checkpoint <PRJ> "<type>(<scope>): <subject>"   # stages tracked changes + commits with the SOFI trailer auto-appended
```

**HANDOFF (before writing the next ticket):**
```bash
sofi checkpoint <PRJ> "feat(x): finish TKT-NN"     # final commit
sofi sync <PRJ> --push                              # push branch if a remote exists; record head_sha in STATE.md
```
Then update `STATE.md.head_sha` + write the next ticket. The next agent reads that SHA and continues.

## 6. Multi-session continuity — picking up another session's work

A fresh session that finds a project mid-flight:
1. `sofi brain <PRJ>` → reads STATE (gate, active, **branch + head_sha**).
2. `sofi sync <PRJ>` → `git switch prj/<PRJ>`, fetch, fast-forward.
3. `git log --oneline -15` → the prior session's checkpoints, each with its `SOFI:` trailer = full audit of who/what/when.
4. Open ticket in `HANDOFFS.md` = exactly where to resume. No re-derivation, no overwrite.

This is why checkpoints are mandatory: an uncommitted session is **invisible** to the next one and *will* be stepped on.

## 7. Never commit (enforced: `.gitignore` + hook)

Secrets (`.env*` except `.env.example`, tokens, keys), runtime state (`.gstack/`, `audit.jsonl`), caches (`__pycache__`), `_scratch/` (ephemeral, GOVERNANCE Rule 3), build artifacts (`vendor/`, `node_modules/`, `build/`). The hook blocks a commit that stages any of these even if `.gitignore` is bypassed.

## 8. Rollback & recovery — checkpoints are restore points

- Undo a bad commit: `git revert <sha>` (forward-only, safe, keeps history). **Never** `git reset --hard` or `git push --force` — the hook blocks both (they destroy others' work and the recovery trail).
- Lost a commit? `git reflog` — every checkpoint is recoverable.
- **Tag at gate close:** `sofi gate-tag <PRJ> <N>` → `<PRJ>-gate<N>-done`, an immutable restore point per gate (mirrors "migration without rollback = rejected").

## 9. Strictness — reject conditions (صرامة)

| Violation | Result |
|-----------|--------|
| Commit message lacks a valid `<type>` | **blocked at commit (hook)** |
| Project commit lacks the `SOFI:` trailer | rejected at PR/review |
| Stages a secret / `_scratch/` file | **blocked at commit (hook)** |
| `git reset --hard` / `push --force` / history rewrite | **blocked (hook)** |
| Started work without `sofi sync` (uncommitted, blind) | rejected — re-orient |
| Squad merged to `prj/<PRJ>` before its gate closed | rejected — revert, wait for gate sign-off |
| Edited a path claimed by another live role | rejected — claim/worktree first |

> Verify a project's git hygiene any time: `sofi git-check <PRJ>` (exit ≠ 0 gates the pipeline).
