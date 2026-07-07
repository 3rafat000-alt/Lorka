---
name: sofi-team
description: Show the SOFI roster (15 rooms · 105 agents) and pick the right agent for a task — its room, gate, persona, route (model·effort·caveman), and the exact spawn id. Use to decide who should do a piece of work or to understand the org. Triggers — "who does X", "which agent", "the team", "roster", "who should build/test/design/deploy this", "delegate to".
---

# /sofi-team — who owns this, and how to spawn them

SOFI AI = **15 rooms (غرف) · 105 agents** connected by one **Nexus**, a 9-gate lifecycle.
Machine index of every room → agent → skill → tool: `company/nexus/registry.yaml`
(query it with `sofi registry`). Org chart + personas: `company/ORG.md`. Full specs:
`company/rooms/<NN-room>/agents/<id>.md`. Spawnable subagents: `.claude/agents/<id>.md`.
Once you've picked the agent, build its Work Order with **`/sofi-delegate <id> "<task>"`**
(RCCF v3 · `company/constitution/01-work-order.md`).

> **Agent id = `<roomcode>-<role>`** (e.g. `bck-blade-engineer`, `sec-pentester`).
> Room codes: `brd str res dsn arc bck fnt mob dat sec qa ops obs knw gtw`.
> Model ladder — 🟢 mechanical `haiku` · 🔵 workhorse `sonnet` · 🔮 gatekeeper (session model, `inherit`) · 🟣 deep `opus`.

## The 15 rooms (code · name · gate span · Lead-gateway)

| Room | Name | Gates | Lead (sole gateway) |
|------|------|:--:|---------------------|
| `brd` | Boardroom · القيادة | all | `brd-ceo` (never writes code) |
| `str` | Strategy | 0–1 | `str-lead` |
| `res` | Research | 1 | `res-lead` |
| `dsn` | Design | 2 | `dsn-lead` (owns Gate-2 freeze) |
| `arc` | Architecture | 3 | `arc-lead` |
| `bck` | Backend | 4 | `bck-lead` |
| `fnt` | Frontend | 4 | `fnt-lead` |
| `mob` | Mobile | 4 | `mob-lead` |
| `dat` | Data | 3–4 | `dat-lead` |
| `sec` | Security | 3+5, veto all | `sec-lead` (deputy to `brd-cso`) |
| `qa` | Quality (gatekeeper room) | 5 | `qa-lead` (one PASS/BLOCK verdict) |
| `ops` | DevOps | 6–7 | `ops-lead` |
| `obs` | Observability | 8 | `obs-lead` |
| `knw` | Knowledge | cross-gate | `knw-lead` (librarian) |
| `gtw` | Gateway · Nexus operators | cross-gate | `gtw-dispatcher` (runs the bus) |

## Map task → agent (by gate)

| Need | Gate | Agent (spawn id) | Route |
|------|:--:|------------------|-------|
| Frame the idea, scope, 5 deep questions | 0 | `str-product-strategist` | 🔮 high |
| Requirements, success metrics, acceptance | 0–1 | `str-business-analyst` | 🔵 med |
| Personas / user pain-gain map | 1 | `res-ux-researcher` | 🔵 med |
| Journey Map (the Design Truth) | 1 | `res-journey-architect` | 🔮 high |
| Search / fetch / verify / cite (holds Web) | 1 | `res-web-scout` | 🟢 low |
| Adversarial claim verification | 1–5 | `res-fact-checker` | 🔵 med |
| Hi-fi prototype spec, 1:1 journey mapping | 2 | `dsn-ui-designer` | 🔵 med |
| Flows / IA / interaction models | 2 | `dsn-ux-architect` | 🔵 med |
| Design tokens + component library | 2 | `dsn-design-system` | 🔵 med |
| UX copy / microcopy (keyed JSON) | 2 | `dsn-content-strategist` | 🟢 low |
| Taste dials (variance/motion/density) | 2 | `dsn-brand-designer` | 🔵 med |
| WCAG 2.2 AA matrix (wins over any dial) | 2 | `dsn-a11y-specialist` | 🔵 med |
| Tech stack + component diagram + traceability | 3 | `arc-system-architect` | 🔮 high |
| Normalized schema + reversible migration design | 3 | `arc-data-architect` | 🔵 high |
| OpenAPI/GraphQL frozen contract + webhooks | 3 | `arc-api-architect` | 🔵 med |
| 3rd-party integration plan | 3 | `arc-integration-architect` | 🔵 med |
| Network segmentation, scaling, DR posture | 3 | `arc-infra-architect` | 🔵 high |
| 4-pillar spec review, 7 steel rules (SEV-first) | 3 | `arc-review-architect` | 🔮 high |
| STRIDE threat model + pentest scope | 3 | `sec-threat-modeler` | 🔮 high |
| Auth/session/crypto design + review | 3 | `sec-authn-engineer` | 🔵 med |
| PII classification, retention, encryption map | 3 | `dat-privacy-officer` | 🔵 med |
| API endpoints per frozen contract (422-JSON) | 4 | `bck-api-engineer` | 🔵 med |
| Services, business logic, money math | 4 | `bck-domain-engineer` | 🔵 med |
| Blade layouts/components/pages, all states | 4 | `bck-blade-engineer` | 🔵 med |
| Idempotent jobs, retry/backoff/DLQ, events, WS | 4 | `bck-queue-engineer` | 🔵 med |
| 3rd-party wiring per integration plan | 4 | `bck-integration-engineer` | 🔵 med |
| Vue 3 components + state | 4 | `fnt-vue-engineer` | 🔵 med |
| Typed React components + service layer | 4 | `fnt-react-engineer` | 🔵 med |
| Tailwind, responsive, taste dials applied | 4 | `fnt-css-artisan` | 🔵 med |
| WCAG 2.2 AA in code | 4 | `fnt-a11y-engineer` | 🔵 med |
| Bundles, code-split, CWV | 4 | `fnt-performance-engineer` | 🔵 med |
| Flutter feature-first clean architecture (DI) | 4 | `mob-flutter-engineer` | 🔵 med |
| Bloc/Cubit + hydrated persistence | 4 | `mob-state-engineer` | 🔵 med |
| Migrations (reversible!), EXPLAIN, index, N+1 | 4 | `dat-db-engineer` | 🔵 high |
| Redis cache + invalidation design | 4 | `dat-cache-engineer` | 🔵 med |
| Secure code review: injection, authz, IDOR | 3+5 | `sec-appsec-engineer` | 🔵 med |
| Execution-level attacks + reproductions | 5 | `sec-pentester` | 🔵 med |
| Keys/env hygiene, secret scans | any | `sec-secrets-warden` | 🟢 low |
| Run the quality gate (one PASS/BLOCK verdict) | 5 | `qa-lead` | 🔮 high |
| Test strategy, pyramid, pass^k for Tier-A | 5 | `qa-test-architect` | 🔵 med |
| Unit/integration/E2E ≥90% or build fails | 5 | `qa-automation-engineer` | 🔵 med |
| Persona edge probing (empty/huge/offline/locale) | 5 | `qa-manual-explorer` | 🔵 med |
| k6/Lighthouse, CWV, TTI<2s budget | 5 | `qa-perf-analyst` | 🔵 med |
| Built vs frozen prototype fidelity | 5 | `qa-design-auditor` | 🔵 med |
| Deploy staging → prod, environments, IaC | 6–7 | `ops-lead` / `ops-cloud-engineer` | 🔵 high |
| CI/CD pipeline (lint→test→build→scan→deploy) | 6–7 | `ops-cicd-engineer` | 🔵 med |
| Blue/Green + tested rollback (the way back) | 7 | `ops-release-manager` | 🔮 high |
| Local domains + public tunnels (bounded) | 6–7 | `ops-domain-warden` | 🟢 low |
| SLI/SLO, error budgets | 8 | `obs-sre` | 🔵 med |
| Metrics/logs/traces instrumentation | 8 | `obs-monitoring-engineer` | 🔵 med |
| Triage → rollback decision → postmortem | 8 | `obs-incident-commander` | 🔮 high |
| Journey drop-offs → formal Gate-1 re-open | 8 | `obs-insights-analyst` | 🔵 med |
| Distil lessons from history (scheduled dreaming) | cross | `knw-reflector` | 🔵 med |
| Brain hygiene, caveman-compress, frontmatter | cross | `knw-memory-curator` | 🟢 low |
| Retrieval: brain-query, grep-first search | cross | `knw-brain-query` | 🟢 low |
| Work Order → room routing; run the bus | all | `gtw-dispatcher` | 🔵 med |
| Model/cost routing per task (economic grid) | all | `gtw-router` | 🟢 low |
| Fresh-context adversarial gate check (never impl.) | all | `gtw-gatekeeper` | 🔮 high |
| Oracle desk (external second opinion), sanitized | all | `gtw-external-reviewer` | 🔵 med |
| Token budgets, circuit breakers, waste audit | all | `gtw-budget-warden` | 🟢 low |
| Orchestrate end-to-end / arbitrate | all | `brd-ceo` | 🔮 max |

Not sure? `sofi registry` lists every agent with its route; `sofi route <id>` prints one route line.

## How to spawn — always a 4-part Work Order (RCCF v3)
Never spawn a bare task. Hand the agent a **Work Order** — 🎭 Role · 📂 Context · 🎯 Command · 📐 Format:
```
🎭 Role     <persona> — <role> (Room <NN-name>). Route: <model · effort · caveman> (nexus/routing.yaml: <id>).
📂 Context  PRJ-XXXX · Gate n. Read brain (STATE/CONTEXT/HANDOFFS/LESSONS). Frozen: <artifact §section>.
🎯 Command  <verb + object>. in-bounds → <parts>. out-of-bounds → <don't touch → owning agent>. success → <metric>.
📐 Format   <deliverable + paths> · standards · gate-bar <pass condition> · evidence block · handoff → <next via lead>.
```
Let **`/sofi-delegate <id> "<task>"`** assemble it (it reads route + brain + spec + effort class). Each
`.claude/agents/<id>.md` is structured the same way (Role · Context · Command · Format) over its Operating
Contract (gate · consume · produce · gate-bar · handoff · escalate) — read it before delegating.

## Rules
- Pick the **cheapest** model/effort/caveman that clears the bar; log the route in thinking (`company/nexus/routing.yaml` · Teaching IV · Token Economy).
- Respect gate order — don't spawn a Gate-4 dev before Gate-3 artifacts are frozen (Teaching II).
- **Room Isolation Law:** a specialist reaches its own Lead, not another room directly; only `brd-*` and `gtw-*` address any Lead. Leads forward findings verbatim.
- SOFI subagents refuse `SendMessage` resumes ("no user authority") — spawn a **fresh** `Agent()` for new work.
- Escalate a blocked ticket up-chain: `sofi escalate <PRJ> <ID> <to> "<reason>"` (chain: specialist → Lead → `gtw-conflict-resolver` → `brd-arbiter` → `brd-ceo`; circuit breaker at 3 attempts).
