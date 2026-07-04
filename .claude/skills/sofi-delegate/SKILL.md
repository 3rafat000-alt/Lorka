---
name: sofi-delegate
description: Build a paste-ready RCCF delegation block (Role · Context · Command · Format) for any SOFI agent — looks up the agent's route, gate, persona, and spec, injects the active project's brain pointers + frozen artifact, and pins the command scope + gate-bar so the spawn never guesses. Use to spawn or hand off work the disciplined way. Triggers — "delegate to X", "spawn X to do Y", "write the brief for", "RCCF block", "hand this to", "build a delegation", "task X with".
---

# /sofi-delegate — turn a task into a complete RCCF brief

Doctrine: `engine/protocols/01-delegation-rccf.md`. A SOFI agent is only as good as the brief it gets. This skill assembles the **4-part RCCF block** — 🎭 Role · 📂 Context · 🎯 Command · 📐 Format — so the agent arrives knowing **who it is**, **what is already true**, **the exact ask**, and **what "done" looks like.** No field → the agent guesses → tokens burn.

**Usage:** `/sofi-delegate <agent-key> "<the task>"` — e.g. `/sofi-delegate backend-blade-engineer "build POST /auth/login"`. Agent unsure? run `/sofi-team` first to pick.

## Procedure (build the block by reading 4 places)

1. **Resolve the agent.** Map the key (e.g. `backend-blade-engineer`) → persona + tier + squad from `engine/ROSTER.md`, and full path under `engine/agents/**`. Spawnable name is `sofi-<key>`.
2. **🎭 Role** — pull the **route verbatim** from `engine/routing/routing.yaml` (`routes.<key>`: `model · effort · caveman`). Never invent it. Add persona + tier + spec path.
3. **📂 Context** — resolve the active `PRJ-ID` (from `projects/*/_context/STATE.md`, or ask if ambiguous). State the current **gate**. List the brain pointers (STATE/HANDOFFS/CONTEXT) + `00-operating-system.md`. Name the **one frozen upstream artifact** this work derives from (by path + section) — if none is frozen, STOP and reject upward (Design is Truth).
4. **🎯 Command** — turn the task into one bounded unit: verb + object, explicit **in-bounds** sub-parts, explicit **out-of-bounds**, and the role's `success_metric` (spec frontmatter).
5. **📐 Format** — deliverable shape + exact target paths, standards (PSR-12 / Effective Dart / Airbnb TS), the **gate-bar**, the **grounding clause** (cite file:line, mark `[unverified]`, abstain not fabricate — `grounding.md`), the **evidence block** (paste the real command+exit code on completion — `verification.md` V1), and the **handoff** target + closing ritual (`/sofi-handoff`).
6. **Set the budget (v5).** State the task's effort-scaling class from `routing.yaml` `effort_scaling` (trivial-fix · single-role · cross-tier · audit-sweep · arbitration) — it fixes spawn width + call budget — plus the fail-safe stop (3 attempts → escalate).
7. **Emit** the block in a fenced code box, paste-ready. Then state the spawn line: `Agent(subagent_type: "sofi-<key>", prompt: <the block>)`.

## Clarify before you commit (v5)
If any field can't be filled with **real specifics** — the upstream artifact isn't frozen, the boundary is fuzzy, "done" is a vibe — **do NOT emit a vague block.** Emit the clarifying questions instead (to the requester or up-chain via `sofi escalate`). A guessed brief is more expensive than a paused one. Once emitted and spawned, the block is **frozen** — no correcting the agent one message at a time; if it was wrong, stop, fix the block, re-spawn clean.

## Self-check before emitting (the 6 yeses — `01-delegation-rccf.md §7`)
- 🎭 names persona, tier, **exact route** from routing.yaml?
- 📂 points at the brain **+ the one frozen artifact** (not pasted)?
- 🎯 one bounded ask with an explicit **out-of-bounds**?
- 📐 "done" is gradeable — path, gate-bar, **grounding clause + evidence block**, named handoff?
- 🎚️ **effort-scaling class + fail-safe stop** stated?
- ❓ could every field be filled with **real specifics** — or clarify first?

Any "no" → clarify or fix the brief, don't spawn.

## Worked example
`/sofi-delegate backend-blade-engineer "build POST /auth/login"` →

```
🎭 Role     You are Aisha Rahman — Backend/Blade Engineer (Tier 2 · Development).
            Route: sonnet · medium · ultra  (routing.yaml: backend-blade-engineer).
            Spec: engine/agents/tier-2-development/backend-blade-engineer.md.

📂 Context  Project PRJ-sakk · Gate 4 (Parallel Implementation).
            Read first, in order:
              - engine/protocols/00-operating-system.md          (your contract)
              - engine/protocols/01-delegation-rccf.md            (this brief's shape)
              - projects/PRJ-sakk/_context/STATE.md            (branch · head_sha)
              - projects/PRJ-sakk/_context/HANDOFFS.md          (ticket TKT-0042)
              - projects/PRJ-sakk/_context/CONTEXT.md           (facts + decisions)
            Frozen source of truth: PRJ-sakk_OpenAPI.yaml §POST /auth/login.
            Constraint: reuse the existing Sanctum guard; no new auth scheme.

🎯 Command  Build POST /auth/login end-to-end.
            in-bounds  → Form Request · thin Controller · Service · API Resource
                         (matches OpenAPI) · Eloquent touch-points · unit test.
            out-of-bounds → schema migrations · other endpoints · the mobile client.
            success → request/response shape is byte-identical to the OpenAPI spec.

📐 Format   PSR-12, strict types, PHPDoc on public methods. Code normal prose; chatter ultra.
            Files: app/Http/Requests · app/Http/Controllers/API · app/Services ·
                   app/Http/Resources · test under tests/Feature.
            Gate-bar: response matches OpenAPI · authz enforced · unit tests green.
            Handoff: → tier-2-advisor (PR review). Close with /sofi-handoff
              (checkpoint · append CONTEXT.md · update STATE.md head_sha · next ticket).
```
Spawn: `Agent(subagent_type: "sofi-backend-blade-engineer", prompt: <block above>)`.

## Rules
- Route comes from `engine/routing/routing.yaml` only — apply the `CRITICAL/LOW` priority override if the project is tagged.
- Respect gate order — refuse to build a Gate-4 brief while Gate-3 artifacts aren't frozen.
- One bounded artifact per spawn; if the task is multi-artifact, emit one block per artifact.
- SOFI subagents refuse `SendMessage` resumes — spawn a **fresh** `Agent()` per brief.
- Compact form (`@squad.agent → ask → bar {route} ⮕ next`) only when context is already shared.
