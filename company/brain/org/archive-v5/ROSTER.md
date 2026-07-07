# 🧑‍🤝‍🧑 SOFI AI Team Roster

> **Foundation:** Every agent on this roster serves one or more teachings of the Doctrine (`engine/DOCTRINE.md`). The "Serves" column names which. Read the Doctrine before reading this roster.

**30 agents = CEO + 5 Advisors (one per tier, sole cross-tier gateway) + 24 specialists (Tier-4 has 4, all others have 5).** Tiers are strictly isolated: a specialist never addresses a specialist in another tier directly — every cross-tier need is a **request** to your own tier's Advisor, who forwards it to the target tier's Advisor, who assigns it and returns a **report** the same way. See `engine/protocols/handoff-and-interconnection.md` for the mechanism and `engine/tooling/sofi_tools/tickets.py::validate_tier_boundary()` for the enforcement. Each row shows persona, routing tag (the cheapest setting that clears the bar), and which Doctrine teachings it serves. Full spec in each linked file. Spawn any of them with a 4-part **RCCF** block (Role · Context · Command · Format) — see `engine/protocols/01-delegation-rccf.md` or run `/sofi-delegate`.

> Legend — Model: 🟣 Opus 4.8 (deep) · 🔵 Sonnet 4.6 (workhorse) · 🟢 Haiku 4.5 (mechanical). Effort: low/medium/high/max. Caveman: lite/full/ultra. Teaching: I–VI per `engine/DOCTRINE.md`.

## 👑 Executive
| Agent | Persona | File | Model | Effort | Caveman | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|
| CEO / Principal Architect (SOFI AI) | Magnus Holt | `agents/ceo-sofi.md` | 🟣 | max | full | I II III IV V VI |

## 🧠 Tier 0 — Strategy & Product Design
| Agent | Persona | File | Model | Effort | Caveman | Gate | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|:--:|
| **Tier-0 Advisor** (gateway) | Isabelle Duarte | `agents/advisors/tier-0-advisor.md` | 🟣 | high | full | 0–2 | II III |
| Chief Product Strategist | Dr. Amara Okafor | `agents/tier-0-strategy/chief-product-strategist.md` | 🟣 | high | lite | 0 | I |
| UX Researcher | Hiroshi Tanaka | `agents/tier-0-strategy/ux-researcher.md` | 🟣 | high | lite | 1 | I |
| Journey Architect | Sofia Marchetti | `agents/tier-0-strategy/journey-architect.md` | 🟣 | high | lite | 1 | I |
| UI/UX Designer | Daniel "Dan" Kim | `agents/tier-0-strategy/ui-ux-designer.md` | 🔵 | medium | lite | 2 | I |
| Content Strategist | Margaret "Peg" O'Sullivan | `agents/tier-0-strategy/content-strategist.md` | 🟢 | low | full | 2 | I |

## 🏗️ Tier 1 — System Engineering & Architecture
| Agent | Persona | File | Model | Effort | Caveman | Gate | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|:--:|
| **Tier-1 Advisor** (gateway) | Ingrid Voss | `agents/advisors/tier-1-advisor.md` | 🟣 | high | full | 3 | II III |
| Principal System Architect | Vikram Rao | `agents/tier-1-architecture/principal-system-architect.md` | 🟣 | high | full | 3 | I II VI |
| Data & Schema Engineer | Elena Petrova | `agents/tier-1-architecture/data-schema-engineer.md` | 🔵 | high | full | 3 | VI |
| API & Integration Specialist | Marcus "Marco" Blackwood | `agents/tier-1-architecture/api-integration-specialist.md` | 🔵 | medium | full | 3 | II |
| Security & Compliance Architect | Dr. Ruth Goldberg | `agents/tier-1-architecture/security-compliance-architect.md` | 🟣 | max | full | 3 | VI |
| Infrastructure & Cloud Architect | Kenji Watanabe | `agents/tier-1-architecture/infrastructure-cloud-architect.md` | 🔵 | high | full | 3 | VI |

## 💻 Tier 2 — Development Execution
5 full-ownership roles, not squads — each owns their concern end to end (DB, API, backend/Blade, frontend/React, mobile). No separate Tech Lead: the Tier-2 Advisor owns coordination + cross-tier gateway duty.

| Agent | Persona | File | Model | Effort | Caveman | Gate | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|:--:|
| **Tier-2 Advisor** (gateway) | Elif Kaya | `agents/advisors/tier-2-advisor.md` | 🟣 | high | full | 2,4 | II III |
| Database Engineer | Günther Weber | `agents/tier-2-development/database-engineer.md` | 🔵 | high | full | 4 | VI |
| API Engineer | Priya Nair | `agents/tier-2-development/api-engineer.md` | 🔵 | medium | ultra | 4 | II |
| Backend/Blade Engineer | Aisha Rahman | `agents/tier-2-development/backend-blade-engineer.md` | 🔵 | medium | ultra | 4 | I IV |
| Frontend/React Engineer | Grace Achieng | `agents/tier-2-development/frontend-react-engineer.md` | 🔵 | medium | ultra | 4 | I IV |
| Mobile Engineer | João Silva | `agents/tier-2-development/mobile-engineer.md` | 🔵 | high | full | 4 | I IV VI |

## ✅ Tier 3 — Quality Assurance & Reliability
| Agent | Persona | File | Model | Effort | Caveman | Gate | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|:--:|
| **Tier-3 Advisor** (gateway) | Otieno Wambua | `agents/advisors/tier-3-advisor.md` | 🟣 | high | full | 5 | II III |
| QA & SRE Lead | Barbara "Barb" Jensen | `agents/tier-3-quality/qa-sre-lead.md` | 🔵 | high | full | 5 | II V |
| Automated Testing Engineer | Kwame Mensah | `agents/tier-3-quality/automated-testing-engineer.md` | 🔵 | medium | full | 5 | VI |
| Manual Exploratory Tester | Rosa Giménez | `agents/tier-3-quality/manual-exploratory-tester.md` | 🟢 | low | full | 5 | I |
| Performance & Load Analyst | Ahmed Farouk | `agents/tier-3-quality/performance-load-analyst.md` | 🔵 | medium | full | 5 | V |
| Security & Penetration Tester | Sirak Haile | `agents/tier-3-quality/security-penetration-tester.md` | 🟣 | max | full | 5 | VI |

## ⚙️ Tier 4 — Infrastructure & Deployment
| Agent | Persona | File | Model | Effort | Caveman | Gate | Serves |
|-------|---------|------|:--:|:--:|:--:|:--:|:--:|
| **Tier-4 Advisor** (gateway) | Astrid Lindqvist | `agents/advisors/tier-4-advisor.md` | 🟣 | high | full | 6–8 | II III |
| DevOps & Cloud Lead | Linda Schmidt | `agents/tier-4-infrastructure/devops-cloud-lead.md` | 🔵 | high | full | 6–7 | II V |
| CI/CD Pipeline Engineer | Tomás Herrera | `agents/tier-4-infrastructure/cicd-pipeline-engineer.md` | 🔵 | medium | ultra | 6–7 | IV V |
| Observability & Monitoring (SRE) | Naomi Brooks | `agents/tier-4-infrastructure/observability-sre.md` | 🔵 | medium | full | 8 | V |
| Release & Incident Manager | Camille Dubois | `agents/tier-4-infrastructure/release-incident-manager.md` | 🔵 | high | full | 6–8 | II V |
