# Room 10-quality — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`). `qa-perf-analyst` is the one specialist in this room holding `WebSearch`/`WebFetch` grants (see `company/nexus/registry.yaml`) — the other five specialists confirm any external threshold or standard through her, or through `arc-lead`'s already-fetched, dated artifacts, never a live fetch of their own.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner (per `registry.yaml`) | What it does |
|---|---|---|
| `company/os/toolkit/gate/coverage_gate.py` | `qa-lead` (mechanical enforcement), executed on `qa-automation-engineer`'s output | Enforces the >=90% coverage bar — fails the build below it. Accepts a raw percentage or a `coverage.xml` (Cobertura/Clover line-rate). Exit: `0` meets bar · `1` below bar · `2` bad input. Ported forward from v5's flat `qa-sre-lead` toolkit; `qa-automation-engineer` runs it on every suite before handing coverage to `qa-lead`, and `qa-lead` re-confirms it as part of the Gate-5 aggregate check. |
| `company/os/toolkit/gate/perf_budget.py` | `qa-perf-analyst` | Enforces the performance budget — fails when TTI>=2s or a Core Web Vital breaches threshold. Accepts metrics as flags (`--tti`/`--lcp`/`--inp`/`--cls`) or a JSON file. Exit: `0` within budget · `1` budget breached · `2` bad input. The mechanical backbone of `playbooks/gate-5-quality-procedure.md` step 7's perf check — `qa-perf-analyst` runs it against every load-test/Lighthouse result before writing the budget verdict. |
| `company/os/toolkit/uiux/uiux_pipeline.py` (`gate` mode) | `qa-design-auditor` | Token-frugal, GATED pipeline: taste-dial, design-fidelity, and RTL-currency-hygiene checks in one pass at zero-to-low model cost, before the manual field-by-field walk against `Prototype_Spec.md`. `qa-design-auditor` runs `gate` mode first so her own model-judgment budget goes to the ambiguous cases the script can't resolve on its own. |
| `company/os/toolkit/ceo/sofi_verify.py` | every `qa-*` specialist, and `qa-lead` re-confirming before the aggregate check | Mechanical `php -l` / lint / build-sanity pass over the merged build — the first, cheapest signal before any specialist spends model tokens reading code by hand. |
| `company/os/toolkit/ceo/sofi_scan.py` (`search`/`wiring`/`design`/`security` modes) | `qa-automation-engineer`, `qa-manual-explorer`, `qa-design-auditor` | Locates a test seam, a route↔controller↔view wiring path, a design-token mismatch, or an OWASP static pre-flag — the zero-token location pass before a specialist's model judgment reads the actual file. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `qa-lead` | Mechanical Gate-5 validation of both `10-quality`'s own six-dimension slice and the aggregate (incl. `09-security`'s squad-partner contribution) against `company/nexus/gates.yaml` — artifact existence, evidence-block presence, no boundary violations. Runs before any adversarial verify. |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `qa-*` agent | Reads/writes the project brain; `brain-query type:lesson` is the lookup `qa-test-architect` runs before sizing a pass^k plan on a surface-shape she's seen flake before in a prior project's `LESSONS.md`. |
| `company/os/sofi_tools/runlog.py` | every `qa-*` agent that mutates the brain | Appends a `_context/_runlog.md` line on any state-mutating operation (Rule 6) — a quarantine action, a verdict issued. |
| `company/os/toolkit/ceo/feature_scan.py` + `spec_review_preflight.py` | `qa-lead` (Phase-1 scan, when this room's surface is the subject of a `/sofi-spec-review`) | Locates and groups a feature's file set by the 4-pillar matrix at zero model tokens — read when `arc-review-architect` requests this room's context for a cross-layer review touching test coverage or quality gates. |

No script above is owned exclusively by this room's *process* — `sofi_tools` is the company's standing console, invoked here under each specialist's own agent id and logged to `.claude/memory/audit.jsonl`. The two scripts genuinely re-owned into this room from v5's flat tier-3 toolkit are `coverage_gate.py` and `perf_budget.py` — both carry their original `role:` header forward, now read against the v6 `qa-lead`/`qa-perf-analyst` ids.

## What a new Quality tool would look like

A genuinely new script belongs at `company/rooms/10-quality/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/toolkit/gate/`, `company/os/toolkit/uiux/`, or `company/os/toolkit/ceo/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. qa-test-architect>
purpose: <one-line purpose>
gate:    5
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network
(only qa-perf-analyst holds Web-tool grants in this room — see tooling-matrix).
"""
```

Candidates that would justify a new Quality-owned script (none exist yet — build only on real recurring need):

- A `pass_k_check.py` for `qa-test-architect`/`qa-lead` that mechanically parses a pass^k run log (per-run pass/fail, timestamp, whether state was reset between runs) and fails closed if the declared independence condition (fresh state per run) can't be confirmed from the log — turning `playbooks/pass-k-reliability-tier-a.md` step 3's "genuinely independent" check from a manual read into a mechanical gate.
- A `flake_tracker.py` for `qa-regression-warden` that ingests CI run history and mechanically flags any test crossing the second-unexplained-red threshold, auto-drafting the quarantine entry (test id, first/second red timestamps, suggested owner from the git blame of the test file) — closing the "quarantine on sight" bar with zero-token detection instead of a manual scan of run logs.
- A `design_diff.py` for `qa-design-auditor` that mechanically diffs a built screen's rendered DOM/string set against `Content_Strings.json` and flags any visible string with no matching key — pre-flagging the exact "hardcoded string outside the frozen JSON" smell before the manual screen-by-screen walk.
- A `budget_trend.py` for `qa-perf-analyst` that compares the current `perf_budget.py` run against the prior Gate-5 pass's stored result and flags a regression even when the current run is still technically within budget — catching the "creeping toward the ceiling" pattern before it becomes an actual breach.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.10-quality` and get an entry in this table — never silently added.
