# Room 00-boardroom — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script the Boardroom touches. Header rule, restated here because it's the one the Boardroom checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only if the owning role holds Web tools (none of the Boardroom's seven do — they route research through the rooms that hold Web tools).

## Existing tools this room uses (real paths, grep-verified)

All under `company/os/toolkit/core/` — this directory is effectively the Boardroom's toolbox, ported from v5's `engine/tooling/agents/ceo/` and adapted for the 15-room/105-agent structure:

| Script | Used by | What it does |
|---|---|---|
| `ceo_toolkit.py` | `brd-ceo` | The standing console: **Orchestrator** (one call = one fully-oriented RCCF delegation block, local PromptCache so shared context is sent once), **ProjectInspector** (health-check a project tree: stack, gaps, smells, secret leaks), **ComplianceEngine** (declarative conditions checked against an agent's output before it's accepted). CLI: `delegate <role> --prj PRJ-XXXX`, `inspect <path\|PRJ-XXXX>`, `health <path\|PRJ-XXXX>`, `comply <output-file> --rules rules.json`, `routes` (dump the resolved route table). |
| `route.py` | `brd-ceo`, `brd-chief-of-staff` | Resolves `model·effort·caveman` for a given agent id against `company/nexus/routing.yaml` — the mechanical half of "route every task, log it." |
| `dispatch.py` | `brd-ceo`, `brd-chief-of-staff` | Renders a Work Order for an open ticket / raw intent; backs `sofi dispatch`. |
| `squad_orchestrator_v2.py` | `brd-ceo` | Renders the parallel-squad delegation set for Gates 3/4/5 fan-out (`sofi squad`) — enforces "only behind a frozen input, never sequential phases of one ticket." |
| `handoff_validator.py` | `brd-ceo`, `brd-chief-of-staff` | Validates a ticket's Room Isolation Law trail (specialist → own Lead → target Lead) and evidence-block presence before a handoff is accepted — the mechanical half of Article 08. |
| `agent_preflight.py` / `agent_output_guard.py` | `brd-ceo` | Pre-spawn sanity (does the target agent id + route resolve) and post-spawn output guard (did the returned artifact match the declared Format) — the ComplianceEngine's supporting checks. |
| `feature_scan.py` | `brd-ceo` (via `/sofi-feature`) | 0-token static location pass — flags file:line candidates before any model judges them. |
| `sofi_scan.py` | `brd-ceo` (via `/sofi-audit`) | Modes `search\|security\|design\|flow\|wiring\|all` — the grep-first sweep engine behind layered audits. |
| `spec_review_preflight.py` | `brd-cto`, `brd-cpo` (via `/sofi-spec-review`) | Phase-1 mechanical scan + SEV draft before the Gate-3 hard gate hands off to `arc-review-architect` / `gtw-gatekeeper`. |
| `gemini_bridge.py` + `gemini_review.py` + `sanitize_gemini_payload.py` + `gemini-github-sync.py` + `sofi-gemini-monitor.sh` + `notify-gemini-full-dump.sh` | `brd-ceo` | The oracle desk (Teaching VII): sanitize → push → capture → digest-ingest. Config: `--chat` / `$SOFI_GEMINI_CHAT` / `~/.engine/gemini_bridge.json` (v6 path pending nexus migration — verify against `company/nexus/` before use). |
| `sofi_automator.py` | `brd-ceo` | Batch/scheduled automation entrypoint for recurring Boardroom checks (weekly exec summary). |
| `sofi_verify.py` | `brd-cqo`, `brd-cto` | Mechanical evidence validation (Article 03 V1) — used when confirming a gate-advance claim carries real cmd+exit-code proof, not self-report. |

No script above is owned exclusively by a single Boardroom officer — `ceo_toolkit.py` and its siblings are shared console commands any of the seven may invoke through their own Work Order, logged under their own agent id in `.claude/memory/audit.jsonl`.

## What a new Boardroom tool would look like

A genuinely new script belongs at `company/rooms/00-boardroom/tools/<name>.py`, only when no existing script in `company/os/toolkit/core/` (or a shared `sofi_tools` module) already covers the job — check `company/nexus/registry.yaml` and `company/os/GOVERNANCE.md`'s registry before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. brd-cqo>
Gate(s): <n or range>
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Boardroom-owned script (none exist yet — build only on real recurring need):
- A pass^k reliability-run aggregator for `brd-cqo` that reads `qa-lead`'s five-front bundle and mechanically confirms pass^k was executed (not just claimed) on every path named in the Gate-3 threat model.
- A veto-ledger tool for `brd-cso` that tracks open vetoes across all live projects with their remediation bar and evidence status, so nothing sits silently blocked without a visible clock.
- An ADR-line linter for `brd-arbiter` that checks a filed ruling actually fits the one-line contract before it's accepted into `DECISIONS.md`.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.00-boardroom` and get an entry in this table — never silently added.
