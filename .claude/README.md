# 🏛️ SOFI AI — Autonomous AI Software Enterprise (v6 · "The Company of Rooms")

A complete, runnable scaffold of an AI software enterprise organized as **15 self-contained Rooms (غرف)**, wired together by one **Nexus**, given memory by a **Brain**, and governed by a **Constitution**. **105 agents** run the work through **9 gates**, and **every delegation is a 4-part RCCF Work Order** (Role · Context · Command · Format) so each job runs at the cheapest setting that still clears the quality bar.

> Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨

Law of the land: [`company/CONSTITUTION.md`](../company/CONSTITUTION.md) (7 Teachings + articles `00–10`). One source of truth for routing: [`company/nexus/routing.yaml`](../company/nexus/routing.yaml).

---

## 📂 The Layout

```
Lorka/
├── CLAUDE.md                     ← auto-context boot map (v6)
├── MEMORY.md                     ← routing map — "where do I find X?" (pointers only)
├── company/                      ← THE ENTERPRISE
│   ├── CONSTITUTION.md           supreme law — 7 Teachings + 8 articles, binding
│   ├── ORG.md                    org chart: 15 rooms · 105 agents (human mirror of the registry)
│   ├── RUNBOOK.md                ← how a project is driven, gate by gate
│   ├── BLUEPRINT.md              the design record (why the shape is the shape)
│   ├── constitution/             the articles — 00-operating-system … 10-lifecycle-gates
│   ├── nexus/                    THE CONNECTING LAYER
│   │   ├── NEXUS.md              how rooms talk: bus, Leads-as-gateways, escalation
│   │   ├── registry.yaml         machine index: rooms → agents → skills → tools
│   │   ├── routing.yaml          economic grid: ladder, per-agent routes, effort_scaling
│   │   ├── gates.yaml            9 gates machine-readable: owner, entry, exit bar, artifacts
│   │   └── bus/                  ticket-schema.md · escalation.md
│   ├── rooms/<NN-room>/          15 self-contained rooms
│   │   ├── CHARTER.md            mission · members · gate ownership · interfaces · bar
│   │   ├── agents/<id>.md        full spec per agent (persona + Operating Prompt)
│   │   ├── skills/               room-owned skill docs
│   │   ├── playbooks/            step-by-step procedures
│   │   └── tools/                room scripts (+ README)
│   ├── brain/                    memory architecture — BRAIN.md · templates/ · org/
│   ├── os/                       executable layer — bin/sofi · sofi_tools/ · agents/ · GOVERNANCE.md
│   ├── superpowers/              vetted external power-ups (+ vendored cybersecurity-skills)
│   └── research/PATTERNS.md      GitHub research synthesis — the evidence base
├── .claude/                      ← YOU ARE HERE (how the harness runs the company)
│   ├── agents/                   105 spawnable subagents, one file per <roomcode>-<role>
│   ├── skills/                   13 /sofi-* skills (boot · gate · handoff · delegate · team …)
│   ├── hooks/                    4 lifecycle hooks (security · session-start · checkpoint · breadcrumb)
│   ├── README.md · USER_GUIDE.md · COMMANDS.md   ← client docs
│   └── settings.json             hook + harness wiring
└── projects/<PRJ-XXXX>/          ← per-project brain + code (each its own git repo)
    └── _context/                 STATE · CONTEXT · DECISIONS · HANDOFFS · LESSONS
```

**Rooms replace tiers.** Each room is a self-contained department with its own charter, agents, skills, playbooks and tools, and each **room's Lead is its sole gateway** (Room Isolation Law): specialist → own Lead → target room's Lead → specialist, findings forwarded verbatim. Only the boardroom and the gateway room address any Lead directly.

## 🏢 The 15 Rooms

| # | code | room | gates | mission |
|---|------|------|-------|---------|
| 00 | `brd` | boardroom · القيادة | all | CEO orchestrates & routes (never writes code); CPO/CTO/CQO accountable per gate span; CSO holds the security veto; arbiter settles disputes |
| 01 | `str` | strategy | 0–1 | problem statement · requirements · market · roadmap · risk · monetization |
| 02 | `res` | research | 1 | evidence-grounded personas · the Journey Map (the Design Truth) · web scouting · fact-checking |
| 03 | `dsn` | design | 2 | prototype spec · IA/flows · design system · content · taste dials · motion — WCAG 2.2 AA wins over any dial |
| 04 | `arc` | architecture | 3 | stack · normalized schema · frozen API contract · integrations · infra · 4-pillar spec review |
| 05 | `bck` | backend | 4 | API · domain · Blade · queue · integration engineering + fresh-context code review |
| 06 | `fnt` | frontend | 4 | Vue3/React · CSS taste · micro-interactions · a11y-in-code · performance + review |
| 07 | `mob` | mobile | 4 | Flutter/Bloc clean architecture · platform channels · perf profiling · store releases |
| 08 | `dat` | data | 3–4 | reversible migrations · cache · analytics · ML · ETL · PII privacy |
| 09 | `sec` | security | 3+5 · veto | STRIDE · appsec review · pentest · authn/crypto · secrets · compliance · incident |
| 10 | `qa` | quality | 5 | ONE aggregated PASS/BLOCK verdict · ≥90% coverage · perf budgets · design-fidelity audit |
| 11 | `ops` | devops | 6–7 | CI/CD · environments/IaC · Blue/Green + tested rollback · domains & tunnels · cost |
| 12 | `obs` | observability | 8 | SLI/SLO · instrumentation · alerting · incident command · journey insights → Gate-1 re-open |
| 13 | `knw` | knowledge | cross | the librarian room — owns MEMORY.md · brain hygiene · LESSONS dreaming · docs · ADR history · retrieval |
| 14 | `gtw` | gateway | cross | the Nexus operators — Work-Order dispatch · cost routing · fresh-context gate checks · oracle desk · conflict resolution · budget |

## 🔮 Routing — the economic grid

Always pick the cheapest tier that clears the bar; escalate on evidence only. Single source: `company/nexus/routing.yaml`.

`🟢 mechanical (haiku)` → `🔵 workhorse (sonnet)` → `🔮 gatekeeper (model: inherit — the session's frontier model)` → `🟣 deep (opus, last resort)`

Mechanical is the first line (~80% of routine ops); the gatekeeper tier is reserved for cross-layer sweeps, fresh-context gate checks, and the `/sofi-spec-review` hard gate; deep is a last resort for repo-wide debugging and is forbidden for routine code-writing.

## 📖 Client docs
- **[USER_GUIDE.md](USER_GUIDE.md)** — how to ask the team, the request format, the skills, best practices.
- **[COMMANDS.md](COMMANDS.md)** — the quick cheat-sheet.

## 🚀 How to Run

1. **Boot the CEO.** In Claude Code, spawn the `brd-ceo` agent (Magnus Holt), or run `/sofi-boot` to orient on the active project.
2. **Give it an idea.** e.g. *"New project: internal warehouse inventory tool. Start onboarding."*
3. **SOFI executes** the onboarding sequence → the CEO assigns the next `PRJ-XXXX`, scaffolds the brain, and routes the work across the rooms through the 9 gates.
4. **Delegate the disciplined way** with `/sofi-delegate <agent> "<task>"` — it builds a paste-ready 4-part RCCF Work Order. Drive the whole lifecycle from **[`company/RUNBOOK.md`](../company/RUNBOOK.md)**.

## 🧭 Read in This Order

1. `company/CONSTITUTION.md` — the supreme law (7 Teachings + articles).
2. `company/constitution/10-lifecycle-gates.md` — how work flows (Gate 0→8).
3. `company/nexus/routing.yaml` — how each job is costed.
4. `company/ORG.md` — who does what (15 rooms · 105 agents).
5. `company/nexus/NEXUS.md` — how the rooms connect (bus · Leads · escalation).
6. `company/RUNBOOK.md` — how a project is driven, gate by gate.

## 🧱 Stack Defaults

Backend **Laravel/PHP** · Web **Blade + Vue 3 + Tailwind** · Mobile **Flutter/Bloc** · CI/CD **Harness** · Observability **Prometheus/Grafana/Sentry**. Swap in any agent's frontmatter.

---

*15 rooms · 105 agents · 1 Nexus · 1 Brain · 1 Constitution · 9 gates. `sofi doctor` enforces 105 ↔ 105 parity between `company/rooms/*/agents/` and `.claude/agents/`. Status: ✅ live.*
