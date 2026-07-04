# 🎯 RCCF — The SOFI Delegation Doctrine

> **Every spawn is a contract, not a chat.** A SOFI agent is only as good as the brief it receives. Bad briefs are the #1 cause of wasted tokens, off-scope work, and re-runs. This protocol kills that.

The doctrine in four words: **Role · Context · Command · Format.** No agent is spawned without all four. Miss one and the agent guesses — and a guessing agent is an expensive agent.

```
🎭 Role     — who it is        →  tell it who it is
📂 Context  — the full file    →  give it the whole file
🎯 Command  — the exact ask    →  ask for exactly what you want
📐 Format   — how to deliver   →  tell it how to hand it over
```

This is the **runtime** half of the org. `00-operating-system.md` says *how an agent behaves once running*; RCCF says *how you hand it the work*. Together they are the universal contract. The CEO (`sofi-ceo`) emits an RCCF block on every delegation; `/sofi-delegate` builds one for you.

---

## 1. Why four fields (and not three, not five)

Each field removes one specific failure mode. Drop a field → you re-introduce its failure.

| Field | Answers | If you omit it, the agent… |
|-------|---------|-----------------------------|
| 🎭 **Role** | *Who are you?* | …defaults to a generic assistant — wrong persona, wrong route, wrong standards. |
| 📂 **Context** | *What is already true?* | …re-derives state from scratch, reads the wrong files, contradicts a frozen decision. |
| 🎯 **Command** | *What exactly do I want?* | …builds the adjacent thing, over-builds, or stops half-done. |
| 📐 **Format** | *What does "done" look like?* | …returns prose when you needed a file, the wrong shape, or no handoff. |

Three is too few (no shape → ungradeable output). Five is too many (scope + acceptance both live inside Command/Format). Four is the minimum complete brief.

---

## 2. The four fields in full

### 🎭 Role — *who it is*
The agent's identity, tier, and route. This is **not** a job title — it carries the persona, the standards that persona enforces, and the three routing dials.

Must contain:
- **Persona + role name** — e.g. *Aisha Rahman — Laravel/PHP Core Developer*. The persona is the standard-bearer (PSR-12, strict types, etc. ride along with the name). Personas live in `engine/ROSTER.md`; full spec in `engine/agents/**`.
- **Tier** — T0–T4 or Exec. Sets authority and what it may reject vs escalate.
- **Route** — `model · effort · caveman`, copied verbatim from `engine/routing/routing.yaml`. The cheapest setting that clears the bar. Never invent a route; look it up.

> Anti-pattern: "You are a backend dev." → no persona, no tier, no route → the agent picks its own cost and standards. Expensive and inconsistent.

### 📂 Context — *the full file*
Everything the agent needs to know that it cannot see by default. The agent starts blind; Context is the cure. This is the single highest-leverage field — most off-scope work traces to a thin Context.

Must contain:
- **Project** — the `PRJ-ID`. Enforces isolation; the agent touches only `projects/<PRJ-ID>/`.
- **Gate** — current lifecycle gate. Tells the agent which deliverables it may assume exist upstream.
- **Brain pointers** — the agent reads, in order: `projects/<PRJ-ID>/_context/STATE.md` (where we are + `branch`/`head_sha`), `HANDOFFS.md` (its inbound ticket), `CONTEXT.md` (facts + decisions so far). Never paste the brain — point at it; it is the live source of truth.
- **The frozen upstream artifact** — the *specific* spec this work derives from, by path and section. e.g. `frozen: PRJ-sakk_OpenAPI.yaml §/auth/login`. "Design is Truth" lives here: if the artifact isn't frozen, the agent must reject upward, not improvise.
- **Constraints that bind this task** — relevant `DECISIONS.md` lines, the stack, a security surface, a deadline/priority. Only what bears on *this* command.

> Anti-pattern: pasting whole files into the prompt. Point at the brain and the frozen artifact; the agent reads them. Pasting wastes tokens and goes stale the moment the file changes.

### 🎯 Command — *the exact ask*
The precise unit of work — exact, to the millimetre. One coherent deliverable per spawn. Ambiguity here is the agent's licence to wander.

Must contain:
- **The verb + the object** — "Build POST /auth/login", "Design the wallet schema", "Audit the checkout screen vs prototype". One primary objective.
- **In-bounds** — the concrete sub-parts that count as the job (Form Request + Controller + Service + Resource + model + unit test).
- **Out-of-bounds** — what NOT to touch. The single most under-used line in delegation. e.g. *"Out of bounds: schema changes, other endpoints, the mobile client."* Without it, scope creeps every time.
- **The success metric** — how the agent knows it cleared its own bar (the role's `success_metric` from spec frontmatter).

> Anti-pattern: "improve the auth." → no object, no bound, no metric → the agent rewrites half the app. Pin the verb, the object, the fence.

### 📐 Format — *how to deliver*
The shape of "done." Format makes output **gradeable** — without it you cannot tell success from a plausible miss.

Must contain:
- **Deliverable shape** — files at exact paths / a Mermaid diagram / keyed JSON / a one-line-per-finding review. State the artifact type and where it lands (`projects/<PRJ-ID>/...`).
- **The gate-bar** — the objective pass condition (response matches OpenAPI · WCAG 2.2 AA · coverage > 90% · TTI < 2s · authz enforced). Copied from the role's Operating Contract.
- **Standards** — PSR-12 / Effective Dart / Airbnb TS / Conventional Commits. Code is always normal prose; chatter rides the caveman dial.
- **Grounding clause (v5, `grounding.md`)** — answer strictly from the cited brain files + the frozen artifact; cite `file:line` for every factual claim, mark anything ungrounded `[unverified]`, and **abstain rather than fabricate** ("insufficient information → escalate" is the rewarded output). Distinguish `[verified: source]` from `[inferred]`.
- **The evidence block (v5, `verification.md` V1)** — completion is not a claim; it is proof. The handoff must paste the actual command + output/exit code, a `file:line` proof, or the git diff/SHA. A ticket marked `done` without an evidence block is rejected by `sofi gate-check`. Self-report is not evidence.
- **The handoff** — who receives the work next, and the closing ritual: checkpoint to git, append `CONTEXT.md`, update `STATE.md` (`head_sha`), write the next ticket in `HANDOFFS.md` — i.e. close with `/sofi-handoff`.

> Anti-pattern: "send me the code." → no path, no bar, no handoff → output is unplaceable and the chain breaks. Name the path, the bar, the next agent.

---

## 3. The canonical block (copy this shape)

```
🎭 Role     You are Aisha Rahman — Backend/Blade Engineer (Tier 2 · full-ownership).
            Route: sonnet · medium · ultra (routing.yaml: backend-blade-engineer).
            Spec: engine/agents/tier-2-development/backend-blade-engineer.md.

📂 Context  Foundation: you serve Teaching I (Design is Truth) + Teaching IV (Token Economy).
            Read `engine/DOCTRINE.md` (the 6 teachings) before your first task.
            Project PRJ-sakk · Gate 4 (Parallel Implementation).
            Read first, in order: 00-operating-system.md (your contract) ·
              projects/PRJ-sakk/_context/STATE.md (branch + head_sha) ·
              projects/PRJ-sakk/_context/FOUNDATIONS.md (project's doctrine pinning) ·
              HANDOFFS.md (ticket TKT-0042) · CONTEXT.md (facts so far).
            Frozen source of truth: PRJ-sakk_OpenAPI.yaml §POST /auth/login.
            Stack: Laravel 12. Constraint: auth must use the existing Sanctum guard.

🎯 Command  Build the POST /auth/login endpoint end-to-end:
            effort-class → single-role (1 agent, no subagents, budget 3-10 calls;
                           fail-safe: 3 correction attempts then escalate).
            in-bounds  → Form Request (validation) · thin Controller · Service
                         (business logic) · API Resource (matches OpenAPI) ·
                         Eloquent touch-points · unit test.
            out-of-bounds → schema migrations · other endpoints · the mobile client.
            success → request/response shape is byte-identical to the OpenAPI spec.

📐 Format   PSR-12, strict types, PHPDoc on public methods.
            Files at app/Http/Requests, app/Http/Controllers/API, app/Services,
              app/Http/Resources; test under tests/Feature.
            Gate-bar: response matches OpenAPI · authz enforced · unit tests green.
            Grounding: cite file:line for every claim about existing code; mark
              anything ungrounded [unverified]; abstain rather than guess.
            Evidence: paste the actual `php artisan test` output + exit code into
              the handoff — "tests pass" without the output is rejected at gate-check.
            Handoff: → tier-2-advisor for PR review. Close with /sofi-handoff
              (checkpoint · append CONTEXT.md · update STATE.md head_sha · next ticket).
```

**Compact form** (for quick chatter / the org chart) — the same contract, one line:
```
@Backend.backend-blade-engineer → POST /auth/login (FormReq+Ctrl+Svc+Resource+test) → matches OpenAPI §/auth/login {sonnet·medium·ultra} ⮕ tier-2-advisor
```
Use the compact form only when Context is already shared (same project, same gate, agent already oriented). First spawn of a task = full block.

---

## 4. RCCF maps onto what already exists (nothing is thrown away)

The doctrine is a *lens* over the existing system — it renames and orders fields you already have:

| RCCF field | Pulled from |
|------------|-------------|
| 🎭 Role | `engine/ROSTER.md` (persona) + `engine/agents/**` (spec) + `engine/routing/routing.yaml` (route) |
| 📂 Context | the project brain `projects/<PRJ-ID>/_context/{STATE,CONTEXT,HANDOFFS,DECISIONS}.md` + the frozen Gate-N artifact |
| 🎯 Command | the inbound ticket in `HANDOFFS.md` + the role's `consume`/`success_metric` |
| 📐 Format | the role's `produce` + `gate-bar` + `handoff` (Operating Contract) + `engine/lifecycle/gates.md` |

So building a block = reading four places you already maintain. `/sofi-delegate` does the reading for you.

---

## 5. Doctrine alignment (RCCF never overrides these)

The full Doctrine is at `engine/DOCTRINE.md`. The 6 teachings constrain every RCCF block:

| Teaching | RCCF implication |
|----------|------------------|
| **I — Design is Truth** | 📂 Context must name a *frozen* artifact; no frozen upstream → reject upward, don't improvise. |
| **II — Hierarchical Flow** | 📂 Context names the gate; a Gate-4 spawn before Gate-3 artifacts are frozen is invalid. |
| **III — Radical Isolation** | 📂 Context names one `PRJ-ID`; the agent touches only that tree. |
| **IV — Token Economy** | 🎭 Role carries the cheapest dials that clear the bar; log in `<thinking>`. |
| **V — Continuous Metamorphosis** | 📐 Format ends with a handoff; the chain must not break. The agent's output feeds the next cycle. |
| **VI — Reversibility Principle** | 🎯 Command for irreversible work must require an ADR. An RCCF that asks for a rollback-free migration is invalid — reject it. |

Additional:
- **Safety > brevity** — security warnings, irreversible confirmations, and all code/commits are normal prose, never caveman, regardless of the Role's caveman dial.
- **One artifact, then checkpoint** — Format always ends in the handoff ritual; an uncommitted agent is invisible to the next.

---

## 6. RCCF v2 — the freeze, the budget, the branch (SOFI v5)

Three upgrades that turn the four-field block from "a good brief" into "a frozen contract." Grounded in the spec-driven-development + bounded-autonomy research (`.claude/docs/ai-guides/research/agent-spec-design.md`).

**Clarify before you commit — don't spawn a half-brief.** If you cannot fill Role/Context/Command/Format with real specifics — the artifact isn't frozen, the boundary is fuzzy, the success metric is a vibe — **do not spawn a vague block and hope.** Emit the clarifying questions instead (to the requester, or up-chain via `sofi escalate`). This is the industry's answer (interview → freeze spec → implement) to the #1 agent failure: solving the *wrong* problem because scope was inferred, not fixed. A guessed brief is more expensive than a paused one.

**Freeze the brief — no instruction drip.** Once the block is complete and the agent is spawned, the RCCF is **frozen**: you do not feed it corrections one message at a time as it works. Mid-flight instruction drip is how scope creeps and context rots. If the brief was wrong, stop the agent, fix the block, re-spawn clean — don't patch it live.

**Budget the autonomy — pick the effort-scaling row.** Every block states its task class from `routing.yaml` `effort_scaling` (trivial-fix · single-role · cross-tier · audit-sweep · arbitration), which fixes the spawn width and call budget, plus a **fail-safe stop** (the 3-attempt self-correction ceiling → 4th = circuit breaker). Bounded autonomy empirically completes *more* tasks, not fewer. Fan out parallel specialists ONLY when the sub-tasks are context-independent; never fan out the sequential phases of one ticket.

The **boundaries field is first-class** — Command's `out-of-bounds` is not optional decoration; it is the single most under-used, highest-value line. "What this must NOT touch" (files, other projects, other endpoints, the schema) gets stated explicitly every time.

---

## 7. Quick self-check before you hit spawn

If you cannot answer all six, the brief is incomplete — fix it or clarify, don't spawn:

1. 🎭 Does it name the **persona, tier, and exact route**?
2. 📂 Does it point at the **brain + the one frozen artifact** this derives from?
3. 🎯 Is the ask one **bounded** unit — with an explicit **out-of-bounds**?
4. 📐 Is "done" **gradeable** — path, gate-bar, grounding clause, **evidence block**, and named handoff?
5. 🎚️ Is the **effort-scaling class + fail-safe stop** stated (spawn width, call budget)?
6. ❓ Could every field be filled with **real specifics** — or should you **clarify first** instead of guessing?

Six yeses → spawn a frozen block. Any no → clarify or fix; a guessing agent burns tokens. Big brain, small mouth — but only after a complete, grounded, budgeted brief. 🪨
