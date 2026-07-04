---
name: sofi-audit
description: One flexible command to run a comprehensive, token-frugal audit of any layer of the codebase — UI/Blade, CSS/JS, data/schema, API, integration/wiring, agents/config, or the whole stack. Grep-first static sweep (free), findings ranked by severity, then optional agent delegation only where a fix needs a specialist. Use to inspect, review, or health-check any part of a SOFI project. Triggers — "audit", "inspect", "review the <layer>", "health check", "scan the code", "what's broken in", "check the blade/css/api/db".
---

# /sofi-audit — comprehensive layered inspection, cheapest-first

> Doctrine: **few token do trick.** Static grep sweep is free — run it FIRST.
> Never open a 100-agent swarm for a read ([[prefer-grep-over-swarm-audit]]).
> Agents only spawn to FIX, not to look.

**Usage:** `/sofi-audit <layer> [PRJ-ID]` — layer ∈
`ui · blade · css · js · db · api · integration · agents · all`.
No layer → `all`. No PRJ → active project (newest `STATE.md`).

## Layer → what to sweep (grep/ctx first, cite `file:line`)

| Layer | Sweep for | Common defects |
|-------|-----------|----------------|
| `ui` / `blade` | `@include`/`@extends` orphans, missing `@csrf`, `{{ }}` vs `{!! !!}` escaping, unbound vars, dead partials, duplicated markup | XSS via `{!!`, broken `@include`, `->user->name` null ([[sakk-user-has-no-name-column]]) |
| `css` | hardcoded hex vs design tokens, `!important` wars, unused selectors, non-token spacing, RTL/`&lrm;` gaps | drift from `:root` tokens, generic AI-UI (run `/sofi-design-taste`) |
| `js` | inline handlers, unescaped interpolation, dead listeners, Alpine `fmt()` misuse, console leftovers, N+1 fetch | leaks, double-submit, unguarded await |
| `db` | missing indexes, N+1 (`->with` gaps), migrations w/o rollback, `$fillable`/`$guarded` mass-assign ([[guarded-field-mass-assignment-bug]]), model-cache incomplete-class ([[carda-model-cache-incomplete-class]]) | reject: migration w/o rollback |
| `api` | route↔controller drift, contract vs OpenAPI, missing FormRequest validation, swallowed status codes ([[sakk-mobile-dio-swallows-403]]), webhook shape ([[ccpayment-deposit-webhook-shape]]) | uncontracted endpoint |
| `integration` | env/config reads, secrets in git, dead wiring, scheduler bind ([[sakk-scheduler-routes-console-not-kernel]]), seed gaps ([[sakk-installer-underseed]]) | secret leak = STOP |
| `agents` | `.claude/agents/sofi-*.md` RCCF integrity, routing.yaml parity, model-id drift, skill-path validity | run `sofi doctor` |
| `all` | fan the above in parallel, one grep pass each | — |

## Engine first (token-frugal — 0 model tokens)

Lean on the unified Python engine before reading anything by hand:
```bash
python3 engine/tooling/agents/ceo/sofi_scan.py <mode> "<query>" --prj <PRJ> --md
```
Mode per layer: `ui/blade/css` → `design` · `integration` → `wiring` · `api/db/js` → `search` then open hits · `all` → `all`. UserFlow/journey → `flow` (routes→views + orphan/dead-end views). Read the skeleton it emits; open only flagged `file:line`.

## Procedure

1. **Orient** — `/sofi-boot` (git sync + brain). Never blind.
2. **Sweep** — run the engine mode above (static, 0 agents). For anything it can't see, `ctx_search`/ripgrep the patterns below. Batch parallel.
3. **Rank** — findings `SEV path:line — defect → fix`. Severity: 🔴 breaks/security · 🟠 correctness · 🟡 quality/taste · ⚪ nit. Cross-link the memory gotchas above when a pattern matches.
4. **Report** — terse table (caveman). No praise, no scope creep. End with: how many 🔴/🟠, and the one-line next move.
5. **Review desk (standing, before handoff)** — push the findings through the desk: `sofi gemini review --prj <PRJ> --json --text "<findings + context + ask>"` (inline, no `.md`) → analyze + EXECUTE the reply, loop till done, don't ask. `engine/protocols/external-review-desk.md`.
6. **Handoff** — if fixes wanted → `/sofi-fix <target>`; if security-shaped → `/sofi-secure`; deep design → `/sofi-design-taste`.

**Bar:** every finding cites `file:line` + a concrete fix. No vague "consider improving." Audit reads, never writes.
