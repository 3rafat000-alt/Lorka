# 🎭 Intake → Orchestration — the wear-the-hierarchy flow (binding)

> **The org chart is a script the main session runs, not a tree of live processes.** This protocol
> is how a raw stakeholder ask becomes coordinated specialist work — through **one context wearing
> masks in sequence**, never through nested live agents. Read `01-delegation-rccf.md §0` first; this
> is its operational companion.

The stakeholder pictures a hierarchy: *a reception agent cleans my request → the CEO decides → each
tier researches its domain and delegates its own people → those people spin up temporary helpers.*
That mental model is **correct as authority + specialization**, and **wrong as live processes.** This
protocol keeps the intelligence of the hierarchy while running it on the only substrate the platform
gives us: **the main session, wearing personas one after another, spawning leaves one hop deep.**

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
**processes**.

---

## §1. The stakeholder's model → the real mechanism (the translation table)

| What the stakeholder asked for | Literal? | How it actually runs (flat topology) |
|--------------------------------|----------|--------------------------------------|
| A reception agent that reformulates my request before the CEO | ❌ not a live agent | Main session wears the **Intake** persona as its first pass (`/sofi-intake`) → frozen intent brief. 0 spawn. |
| The CEO analyzes, thinks, and decides | ✅ | Main session switches mask to **`sofi-ceo`** → reasons over the intent brief → decides route · gate · which tier(s). 0 spawn. |
| Each tier works in sequence, researches the web, then delegates its own people | ✅ as authority | Main session wears each **tier-advisor** persona in sequence → does the web research itself (advisors/web roles hold `WebSearch`/`WebFetch`) → decides the route per specialist. 0 spawn. |
| Tier agents fan out to their internal specialists | ✅ as fan-out | The tier-advisor mask's routing decision is **executed by the main session spawning those leaf specialists directly** — several `Agent()` calls **in one message** = the parallel squad. One hop. |
| Sub-agents spin up temporary sub-agents (recursion) | ❌ **impossible** | A leaf specialist cannot spawn. **Substitute:** the main session spawns any additional specialists itself, in a **later round**, once the first round returns. Same output, no nesting, no token-eating depth. |
| Shared Python tools + per-team tools + speed + token thrift | ✅ real today | `routing.yaml` (haiku-first, 80% of ops) + `sofi_scan.py`/`feature_scan.py` (0-model-token locators) + per-role static gates. Frugality is built in, not bolted on. |

**One-line rule:** *wear the masks in order, spawn only the leaves, spawn them in parallel, and if you
need another level — spawn again from the top, never from inside.*

---

## §2. The flow (the main session's orchestration script)

```
raw stakeholder ask
   │
   ▼  ── mask 1 ─────────────────────────────────────────────────────────────
/sofi-intake                RECEPTION.  Reformulate → classify (kind·gate·PRJ)
   │                        → clarify-gate (§6 RCCF) → FROZEN INTENT BRIEF.
   │                        0 spawn · haiku · fast.
   ▼  ── mask 2 ─────────────────────────────────────────────────────────────
sofi-ceo (worn)             DECISION.  Reason over the intent brief → pick the
   │                        active gate, the tier(s) in play, and the route
   │                        ladder. Arbitrate Design-vs-Dev. 0 spawn.
   ▼  ── mask 3 (repeat per tier, IN SEQUENCE) ──────────────────────────────
sofi-tier-N-advisor (worn)  DOMAIN THINK + RESEARCH.  For each tier the CEO
   │                        engaged: wear that advisor → read the frozen
   │                        upstream artifact → RESEARCH THE WEB for current
   │                        best-practice/context → decide which of its ≤5
   │                        specialists are needed and their exact route. 0 spawn.
   ▼  ── the ONLY spawn boundary ────────────────────────────────────────────
/sofi-delegate → Agent()    EXECUTION.  Build one RCCF block per specialist →
   ├─ sofi-<leaf-a>         emit SEVERAL Agent() calls IN ONE MESSAGE → they run
   ├─ sofi-<leaf-b>         concurrently. One hop. Each returns its artifact and
   └─ sofi-<leaf-c>         CANNOT spawn anyone. This is the parallel squad.
   │
   ▼  need more work the returns revealed? → GO BACK TO mask 2/3, spawn a NEW round.
   ▼  ── close ──────────────────────────────────────────────────────────────
/sofi-handoff               RECORD.  Checkpoint → CONTEXT/DECISIONS → STATE
                            (head_sha) → next ticket. Uncommitted = invisible.
```

**Sequence vs parallel — the rule that keeps it cheap and correct:**
- **Masks are worn in sequence** (Intake → CEO → each tier-advisor). This is the stakeholder's "one
  after another" — realized as sequential reasoning passes in one context, costing only thinking.
- **Leaves are spawned in parallel** *within a round*, but **only when their sub-tasks are
  context-independent** (`routing.yaml budgeted_autonomy`). Never fan out the sequential phases of a
  single ticket; those are one specialist, one artifact.
- **Depth is faked by rounds, not nesting.** Round 1's returns inform round 2's spawns. The main
  session is the memory between rounds — that is what replaces the impossible recursive tree.

---

## §3. Token frugality is the point, not a footnote

The whole flow is engineered so the model spends tokens on **judgment**, not on **locating or
parsing**:

- **Front-door thrift.** `/sofi-intake` runs on `haiku` and collapses a messy ask before the CEO
  ever reasons — the CEO never pays to untangle noise.
- **Mask thrift.** Reception/CEO/advisor passes are 0-spawn reasoning; no process is paid for until a
  leaf is genuinely needed.
- **Locator thrift.** Before any specialist reads the tree, the Python engine pre-locates and
  pre-flags at **0 model tokens**: `python3 engine/tooling/agents/ceo/sofi_scan.py <mode> "<q>" --prj
  <PRJ> --md` and `feature_scan.py`. The model opens only flagged `file:line`.
- **Route thrift.** `routing.yaml`: 80% of ops land on `haiku`; escalate to `sonnet`/`fable`/`opus`
  only on evidence. The advisor mask picks the cheapest route that clears each specialist's bar.
- **Round thrift.** Faking depth with rounds (not nesting) means no idle parent context is held open
  waiting on children — each round spawns, collects, and closes.

*few token do trick · big brain small mouth* — the front door normalizes, Python locates, the model
only judges.

---

## §4. Worked example (one tangled ask → coordinated work)

Stakeholder: *"the admin pages look inconsistent and I think withdrawals is slow and also is it even
secure, fix all this."*

1. **Intake (mask 1, haiku).** Splits into 3 objectives → #1 design-unification (Gate 4, PRJ-SAKK),
   #2 performance (Gate 5), #3 security (Gate 5). Flags "slow" and "secure" as **vibes** → asks one
   clarifying question ("slow = which page + a target TTI?") or proceeds with the perf-budget default.
   Emits the frozen intent brief.
2. **CEO (mask 2).** Decides: #1 → Tier-2 (Development), #2 → Tier-3 (Performance), #3 → Tier-3
   (Security). Sequences them; routes #1 on `sonnet`, #2/#3 audits on `haiku`/`fable`.
3. **Tier-advisors (mask 3, in sequence).** Wears Tier-2 advisor → researches current admin-UI
   unification patterns on the web → picks `backend-blade-engineer` + `frontend-react-engineer`.
   Then wears Tier-3 advisor → picks `performance-load-analyst` + `security-penetration-tester`.
4. **Execution (the one spawn boundary).** `/sofi-delegate` builds 4 RCCF blocks → **4 `Agent()`
   calls in one message** → they run concurrently, each returns its artifact, none spawns anyone.
5. **Round 2 if needed.** If the pentester's return reveals a schema fix, the main session (back at
   mask 2/3) spawns `data-schema-engineer` in a **new** round — never nested inside the pentester.
6. **`/sofi-handoff`.** Checkpoint, record `head_sha`, write the next ticket.

---

## §5. Grounding

- Flat topology / no nested spawn: `engine/protocols/01-delegation-rccf.md §0`.
- Clarify-before-commit + frozen brief: `01-delegation-rccf.md §6`; `/sofi-intake` skill.
- Roster (CEO + 5 advisors + 24 specialists = 30): `engine/ROSTER.md`.
- Route ladder + `effort_scaling` + `budgeted_autonomy`: `engine/routing/routing.yaml`.
- 0-model-token locators: `engine/tooling/agents/ceo/{sofi_scan,feature_scan}.py`.
- Palette placement: `engine/protocols/command-palette.md`.

**The doctrine in one line:** *reception cleans it, the CEO decides it, each tier thinks and
researches it, the leaves build it — all one context wearing masks, spawning flat, faking depth with
rounds, never nesting a soul.* 🪨
