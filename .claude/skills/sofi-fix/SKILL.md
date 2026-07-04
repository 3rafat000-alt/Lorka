---
name: sofi-fix
description: Turn audit/security findings into applied, checkpointed fixes — routes each finding to the cheapest specialist agent that clears the bar, delegates via RCCF, and commits every change (CEO never writes code). Flexible target: a single finding, a whole layer, or a report file. Use after /sofi-audit or /sofi-secure to actually repair. Triggers — "fix it", "apply the fixes", "repair the <layer>", "remediate", "patch these findings", "make the changes".
---

# /sofi-fix — findings → applied, committed repairs

> **CEO no-write doctrine** ([[ceo-orchestrator-no-write-doctrine]]): I don't author
> code — I route each finding to a specialist, then checkpoint. Every op = commit.

**Usage:** `/sofi-fix <target>` — target = a finding id, a layer (`blade`/`db`/`api`/…),
or a report path from `/sofi-report`. No target → the open findings from the last audit/secure run.

## Route finding → agent (cheapest that clears the bar)

| Finding kind | Agent | Route |
|--------------|-------|-------|
| Blade view / partial / escaping | `sofi-backend-blade-engineer` | 🔵 sonnet |
| CSS / tokens / a11y / RTL | `sofi-frontend-react-engineer` | 🔵 sonnet |
| Vue / JS interactivity | `sofi-frontend-react-engineer` | 🔵 sonnet |
| Controller / service / model / validation | `sofi-backend-blade-engineer` | 🔵 sonnet |
| Schema / migration / index / N+1 | `sofi-data-schema-engineer` / `sofi-database-engineer` | 🔵 sonnet |
| API contract / webhook / integration | `sofi-api-integration-specialist` | 🟣 opus |
| Security remediation | `sofi-security-compliance-architect` | 🟣 opus/max |
| Mobile (Flutter/Bloc) | `sofi-mobile-engineer` → squad | 🔵 sonnet |
| Trivial 1–2 file mechanical | `cavecrew-builder` | 🟢 cheap |

## Procedure

1. **Load findings** — from the prior run or the named report. Group by agent + file to batch (one agent, one bounded pass).
2. **Delegate** — build each brief with `/sofi-delegate <key> "<fix scope>"` (full RCCF: frozen artifact, in/out bounds, gate-bar). Independent groups spawn in parallel.
3. **Guard** — no secrets committed, no `reset --hard`/`--force` (hook-blocked), respect `$fillable` traps ([[guarded-field-mass-assignment-bug]]), SYP true-scale ([[sakk-syp-magnitude-truescale]]).
4. **Checkpoint EACH change** — `sofi checkpoint <PRJ> "fix(<scope>): <subject>"`. Uncommitted = invisible.
5. **Verify** — security fixes → `/sofi-secure verify`; tests → run suite; UI → `view:cache` compiles.
6. **Review desk (standing, before handoff)** — push the fix summary (what changed + why + residual risk) through the desk: `sofi gemini review --prj <PRJ> --json --text "<changes + context + ask>"` (inline, no `.md`) → analyze + EXECUTE the reply, loop till done, don't ask. `engine/protocols/external-review-desk.md`.
7. **Handoff** — `/sofi-handoff` records head_sha + next ticket; `/sofi-report` if a writeup is wanted.

**Bar:** every finding either fixed+committed, or explicitly deferred with reason. No silent drops, no scope creep beyond the finding.
