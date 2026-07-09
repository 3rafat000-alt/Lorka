---
name: sofi-v6-gate-flow
description: "SOFI v6 gate lifecycle flow — orchestrates the 9-gate lifecycle across 15 rooms. Use when delegating a full product lifecycle, advancing through gates, or orchestrating multi-room workflows. Cover letter: use with @brd-ceo for start-to-finish product delivery."
---

# SOFI v6 · Gate Lifecycle Flow

The 9-gate lifecycle across 15 rooms. No gate is skipped. Advance only through `@gtw-gatekeeper`.

## Gate-by-gate flow

### Gate 0 — Inception
Rooms: **str** (Strategy)
Output: Project Blueprint (problem, JTBD, scope, metrics)
Lead: `@brd-cpo` signs → `@str-lead` assigns → `@str-product-strategist` + `@str-business-analyst` + `@str-market-analyst`

### Gate 1 — Discovery
Rooms: **res** (Research)
Output: Personas, Journey Map, competitor analysis
Lead: `@res-lead` assigns → `@res-ux-researcher` + `@res-journey-architect` + `@res-competitor-analyst`
Verify: `@res-fact-checker` grounds every claim

### Gate 2 — Design
Rooms: **dsn** (Design)
Output: Frozen UI spec, design tokens, a11y matrix, copy JSON, flow diagrams
Lead: `@dsn-lead` — once signed, no visual change without new Gate 2

### Gate 3 — Architecture
Rooms: **arc** (Architecture), **dat** (Data), **sec** (Security)
Output: System design, API contract, schema, infra plan, threat model
Lead: `@arc-lead` assembles, `@arc-review-architect` adversarially reviews, `@brd-cto` signs

### Gate 4 — Build
Rooms: **bck** (Backend), **fnt** (Frontend), **mob** (Mobile), **dat** (Data)
All rooms work in parallel. Each has a code-reviewer (or lead reviews for mob/dat).
Lead: `@brd-cto` coordinates

### Gate 5 — Quality
Rooms: **qa** (Quality), **sec** (Security)
Output: Test report, perf report, security scan, design audit
Lead: `@qa-lead` assembles, `@brd-cqo` issues PASS/BLOCK verdict
Gatekeeper: `@gtw-gatekeeper` adversarial check

### Gate 6 — Staging
Rooms: **ops** (DevOps)
Output: Deployed staging environment, migrations run, rollback proven
Lead: `@ops-lead`

### Gate 7 — Production
Rooms: **ops** (DevOps)
Output: Production deploy, domain/SSL, monitored
Lead: `@ops-release-manager`

### Gate 8 — Observe
Rooms: **obs** (Observability)
SLO breach → formal Gate 1 reopen for that component.
Lead: `@obs-lead`

## Parallelism pattern

When advancing from Gate 3 → 4, spawn build agents in parallel:
```
@bck-api-engineer + @bck-domain-engineer + @bck-blade-engineer
@fnt-vue-engineer + @fnt-css-artisan
@mob-flutter-engineer + @mob-state-engineer
@dat-db-engineer + @dat-cache-engineer
```

Each in their own worktree branch. Lead merges.

## Verification rule

Every gate pass requires `@gtw-gatekeeper` with:
- Fresh context (not the implementer's session)
- Adversarial stance
- Pasted mechanical evidence against the gate criteria
- Single PASS/BLOCK verdict

## Escalation

Blocked at a gate? `@gtw-conflict-resolver` → `@brd-arbiter` → `@brd-ceo`