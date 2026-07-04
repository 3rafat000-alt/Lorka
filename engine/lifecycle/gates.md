# 🚦 The Binding Project Lifecycle — 9 Gates

Work cascades **down** and **in order**. A gate cannot open until the prior gate's deliverables are validated and signed off by the originating department. Each gate names the agents it activates and their route.

| Gate | Name | Trigger | Owner(s) | Output | Validation |
|:--:|------|---------|----------|--------|------------|
| **0** | Inception | User submits request | `chief-product-strategist` 🟣 high | `Project_Blueprint.md` + Problem Statement · **local domain `<slug>.local` registered** | Charter exists · `sofi domain list` shows the project |
| **1** | Discovery & Empathy | Problem Statement approved | `ux-researcher` + `journey-architect` 🟣 high | `[ID]_Personas.md`, `[ID]_Journey_Map.md` | Answers *"what does the user want & what blocks them today?"* |
| **2** | Solution Design | Journey Map validated | `ui-ux-designer` + `content-strategist` | `[ID]_Prototype_Spec.md`, `[ID]_Content_Strings.json` | WCAG 2.2 **AA** |
| **3** | Technical Architecture | Prototypes frozen | `principal-system-architect` + Data/API/Security | `[ID]_Schema.sql`, `[ID]_OpenAPI.yaml`, `[ID]_Tech_Stack.md`, `[ID]_Threat_Model.md` | Schema ↔ screens traceable |
| **4** | Parallel Implementation | Specs committed | Backend + Frontend + Mobile squads (parallel) | Compiled assets, packages, unit tests | OpenAPI + Journey Map = single source of truth |
| **5** | Integration & Quality | All squads "Complete" | `qa-sre-lead` + QA squad | Test reports, bug logs, Design Audit | Critical/High fixed · coverage > 90% · perf budget pass |
| **6** | Staging & UAT | Quality gate passed | `devops-cloud-lead` | Staging URL, UAT sign-off log | Simulated UAT pass |
| **7** | Production Rollout | UAT signed off | `devops-cloud-lead` + `cicd-pipeline-engineer` | Prod confirmation, rollback script ready | Blue/Green healthy |
| **8** | Observe & Evolve | Release live | `observability-sre` + `performance-load-analyst` | Weekly Perf Report, Bug Backlog, Feature Suggestions | Critical error → auto-file issue → **restart Gate 1** |

## Gate Discipline
- **Local domain first.** The very first act of standing a project up is its domain: scaffold (Gate 0) auto-registers `<slug>.local`; the build squad (Gate 4) runs `sofi domain up <PRJ>` so the app is reachable at `http://<slug>.local`; Gate 6 staging reuses that same URL. No agent shares a bare `127.0.0.1:PORT` link — the clean domain is the address of record (`STATE.md` → `local_domain`). See `engine/protocols/local-domains.md`.
- **No skipping.** A downstream agent that receives incomplete upstream deliverables **rejects** and files a blocker back up the chain.
- **Design is Truth.** Any feature without a Journey Map step is rejected at Gate 3 and routed to Backlog (see governance).
- **Feedback loop.** Gate 8 telemetry that breaches an SLO opens a new `PRJ`-scoped issue and re-enters at Gate 1 for that component only.
