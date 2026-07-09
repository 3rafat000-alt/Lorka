# Superpowers — External Capability Registry

Vetted open-source capabilities the enterprise can plug in. No power overrides a gate bar.

## Registry

| Power | Domain | Purpose | Status |
|-------|--------|---------|--------|
| **FossFLOW** | Architecture | Isometric architecture diagrams, component relationship visualization | 🟢 Pilot |
| **taste-skill** | Design/UI | Anti-generic-UI design dials (personality, warmth, brand character) | 🟢 Pilot |
| **The Agency** | Organization | Org-structure patterns: escalation chains, parallel squads, per-role success metrics | 🟢 Pilot |
| **k6** | Performance | Load testing, stress testing, performance budgets | 🟢 Active |
| **Lighthouse CI** | Performance | Core Web Vitals enforcement in CI pipeline | 🟢 Active |
| **Semgrep** | Security | SAST rule engine for custom security patterns | 🟢 Pilot |
| **Trivy** | Security | Container/FS vulnerability scanner | 🟢 Active |
| **Renovate** | Maintenance | Automated dependency updates | 🔵 Proposed |

## Lifecycle

1. **Proposed** — identified as potentially useful, not yet evaluated
2. **Pilot** — active trial on one project, metrics being collected
3. **Active** — proven value, used across projects, documented in templates
4. **Retired** — replaced by built-in capability, no longer maintained

## Rules

- Pilot requires a project sponsor and a 2-sprint evaluation window
- Promotion to Active requires: 2+ successful projects, documented integration, no negative security impact
- Retirement requires ADR entry explaining replacement rationale
- No superpower overrides a gate bar. Code/security never compromised.
