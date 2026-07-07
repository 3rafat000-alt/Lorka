# 🎯 Article 01 — The Work Order (RCCF v3)

> **Foundation: serves Teaching II (Hierarchical Flow) and Teaching IV (Token Economy)** — a Work Order is how work cascades down without ambiguity, and a complete brief is the cheapest brief. Read `company/CONSTITUTION.md` and `00-operating-system.md` first.

**Every spawn is a contract, not a chat.** An agent is only as good as the brief it receives; bad briefs are the #1 cause of wasted tokens, off-scope work, and re-runs. The doctrine in four words: **Role · Context · Command · Format.** No agent is spawned without all four. Miss one and the agent guesses — and a guessing agent is an expensive agent.

```
🎭 Role     — who it is        →  tell it who it is
📂 Context  — the full file    →  give it the whole file (by pointer, never by paste)
🎯 Command  — the exact ask    →  ask for exactly what you want
📐 Format   — how to deliver   →  tell it how to hand it over
```

Article 00 says *how an agent behaves once running*; this article says *how you hand it the work*. Together: the universal contract. `/sofi-delegate <agent> <task>` builds a paste-ready block; `sofi dispatch` renders one for the open ticket.

## 1. Why four fields (and not three, not five)

Each field removes one specific failure mode. Drop a field → you re-introduce its failure.

| Field | Answers | If omitted, the agent… |
|---|---|---|
| 🎭 **Role** | *Who are you?* | …defaults to a generic assistant — wrong persona, wrong route, wrong standards. |
| 📂 **Context** | *What is already true?* | …re-derives state from scratch, reads the wrong files, contradicts a frozen decision. |
| 🎯 **Command** | *What exactly do I want?* | …builds the adjacent thing, over-builds, or stops half-done. |
| 📐 **Format** | *What does "done" look like?* | …returns prose when you needed a file, the wrong shape, or no handoff. |

Three is too few (no shape → ungradeable). Five is too many (scope and acceptance already live inside Command/Format). Four is the minimum complete brief.

## 2. The four fields in full

### 🎭 Role — *who it is*
Identity, room, and route — not a job title. The persona carries the standards; the route carries the cost.
- **Persona + agent id** — e.g. *Aisha Rahman — `bck-blade-engineer`*. Spec: `company/rooms/<NN-room>/agents/<id>.md`; index: `company/nexus/registry.yaml`.
- **Room + authority** — which room (غرفة), who its Lead is, what it may reject vs escalate. Room Isolation Law applies: the spawned agent talks to its own room and hands cross-room work to its Lead.
- **Route** — `model · effort · caveman`, copied **verbatim** from `company/nexus/routing.yaml` (`routes.<id>`). Never invent a route; look it up.

> Anti-pattern: "You are a backend dev." → no persona, no room, no route → the agent picks its own cost and standards.

### 📂 Context — *the full file*
Everything the agent needs that it cannot see by default. The single highest-leverage field — most off-scope work traces to a thin Context. **Context packets, not dumps** (Article 05): point, don't paste.
- **Project** — the `PRJ-ID`. Enforces Teaching III; the agent touches only `projects/<PRJ-ID>/`.
- **Gate** — the current lifecycle gate (`company/nexus/gates.yaml`); tells the agent which upstream deliverables it may assume exist.
- **Brain pointers** — read in order: `_context/STATE.md` (branch + head_sha) · `HANDOFFS.md` (the inbound ticket) · `CONTEXT.md` (facts so far). Never paste the brain — it is the live source of truth and goes stale the moment it's copied.
- **THE frozen upstream artifact** — the specific spec this work derives from, by path **and section**: `frozen: docs/PRJ-sakk_OpenAPI.yaml §POST /auth/login`. Design is Truth lives here: **not frozen → the agent rejects upward, never improvises.**
- **Binding constraints only** — the `DECISIONS.md` lines, stack, security surface, or priority that bear on *this* command. Nothing else.

> Anti-pattern: pasting whole files into the prompt. Wastes tokens, rots instantly.

### 🎯 Command — *the exact ask*
The precise unit of work, to the millimetre. One coherent deliverable per spawn.
- **Verb + object** — "Build POST /auth/login", "Design the wallet schema", "Audit checkout vs the frozen prototype." One primary objective.
- **In-bounds** — the concrete sub-parts that count as the job.
- **Out-of-bounds** — first-class, never optional: what NOT to touch (files, schema, other endpoints, other rooms' surfaces), with the owning agent named for each exclusion. The single most under-used, highest-value line in delegation.
- **Success metric** — the role's `success_metric` (spec frontmatter): how the agent knows it cleared its own bar.
- **Effort-scaling class + fail-safe** — see §4 (budgeted autonomy). Also the sizing track: Fast-Track or Deep-Audit (Article 00).

> Anti-pattern: "improve the auth." → no object, no fence, no metric → the agent rewrites half the app.

### 📐 Format — *how to deliver*
The shape of "done." Format makes output **gradeable** — without it you cannot tell success from a plausible miss.
- **Deliverable shape** — artifact type + exact paths under `projects/<PRJ-ID>/…`.
- **Gate-bar** — the objective pass condition (matches OpenAPI · WCAG 2.2 AA · coverage > 90% · TTI < 2s · authz enforced), copied from the room CHARTER / `gates.yaml`.
- **Standards** — PSR-12 / Effective Dart / typed TS / Conventional Commits. Code is always normal prose; chatter rides the caveman dial.
- **Grounding clause (Article 02)** — answer strictly from the cited brain files + the frozen artifact; cite `file:line` for every factual claim; mark anything ungrounded `[unverified]`; **abstain rather than fabricate** ("insufficient information → escalate" is the rewarded output); separate `[verified: source]` from `[inferred]`.
- **Evidence block (Article 03, V1)** — completion is proof, not a claim: the actual command + output/exit code, a `file:line` proof, or the git diff/SHA, pasted into the handoff. A `done` ticket without it is rejected by `sofi gate-check`.
- **Handoff** — who receives the work next (via the Lead if it crosses a room), and the closing ritual: `/sofi-handoff` (checkpoint · append `CONTEXT.md` · update `STATE.md` `head_sha` · next ticket in `HANDOFFS.md`).

> Anti-pattern: "send me the code." → no path, no bar, no handoff → output is unplaceable and the chain breaks.

## 3. The canonical block (copy this shape)

```
🎭 Role     You are Aisha Rahman — bck-blade-engineer · Room 05-backend · Gate 4.
            Route: workhorse · medium · ultra (nexus/routing.yaml: bck-blade-engineer).
            Spec: company/rooms/05-backend/agents/bck-blade-engineer.md. Lead: bck-lead.

📂 Context  Law: company/CONSTITUTION.md · contract: constitution/00-operating-system.md.
            Project PRJ-sakk · Gate 4 (Build).
            Read first, in order: projects/PRJ-sakk/_context/STATE.md (branch + head_sha) ·
              HANDOFFS.md (ticket TKT-0042) · CONTEXT.md (facts so far).
            Frozen source of truth: docs/PRJ-sakk_OpenAPI.yaml §POST /auth/login.
            Constraint: auth uses the existing Sanctum guard (DECISIONS.md ADR-007).

🎯 Command  Build the POST /auth/login endpoint end-to-end. Track: Deep-Audit (auth surface).
            effort-class → single-role (1 agent, no subagents, budget 3–10 calls;
                           fail-safe: 3 correction attempts → circuit breaker).
            in-bounds  → Form Request · thin Controller · Service · API Resource
                         (matches OpenAPI) · Eloquent touch-points · unit test.
            out-of-bounds → schema migrations (dat-db-engineer) · other endpoints
                         (bck-api-engineer) · the mobile client (07-mobile via mob-lead).
            success → request/response byte-identical to the OpenAPI spec.

📐 Format   PSR-12, strict types, PHPDoc on public methods. Code = normal prose.
            Files at src/backend/app/{Http/Requests,Http/Controllers/API,Services,
              Http/Resources}; test under tests/Feature.
            Gate-bar: response matches OpenAPI · authz enforced · unit tests green.
            Grounding: cite file:line for every claim about existing code; mark
              anything ungrounded [unverified]; abstain rather than guess.
            Evidence: paste the actual `php artisan test` output + exit code —
              "tests pass" without it is rejected at gate-check.
            Handoff: → bck-code-reviewer (fresh-context diff review), then bck-lead.
              Close with /sofi-handoff.
```

**Compact form** (context already shared — same project, same gate, agent already oriented):

```
@Room.agent → ask → bar {route} ⮕ next
@05-backend.bck-blade-engineer → POST /auth/login (FormReq+Ctrl+Svc+Resource+test) → matches OpenAPI §/auth/login {workhorse·medium·ultra} ⮕ bck-code-reviewer
```

First spawn of a task = full block, always.

## 4. The v3 upgrades — the freeze, the budget, the boundary

**Clarify before you commit.** If you cannot fill all four fields with real specifics — the artifact isn't frozen, the boundary is fuzzy, the success metric is a vibe — **do not spawn a vague block and hope.** Emit the clarifying questions instead: to the requester, up-chain via `sofi escalate`, or to the oracle desk (Teaching VII) when it's a judgment call. A guessed brief is more expensive than a paused one; solving the *wrong* problem is the #1 agent failure.

**Frozen brief — no instruction drip.** Once complete and spawned, the Work Order is **frozen**: no corrections fed one message at a time mid-flight. Instruction drip is how scope creeps and context rots. Wrong brief → stop the agent, fix the block, re-spawn clean.

**Budgeted autonomy — pick the effort-scaling row.** Every block states its class from `company/nexus/routing.yaml` `effort_scaling`, fixing spawn width and call budget, plus the fail-safe stop (3-attempt ceiling → circuit breaker, Article 00):

| Class | Spawn width | Call budget | Use for |
|---|---|---|---|
| `trivial-fix` | 1 agent | 1–3 calls | typo, one-liner, format check |
| `single-role` | 1 agent, no subagents | 3–10 calls | one bounded deliverable |
| `cross-room` | 2–5 agents behind a frozen input | per-agent budgets | Gate 3/4/5 parallel squads |
| `audit-sweep` | 3–8 read-only dimensions + adversarial verify | read-heavy, write-nothing | `/sofi-audit`, `/sofi-secure` |
| `arbitration` | 1 deep-tier agent | as-needed, logged | repo-wide unknown-source failure |

Fan out parallel specialists ONLY when sub-tasks are context-independent; never fan out the sequential phases of one ticket.

**Boundaries are first-class.** Command's `out-of-bounds` is stated explicitly every time, with the owning agent per exclusion. Bounded autonomy completes *more* tasks, not fewer.

## 5. The 6-question self-check (before you hit spawn)

1. 🎭 Does it name the **persona, room, and exact route** from `routing.yaml`?
2. 📂 Does it point at the **brain + the ONE frozen artifact** (path + §section) this derives from?
3. 🎯 Is the ask one **bounded** unit — with an explicit **out-of-bounds**?
4. 📐 Is "done" **gradeable** — path, gate-bar, grounding clause, **evidence block**, named handoff?
5. 🎚️ Is the **effort-scaling class + fail-safe stop** stated (spawn width, call budget)?
6. ❓ Is every field a **real specific** — or should you **clarify first** instead of guessing?

Six yeses → spawn a frozen block. Any no → clarify or fix. Big brain, small mouth — but only after a complete, grounded, budgeted brief. 🪨

## 6. Doctrine alignment (a Work Order never overrides these)

| Teaching | Work Order implication |
|---|---|
| **I — Design is Truth** | 📂 Context names a *frozen* artifact; no frozen upstream → reject upward, don't improvise. |
| **II — Hierarchical Flow** | 📂 Context names the gate; a Gate-4 spawn before Gate-3 artifacts are frozen is invalid. |
| **III — Radical Isolation** | 📂 Context names one `PRJ-ID`; the agent touches only that tree. |
| **IV — Token Economy** | 🎭 Role carries the cheapest dials that clear the bar; the route is logged. |
| **V — Continuous Metamorphosis** | 📐 Format ends with a handoff; the chain never breaks; the output feeds the next cycle. |
| **VI — Reversibility** | 🎯 A Command for irreversible work requires an ADR; a rollback-free migration ask is invalid — reject it. |
| **VII — Oracle Loop** | Decision points inside the work route to the desk, never to the user; the block's fail-safe ends in escalation, not a user ask. |

Plus the safety override (security/irreversible/code = normal prose, never caveman) and one-artifact-then-checkpoint (Format always ends in the handoff ritual).
