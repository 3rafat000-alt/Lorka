# 🔀 Article 06 — Git Discipline (the spine)

> **Foundation: serves Teaching VI (Reversibility)** — every checkpoint is a rollback point; `git reset --hard` destroys reversibility and is hook-blocked — **and Teaching II (Hierarchical Flow)** — branches mirror the gate cascade. Read `company/CONSTITUTION.md` first. Pairs with Article 08 (tickets) and `company/brain/BRAIN.md` (the brain files).

The collision-proof contract for 105 agents sharing repos across parallel squads and separate sessions. Git is the brain's *spine*: every state is a commit, every handoff a recorded SHA, every parallel squad a worktree. No blind starts. No silent overwrites. No lost work. **Every milestone is a checkpoint (نقطة) — commit early, commit often, never lose a session's work.** Code and commits = normal prose, never caveman.

## 1. Branch model — `main` is doctrine, `prj/<ID>` is work

| Branch | Holds | Who commits |
|---|---|---|
| `main` | SOFI doctrine, constitution, nexus, rooms, tooling — the enterprise's own evolution | `brd-ceo` / whoever edits the SOFI system itself |
| `prj/<PRJ-ID>` | All work for one project — the integration branch, created at Gate-0 scaffold (`company/os/bin/new-project.sh`) | every agent on that project (via its worktree) |
| `worktrees/<PRJ-ID>-gate<N>-<squad>` | A parallel squad's isolated tree at Gates 3 · 4 · 5 | one squad, never another |

- **Project isolation is a branch boundary** (Teaching III). Work for `PRJ-0001` lives only on `prj/PRJ-0001`; each project is its own git repo with the brain (`_context/`) inside it. Never cross-commit.
- A project branch never merges to `main`. `main` carries doctrine, not deliverables.

## 2. Worktree-per-squad — parallelism that cannot collide

Gates 3/4/5 run squads concurrently behind a frozen input (`00-operating-system.md`). Each squad gets its own working tree so two agents physically cannot edit the same file at once:

```bash
sofi worktree <PRJ> <gate> <squad>   # creates worktrees/<PRJ>-gate<N>-<squad> off prj/<PRJ>
# gate 4 → three trees, three rooms, zero contention:
#   worktrees/PRJ-0001-gate4-backend    (05-backend, merged by bck-lead)
#   worktrees/PRJ-0001-gate4-frontend   (06-frontend, merged by fnt-lead)
#   worktrees/PRJ-0001-gate4-mobile     (07-mobile, merged by mob-lead)
```

- The room Lead owns its worktree's commits; members commit through the Lead's tree or serialize via the Lead.
- **Merge at gate close, not before.** The Lead runs `sofi gate-merge <PRJ> <gate> <squad>` (`--no-ff`) into `prj/<PRJ>`, then deletes the worktree. Integration happens once, at gate close — never mid-build.
- Worktrees live under `worktrees/` (git-ignored). Never a deliverable.
- **Per-worktree build caches (hard rule).** Parallel squads sharing one physical root corrupt each other's `vendor/`, pub and composer/npm caches. Each worktree exports its own cache dirs before building: `export PUB_CACHE="${PWD}/.dart_tool/pub-cache"` · `export COMPOSER_CACHE_DIR="${PWD}/.composer_cache"` (mirror for npm/pip as needed).

## 3. Checkpoints (نقاط) — commit cadence

A checkpoint makes a moment recoverable. **You may never hold more than one artifact's worth of uncommitted work.**

- **Minimum: one commit per ticket** — when its Definition of Done passes, before the next ticket is written.
- **During long work:** checkpoint each sub-milestone (`wip:` type) so a crash or takeover loses nothing.
- **Before any risky op** (migration, dependency bump, large refactor): checkpoint first — that commit is your rollback point.
- **Before handoff: always.** The receiver reads your last SHA.

## 4. Commit message — the traceable format (HARD RULE, hook-enforced)

```
<type>(<scope>): <subject ≤ 50 chars, imperative>

<body — the "why", wrapped, optional for trivial commits>

SOFI: <PRJ-ID> · <TKT-ID> · gate <N> · <agent-id>
```

- **type** ∈ `feat fix chore docs refactor test perf ci build style revert wip`. Missing/invalid type → commit **blocked by the hook**.
- The `SOFI:` trailer ties every commit to its project, ticket, gate, and author agent — how a later session reconstructs *who did what, when, under which ticket*. Project-scoped commits without it are rejected at review. `sofi checkpoint` appends it automatically.
- When the work executed oracle guidance, the body cites it: `Guided by oracle review <date>: <action-item-title>` (Teaching VII audit trail).

Example:
```
feat(auth): add 2FA challenge endpoint

Fulfils OpenAPI POST /auth/2fa; rate-limited per threat model T-07.

SOFI: PRJ-0001 · TKT-031 · gate 4 · bck-api-engineer
```

## 5. The git steps inside the universal contract

**ORIENT (before acting — never start blind):**
```bash
sofi sync <PRJ>        # fetch + switch to your branch/worktree + show divergence
git log --oneline -8   # what the prior session/squad already did
```
Read `STATE.md` → `branch`, `head_sha`. If `head_sha` ≠ your tree's HEAD, a session moved ahead of you → reconcile before touching anything.

**CLAIM (before editing shared paths):**
```bash
sofi claim <PRJ> <path-glob>     # records path → agent → ts in _context/LOCKS.md
sofi release <PRJ> <path-glob>   # when done
```
Check `LOCKS.md` first. Path claimed by a live agent → use a worktree or serialize via the Lead.

**CHECKPOINT (during + after work):**
```bash
sofi checkpoint <PRJ> "<type>(<scope>): <subject>"   # stages tracked changes, commits with the SOFI: trailer, updates STATE branch/head_sha
```

**HANDOFF (before writing the next ticket):**
```bash
sofi checkpoint <PRJ> "feat(x): finish TKT-NN"
sofi sync <PRJ> --push           # push if a remote exists; record head_sha in STATE.md
```
Then write the next ticket. The next agent reads that SHA and continues. `sofi git-check` audits the recent history (clean brain, no leaks, trailer + type on the last 10 commits).

## 6. Multi-session continuity

A fresh session finding a project mid-flight: `sofi brain <PRJ>` (STATE → gate, branch, head_sha) → `sofi sync <PRJ>` → `git log --oneline -15` (every checkpoint carries its `SOFI:` trailer = full audit of who/what/when) → the open ticket in `HANDOFFS.md` = exactly where to resume. No re-derivation, no overwrite. This is why checkpoints are mandatory: an uncommitted session is **invisible** to the next one and *will* be stepped on.

## 7. Never commit (enforced: `.gitignore` + hook)

Secrets (`.env*` except `.env.example`, tokens, keys, `PRIVATE KEY` blocks) · runtime state (`.sofi-run/`, `audit.jsonl`, `sessions.jsonl`) · caches (`__pycache__`, composer/npm/pub caches) · `_scratch/` (ephemeral, purged at gate exit — `company/os/GOVERNANCE.md` Rule 3) · build artifacts (`vendor/`, `node_modules/`, `build/`). The hook blocks a commit that stages any of these even if `.gitignore` is bypassed, and `guard.scan_secrets` patterns catch keys in content, not just filenames.

## 8. Rollback & recovery — checkpoints are restore points

- Undo a bad commit: `git revert <sha>` — forward-only, safe, keeps history. **Never** `git reset --hard`, **never** `git push --force` — both destroy others' work and the recovery trail; both are hook-blocked.
- Lost a commit? `git reflog` — every checkpoint is recoverable.
- **Tag at gate close:** `sofi gate-tag <PRJ> <N>` → `<PRJ>-gate<N>-done`, an immutable restore point per gate. Mirrors "migration without rollback = rejected."

## 9. Strictness — reject conditions (صرامة)

| Violation | Result |
|---|---|
| Missing/invalid conventional type | Commit blocked by hook |
| Missing `SOFI:` trailer on project-scoped commit | Rejected at review |
| Blind start (no `sofi sync`, stale `head_sha`) | Work invalid — reconcile first |
| Merge into `prj/<PRJ>` before gate close | Rejected; gate-merge only |
| Editing a path claimed in `LOCKS.md` | Rejected; claim or worktree first |
| Secrets / `_scratch/` / caches staged | Commit blocked by hook |
| `reset --hard` / `push --force` | Hook-blocked, always |
| Uncommitted handoff | Invisible to the next session — treated as not done |
