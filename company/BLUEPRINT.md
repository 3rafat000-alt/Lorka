# SOFI v6 — "The Company of Rooms" · Architecture Blueprint

> **SOFI AI v6** — autonomous AI software enterprise, rebuilt from scratch inside this repo.
> Doctrine unchanged and eternal: **Design is Truth · few token do trick · big brain small mouth.** 🪨
> This file is the design record. The Constitution (`company/CONSTITUTION.md`) is the law; this explains the shape.

## 1. The idea

SOFI v6 organizes the enterprise as **15 independent Rooms (غرف)** — each a self-contained department with its own charter, agents, skills, playbooks, and tools — connected by one **Nexus** (registry · routing · gates · bus). A **Brain** gives memory (org-level + per-project). A **Constitution** gives law (7 teachings + grounding, verification, reflection, token economy, git, security, research). Work flows through **9 gates** and every delegation is a 4-part **RCCF Work Order**. The company is deliberately **token-miserly**: mechanical-model-first routing, Python-locates-model-judges, progressive disclosure, structured returns, hard budgets with circuit breakers.

**105 agents.** v5's 30 grew into 15 rooms; every v5 persona kept their job (mapped below); 75 new colleagues joined.

## 2. Directory layout (physical truth)

```
Lorka/
├── CLAUDE.md                    boot map (v6)
├── MEMORY.md                    routing map — pointers only
├── company/
│   ├── CONSTITUTION.md          supreme law — 7 teachings + 8 articles, binding
│   ├── ORG.md                   org chart: 15 rooms · 105 agents (mermaid + tables)
│   ├── RUNBOOK.md               drive a project gate-by-gate
│   ├── BLUEPRINT.md             this file
│   ├── constitution/            the laws (00-10, one file each)
│   ├── nexus/                   THE CONNECTING LAYER
│   │   ├── NEXUS.md             how rooms talk: bus, leads-as-gateways, escalation
│   │   ├── registry.yaml        machine index: rooms → agents → skills → tools
│   │   ├── routing.yaml         economic grid: ladder, per-agent routes, effort_scaling
│   │   ├── gates.yaml           9 gates machine-readable: owner, entry, exit bar, artifacts
│   │   └── bus/                 ticket-schema.md · escalation.md
│   ├── brain/
│   │   ├── BRAIN.md             memory architecture (org vs project vs session)
│   │   ├── templates/           STATE/CONTEXT/DECISIONS/HANDOFFS/LESSONS/FOUNDATIONS
│   │   └── org/                 org-level memory (DECISIONS, EVOLUTION, LESSONS, archive-v5/)
│   ├── rooms/<NN-room>/         15 self-contained rooms
│   │   ├── CHARTER.md           mission, members, gates, interfaces, bar
│   │   ├── agents/<id>.md       full spec per agent
│   │   ├── skills/              room-owned skill docs
│   │   ├── playbooks/           step-by-step procedures
│   │   └── tools/               room scripts (+ README)
│   ├── os/                      executable layer (ported from v5, adapted)
│   │   ├── bin/sofi             dispatcher (+ rooms/registry/budget subcommands)
│   │   ├── sofi_tools/          python lib: brain·tickets·routing·gates·guard·runlog·gitops·domain·tunnel
│   │   ├── agents/              per-role toolkits (scanners: feature_scan, sofi_scan, uiux_pipeline…)
│   │   ├── ooda/                autonomous OODA engine
│   │   ├── oracle/ autopilot/ caveman/ server-plane/   operational docs+configs
│   │   └── GOVERNANCE.md        tooling law (10 rules)
│   ├── superpowers/             vendored powers (cybersecurity-skills 817 + SUPERPOWERS.md)
│   ├── research/                PATTERNS.md — GitHub research synthesis (evidence base)
│   └── templates/               artifact templates (adr, openapi, journey-map, …)
├── .claude/
│   ├── agents/                  105 spawnable subagents  <roomcode>-<role>.md
│   ├── skills/                  13 sofi-* skills (rebuilt for v6 paths)
│   ├── hooks/                   4 lifecycle hooks (kept, paths updated)
│   └── settings.json            unchanged wiring
├── dashboard/                   observability console (paths updated, registry-driven)
└── projects/<PRJ-XXXX>/         per-project brain + code (contract unchanged)
```

## 3. Naming & identity

- Brand stays **SOFI** (CLI `sofi`, skills `/sofi-*`, commit trailer `SOFI:`) — muscle memory is capital.
- Agent id = `<roomcode>-<role>` (e.g. `sec-pentester`, `bck-api-engineer`). Room codes:
  `brd str res dsn arc bck fnt mob dat sec qa ops obs knw gtw`.
- Spawnable file `.claude/agents/<id>.md` ↔ spec file `company/rooms/<NN-room>/agents/<id>.md` — **dual-file parity, enforced by `sofi doctor` (105 ↔ 105)**.

## 4. The 15 rooms · 105 agents (frozen roster)

Model ladder (routing.yaml): 🟢 mechanical `haiku` · 🔵 workhorse `sonnet` · 🔮 gatekeeper (`model: inherit` in frontmatter, noted "gatekeeper-tier" in body) · 🟣 deep `opus`.
Every room's **Lead is its sole gateway** (Room Isolation Law). ★ = persona inherited from v5.

### 00-boardroom (brd) — القيادة · 7 — all gates
| id | role | model | persona |
|---|---|---|---|
| brd-ceo | CEO / Principal Orchestrator — owns lifecycle, routes, arbitrates; never writes code | 🔮 | ★ Magnus Holt |
| brd-chief-of-staff | raw intent → Work Orders; keeps org state current | 🔵 | new |
| brd-cpo | Chief Product Officer — accountable gates 0–2 | 🔮 | ★ Isabelle Duarte (was T0 advisor) |
| brd-cto | Chief Technology Officer — accountable gates 3–4 | 🔮 | ★ Ingrid Voss (was T1 advisor) |
| brd-cso | Chief Security Officer — company-wide security veto | 🔮 | new |
| brd-cqo | Chief Quality Officer — accountable gate 5 verdicts | 🔮 | ★ Otieno Wambua (was T3 advisor) |
| brd-arbiter | cross-room dispute arbitration (Design-vs-Dev); final below CEO | 🔮 | new |

### 01-strategy (str) · 7 — gates 0–1
| id | role | model | persona |
|---|---|---|---|
| str-lead | Room Lead / gateway | 🔮 | ★ Dr. Amara Okafor |
| str-product-strategist | problem statement, scope boundary, 5 deep questions | 🔮 | new |
| str-business-analyst | requirements, success metrics, acceptance criteria | 🔵 | new |
| str-market-analyst | market sizing, positioning | 🔵 | new |
| str-roadmap-planner | milestones, backlog, two-track sizing | 🔵 | new |
| str-risk-analyst | business risk register, kill criteria | 🔵 | new |
| str-monetization-strategist | pricing, business model | 🔵 | new |

### 02-research (res) · 7 — gate 1
| id | role | model | persona |
|---|---|---|---|
| res-lead | Room Lead / gateway | 🔵 | ★ Hiroshi Tanaka |
| res-ux-researcher | evidence-grounded personas, pain/gain map | 🔵 | new |
| res-journey-architect | Customer Journey Map (Mermaid) — the Design Truth | 🔮 | ★ Sofia Marchetti |
| res-web-scout | search/fetch/verify/cite (holds Web tools) | 🟢 | new |
| res-competitor-analyst | competitor teardowns | 🔵 | new |
| res-data-researcher | quantitative evidence, surveys, telemetry mining | 🔵 | new |
| res-fact-checker | adversarial claim verification (G1–G5 enforcer) | 🔵 | new |

### 03-design (dsn) · 8 — gate 2
| id | role | model | persona |
|---|---|---|---|
| dsn-lead | Room Lead / gateway; owns Gate-2 freeze | 🔵 | ★ Daniel "Dan" Kim |
| dsn-ui-designer | textual hi-fi prototype spec, 1:1 journey mapping | 🔵 | new |
| dsn-ux-architect | flows, information architecture, interaction models | 🔵 | new |
| dsn-design-system | tokens, component library | 🔵 | new |
| dsn-content-strategist | UX copy + microcopy as keyed JSON, one voice | 🟢 | ★ Peg O'Sullivan |
| dsn-brand-designer | taste dials (variance/motion/density), anti-generic | 🔵 | new |
| dsn-motion-designer | motion & micro-interaction specs | 🟢 | new |
| dsn-a11y-specialist | WCAG 2.2 AA matrix (always wins over any dial) | 🔵 | new |

### 04-architecture (arc) · 7 — gate 3
| id | role | model | persona |
|---|---|---|---|
| arc-lead | Room Lead / gateway; assembles the frozen Gate-3 bundle | 🔮 | ★ Vikram Rao |
| arc-system-architect | stack, component diagram, screen→component traceability | 🔮 | new |
| arc-data-architect | normalized schema, ER, reversible migrations design | 🔵 | ★ Elena Petrova |
| arc-api-architect | OpenAPI/GraphQL frozen contract, webhook payloads | 🔵 | ★ Marco Blackwood |
| arc-integration-architect | 3rd-party integration plans | 🔵 | new |
| arc-infra-architect | network segmentation, scaling, DR posture | 🔵 | ★ Kenji Watanabe |
| arc-review-architect | 4-pillar spec review, 7 steel rules (SEV-first) | 🔮 | new |

### 05-backend (bck) · 8 — gate 4
| id | role | model | persona |
|---|---|---|---|
| bck-lead | Room Lead / gateway; merges worktrees at gate close | 🔵 | ★ Elif Kaya (was T2 advisor) |
| bck-api-engineer | endpoints per frozen contract (422-JSON law) | 🔵 | ★ Priya Nair |
| bck-domain-engineer | services, business logic, money math | 🔵 | new |
| bck-blade-engineer | Blade layouts/components/pages, all states | 🔵 | ★ Aisha Rahman |
| bck-queue-engineer | idempotent jobs, retry/backoff/DLQ, events, websockets | 🔵 | new |
| bck-integration-engineer | 3rd-party wiring per integration plan | 🔵 | new |
| bck-refactoring-surgeon | behavior-preserving debt paydown | 🔵 | new |
| bck-code-reviewer | fresh-context backend diff review (V2) | 🔵 | new |

### 06-frontend (fnt) · 8 — gate 4
| id | role | model | persona |
|---|---|---|---|
| fnt-lead | Room Lead / gateway | 🔵 | ★ Grace Achieng |
| fnt-vue-engineer | Vue3 components + state | 🔵 | new |
| fnt-react-engineer | typed React components + service layer per contract | 🔵 | new |
| fnt-css-artisan | Tailwind, responsive, taste dials applied | 🔵 | new |
| fnt-interaction-engineer | micro-interactions, motion implementation | 🔵 | new |
| fnt-a11y-engineer | WCAG 2.2 AA in code | 🔵 | new |
| fnt-performance-engineer | bundles, code-split, CWV | 🔵 | new |
| fnt-code-reviewer | fresh-context frontend diff review (V2) | 🔵 | new |

### 07-mobile (mob) · 6 — gate 4
| id | role | model | persona |
|---|---|---|---|
| mob-lead | Room Lead / gateway | 🔵 | ★ João Silva |
| mob-flutter-engineer | feature-first clean architecture (GetIt DI, DTO mappers) | 🔵 | new |
| mob-state-engineer | Bloc/Cubit + hydrated persistence | 🔵 | new |
| mob-platform-engineer | channels, iOS/Android specifics, typed ApiException law | 🔵 | new |
| mob-perf-profiler | jank/leaks, before-after benchmarks | 🔵 | new |
| mob-release-engineer | store builds, signing, release channels | 🟢 | new |

### 08-data (dat) · 7 — gates 3–4
| id | role | model | persona |
|---|---|---|---|
| dat-lead | Room Lead / gateway | 🔵 | ★ Günther Weber |
| dat-db-engineer | migrations (reversible!), EXPLAIN, indexes, N+1 kills | 🔵 | new |
| dat-cache-engineer | Redis + invalidation design | 🔵 | new |
| dat-analytics-engineer | pipelines, product metrics | 🔵 | new |
| dat-ml-engineer | ML/AI features, model integration | 🔵 | new |
| dat-etl-engineer | imports/exports/syncs | 🔵 | new |
| dat-privacy-officer | PII classification, retention, encryption-at-rest map | 🔵 | new |

### 09-security (sec) · 8 — gates 3+5, veto everywhere
| id | role | model | persona |
|---|---|---|---|
| sec-lead | Room Lead / gateway; deputy to brd-cso | 🔮 | ★ Dr. Ruth Goldberg |
| sec-threat-modeler | STRIDE threat model, pen-test scope | 🔮 | new |
| sec-appsec-engineer | secure code review: injection, authz, IDOR | 🔵 | new |
| sec-pentester | execution-level attacks, reproductions + severity | 🔵 | ★ Sirak Haile |
| sec-authn-engineer | auth/session/crypto design + implementation review | 🔵 | new |
| sec-secrets-warden | keys/env hygiene, secret scans | 🟢 | new |
| sec-compliance-auditor | compliance checklists, regulatory mapping | 🔵 | new |
| sec-incident-responder | security incident runbooks + response | 🔵 | new |

### 10-quality (qa) · 7 — gate 5 (gatekeeper room)
| id | role | model | persona |
|---|---|---|---|
| qa-lead | Room Lead / gateway; aggregates ONE PASS/BLOCK verdict | 🔮 | ★ Barb Jensen |
| qa-test-architect | test strategy, pyramid, pass^k plan for Tier-A | 🔵 | new |
| qa-automation-engineer | unit/integration/E2E, ≥90% coverage or build fails | 🔵 | ★ Kwame Mensah |
| qa-manual-explorer | persona-driven edge probing (empty/huge/offline/locale) | 🔵 | ★ Rosa Giménez |
| qa-perf-analyst | k6/Lighthouse, CWV, TTI<2s budget | 🔵 | ★ Ahmed Farouk |
| qa-regression-warden | suites, flake control, quarantine | 🟢 | new |
| qa-design-auditor | built vs frozen prototype fidelity | 🔵 | new |

### 11-devops (ops) · 7 — gates 6–7
| id | role | model | persona |
|---|---|---|---|
| ops-lead | Room Lead / gateway | 🔵 | ★ Linda Schmidt |
| ops-cicd-engineer | pipeline lint→test→build→scan→deploy | 🔵 | ★ Tomás Herrera |
| ops-cloud-engineer | environments, IaC | 🔵 | new |
| ops-release-manager | Blue/Green + tested rollback (owns the way back) | 🔮 | ★ Camille Dubois |
| ops-domain-warden | local domains + public tunnels (bounded, seed-data-only) | 🟢 | new |
| ops-migration-runner | deploy-time data ops with rollback rehearsal | 🔵 | new |
| ops-cost-optimizer | infra economics | 🟢 | new |

### 12-observability (obs) · 6 — gate 8
| id | role | model | persona |
|---|---|---|---|
| obs-lead | Room Lead / gateway | 🔵 | ★ Naomi Brooks |
| obs-sre | SLI/SLO, error budgets | 🔵 | new |
| obs-monitoring-engineer | metrics/logs/traces instrumentation | 🔵 | new |
| obs-alerting-engineer | alerts + runbooks | 🟢 | new |
| obs-incident-commander | triage → rollback decision → postmortem | 🔮 | new |
| obs-insights-analyst | journey drop-offs → formal Gate-1 re-open | 🔵 | new |

### 13-knowledge (knw) · 6 — cross-gate
| id | role | model | persona |
|---|---|---|---|
| knw-lead | Librarian / gateway; owns MEMORY.md routing map | 🔵 | new |
| knw-memory-curator | brain hygiene, caveman-compress, frontmatter | 🟢 | new |
| knw-reflector | LESSONS distillation (scheduled dreaming, never per-turn) | 🔵 | new |
| knw-doc-writer | READMEs, guides | 🟢 | new |
| knw-historian | DECISIONS/ADR log keeper | 🟢 | new |
| knw-brain-query | retrieval: brain-query, grep-first search | 🟢 | new |

### 14-gateway (gtw) — the Nexus operators · 6 — cross-gate
| id | role | model | persona |
|---|---|---|---|
| gtw-dispatcher | Work Order → room routing; runs the bus | 🔵 | ★ Astrid Lindqvist (was T4 advisor) |
| gtw-router | model/cost routing per task (economic grid) | 🟢 | new |
| gtw-gatekeeper | fresh-context adversarial gate checks (NEVER the implementer) | 🔮 | new |
| gtw-external-reviewer | oracle desk (Gemini), sanitized, digest-ingesting | 🔵 | new |
| gtw-conflict-resolver | cross-room deadlocks → brd-arbiter | 🔵 | new |
| gtw-budget-warden | token budgets, circuit breakers, waste audit | 🟢 | new |

**TOTAL = 7+7+7+8+7+8+8+6+7+8+7+7+6+6+6 = 105.**

## 5. The Nexus — how everything connects

1. **Registry** (`nexus/registry.yaml`) — one machine-readable index: room → agents (id, file, spawnable, route, gate) → skills → tools. Everything discoverable in one read. `sofi registry` queries it; `sofi doctor` checks parity against the filesystem.
2. **Bus** — tickets in the project brain's `HANDOFFS.md` (schema `bus/ticket-schema.md`). **Room Isolation Law:** specialist → own Lead → target room's Lead → specialist. Leads forward findings **verbatim** (no translation tax). Boardroom + gateway room may address any Lead.
3. **Routing** (`nexus/routing.yaml`) — single source: ladder (mechanical→workhorse→gatekeeper→deep), per-agent routes `routes.<id> = model·effort·caveman·budget·gate`, `effort_scaling` (trivial-fix·single-role·cross-room·audit-sweep·arbitration), `priority_override`, safety overrides.
4. **Gates** (`nexus/gates.yaml`) — 9 gates with owner room, entry criteria, exit bar, artifacts. Advancement only via `gtw-gatekeeper` fresh-context adversarial check (V2) + mechanical evidence (V1, `sofi gate-check`).
5. **Escalation chain** — specialist → room lead → gtw-conflict-resolver → brd-arbiter → brd-ceo. Circuit breaker at 3 failed attempts (crash-dump JSON + escalation ticket). Security: brd-cso veto is absolute below the CEO.

## 6. What v6 fixes (from v5 known debts)

1. routing hardcodes lag the yaml → **routing.yaml is the only source**, gatekeeper tier reachable by CRITICAL bump.
2. doctor parity 30↔30 → **105↔105** (rooms/*/agents ↔ .claude/agents).
3. `paths.repo_root()` sentinel `engine/` → **`company/`** (accepts either during transition).
4. `tickets.ROLE_TIER` hardcode → **ROLE_ROOM loaded from registry.yaml** (fail-open on unknown).
5. `gates.GATE_ROLES` hardcode → **loaded from gates.yaml**.
6. dashboard 30-agent hardcode → **registry-driven**.
7. Tier-advisor bottleneck → room Leads + a dedicated gateway room + boardroom accountability (CPO/CTO/CQO per gate span).

## 7. Templates (exact, binding for builders)

### 7a. Spawnable subagent `.claude/agents/<id>.md`
```markdown
---
name: <id>
description: Room <NN-name> — <Role>. Gate <g>. <mission one-liner>. Use when <trigger phrases>.
tools:            # workers: explicit minimal grants; boardroom/leads may omit (inherit all)
  Read: true
  Grep: true
  Glob: true
model: haiku|sonnet|opus|inherit   # inherit = gatekeeper tier (session model)
---
# 🎭 <Persona> — <Role> · Room <NN-name> · Gate <g>

Spawn me with a 4-part RCCF Work Order (company/constitution/01-work-order.md).
Route: <model · effort · caveman> (nexus/routing.yaml: <id>). Spec: company/rooms/<room>/agents/<id>.md.
Chatter caveman <level>; code/security always normal prose.

## 🎭 Role — who I am
<identity, what I do / do NOT do>

## 📂 Context — read before acting
- **Law:** company/CONSTITUTION.md · contract: constitution/00-operating-system.md · brief shape: constitution/01-work-order.md
- **Room:** company/rooms/<NN-room>/CHARTER.md (my interfaces) · playbooks I follow
- **Brain:** projects/<PRJ>/_context/STATE.md (branch·head_sha) · HANDOFFS.md (my ticket) · CONTEXT.md
- **Consume:** <frozen upstream artifact(s)>. Not frozen → reject upward.

## 🎯 Command — my scope
- **in-bounds:** <bounded production list>
- **out-of-bounds:** <explicit exclusions → owning agent for each>
- **success:** <success_metric, one line>

## 📐 Format — deliverable
- **Produce:** <artifacts at exact paths>
- **Gate-bar:** <objective checklist>
- **Evidence:** every 'done' carries cmd+exit code | file:line | diff/SHA (else gate-check rejects)
- **Standards:** <code standard normal prose; chatter caveman level>

## ↪ Handoff & escalation
- **Handoff:** <inbound via lead → me → outbound via lead>. Close with /sofi-handoff.
- **Escalate when:** <trigger> — `sofi escalate <PRJ> <TKT> <to> "<reason>"` after 3 failed attempts (circuit breaker).
- **Doctrine:** Design-is-Truth · isolate by PROJECT_ID · cheapest route that clears the bar (log it) · big-brain-small-mouth.
```

### 7b. Room spec `company/rooms/<NN-room>/agents/<id>.md`
```markdown
---
agent: <id>
persona_name: <Full Name>
title: <Role Title>
room: <NN-room>
reports_to: <room lead id | brd-ceo for leads>
gate: <n or range>
experience: "<years — one-line career>"
route: { model: <tier-name>, effort: <e>, caveman: <c>, budget: "<band>" }
success_metric: "<one gradeable sentence>"
---
# <emoji> <Persona> — <Title>
> <tagline>

## Who they are            (nationality, age, philosophy, Hobbies-as-metaphor ×2, Tell, Motto)
## How their mind works    (method bullets + Smells: anti-patterns)
## Mission                 (one paragraph, full scope)
## Mastery                 (· separated skills)
## How they work           (workflow; frozen artifacts consumed; caveman/code standard)
## Activates · Consumes · Produces   (- **Gate N.** Consumes: … Produces: …)
## Operating Prompt (paste to run)   (> imperative runnable block)
## Handoff                 (Inbound → same-room colleagues → Outbound via lead)
## Definition of Done      (· separated exit checklist)
## Non-negotiables         (hard rules)
```

### 7c. Room `CHARTER.md`
Mission · Members table (id, role, route) · Gate ownership · Interfaces (consumes-from / produces-to, by room) · Room bar (what the Lead blocks on) · Playbook index · Tools index · Escalation path.

## 8. What migrated where (v5 → v6)

| v5 | v6 |
|---|---|
| engine/tooling | company/os (lib `sofi_tools`, dispatcher `bin/sofi`, per-role toolkits `agents/`) |
| engine/ooda | company/os/ooda |
| engine/superpowers (+SUPERPOWERS.md) | company/superpowers |
| engine/templates | company/templates |
| engine/bin/new-project.sh | company/os/bin/new-project.sh |
| engine/server-plane | company/os/server-plane |
| engine/{DECISIONS,HANDOFFS,EVOLUTION,TEAM_STATUS,PERSONAS}.md | company/brain/org/ |
| engine/AUTOPILOT*.md | company/os/autopilot/ |
| engine/GEMINI_*.md + TESTING_TEACHING_VII.md | company/os/oracle/ |
| engine/caveman | company/os/caveman |
| engine/routing/gemini-audit-dispatch.yaml | company/nexus/ |
| engine/{DOCTRINE,ROSTER,RUNBOOK,AGENT_BRIEFING}.md · protocols/ · agents/ · routing.yaml · gates.md · .claude/SOFI_SYSTEM_PROMPT.md | company/brain/org/archive-v5/ (verbatim law preserved; reborn as constitution/, nexus/, rooms/) |
| .claude/agents/sofi-*.md (30) | .claude/agents/<id>.md (105) |
| .claude/skills/sofi-* (13) | same names, rebuilt for v6 paths |
```
