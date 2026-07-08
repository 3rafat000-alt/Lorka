---
name: sofi-delegate
description: Build a paste-ready RCCF v3 Work Order (Role · Context · Command · Format) for any SOFI agent — looks up the agent's route, gate, persona, and spec, injects the active project's brain pointers + frozen artifact, and pins the command scope + gate-bar so the spawn never guesses. Use to spawn or hand off work the disciplined way. Triggers — "delegate to X", "spawn X to do Y", "write the brief for", "RCCF block", "Work Order", "hand this to", "build a delegation", "task X with".
---

# /sofi-delegate — turn a task into a complete Work Order

Law: `company/constitution/01-work-order.md` (RCCF v3). A SOFI agent is only as good as the
Work Order it gets. This skill assembles the **4-part RCCF block** — 🎭 Role · 📂 Context ·
🎯 Command · 📐 Format — so the agent arrives knowing **who it is**, **what is already true**,
**the exact ask**, and **what "done" looks like.** No field → the agent guesses → tokens burn
(Teaching IV).

**Usage — two modes:**
- **One agent:** `/sofi-delegate <agent-id> "<the task>"` — e.g. `/sofi-delegate bck-blade-engineer "build POST /auth/login"`. Unsure who? run `/sofi-team` (or `sofi registry`) first.
- **Whole room, in parallel:** `/sofi-delegate <room>` — just a number `00`–`14`, a slug `04-architecture`, or a code `arc` → fan the SAME ask out to **every agent in that room at once**. Task inline: `/sofi-delegate 04 "review the payment schema"`.

## Room mode (one number = the whole room, in parallel)
When the arg is a room (number `00`–`14`, slug `05-backend`, or code `bck`), don't hand-build one block — render them all at 0 model tokens, then spawn together:
1. `sofi room <room> [--prj <PRJ>] [--task "<the ask>"]` — prints a full RCCF delegation block for **every** agent in the room (route · spec · contract already filled; resolves the room by number/slug/code).
2. **Spawn them all in ONE message** (several Agent calls in the same turn) so they run concurrently — that IS the parallelism (flat topology: depth = new rounds, never nesting).
3. The room **Lead** coordinates + gate-merges; specialists execute their slice. Same frozen brief to all; each returns its own artifact.
- Omit `--task` → the block carries a `<the shared ask>` placeholder to fill before spawning. Include the room Lead? `sofi room` lists the whole roster (Lead + specialists); drop the Lead's block if you want workers-only.

## Procedure (build the block by reading 4 places)

1. **Resolve the agent.** Look the id up in `company/nexus/registry.yaml` (`sofi registry`) →
   room + spawnable file `.claude/agents/<id>.md` + full spec `company/rooms/<NN-room>/agents/<id>.md`.
   The id IS the spawn name (e.g. `bck-blade-engineer`, `sec-pentester`).
2. **🎭 Role** — pull the **route verbatim** from `company/nexus/routing.yaml` (`routes.<id>`:
   `model · effort · caveman · budget`). Never invent it. Add persona + room + spec path.
3. **📂 Context** — resolve the active `PRJ-ID` (from `projects/*/_context/STATE.md`, or ask if
   ambiguous). State the current **gate**. List the brain pointers (STATE/HANDOFFS/CONTEXT/LESSONS)
   + `company/constitution/00-operating-system.md`. Name the **one frozen upstream artifact** this
   work derives from (by path + section) — if none is frozen, STOP and reject upward (Teaching I ·
   Design is Truth).
4. **🎯 Command** — turn the task into one bounded unit: verb + object, explicit **in-bounds**
   sub-parts, explicit **out-of-bounds** (each → its owning agent id), and the role's `success_metric`
   (spec frontmatter).
5. **📐 Format** — deliverable shape + exact target paths, standards (PSR-12 / Effective Dart /
   Airbnb TS), the **gate-bar**, the **grounding clause** (cite file:line, mark `[unverified]`,
   abstain not fabricate — `company/constitution/02-grounding.md`, G1–G5), the **evidence block**
   (paste the real command+exit code / file:line / diff-SHA on completion —
   `company/constitution/03-verification.md`, V1), and the **handoff** target + closing ritual
   (`/sofi-handoff`).
6. **Set the budget.** State the task's **effort-scaling class** from `routing.yaml` `effort_scaling`
   (`trivial-fix · single-role · cross-room · audit-sweep · arbitration`) — it fixes spawn width +
   call budget (enforced by `gtw-budget-warden`) — plus the **fail-safe stop** (3 attempts → escalate,
   circuit breaker).
7. **Emit** the block in a fenced code box, paste-ready. Then state the spawn line:
   `Agent(subagent_type: "<id>", prompt: <the block>)`.

## Clarify before you commit
If any field can't be filled with **real specifics** — the upstream artifact isn't frozen, the
boundary is fuzzy, "done" is a vibe — **do NOT emit a vague block.** Emit the clarifying questions
instead (to the requester or up-chain via `sofi escalate`). A guessed Work Order is more expensive
than a paused one. Once emitted and spawned, the block is **frozen** — no correcting the agent one
message at a time; if it was wrong, stop, fix the block, re-spawn clean.

## Self-check before emitting (the 6 yeses — `01-work-order.md`)
- 🎭 names persona, room, **exact route** from routing.yaml?
- 📂 points at the brain **+ the one frozen artifact** (not pasted)?
- 🎯 one bounded ask with an explicit **out-of-bounds** (each → owning agent)?
- 📐 "done" is gradeable — path, gate-bar, **grounding clause + evidence block**, named handoff via lead?
- 🎚️ **effort-scaling class + fail-safe stop** stated?
- ❓ could every field be filled with **real specifics** — or clarify first?

Any "no" → clarify or fix the brief, don't spawn.

## Worked example
`/sofi-delegate bck-blade-engineer "build POST /auth/login"` →

```
🎭 Role     You are Aisha Rahman — Backend/Blade Engineer · Room 05-backend.
            Route: sonnet · medium · ultra  (nexus/routing.yaml: bck-blade-engineer).
            Spec: company/rooms/05-backend/agents/bck-blade-engineer.md.

📂 Context  Project PRJ-sakk · Gate 4 (Implementation).
            Read first, in order:
              - company/constitution/00-operating-system.md    (your contract)
              - company/constitution/01-work-order.md           (this brief's shape)
              - projects/PRJ-sakk/_context/STATE.md           (branch · head_sha)
              - projects/PRJ-sakk/_context/HANDOFFS.md         (ticket TKT-0042)
              - projects/PRJ-sakk/_context/CONTEXT.md          (facts + decisions)
              - projects/PRJ-sakk/_context/LESSONS.md          (procedural memory)
            Frozen source of truth: PRJ-sakk_OpenAPI.yaml §POST /auth/login (arc-api-architect).
            Constraint: reuse the existing Sanctum guard; no new auth scheme.

🎯 Command  Build POST /auth/login end-to-end.
            in-bounds  → Form Request · thin Controller · Service · API Resource
                         (matches OpenAPI) · Eloquent touch-points · unit test.
            out-of-bounds → schema migrations (→ dat-db-engineer) · other endpoints ·
                            the mobile client (→ mob-flutter-engineer).
            success → request/response shape is byte-identical to the OpenAPI spec.

📐 Format   PSR-12, strict types, PHPDoc on public methods. Code normal prose; chatter ultra.
            Files: app/Http/Requests · app/Http/Controllers/API · app/Services ·
                   app/Http/Resources · test under tests/Feature.
            Gate-bar: response matches OpenAPI · authz enforced · unit tests green.
            Grounding: cite file:line, mark [unverified], abstain not fabricate.
            Evidence: paste `php artisan test --filter=Login` + exit code on completion.
            Effort class: single-role · fail-safe: 3 attempts → sofi escalate.
            Handoff: → bck-lead (PR review via lead) → then bck-code-reviewer.
              Close with /sofi-handoff (checkpoint · CONTEXT · STATE head_sha · next ticket).
```
Spawn: `Agent(subagent_type: "bck-blade-engineer", prompt: <block above>)`.

## Rules
- Route comes from `company/nexus/routing.yaml` only — apply the `priority_override` (CRITICAL/LOW) if the project is tagged; the gatekeeper tier is reachable only by a CRITICAL bump.
- Respect gate order — refuse to build a Gate-4 brief while Gate-3 artifacts aren't frozen (Teaching II).
- One bounded artifact per spawn; if the task is multi-artifact, emit one block per artifact.
- Room Isolation Law — a cross-room ask is addressed to the target Lead, not the specialist; only `brd-*`/`gtw-*` bypass. Leads forward verbatim (Article 08).
- SOFI subagents refuse `SendMessage` resumes — spawn a **fresh** `Agent()` per brief.
- Compact form (`@room.agent → ask → bar {route} ⮕ next`) only when context is already shared.
