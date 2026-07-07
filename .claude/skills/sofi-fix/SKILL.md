---
name: sofi-fix
description: Turn audit/security findings into applied, checkpointed fixes — routes each finding to the cheapest specialist agent that clears the bar, delegates via RCCF Work Order, and commits every change (CEO never writes code). Flexible target: a single finding, a whole layer, or a report file. Use after /sofi-audit or /sofi-secure to actually repair. Triggers — "fix it", "apply the fixes", "repair the <layer>", "remediate", "patch these findings", "make the changes".
---

# /sofi-fix — findings → applied, committed repairs

> **CEO no-write doctrine** (CEO Covenant §5 · [[ceo-orchestrator-no-write-doctrine]]): I don't
> author code — I route each finding to a specialist through their Lead, then checkpoint. Every op = commit.

**Usage:** `/sofi-fix <target>` — target = a finding id, a layer (`blade`/`db`/`api`/…),
or a report path from `/sofi-report`. No target → the open findings from the last audit/secure run.

## Route finding → agent (cheapest that clears the bar · `company/nexus/routing.yaml`)

| Finding kind | Agent (spawn id) | Route |
|--------------|------------------|-------|
| Blade view / partial / escaping / all states | `bck-blade-engineer` | 🔵 sonnet |
| Controller / service / business logic / validation | `bck-api-engineer` / `bck-domain-engineer` | 🔵 sonnet |
| Queues / jobs / retry-DLQ / websockets / events | `bck-queue-engineer` | 🔵 sonnet |
| CSS / Tailwind / taste dials / RTL | `fnt-css-artisan` | 🔵 sonnet |
| WCAG 2.2 AA in code | `fnt-a11y-engineer` | 🔵 sonnet |
| Vue / React interactivity + service layer | `fnt-vue-engineer` / `fnt-react-engineer` | 🔵 sonnet |
| Schema design / reversible migration design | `arc-data-architect` | 🔵 sonnet |
| Migration / index / N+1 / EXPLAIN | `dat-db-engineer` | 🔵 sonnet |
| Cache / invalidation | `dat-cache-engineer` | 🔵 sonnet |
| API contract / webhook / OpenAPI drift | `arc-api-architect` | 🔵 sonnet |
| 3rd-party integration wiring | `bck-integration-engineer` | 🔵 sonnet |
| Security remediation (appsec / injection / IDOR / authz) | `sec-appsec-engineer` (via `sec-lead`) | 🔵 sonnet |
| Auth / session / crypto | `sec-authn-engineer` | 🔵 sonnet |
| Secrets / env hygiene | `sec-secrets-warden` | 🟢 haiku |
| Mobile (Flutter/Bloc) | `mob-flutter-engineer` / `mob-state-engineer` | 🔵 sonnet |
| Behavior-preserving debt paydown | `bck-refactoring-surgeon` | 🔵 sonnet |
| Trivial 1–2 file mechanical | owning specialist @ **trivial-fix** effort class | 🟢 haiku |

## Procedure

1. **Load findings** — from the prior run or the named report. Group by agent + file to batch
   (one agent, one bounded pass). Prefer the Execution Plan block `/sofi-secure` attaches to each finding.
2. **Delegate** — build each Work Order with `/sofi-delegate <id> "<fix scope>"` (full RCCF v3: frozen
   artifact, in/out bounds, gate-bar, evidence block, effort class). Independent groups spawn in parallel.
   Cross-room fixes route through the target Lead (Room Isolation Law · Article 08).
3. **Guard** — no secrets committed (Article 07), no `reset --hard`/`--force` (hook-blocked · Teaching VI),
   respect `$fillable` traps ([[guarded-field-mass-assignment-bug]]), SYP true-scale ([[sakk-syp-magnitude-truescale]]).
4. **Checkpoint EACH change** — `sofi checkpoint <PRJ> "fix(<scope>): <subject>"`. Uncommitted = invisible (Article 06).
5. **Verify** — security fixes → `/sofi-secure verify`; tests → run suite; UI → `view:cache` compiles.
   Re-run the originating scan to confirm the pre-flag cleared (V1 evidence · Article 03).
6. **Oracle desk (standing, before handoff)** — push the fix summary (what changed + why + residual risk)
   through the desk: `sofi oracle review --prj <PRJ> --json --text "<changes + context + ask>"` (inline, no `.md`)
   → analyze + EXECUTE the reply, loop till done, don't ask (Teaching VII; operator `gtw-external-reviewer`).
7. **Handoff** — `/sofi-handoff` records head_sha + next ticket; `/sofi-report` if a writeup is wanted.

**Bar:** every finding either fixed+committed, or explicitly deferred with reason. No silent drops, no scope creep beyond the finding.
