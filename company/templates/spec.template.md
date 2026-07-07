# Feature Spec: [Name]

**PRJ:** PRJ-XXXX · **Created:** YYYY-MM-DD · **Status:** Draft | Review | Approved | Implemented | Archived
**Journey stage:** [which Journey Map stage — if none, this goes to Backlog (Design is Truth)]

## 1. Overview
- **Goal:** one sentence — what this achieves.
- **Target user / persona:** who it serves.
- **Business value:** why it matters now.

## 2. Requirements
- [ ] Functional req 1
- [ ] Functional req 2
- **Non-functional:** perf budget (see `templates/PERF_BUDGET.md`), security (STRIDE per Ruth), a11y (WCAG 2.2 AA), RTL + responsive.

## 3. Acceptance criteria (measurable → these are the gate)
- [ ] Criterion 1 (observable, testable)
- [ ] Criterion 2
- **Success metric:** the one number that says "done" (ties to the owning role's `success_metric`).

## 4. File scope (the frozen contract — Gate 4 builds only inside this)
- `backend/...` · `frontend/...` · `mobile/...`

## 5. Constraints & invariants
- Must use: [pattern/stack]. Must NOT: [forbidden dep/approach].
- Invariants that must hold true before and after.

## 6. Research / prior art
- Internal (brain/codebase) → web (cited). Decisions that are irreversible → log an ADR (`templates/ADR.md`).

## 7. Approvals (gate sign-off)
- [ ] Product/Scope — Amara
- [ ] Design — Dan · Content — Peg
- [ ] Architecture — Vikram · Security — Ruth
- [ ] Quality — Barb
