# 🧰 SOFI AI Tooling — agent scripts, libraries, helpers

Every team and agent works through Python here. Three layers, one law.

```
engine/tooling/
├── GOVERNANCE.md        ← the law (read first). Enforced in code by guard.py.
├── registry.yaml        ← discovery index — find a tool before writing one.
├── sofi_tools/          ← shared library: import in any role with Bash.
│   paths brain tickets routing gates guard runlog cli
├── bin/sofi             ← the dispatcher every agent calls
└── agents/<tier>/<role>/*.py   ← per-role toolkits
    plus _TEMPLATE_agent_tool.py to add new ones.
```
Ephemeral one-off scripts live per-project in `projects/<PRJ-ID>/_scratch/` and are
purged at gate exit — never a deliverable (GOVERNANCE Rule 3).

## Use it
```bash
engine/tooling/bin/sofi doctor              # self-check
engine/tooling/bin/sofi route qa-sre-lead   # cheapest clearing route
engine/tooling/bin/sofi brain  PRJ-0001     # STATE + next open ticket
engine/tooling/bin/sofi gate-check PRJ-0001 # validate gate order + artifacts
engine/tooling/bin/sofi dispatch PRJ-0001   # delegation prompt for the open ticket
```
Add `engine/tooling/bin` to PATH and it's just `sofi <cmd>`.

## Per-role tools (examples shipped)
| Role | Tool | Does |
|------|------|------|
| ceo-sofi | `agents/ceo/route.py` · `dispatch.py` | route resolution · delegation prompt |
| data-schema-engineer | `migration_check.py` | reject migrations missing rollback |
| security-compliance-architect | `stride_scaffold.py` | STRIDE skeleton, no surface skipped |
| qa-sre-lead | `coverage_gate.py` | fail build under 90% coverage |
| performance-load-analyst | `perf_budget.py` | fail when TTI≥2s / CWV breached |

## Add a tool
1. Prototype in `projects/<PRJ>/_scratch/tmp_<role>_<purpose>.py`.
2. Proved useful → copy `agents/_TEMPLATE_agent_tool.py`, fill the header.
3. Register the row in `registry.yaml`; log the promotion in `DECISIONS.md`.
4. `sofi doctor` + run it. Exit-code 0/≠0 is the contract.

## The shared library in one breath
`paths` (where things are) · `brain` (read/write STATE·CONTEXT·DECISIONS) ·
`tickets` (the handoff queue) · `routing` (model·effort·caveman) · `gates`
(9-gate order + no-skip) · `guard` (the sandbox) · `runlog` (the trace).
