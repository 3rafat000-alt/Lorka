---
name: sofi-gate
description: Check the current SOFI lifecycle gate's exit bar and decide whether to advance. Validates that the gate's deliverables exist and its validation criteria pass — then a fresh-context adversarial verify by gtw-gatekeeper — before opening the next gate (no skipping). Use to run a gate, check readiness, or advance the lifecycle. Triggers — "gate check", "advance gate", "can we move to gate N", "is this gate done", "ready for the next gate".
---

# /sofi-gate — gate-bar check & advance

Work cascades **down and in order** through 9 gates (`company/constitution/10-lifecycle-gates.md`;
machine-readable `company/nexus/gates.yaml`). A gate cannot open until the prior gate's deliverables
are validated and signed off by the owning room's Lead. **No skipping** (Teaching II · Hierarchical
Flow). This skill checks the bar and advances exactly one gate.

## The 9 gates (owner room · output · validation)

| G | Name | Owner (Lead) | Output | Bar |
|--|------|--------------|--------|-----|
| 0 | Inception | `str-lead` (acct. `brd-cpo`) | `Project_Blueprint.md` + Problem Statement · `<slug>.local` registered | charter exists · `sofi domain list` shows it |
| 1 | Discovery | `res-lead` | Personas, Journey Map (Mermaid) | answers "what does the user want & what blocks them?" |
| 2 | Solution Design | `dsn-lead` | Prototype Spec, Content Strings | WCAG 2.2 **AA** (`dsn-a11y-specialist`) |
| 3 | Architecture | `arc-lead` (acct. `brd-cto`) | Schema, OpenAPI, Tech Stack, Threat Model | schema ↔ screens traceable · `sec-threat-modeler` signs |
| 4 | Implementation | `bck/fnt/mob/dat` Leads (parallel) | compiled assets, packages, unit tests | OpenAPI + Journey Map = single source of truth |
| 5 | Integration & Quality | `qa-lead` (acct. `brd-cqo`) | test reports, bug logs, Design Audit | Critical/High = 0 · coverage > 90% · perf budget pass |
| 6 | Staging & UAT | `ops-lead` | staging URL, UAT sign-off | simulated UAT pass |
| 7 | Production | `ops-lead` + `ops-release-manager` | prod confirmation, rollback script | Blue/Green healthy · tested rollback |
| 8 | Observe & Evolve | `obs-lead` | perf report, backlog | SLO breach → `obs-insights-analyst` files issue → **re-enter Gate 1** |

## Steps

1. **Find the current gate** — `projects/<PRJ>/_context/STATE.md` → `gate:`.
2. **Mechanical check (V1 — authoritative, evidence-present, room-boundary):**
   ```bash
   sofi gate-check <PRJ>
   ```
   This runs no-skip + artifacts-exist + `validate_evidence` + `validate_room_boundary`
   (a boundary violation fails the gate exactly like a skipped gate).
3. **Verify deliverables exist** for the current gate (table above / `gates.yaml`) under
   `projects/<PRJ>/` — each named artifact present and non-stub.
4. **Verify the validation bar passes.** Run the real check, don't assume:
   - Gate 5 → run the test suite; confirm coverage > 90%, 0 Critical/High, perf budget.
   - Migrations without rollback = **rejected** (Teaching VI). Coverage < 90% = **rejected**. TTI ≥ 2s = **rejected**.
5. **Fresh-context adversarial verify (V2 — `company/constitution/03-verification.md`).** The gate
   advances only on a fresh-context adversarial check by **`gtw-gatekeeper`** against the *original*
   exit criteria + pasted mechanical evidence — **never the implementer grading itself**. Spawn the
   gatekeeper (`/sofi-delegate gtw-gatekeeper "verify Gate <N> for <PRJ> against gates.yaml exit bar"`);
   it tries to prove the gate is NOT met. Survives refutation → PASS; else → FAIL.
6. **Decide:**
   - **PASS** → advance: bump `gate:` in STATE.md, set the next gate's owner Lead as `active:`,
     write the opening ticket in HANDOFFS.md, then `sofi checkpoint <PRJ> "chore(gate): open gate <N+1>"`.
   - **FAIL** → do **not** advance. File a blocker back up the chain in HANDOFFS.md and
     name the missing/failing deliverable.

## Report

```
GATE <N> (<name>) — <PASS|FAIL>
owner room: <lead id>
deliverables: <present / missing list>
bar: <each criterion → pass/fail with evidence>
gtw-gatekeeper verdict: <survived refutation | refuted on …>
decision: advance to <N+1> | blocked on <reason>
```

## Rules
- A downstream gate receiving incomplete upstream deliverables **rejects** and files a blocker — it does not paper over the gap (Teaching II · reject upward).
- Design is Truth: any feature without a Journey Map step is rejected at Gate 3 → Backlog.
- Local domain first: Gate 0 registers `<slug>.local` (`ops-domain-warden`); Gate 4 runs `sofi domain up <PRJ>`.
- The gatekeeper who advances a gate is **never** the agent who did the work (V2 · same-agent self-report is not evidence).
- Advancing a gate is a milestone → always `sofi checkpoint`. See `/sofi-handoff`.
