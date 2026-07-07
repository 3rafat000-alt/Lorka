# Room 12-observability — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`). `obs-sre` is the one specialist in this room holding `WebSearch`/`WebFetch` grants (see `company/nexus/registry.yaml`) — she's the one who confirms an external reliability benchmark or SRE-industry threshold before it enters an SLO target; the other four specialists confirm any external standard through her, or through `arc-lead`'s already-fetched, dated artifacts, never a live fetch of their own.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner (per `registry.yaml`) | What it does |
|---|---|---|
| `company/os/agents/tier-4-infrastructure/observe_sentry_loop.py` | `obs-monitoring-engineer` (instrumentation + classification), read by `obs-insights-analyst` and `obs-incident-commander` for root-cause context | The Gate-8 feedback hook (ADR-006): polls Sentry for high-frequency exceptions over a rolling window, classifies root cause (data constraint / API contract / user input / perf), and injects runtime-observed constraints straight into `_context/DECISIONS.md` — closing the "production anomaly → project brain" loop mechanically instead of by hand. Ported forward verbatim from v5's flat tier-4 toolkit; still the room's only genuinely observability-owned script. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `obs-lead` | Mechanical Gate-8 validation against `company/nexus/gates.yaml` — artifact existence (`SLO_Report.md`, `Insights.md`), evidence-block presence, no boundary violations. Runs before any adversarial verify (`playbooks/gate-8-observe-procedure.md` step 9). |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `obs-*` agent | Reads/writes the project brain; `brain-query type:lesson` is the lookup `obs-incident-commander` runs before triaging and `obs-insights-analyst` runs before analyzing a drop-off, both checking for a comparable prior pattern in `LESSONS.md` before starting from a blank page. |
| `company/os/sofi_tools/runlog.py` | every `obs-*` agent that mutates the brain | Appends a `_context/_runlog.md` line on any state-mutating action this room takes — an SLO redefinition, an issue auto-filed on breach, a Gate-1 re-open ticket written (Rule 6). |
| `company/os/sofi_tools/tickets.py` (`sofi escalate`, ticket read/write) | `obs-lead`, `obs-incident-commander` | The mechanical ticket layer under `sofi escalate`/`sofi dispatch` — what `obs-incident-commander`'s immediate security-spur handoff (step 4a, `playbooks/incident-response-postmortem.md`) actually files, and what `obs-lead` uses to open the formal Gate-1 re-open. |
| `company/os/agents/ceo/sofi_scan.py` (`search`/`wiring` modes) | `obs-monitoring-engineer` | Locates existing instrumentation hooks or a metric-emission seam in the codebase at zero model tokens before he writes new instrumentation from scratch — the same Python-locates-model-judges pattern the rest of the company uses. |

No script above is owned exclusively by this room's *process* — `sofi_tools` is the company's standing console, invoked here under each specialist's own agent id and logged to `.claude/memory/audit.jsonl`. `observe_sentry_loop.py` is the one script genuinely re-owned into this room from v5's flat tier-4 toolkit; it carries its original header forward, now read against the v6 `obs-monitoring-engineer`/`obs-lead` ids.

## What a new Observability tool would look like

A genuinely new script belongs at `company/rooms/12-observability/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/agents/tier-4-infrastructure/`, or `company/os/agents/ceo/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. obs-sre>
purpose: <one-line purpose>
gate:    8
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network
(only obs-sre holds Web-tool grants in this room — see tooling-matrix).
"""
```

Candidates that would justify a new Observability-owned script (none exist yet — build only on real recurring need):

- An `error_budget_ledger.py` for `obs-sre` that mechanically tracks a rolling error-budget burn against the stated window and fails closed the moment the 100%-spent threshold is crossed — turning `playbooks/gate-8-observe-procedure.md` step 3's budget math from a manual read into a mechanical, re-runnable check every reporting cycle.
- A `runbook_lint.py` for `obs-alerting-engineer` that mechanically confirms every alert rule in the room's config has a matching runbook file, and flags any runbook whose "last dry-run" timestamp has gone stale past a set threshold — closing the "an alert with no runbook" bar (and the quieter "a runbook nobody's re-tested since the system changed" bar) with zero-token detection instead of a manual audit.
- A `dropoff_significance.py` for `obs-insights-analyst` that mechanically applies a real statistical-significance check (not just "the number looks lower") to a candidate drop-off, factoring in traffic volume, so a genuinely thin sample never reaches the point of a filed Gate-1 re-open on noise.
- An `incident_timeline_builder.py` for `obs-incident-commander` that mechanically assembles the post-mortem timeline directly from `obs-monitoring-engineer`'s telemetry/alert-fire timestamps, removing the risk of a memory-reconstructed timeline drifting from what the instrumentation actually recorded.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.12-observability` and get an entry in this table — never silently added.
