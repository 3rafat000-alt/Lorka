# 🧰 SOFI OS — the executable layer (agent scripts, libraries, helpers)

Every room and agent works through Python here. Three layers, one law.

```
company/os/
├── GOVERNANCE.md        ← the law (read first). Enforced in code by guard.py.
├── registry.yaml        ← TOOLING index — find a tool before writing one.
│                          (the ORG index lives at company/nexus/registry.yaml)
├── sofi_tools/          ← shared library: import in any role with Bash.
│   paths registry brain tickets routing gates guard runlog gitops domain tunnel cli
├── bin/sofi             ← the dispatcher every agent calls
├── bin/new-project.sh   ← project scaffolder (brain + prj branch + <slug>.local)
├── agents/<family>/<role>/*.py   ← per-role toolkits
│   plus _TEMPLATE_agent_tool.py to add new ones.
├── ooda/                ← autonomous OODA engine (perceive → orient → decide → act)
├── oracle/  autopilot/  caveman/  server-plane/   ← operational docs + configs
```
Ephemeral one-off scripts live per-project in `projects/<PRJ-ID>/_scratch/` and are
purged at gate exit — never a deliverable (GOVERNANCE Rule 3).

## Use it
```bash
company/os/bin/sofi doctor                    # self-check incl. 105↔105 agent parity
company/os/bin/sofi rooms                     # the 15 rooms: lead · members · gates
company/os/bin/sofi registry sec-pentester    # query the org index for any agent
company/os/bin/sofi route bck-api-engineer    # cheapest clearing route
company/os/bin/sofi budget                    # spawn-width grid + hard ceilings
company/os/bin/sofi brain  PRJ-0001           # STATE + next open ticket
company/os/bin/sofi gate-check PRJ-0001       # 4 validators + VERDICT (exit gates CI)
company/os/bin/sofi dispatch PRJ-0001         # delegation prompt for the open ticket
```
Add `company/os/bin` to PATH and it's just `sofi <cmd>`.

## Per-role tools (examples shipped — owners are v6 agent ids)
| Owner | Tool | Does |
|------|------|------|
| brd-ceo / gtw-dispatcher | `agents/ceo/route.py` · `dispatch.py` · `ceo_toolkit.py` | route resolution · delegation prompt · CEO console |
| arc-review-architect | `agents/ceo/spec_review_preflight.py` | phase-1 grep sweep + SEV skeleton |
| dat-db-engineer | `agents/tier-1-architecture/data-schema-engineer/migration_check.py` | reject migrations missing rollback |
| sec-threat-modeler | `agents/tier-1-architecture/security-compliance-architect/stride_scaffold.py` | STRIDE skeleton, no surface skipped |
| qa-automation-engineer | `agents/tier-3-quality/qa-sre-lead/coverage_gate.py` | fail build under 90% coverage |
| qa-perf-analyst | `agents/tier-3-quality/performance-load-analyst/perf_budget.py` | fail when TTI≥2s / CWV breached |
| dsn-lead | `agents/uiux/uiux_pipeline.py` | exit-gated design/a11y/RTL pipeline |
| ops-domain-warden | `agents/devops/caddy_isolation.py` | per-project Caddy vhost isolation |
| gtw-external-reviewer | `agents/ceo/gemini_review.py` (+`gemini_bridge.py`) | the oracle desk: sanitize → push → capture → ingest |

Toolkit directories keep their v5 layout during transition (`tier-*` folder names);
`registry.yaml` maps each script to its v6 owner. New tools go under
`agents/<family>/<role>/`.

## Add a tool
1. Prototype in `projects/<PRJ>/_scratch/tmp_<role>_<purpose>.py`.
2. Proved useful → copy `agents/_TEMPLATE_agent_tool.py`, fill the header.
3. Register the row in `registry.yaml`; log the promotion in `DECISIONS.md`.
4. `sofi doctor` + run it. Exit-code 0/≠0 is the contract.

## The shared library in one breath
`paths` (where things are) · `registry` (who's who — 15 rooms · 105 agents from
company/nexus/registry.yaml) · `brain` (read/write STATE·CONTEXT·DECISIONS) ·
`tickets` (the handoff queue + Room Isolation Law) · `routing` (model·effort·caveman,
ladder 🟢→🔵→🔮→🟣) · `gates` (9-gate order + no-skip, roles from nexus/gates.yaml) ·
`guard` (the sandbox + net policy from registry grants) · `runlog` (the trace) ·
`gitops` (sync·checkpoint·worktrees·gate tags) · `domain`/`tunnel` (<slug>.local + bounded public URLs).
