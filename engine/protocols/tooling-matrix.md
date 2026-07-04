# 🧰 Tooling Matrix — which tools each role may use

> **Foundation:** This protocol serves Teaching **III (Radical Isolation)** — tools are scoped per role, no role uses another's tools — and Teaching **IV (Token Economy)** — web tools are gated to research/ops roles to save tokens; devs pull findings via their lead. Read `engine/DOCTRINE.md` before this file.

Tools are granted in each `.claude/agents/sofi-*.md` frontmatter. This is the source of intent. `Read/Grep/Glob` are universal (orient + read brain). Web tools gated to research/ops to save tokens.

| Role | Read/Grep/Glob | Write/Edit | Bash | WebSearch/WebFetch | Why web |
|------|:--:|:--:|:--:|:--:|--------|
| ceo-sofi | ✓ | ✓ | ✓ | ✓ | market/tech scan for arbitration |
| chief-product-strategist | ✓ | ✓ | – | ✓ | competitor + market research |
| ux-researcher | ✓ | ✓ | – | ✓ | personas, real user/market data |
| journey-architect | ✓ | ✓ | – | ✓ | journey benchmarks |
| ui-ux-designer | ✓ | ✓ | – | ✓ | design-system + a11y refs |
| content-strategist | ✓ | ✓ | – | – | bounded; uses brain |
| principal-system-architect | ✓ | ✓ | ✓ | ✓ | tech eval, version/CVE check |
| data-schema-engineer | ✓ | ✓ | ✓ | – | brain + DB docs via lead |
| api-integration-specialist | ✓ | ✓ | ✓ | ✓ | fetch 3rd-party API specs |
| security-compliance-architect | ✓ | ✓ | ✓ | ✓ | OWASP + CVE feeds |
| backend/frontend/mobile leads | ✓ | ✓ | ✓ | ✓ | resolve a finding for the squad |
| devs (core, sql, queue, blade, css, vue, flutter, bloc, perf) | ✓ | ✓ | ✓ | – | request web findings via lead |
| qa-sre-lead | ✓ | ✓ | ✓ | – | brain + reports |
| automated-testing-engineer | ✓ | ✓ | ✓ | – | runs tests |
| manual-exploratory-tester | ✓ | ✓ | – | – | exploratory, no code |
| performance-load-analyst | ✓ | ✓ | ✓ | ✓ | CWV thresholds, tool docs |
| devops-cloud-lead | ✓ | ✓ | ✓ | ✓ | cloud/provider docs |
| cicd-pipeline-engineer | ✓ | ✓ | ✓ | – | provider docs via lead |
| observability-sre | ✓ | ✓ | ✓ | ✓ | monitoring tool docs |

## Public tunnels (`sofi tunnel`)
Opening a public tunnel — exposing `<slug>.local` to the internet for a demo, UAT, or a 3rd-party webhook — is owned by the **DevOps & Cloud Lead**; the **CI/CD Pipeline Engineer** may open one for a webhook test. Any other role that needs an external URL escalates to DevOps rather than opening its own: one owner keeps the security bar (seed data only — no real secrets/PII/prod data — torn down the moment it's done) in a single place. A tunnel is never a deployment; real releases still go through Gates 6–7. Full rules: `protocols/public-tunnels.md`.

## Principle
Grant the **fewest** tools that let the role do its job. Web access is a privilege of research/ops roles; devs stay heads-down on the frozen contract and pull web findings from their lead — one source of truth, fewer tokens, no drift.

## Scripts & the shared library
Every role that holds **Bash** works through `engine/tooling/` (library `sofi_tools` + dispatcher `bin/sofi` + per-role toolkits). The Bash grant and a script's net policy are the same line: a script may reach the internet **only if its role has `WebSearch/WebFetch` above** — enforced in `sofi_tools/guard.py::assert_net_allowed`. Roles with no Bash (strategist, UX researcher, journey, UI, content, manual tester) **think and write specs; they do not run scripts**. Full law: `engine/tooling/GOVERNANCE.md`.
