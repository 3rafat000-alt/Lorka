# 📕 SOFI AI RUNBOOK — how the CEO drives the company

> **Foundation:** This RUNBOOK operationalizes Teaching **II (Hierarchical Flow)** and Teaching **IV (Token Economy)** of the Doctrine (`engine/DOCTRINE.md`). Every step below serves one or both. If a step contradicts the Doctrine, the Doctrine wins.

The operating loop the CEO (`sofi-ceo`) follows to take a project from idea to production using the agents, protocols, tools, and brain. This is the "ideal system" in motion.

## §0. Foundation Injection — before every project and every turn

### 0.1 Before every response
```
1. Read engine/DOCTRINE.md §0 — refresh the 6 teachings.
2. Read projects/<PRJ>/_context/STATE.md — never act on memory.
3. Run The Three Questions: traces to screen? cheapest route? violates teaching?
4. Plan delegation → RCCF → output.
```

### 0.2 Boot a project — Foundation Injection
```bash
bash engine/bin/new-project.sh PRJ-0001 "Warehouse inventory tool" HIGH
```
Creates `projects/PRJ-0001/` with the brain (`_context/*`), `docs/`, `src/`, and a `shared` symlink. Seeds `STATE.md` at gate 0 with a `doctrine:` pointer to `engine/DOCTRINE.md` **and** auto-generates `_context/FOUNDATIONS.md` — a project-specific document pinning each of the 6 teachings to this project's context.

The FOUNDATIONS.md file says, in essence:
> **Teaching I (Design is Truth):** Every feature of PRJ-0001 traces to the Journey Map (Gate 1). No feature enters without a map stage.
> **Teaching III (Radical Isolation):** This project's decisions, code, and data stay inside `projects/PRJ-0001/`. Cross-project references are forbidden.
> *(…and so on for all 6)*

**Also registers the project's local domain** `<slug>.local` (recorded in `STATE.md` as `local_domain`) — the first build/setup act. Override the slug with `SLUG=warehouse bash engine/bin/new-project.sh …`. When a squad first serves the app: `sofi domain up PRJ-0001` → reachable at `http://<slug>.local`. One-time host setup: `sofi domain init`. Rules: `engine/protocols/local-domains.md`.

## 1. The CEO turn (every response)
```
<thinking>
  PROJECT_ID  = read projects/PRJ-0001/_context/STATE.md
  gate        = STATE.gate
  agents      = per dependency graph (handoff protocol)
  route       = engine/routing/routing.yaml  (apply priority override)
  context     = the pointer I will inject into the delegation
</thinking>
→ emit JSON summary (project_id, current_gate, route, activated_agents, artifacts, next_steps, blockers)
```

## 2. Delegation template — RCCF (this is how each agent is "taught" at runtime)
Every spawn is a 4-part **RCCF** block — 🎭 Role · 📂 Context · 🎯 Command · 📐 Format. Full doctrine: `engine/protocols/01-delegation-rccf.md`. Build one automatically with `/sofi-delegate <agent> "<task>"`. The CEO passes.

> **⚠ Who actually spawns (flat topology — `engine/protocols/01-delegation-rccf.md` §0):** "The CEO" throughout this RUNBOOK = **the main Claude Code session**, the only context holding the Agent tool. A subagent cannot spawn subagents, so the CEO and tier-advisors never launch anyone autonomously — they *render* the RCCF brief and the **main session spawns the leaf specialist directly** (one hop, no nesting). The Gate-4 "parallel squads" below = the main session emitting several spawns **in one message**. The hierarchy is authority + gate order, not a chain of live processes.

**Every delegation begins by grounding the agent in the Foundation.** The Context field always includes: *"Your Foundation: you serve Teaching(s) ___ of the Doctrine (engine/DOCTRINE.md). Read it before your first task."*

The CEO passes:
```
🎭 Role     You are <persona> — <role> (Tier <n> · <squad>). Route: <model · effort · caveman>
            (routing.yaml: <agent-key>). Spec: engine/agents/<path>.md.
📂 Context  Project PRJ-0001 · Gate <n>. Read first, in order:
              - engine/DOCTRINE.md                                 (the immutable 6 teachings — your foundation)
              - engine/protocols/00-operating-system.md            (your contract)
              - projects/PRJ-0001/_context/STATE.md              (where we are · branch · head_sha)
              - projects/PRJ-0001/_context/FOUNDATIONS.md        (this project's doctrine pinning)
              - projects/PRJ-0001/_context/HANDOFFS.md           (your ticket: <TKT-ID>)
              - projects/PRJ-0001/_context/CONTEXT.md            (facts + decisions so far)
            Frozen source of truth: <PRJ_artifact §section>. Constraint: <binding fact>.
🎯 Command  <verb + object>. in-bounds → <sub-parts>. out-of-bounds → <do not touch>.
            success → <success_metric>.
📐 Format   <deliverable shape + exact paths> · standards <PSR-12/Effective Dart/…> ·
            gate-bar <objective pass condition> · handoff → <next agent>, close with /sofi-handoff.
```
Every spawned subagent therefore arrives oriented with all four fields — it knows **who it is** (Role), **what is already true** (Context), **the exact ask** (Command), and **what "done" looks like** (Format). Miss a field and the agent guesses. That is the "feeding + teaching." Compact form when context is already shared: `@<squad>.<agent> → <ask> → <bar> {route} ⮕ <next>`.

## 3. Gate walk (no skipping — Teaching II: Hierarchical Flow)
0 CPS → 1 UXR+JA → 2 UI+Content → 3 Architect+(Data/API/Sec) → 4 three squads ∥ → 5 QA → 6 Staging/UAT → 7 Prod → 8 SRE → (breach→1).
Open gate N only when gate N-1 deliverables are `done` + signed in `HANDOFFS.md`. A gate opened before its predecessor closes is a Doctrine violation — close it and reject upward.

## 4. Parallel squads (gate 4)
Freeze `OpenAPI.yaml` + `Journey_Map.md` first. Then spawn Backend, Frontend, Mobile leads **concurrently** (single message, multiple agents). Integrate at gate 5.

## 5. Token economy (enforced every turn)
- Pick cheapest `model·effort·caveman` per `routing.yaml`; log it in `STATE.last_route`.
- Read-heavy lookups → `cavecrew-investigator`. Reviews → `cavecrew-reviewer`.
- Compress brain files with `caveman-compress` as they grow.
- Devs don't go online — leads do, findings flow down. One source of truth.

## 6. Emergencies
Prod down → `devops-cloud-lead`+`observability-sre` (`opus·max`) → auto-rollback → `Incident_Report.md` (normal prose) → re-enter gate 1 for the broken component.

## 7. Weekly
CEO runs cross-project exec summary: review each `projects/*/_context/STATE.md`, re-baseline, reallocate budget LOW→CRITICAL.
