---
name: sofi-team
description: Show the SOFI roster (30 agents across 5 tiers + CEO) and pick the right agent for a task — its tier, gate, persona, route (model·effort·caveman), and the exact spawn command. Use to decide who should do a piece of work or to understand the org. Triggers — "who does X", "which agent", "the team", "roster", "who should build/test/design/deploy this", "delegate to".
---

# /sofi-team — who owns this, and how to spawn them

SOFI AI = **30 agents = 29 specialists across 5 tiers + 1 CEO**, a 9-gate lifecycle. Full roster:
`engine/ROSTER.md`. Specs: `engine/agents/**`. Spawnable subagents: `.claude/agents/sofi-*.md`.
Once you've picked the agent below, build its spawn brief with **`/sofi-delegate <key> "<task>"`** (doctrine: `engine/protocols/01-delegation-rccf.md`).

## Map task → agent (by gate)

| Need | Gate | Agent (spawn name) | Tier · Route |
|------|:--:|--------------------|--------------|
| Frame the idea, scope, success metrics | 0 | `sofi-chief-product-strategist` | T0 · 🟣 high |
| Personas / user pain | 1 | `sofi-ux-researcher` | T0 · 🟣 high |
| Journey Map (Design Truth) | 1 | `sofi-journey-architect` | T0 · 🟣 high |
| Hi-fi prototype spec + component library | 2 | `sofi-ui-ux-designer` | T0 · 🔵 med |
| UX copy / microcopy / error strings | 2 | `sofi-content-strategist` | T0 · 🟢 low |
| Tech stack + component diagram | 3 | `sofi-principal-system-architect` | T1 · 🟣 high |
| DB schema + reversible migrations | 3 | `sofi-data-schema-engineer` | T1 · 🔵 high |
| OpenAPI/GraphQL contract + webhooks | 3 | `sofi-api-integration-specialist` | T1 · 🔵 med |
| Threat model, authz, encryption, PII | 3 | `sofi-security-compliance-architect` | T1 · 🟣 **max** |
| Drive backend build / review PRs | 4 | `sofi-backend-blade-engineer` | T2 · 🔵 high |
| Laravel controllers/services/resources | 4 | `sofi-backend-blade-engineer` | T2 · 🔵 med |
| Query/index/cache optimization | 4 | `sofi-database-engineer` | T2 · 🔵 high |
| Queues, jobs, websockets, events | 4 | `sofi-api-engineer` | T2 · 🔵 med |
| Drive web build / audit vs prototype | 4 | `sofi-frontend-react-engineer` | T2 · 🔵 high |
| Blade layouts/components/pages | 4 | `sofi-backend-blade-engineer` | T2 · 🔵 med |
| Tailwind styling + WCAG 2.2 AA | 4 | `sofi-frontend-react-engineer` | T2 · 🔵 med |
| Vue 3 + TS interactivity, Pinia, Axios | 4 | `sofi-frontend-react-engineer` | T2 · 🔵 med |
| Drive Flutter build / audit screens | 4 | `sofi-mobile-engineer` | T2 · 🔵 high |
| Flutter clean architecture + DI | 4 | `sofi-mobile-engineer` | T2 · 🔵 med |
| Bloc/Cubit state | 4 | `sofi-mobile-engineer` | T2 · 🔵 med |
| Flutter jank/memory/native perf | 4 | `sofi-mobile-engineer` | T2 · 🔵 high |
| Run the quality gate (gatekeeper) | 5 | `sofi-qa-sre-lead` | T3 · 🔵 high |
| Automated unit/integration/E2E >90% | 5 | `sofi-automated-testing-engineer` | T3 · 🔵 med |
| Exploratory / persona edge-case QA | 5 | `sofi-manual-exploratory-tester` | T3 · 🟢 low |
| Load test + Lighthouse/CWV budget | 5 | `sofi-performance-load-analyst` | T3 · 🔵 med |
| Deploy staging → prod, rollback, infra/IaC | 6–7 | `sofi-devops-cloud-lead` | T4 · 🔵 high |
| CI/CD pipeline, Blue/Green | 6–7 | `sofi-cicd-pipeline-engineer` | T4 · 🔵 med |
| Metrics/logs/traces, SLO, alerts | 8 | `sofi-observability-sre` | T4 · 🔵 med |
| Orchestrate end-to-end / arbitrate | all | `sofi-ceo` | Exec · 🟣 **max** |

Legend — 🟣 Opus (deep) · 🔵 Sonnet (workhorse) · 🟢 Haiku (mechanical).

## How to spawn — always RCCF
Never spawn a bare task. Hand the agent a **4-part RCCF block** — 🎭 Role · 📂 Context · 🎯 Command · 📐 Format:
```
🎭 Role     <persona> — <role> (Tier n · squad). Route: <model · effort · caveman> (routing.yaml).
📂 Context  PRJ-XXXX · Gate n. Read brain (STATE/CONTEXT/HANDOFFS). Frozen: <artifact §section>.
🎯 Command  <verb + object>. in-bounds → <parts>. out-of-bounds → <don't touch>. success → <metric>.
📐 Format   <deliverable + paths> · standards · gate-bar <pass condition> · handoff → <next>.
```
Let **`/sofi-delegate <key> "<task>"`** assemble it for you (it reads route + brain + spec). Each agent's
`.claude/agents/sofi-*.md` is structured the same way (Role · Context · Command · Format) over its
Operating Contract (gate, consume, produce, bar, handoff, escalate) — read it before delegating.

## Rules
- Pick the **cheapest** model/effort/caveman that clears the bar; log the route in thinking (`engine/routing/routing.yaml`).
- Respect gate order — don't spawn a Gate-4 dev before Gate-3 artifacts are frozen.
- SOFI subagents refuse `SendMessage` resumes ("no user authority") — spawn a **fresh** `Agent()` for new work.
- Escalate a blocked ticket up-chain: `sofi escalate <PRJ> <ID> <to> "<reason>"` (CEO arbitrates).
