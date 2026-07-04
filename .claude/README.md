# 🏛️ SOFI AI — Autonomous AI Software Enterprise

A complete, runnable scaffold of a hierarchical AI software enterprise. Every team member is a real agent file with a baked-in **routing tag** (`model · effort · caveman`) so each job runs at the cheapest setting that still clears the quality bar.

> Doctrine: **Design is Truth · Few token do trick · Big brain, small mouth.** 🪨

Constitution: [SOFI_SYSTEM_PROMPT.md](SOFI_SYSTEM_PROMPT.md). One source of truth for routing: `engine/routing/routing.yaml`.

---

## 📂 Project Layout

```
SOFI AI/
├── README.md                     ← you are here
├── SOFI_SYSTEM_PROMPT.md         ← paste as system prompt to boot the CEO agent
├── projects/                     ← LIVE company brains, one per PRJ-ID (empty; ready)
│   └── <PRJ-XXXX>/
│       ├── _context/*             STATE · CONTEXT · DECISIONS · HANDOFFS (per project)
│       └── _scratch/              ephemeral temp scripts (purged at gate exit)
└── engine/
    ├── ROSTER.md                 ← full team index (30 agents + CEO)
    ├── PERSONAS.md               ← the team as humans (names, ages, mottos)
    ├── RUNBOOK.md                ← how the CEO drives a project gate→gate
    ├── protocols/                ← the operating system (6 protocols)
    │   ├── 00-operating-system.md      universal agent contract
    │   ├── context-and-memory.md       the shared brain
    │   ├── research-and-internet.md    search/fetch/verify/cite
    │   ├── thinking-and-work.md        reasoning effort + work loop
    │   ├── handoff-and-interconnection.md  tickets + dependency graph
    │   └── tooling-matrix.md            tools per role
    ├── bin/new-project.sh        ← scaffold a project + brain
    ├── routing/routing.yaml      ← machine-readable model/effort/caveman map
    ├── lifecycle/gates.md        ← the 9-gate binding lifecycle
    ├── governance/governance.md  ← multi-project isolation + prioritization
    ├── caveman/integration.md    ← token-optimization engine
    ├── templates/                ← reusable artifact templates
    ├── tooling/                  ← governed Python layer (library + CLI + per-role tools)
    │   ├── GOVERNANCE.md             the law for scripts
    │   ├── registry.yaml            discovery index
    │   ├── bin/sofi                 the dispatcher
    │   ├── sofi_tools/              shared library
    │   └── agents/<tier>/<role>/    per-role toolkits
    └── agents/
        ├── ceo-sofi.md
        ├── tier-0-strategy/      (5 agents)
        ├── tier-1-architecture/  (4 agents)
        ├── tier-2-development/    (backend / frontend / mobile — 12 agents)
        ├── tier-3-quality/       (4 agents)
        └── tier-4-infrastructure/(4 agents)
```

## 📖 Client docs
- **[USER_GUIDE.md](USER_GUIDE.md)** — how to ask the team, the request format, best practices, every agent.
- **[COMMANDS.md](COMMANDS.md)** — quick cheat-sheet.

## 🚀 How to Run

1. **Boot the CEO.** Paste `SOFI_SYSTEM_PROMPT.md` as the system prompt (or first message) of a new Claude project. In Claude Code, just call the `sofi-ceo` agent.
2. **Give it an idea.** e.g. *"New project: internal warehouse inventory tool. Start onboarding."*
3. **SOFI AI executes** the onboarding sequence → generates the next `PRJ-XXXX`, scaffolds dirs, asks 5 deep questions.
4. **Each agent** is invoked by SOFI AI in gate order. Open any agent file to see its **Operating Prompt** — paste it to run that agent standalone.

## 🧭 Read in This Order

1. `SOFI_SYSTEM_PROMPT.md` — the constitution.
2. `engine/lifecycle/gates.md` — how work flows (Gate 0→8).
3. `engine/routing/routing.yaml` — how each job is costed.
4. `engine/ROSTER.md` — who does what.
5. `engine/tooling/README.md` — the scripts every agent works through.
6. `engine/agents/**` — the team, tier by tier.

## 🧱 Stack Defaults

Backend **Laravel/PHP** · Web **Blade + Vue 3 + Tailwind** · Mobile **Flutter/Bloc** · CI/CD **Harness** · Observability **Prometheus/Grafana/Sentry**. Swap in any agent's frontmatter.

---

*Build order: foundation → Tier 0 → 1 → 2 → 3 → 4. Status: ✅ complete.*
