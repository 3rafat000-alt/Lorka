# Room 04-architecture — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only for the specialists whose spawnable frontmatter grants `WebSearch`/`WebFetch` (`arc-system-architect`, `arc-api-architect`, `arc-integration-architect`, `arc-infra-architect`) — `arc-data-architect` and `arc-lead` route research needs through them, `arc-review-architect` holds neither (read-only, no research posture beyond the codebase itself).

## Existing tools this room uses (real paths, grep-verified)

Ported from v5's `tier-1-architecture` toolkit and re-owned per specialist:

| Tool | Owner | What it does |
|---|---|---|
| `company/os/toolkit/gate/fossflow_export.py` | `arc-system-architect` | Turns a small topology spec (`{title, nodes[], connectors[]}`) into an importable FossFLOW/Isoflow isometric-diagram model — so the component diagram is generated, version-controlled, and traceable to the stack, never a hand-drawn picture nobody can regenerate. `node.type ∈ client\|server\|database\|cache\|queue\|service\|user\|external\|block`. Exit: `0` ok · `2` bad input/spec. |
| `company/os/toolkit/gate/migration_check.py` | `arc-data-architect` | Enforces "migration without rollback = rejected" (Teaching VI) — scans a migration file or directory and fails if any lacks a non-empty `down()`/rollback path (Laravel/PHP or raw `*.sql`). Exit: `0` all reversible · `1` one or more irreversible · `2` bad path. Every migration design in this room's Gate-3 bundle runs through this before it reaches `arc-lead`. |
| `company/os/toolkit/gate/stride_scaffold.py` | consumed by `09-security`'s `sec-threat-modeler`, read here for alignment | Generates a STRIDE threat-model skeleton for a feature so no surface gets skipped. `arc-infra-architect` and `arc-lead` read the resulting `Threat_Model.md` to align the topology design and confirm no unmitigated High risk before freezing the bundle — this room does not run the scaffold itself, that ownership stays in `09-security`. |
| `company/os/toolkit/core/feature_scan.py` | `arc-review-architect` (Phase 1 of `/sofi-spec-review`) | Locates and groups a feature's file set by the 4-pillar matrix, at zero model tokens, plus static pre-flags. Read the skeleton, open only flagged spots. |
| `company/os/toolkit/core/sofi_automator.py` | `arc-review-architect` (Phase 1 of `/sofi-spec-review`) | The 7-steel-rules scanner — checks every rule mechanically and emits the raw 🔴/🟡 SEV skeleton before the gatekeeper-tier hard gate. `--rule N` isolates one rule; `--json` for machine output. |
| `company/os/toolkit/core/spec_review_preflight.py` | `arc-review-architect` (Phase 1 of `/sofi-spec-review`) | Gathers the Phase-1 context bundle and pre-flight-classifies a prior spec-review failure's root cause (design-layer vs execution-layer) before a retry, capping blind re-attempts. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `arc-lead` | Mechanical Gate-3 validation against `company/nexus/gates.yaml` `id: 3` — bundle artifact existence, evidence-block presence, traceability completeness, no boundary violations. Runs before any adversarial verify. |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `arc-*` agent | Reads/writes the project brain; `brain-query type:decision` is the lookup a specialist runs before re-deciding something already settled in a past project's `DECISIONS.md`. |

No script above is owned exclusively by this room's *process* — the shared `sofi_tools` modules and the `ceo/`-housed spec-review scanners are the company's standing console, invoked here under the specialist's own agent id and logged to `.claude/memory/audit.jsonl`. The three `tier-1-architecture/*` scripts, however, ARE this room's own toolkit (ported and re-owned from v5's Tier-1 department, which is exactly what `04-architecture` descends from).

## What a new Architecture tool would look like

A genuinely new script belongs at `company/rooms/04-architecture/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/toolkit/gate/`, or `company/os/toolkit/core/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. arc-api-architect>
purpose: <one-line purpose>
gate:    3
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network unless the
owning role holds Web tools.
"""
```

Candidates that would justify a new Architecture-owned script (none exist yet — build only on real recurring need):
- A `contract-schema-parity.py` for `arc-api-architect` that mechanically cross-references every field referenced in `docs/<PRJ>_OpenAPI.yaml` against the columns declared in `docs/<PRJ>_Schema.sql`, flagging any contract field with no schema origin (or vice versa) before `arc-lead`'s gate-check — closing the same gap steel rule 6 checks manually today, but at zero model tokens.
- A `traceability-linter.py` for `arc-system-architect` that mechanically walks `Prototype_Spec.md`'s screen list against the traceability matrix and flags any screen with no resolved component/endpoint row, or any component row that traces to no screen — pre-flagging the orphans `arc-lead`'s room bar exists to catch.
- A `vendor-fetch-log.py` for `arc-integration-architect` that appends every `WebFetch` call's URL + timestamp to a structured citation log inside the project, so `Integration_Plans.md`'s citations can be mechanically cross-checked against actual fetch events rather than trusted on the specialist's word alone.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.04-architecture` and get an entry in this table — never silently added.
