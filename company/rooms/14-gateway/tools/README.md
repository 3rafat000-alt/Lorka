# Room 14-gateway — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. This room's scripts write only inside their own project tree (`projects/<PRJ-ID>/`); only `gtw-external-reviewer` holds `WebSearch`/`WebFetch` grants (see `company/nexus/registry.yaml` tool grants and `company/constitution/09-research-law.md`) — the oracle desk is the one legitimate reason this room touches the open internet, and every send through it is sanitized first (Article 07 §3).

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner (per `registry.yaml`) | What it does |
|---|---|---|
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `gtw-gatekeeper` (mechanical layer, invoked by the owner-room Lead closing the gate) | The mechanical fail-closed check every gate advancement runs first — `validate_no_skip`, `validate_artifacts`, `validate_room_boundary` (formerly `validate_tier_boundary`), `validate_evidence`. `gtw-gatekeeper`'s adversarial verdict never runs against a bundle that fails this layer. |
| `company/os/sofi_tools/routing.py` (`sofi route`) | `gtw-router` | The single source `routes.<id>` lookup every spawn's model/effort/caveman stamp comes from — no agent anywhere in the company invents a route by inference; this is the one legitimate path to a stamped route. |
| `company/os/toolkit/ceo/dispatch.py` | `gtw-dispatcher` | Renders the delegation block for the open ticket (`sofi dispatch`) — turns a ticket's `from/to/task/consumes/expected/route` fields into a paste-ready spawn prompt. |
| `company/os/toolkit/ceo/gemini_review.py` | `gtw-external-reviewer` | The oracle desk's top-level driver — `sofi gemini review/capture/status` all forward here. Implements the full sanitize → condense → push → capture → parse → ingest loop `playbooks/oracle-desk-review.md` walks step by step. |
| `company/os/toolkit/ceo/gemini_bridge.py` | `gtw-external-reviewer` | The low-level pinned-chat browser bridge `gemini_review.py` sits on top of — CDP-driven send/capture against the standing Gemini conversation. Not called directly; `gtw-external-reviewer` always goes through `gemini_review.py`. |
| `company/os/toolkit/ceo/sanitize_gemini_payload.py` | `gtw-external-reviewer` | The redaction pass — strips keys/secrets/`.env`-shaped content before a byte leaves the machine (Article 07 §3). Runs automatically inside `gemini_review.py` unless `--no-sanitize` is explicitly passed, which `gtw-external-reviewer` never does without a logged reason. |
| `company/os/toolkit/ceo/handoff_validator.py` | `gtw-gatekeeper` | Ticket/evidence-block validation support feeding `sofi gate-check`'s `validate_evidence()` — the mechanical half of what makes a bare "done" claim fail closed. |
| `company/os/sofi_tools/tickets.py` (`sofi handoff`, `sofi escalate`, `sofi brain-query`) | every `gtw-*` agent | The ticket-queue library every operator in this room reads and writes through — `gtw-dispatcher` sequencing, `gtw-conflict-resolver` pulling both sides' forwarded positions, `gtw-budget-warden`'s weekly `HANDOFFS.md` sweep. |

No script above is owned exclusively by this room's *process* — `sofi_tools` is the company's standing console, invoked here under each operator's own agent id and logged to `.claude/memory/audit.jsonl`. The three scripts genuinely re-owned into this room (`gemini_review.py`, `gemini_bridge.py`, `sanitize_gemini_payload.py`) form the oracle desk's complete driver stack, all three under `gtw-external-reviewer`.

## What a new Gateway tool would look like

A genuinely new script belongs at `company/rooms/14-gateway/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/toolkit/ceo/`, or elsewhere in `company/os/toolkit/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. gtw-budget-warden>
purpose: <one-line purpose>
gate:    cross
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network
(this room's Web-tool grant is scoped to gtw-external-reviewer only — see
tooling-matrix; the other five agents in this room hold no Web tools at all).
"""
```

Candidates that would justify a new Gateway-owned script (none exist yet — build only on real recurring need):

- A `route_drift.py` for `gtw-router`/`gtw-budget-warden` that mechanically walks a project's `HANDOFFS.md` route history and computes the actual mechanical/workhorse/gatekeeper/deep ratio against the 80%-mechanical rule, flagging drift below threshold without a human eyeballing a week of tickets — the same "reject the pattern mechanically" discipline `migration_check.py` applies to rollbacks, applied to route auditing, at zero model tokens.
- A `breaker_ledger.py` for `gtw-budget-warden` that cross-checks `HANDOFFS.md`'s `escalated`-status tickets against a maintained circuit-breaker trip log, failing closed on any trip missing its `escalation_token` — pre-flagging exactly the ledger gap `gtw-budget-warden`'s room bar exists to catch before a reflection pass has to reconstruct it by hand.
