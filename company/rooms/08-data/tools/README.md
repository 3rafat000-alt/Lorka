# Room 08-data — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); this room holds no `WebSearch`/`WebFetch` grants at all (see `company/nexus/registry.yaml` tool grants and `company/constitution/09-research-law.md`) — `dat-etl-engineer` confirms a vendor's rate-limit/API behavior through `arc-integration-architect`'s already-fetched, dated `Integration_Plans.md`, never a live fetch of its own.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner (per `registry.yaml`) | What it does |
|---|---|---|
| `company/os/toolkit/gate/migration_check.py` | `dat-db-engineer` | Enforces "migration without rollback = rejected" (Teaching VI) — scans a migration file or directory and fails if any lacks a non-empty `down()`/rollback path (Laravel/PHP or raw `*.sql`). Exit: `0` all reversible · `1` one or more irreversible · `2` bad path. Ported from `arc-data-architect`'s design-time tool in `04-architecture`; this room re-owns it at the physical-build stage — every migration `dat-db-engineer` writes at Gate 4 runs through this before it reaches `dat-lead`, and the same script informs her Gate-3 migration-validation feedback on `arc-data-architect`'s design. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `dat-lead` | Mechanical Gate-3/Gate-4 validation of this room's slice against `company/nexus/gates.yaml` — artifact existence, evidence-block presence, no boundary violations. Runs before any adversarial verify, both legs of `playbooks/gate-3-4-data-layer.md`. |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `dat-*` agent | Reads/writes the project brain; `brain-query type:decision` is the lookup a specialist runs before re-deciding something already settled in a past project's `DECISIONS.md` (a prior cache-stampede incident, a prior retention-policy call). |
| `company/os/sofi_tools/runlog.py` | every `dat-*` agent that mutates the brain | Appends a `_context/_runlog.md` line on any state-mutating operation (Rule 6) — a migration run, a batch job's reconciliation pass. |
| `company/os/toolkit/ceo/sofi_scan.py` (`wiring`/`security` modes) | `dat-db-engineer`, `dat-privacy-officer` | Locates a query seam, a route↔model↔migration wiring path, or an OWASP static pre-flag — `dat-db-engineer` uses `wiring` mode to find every place a table is queried before adding an index; `dat-privacy-officer` uses `security` mode as a first pass for fields that look like they carry personal data, then confirms each one by reading the actual prototype screen. |
| `company/os/toolkit/ceo/feature_scan.py` | `dat-lead` (Phase-1 scan, when this room's surface is the subject of a `/sofi-spec-review`) | Locates and groups a feature's file set by the 4-pillar matrix at zero model tokens — read when `arc-review-architect` requests this room's context for a cross-layer review touching the data layer. |

No script above is owned exclusively by this room's *process* — `sofi_tools` is the company's standing console, invoked here under each specialist's own agent id and logged to `.claude/memory/audit.jsonl`. The one script genuinely ported and re-owned into this room's physical-build stage is `migration_check.py` (originally `04-architecture`'s design-time reversibility check; `registry.yaml` names `dat-db-engineer` as its owner at the physical-build layer, which is exactly what this room descends into from `arc-data-architect`'s design).

## What a new Data tool would look like

A genuinely new script belongs at `company/rooms/08-data/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/toolkit/gate/`, or `company/os/toolkit/ceo/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. dat-cache-engineer>
purpose: <one-line purpose>
gate:    4
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network
(this room holds no Web-tool grants — see tooling-matrix).
"""
```

Candidates that would justify a new Data-owned script (none exist yet — build only on real recurring need):

- A `stampede_check.py` for `dat-cache-engineer` that mechanically scans a project's cache-key definitions and flags any key with no declared invalidation trigger, no named stampede-prevention mechanism, or no stated cold-start behavior — the same "reject the missing piece mechanically" discipline `migration_check.py` applies to rollbacks, applied to `playbooks/stampede-safe-cache-invalidation.md`'s step 3-5 checklist, at zero model tokens.
- An `idempotency_lint.py` for `dat-etl-engineer` that scans a batch job's source for a database-level unique constraint tied to its declared dedup key, and fails if the job's "runs twice" test is missing or the constraint can't be found — pre-flagging exactly the gap `dat-lead`'s room bar exists to catch before a specialist's self-report is trusted.
- An `event-lineage-linter.py` for `dat-analytics-engineer` that mechanically walks a metrics model's SQL/transform definitions and flags any metric with no traceable path back to a versioned raw-event table — closing the "folklore, not data" gap the room bar names, at zero model tokens.
- An `eval-diff-gate.py` for `dat-ml-engineer` that compares a new eval-suite run's results against the stated baseline file and fails closed if any tracked metric regresses past a declared tolerance — turning "no eval, no ship" from a review discipline into a mechanical gate.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.08-data` and get an entry in this table — never silently added.
