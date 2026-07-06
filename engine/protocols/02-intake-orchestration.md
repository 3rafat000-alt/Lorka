# 🎭 Intake → Orchestration — how the team actually works (binding)

> **The org chart is a script the main session runs, not a tree of live processes — and it runs
> without slash-commands.** The team works *directly and flexibly*: the main session understands the
> ask, wears the CEO and tier personas in sequence, and spawns leaf specialists one hop deep,
> calling the Python tooling directly for the deterministic heavy lifting. Read `01-delegation-rccf.md
> §0` first; this is its operational companion.

The stakeholder pictures a hierarchy: *reception cleans my request → the CEO decides → each tier
researches its domain and delegates its own people → those people spin up temporary helpers.* That
mental model is **correct as authority + specialization**, and **wrong as live processes.** This
protocol keeps the intelligence of the hierarchy while running it on the only substrate the platform
gives us: **the main session, wearing personas one after another, spawning leaves flat, faking depth
with rounds.** No menu of `/` commands sits in between — the team just understands and acts.

---

## §0. The hard constraint (why this protocol exists)

`01-delegation-rccf.md §0` is binding platform reality: **in Claude Code a subagent cannot spawn
another subagent.** Exactly one context holds the spawn tool — the **main Claude Code session.**
Verify: `grep -L 'Task\|Agent' .claude/agents/sofi-*.md` returns all 30 specs; none holds a spawn
tool. So there is **no** deep tree of live agents; there is one orchestrator and a flat, one-hop,
parallel fan-out of leaf specialists.

**Consequence for this flow:** every "hand off to the next level" below is the **main session
switching which persona it wears** (a reasoning step, 0 spawn), *until* the final leaf, which is a
real `Agent()` spawn. Reception, CEO, and tier-advisor are **masks**; only leaf specialists are
**processes.** None of these steps is a slash-command — they are how the session reasons and the
Python tools it reaches for.

---

## §1. The stakeholder's model → the real mechanism (the translation table)

| What the stakeholder asked for | Literal? | How it actually runs (flat, direct, no shortcuts) |
|--------------------------------|----------|--------------------------------------|
| Reception reformulates my request before the CEO | ❌ not a live agent | Main session's **first reasoning pass**: restate the real objective(s), split tangled asks, classify (kind · gate · PRJ), and clarify if scope is a vibe. 0 spawn. |
| The CEO analyzes, thinks, and decides | ✅ | Main session wears the **CEO** persona (`engine/agents/**` + `sofi-ceo` spec as the *standard*, not a spawn) → decides route · gate · which tier(s). 0 spawn. |
| Each tier works in sequence, researches the web, then delegates | ✅ as authority | Main session wears each **tier-advisor** persona in sequence → does the web research itself (`WebSearch`/`WebFetch`) → decides the route per specialist. 0 spawn. |
| Tier agents fan out to their internal specialists | ✅ as fan-out | The advisor mask's routing decision is **executed by the main session spawning those leaf specialists directly** — several `Agent()` calls **in one message** = the parallel squad. One hop. |
| Sub-agents spin up temporary sub-agents (recursion) | ❌ **impossible** | A leaf specialist cannot spawn. **Substitute:** the main session spawns any additional specialists itself, in a **later round**, once the first round returns. Same output, no nesting. |
| Shared Python tools + per-team tools + speed + token thrift | ✅ real today | The team calls `engine/tooling/` directly — `sofi` CLI + `sofi_scan.py`/`feature_scan.py` (0-model-token locators) + per-role static gates. Frugality is built in, not bolted on. |

**One-line rule:** *understand the ask, wear the masks in order, spawn only the leaves, spawn them in
parallel, call Python for the deterministic work, and if you need another level — spawn again from
the top, never from inside.*

---

## §2. The flow (the main session's orchestration, run directly)

```
raw stakeholder ask
   │
   ▼  ── mask 1 · RECEPTION (reasoning pass, 0 spawn) ──────────────────────────
reformulate            Restate the real objective(s) · split tangled asks ·
   │                   classify each (kind · gate · PRJ) · clarify-before-commit
   │                   if scope/success/artifact is a vibe (§6 RCCF). Frozen intent.
   ▼  ── mask 2 · CEO (worn persona, 0 spawn) ─────────────────────────────────
decide                 Reason over the intent → pick the active gate, the tier(s)
   │                   in play, and the route ladder (`engine/routing/routing.yaml`).
   │                   Arbitrate Design-vs-Dev.
   ▼  ── mask 3 · TIER-ADVISOR (worn, IN SEQUENCE per tier, 0 spawn) ──────────
think + research       For each tier the CEO engaged: wear that advisor → read the
   │                   frozen upstream artifact → RESEARCH THE WEB for current
   │                   best-practice → pre-locate with Python at 0 model tokens:
   │                     python3 engine/tooling/agents/ceo/sofi_scan.py <mode> \
   │                       "<query>" --prj <PRJ> --md
   │                   → decide which of its ≤5 specialists are needed + their route.
   ▼  ── the ONLY spawn boundary · EXECUTION ─────────────────────────────────
spawn leaves           Build one RCCF block per specialist (Role·Context·Command·
   ├─ sofi-<leaf-a>     Format, `01-delegation-rccf.md`) → emit SEVERAL Agent() calls
   ├─ sofi-<leaf-b>     IN ONE MESSAGE → they run concurrently. One hop. Each returns
   └─ sofi-<leaf-c>     its artifact and CANNOT spawn anyone. This is the parallel squad.
   │
   ▼  need more work the returns revealed? → GO BACK TO mask 2/3, spawn a NEW round.
   ▼  ── mask 4 · VERIFY + RECORD (Python + git) ─────────────────────────────
verify + checkpoint    VERIFY WITHOUT READING (04-coordination-registry.md §4):
                       registry.py verify <path> (exists·bytes·words·sha, cross-check
                       the leaf's ✳ RESULT header) → sofi_verify.py --prj <PRJ> --md
                       (exit 0 gates the pipeline) → sofi checkpoint <PRJ> "<type>: …"
                       → registry.py add "<the leaf's `registry:` line>" (index the
                       artifact) → append CONTEXT/DECISIONS · update STATE (head_sha)
                       · next ticket in HANDOFFS. Uncommitted = invisible.
```

**Sequence vs parallel — the rule that keeps it cheap and correct:**
- **Masks are worn in sequence** (Reception → CEO → each tier-advisor). This is the stakeholder's
  "one after another" — realized as sequential reasoning passes in one context, costing only thinking.
- **Leaves are spawned in parallel** *within a round*, but **only when their sub-tasks are
  context-independent** (`routing.yaml budgeted_autonomy`). Never fan out the sequential phases of a
  single ticket; those are one specialist, one artifact.
- **Depth is faked by rounds, not nesting.** Round 1's returns inform round 2's spawns. The main
  session is the memory between rounds — that is what replaces the impossible recursive tree.

---

## §3. Token frugality is the point, not a footnote

The whole flow is engineered so the model spends tokens on **judgment**, not on **locating or
parsing** — and there is no slash-command overhead in between:

- **Front-door thrift.** The reception pass collapses a messy ask before the CEO reasons — the CEO
  never pays to untangle noise. Run it on the mechanical tier (`haiku`).
- **Mask thrift.** Reception/CEO/advisor passes are 0-spawn reasoning; no process is paid for until a
  leaf is genuinely needed.
- **Locator thrift.** Before any specialist reads the tree, the Python engine pre-locates and
  pre-flags at **0 model tokens**: `sofi_scan.py <mode>` and `feature_scan.py`. The model opens only
  flagged `file:line`.
- **Route thrift.** `routing.yaml`: 80% of ops land on `haiku`; escalate to `sonnet`/`fable`/`opus`
  only on evidence. The advisor mask picks the cheapest route that clears each specialist's bar.
- **Round thrift.** Faking depth with rounds (not nesting) means no idle parent context is held open
  waiting on children — each round spawns, collects, and closes.
- **Read-split thrift (the biggest save at scale).** Only the **brain layer** reads the (154 KB+)
  brain; leaves get a distilled slice and never re-read STATE/CONTEXT/HANDOFFS. The **registry**
  (`04-coordination-registry.md`) lets the brain layer see "what already exists" in one screen and
  **verify deliverables without opening them** — instead of N leaves each re-billing a 240 KB brain.

*few token do trick · big brain small mouth* — the front door normalizes, Python locates, the model
only judges.

---

## §4. Worked example (one tangled ask → coordinated work, no shortcuts)

Stakeholder: *"the admin pages look inconsistent and I think withdrawals is slow and also is it even
secure, fix all this."*

1. **Reception (mask 1, haiku).** Splits into 3 objectives → #1 design-unification (Gate 4,
   PRJ-SAKK), #2 performance (Gate 5), #3 security (Gate 5). Flags "slow" and "secure" as **vibes**
   → asks one clarifying question ("slow = which page + a target TTI?") or proceeds with the
   perf-budget default. Holds the frozen intent in-context.
2. **CEO (mask 2).** Decides: #1 → Tier-2 (Development), #2 → Tier-3 (Performance), #3 → Tier-3
   (Security). Sequences them; routes #1 on `sonnet`, #2/#3 audits on `haiku`/`fable`.
3. **Tier-advisors (mask 3, in sequence).** Wears Tier-2 advisor → researches current admin-UI
   unification patterns on the web → runs `sofi_scan.py design "admin" --prj PRJ-SAKK --md` to locate
   → picks `backend-blade-engineer` + `frontend-react-engineer`. Then wears Tier-3 advisor → picks
   `performance-load-analyst` + `security-penetration-tester`.
4. **Execution (the one spawn boundary).** Builds 4 RCCF blocks inline → **4 `Agent()` calls in one
   message** → they run concurrently, each returns its artifact, none spawns anyone.
5. **Round 2 if needed.** If the pentester's return reveals a schema fix, the main session (back at
   mask 2/3) spawns `data-schema-engineer` in a **new** round — never nested inside the pentester.
6. **Verify + record.** `sofi_verify.py --prj PRJ-SAKK --md` (exit 0) → `sofi checkpoint` → record
   `head_sha` → write the next ticket.

---

## §5. Grounding

- Flat topology / no nested spawn: `engine/protocols/01-delegation-rccf.md §0`.
- Clarify-before-commit + frozen brief + the RCCF block shape: `01-delegation-rccf.md §6`, `§3`.
- Roster (CEO + 5 advisors + 24 specialists = 30): `engine/ROSTER.md`; personas/specs `engine/agents/**`.
- Route ladder + `effort_scaling` + `budgeted_autonomy`: `engine/routing/routing.yaml`.
- Python tooling the team calls directly (no slash-commands): `engine/tooling/` — dispatcher
  `engine/tooling/bin/sofi`, locators `engine/tooling/agents/ceo/{sofi_scan,feature_scan}.py`,
  verify gate `sofi_verify.py`, per-role gates under `engine/tooling/agents/<tier>/<role>/`.
  Governance: `engine/tooling/GOVERNANCE.md`; discover before writing: `engine/tooling/registry.yaml`.

**The doctrine in one line:** *reception cleans it, the CEO decides it, each tier thinks and
researches it, the leaves build it — all one context wearing masks, spawning flat, faking depth with
rounds, never nesting a soul, and never needing a slash-command to do any of it.* 🪨
