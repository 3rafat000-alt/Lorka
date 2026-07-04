---
name: sofi-gate
description: Check the current SOFI lifecycle gate's exit bar and decide whether to advance. Validates that the gate's deliverables exist and its validation criteria pass before opening the next gate (no skipping). Use to run a gate, check readiness, or advance the lifecycle. Triggers — "gate check", "advance gate", "can we move to gate N", "is this gate done", "ready for the next gate".
---

# /sofi-gate — gate-bar check & advance

Work cascades **down and in order** through 9 gates (`engine/lifecycle/gates.md`).
A gate cannot open until the prior gate's deliverables are validated and signed
off by the originating department. **No skipping.** This skill checks the bar and
advances exactly one gate.

## The 9 gates (owner · output · validation)

| G | Name | Owner | Output | Bar |
|--|------|-------|--------|-----|
| 0 | Inception | chief-product-strategist | `Project_Blueprint.md` + Problem Statement · `<slug>.local` registered | charter exists · `sofi domain list` shows it |
| 1 | Discovery | ux-researcher + journey-architect | Personas, Journey Map | answers "what does the user want & what blocks them?" |
| 2 | Solution Design | ui-ux-designer + content-strategist | Prototype Spec, Content Strings | WCAG 2.2 **AA** |
| 3 | Architecture | principal-system-architect + Data/API/Security | Schema, OpenAPI, Tech Stack, Threat Model | schema ↔ screens traceable |
| 4 | Implementation | Backend + Frontend + Mobile (parallel) | compiled assets, packages, unit tests | OpenAPI + Journey Map = single source of truth |
| 5 | Integration & Quality | qa-sre-lead + QA squad | test reports, bug logs, Design Audit | Critical/High = 0 · coverage > 90% · perf budget pass |
| 6 | Staging & UAT | devops-cloud-lead | staging URL, UAT sign-off | simulated UAT pass |
| 7 | Production | devops-cloud-lead + cicd-pipeline-engineer | prod confirmation, rollback script | Blue/Green healthy |
| 8 | Observe & Evolve | observability-sre + performance-load-analyst | perf report, backlog | SLO breach → file issue → **re-enter Gate 1** |

## Steps

1. **Find the current gate** — `projects/<PRJ>/_context/STATE.md` → `gate:`.
2. **Tooling check** (authoritative if available):
   ```bash
   engine/tooling/bin/sofi gate-check <PRJ>
   ```
3. **Verify deliverables exist** for the current gate (table above) under
   `projects/<PRJ>/` — each named artifact present and non-stub.
4. **Verify the validation bar passes.** Run the real check, don't assume:
   - Gate 5 → run the test suite; confirm coverage > 90%, 0 Critical/High, perf budget.
   - Migrations without rollback = **rejected**. Coverage < 90% = **rejected**. TTI ≥ 2s = **rejected**.
5. **Decide:**
   - **PASS** → advance: bump `gate:` in STATE.md, set the next gate's owner as `active:`,
     write the opening ticket in HANDOFFS.md, then `sofi checkpoint <PRJ> "chore(gate): open gate <N+1>"`.
   - **FAIL** → do **not** advance. File a blocker back up the chain in HANDOFFS.md and
     name the missing/failing deliverable.

## Report

```
GATE <N> (<name>) — <PASS|FAIL>
deliverables: <present / missing list>
bar: <each criterion → pass/fail with evidence>
decision: advance to <N+1> | blocked on <reason>
```

## Rules
- A downstream gate receiving incomplete upstream deliverables **rejects** and files a blocker — it does not paper over the gap.
- Design is Truth: any feature without a Journey Map step is rejected at Gate 3 → Backlog.
- Local domain first: Gate 0 registers `<slug>.local`; Gate 4 runs `sofi domain up <PRJ>`.
- Advancing a gate is a milestone → always `sofi checkpoint`. See `/sofi-handoff`.
