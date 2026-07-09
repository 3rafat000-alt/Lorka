# Delegation Protocol — RCCF Rendered

Every spawn is a 4-part contract. Missing fields = guessing agent. Don't spawn if you can't fill all 4.

## The RCCF Block

```
🎭 ROLE     — Persona · Tier · Route
📂 CONTEXT  — Brain + frozen artifact(s)
🎯 COMMAND   — One bounded unit + explicit out-of-bounds
📐 FORMAT   — Files · Gate-bar · Evidence · Handoff · Effort class · Fail-safe
```

## Role (🎭)

- **Persona:** One of 105 agents from `registry.yaml` (e.g., `bck-api-engineer`)
- **Tier:** `mechanical | workhorse | gatekeeper | deep`
- **Route:** Model allocation per `routing.yaml`

## Context (📂)

- **Project:** PRJ-XXXX
- **Gate:** Current gate number
- **Brain:** `_context/{STATE,CONTEXT,HANDOFFS,DECISIONS}.md` — always read fresh
- **Frozen artifact:** One or more signed Gate deliverables (e.g., OpenAPI spec, Prototype Spec)
  - Format: `[artifact path] §[section reference]`

## Command (🎯)

- **Build:** Single verb-object pair — one bounded unit of work
- **In:** Numbered sub-parts, each independently verifiable
- **Out:** Explicit boundaries — "DO NOT touch X, Y, Z"
- **Metric:** Success measurement

## Format (📐)

- **Paths:** Exact file paths the agent should create/modify
- **Gate-Bar:** Criteria that must pass before handoff
- **Evidence:** What the agent must paste as proof of completion
- **Handoff:** Next agent or ticket ID
- **Effort class:** `trivial-fix | single-role | cross-tier | audit-sweep | arbitration`
- **Fail-safe:** Stop condition — what triggers abort

## Delegation Lifecycle

```
1. BUILD RCCF  — Fill all 4 fields from registry + frozen artifact
2. FROZEN      — Block is sealed. No mid-flight instruction drip.
3. SPAWN       — Deploy agent with RCCF as sole brief
4. EXECUTE     — Agent works autonomously
5. VERIFY      — Gatekeeper checks outcome against gate-bar
6. COLLECT     — Harvest evidence, update state
7. HANDOFF     — Write next ticket, checkpoint

If wrong brief at step 1-2: KILL, fix block, re-spawn (step 2 repeats)
If blocked at step 4: Agent escalates, never guesses
```

## Flat Topology (Binding)

- Main session is the ONLY context that can spawn
- A subagent CANNOT spawn subagents
- CEO/tier-advisors are personas the main session WEARS, not live orchestrators
- Delegation is ONE HOP (main → leaf specialist)
- Parallelism = multiple spawns in one message
- Depth is faked by rounds (main → leaf A, collect → main → leaf B), not nesting

## Effort Class Reference

| Class | Max Calls | Max Parallel Agents | Fail-Safe |
|-------|-----------|-------------------|-----------|
| trivial-fix | 3 | 1 | 3 attempts → escalate |
| single-role | 10 | 1 | 3 attempts → escalate |
| cross-tier | 30 | 3 | 3 attempts → escalate |
| audit-sweep | 50 | 5 | 3 attempts → escalate |
| arbitration | 10 | 1 (deep) | 1 attempt → escalate |

## Self-Check Before Each Spawn

```
❓ All 6 questions answerable with specifics?
1. 🎭 Persona + tier + route?                        Y/N
2. 📂 Brain + one frozen artifact?                    Y/N
3. 🎯 One bounded unit + out-of-bounds?               Y/N
4. 📐 Gradeable done + gate-bar + evidence?           Y/N
5. 🎚️ Effort class + fail-safe?                       Y/N
6. ❓ All fields filled with real (not placeholder)?  Y/N

Any N → DO NOT SPAWN → clarify first
```
