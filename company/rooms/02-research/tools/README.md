# Room 02-research — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only if the owning role holds Web tools — in this room that's `res-ux-researcher`, `res-web-scout`, `res-competitor-analyst`, `res-data-researcher`, and `res-fact-checker` (all five hold `WebSearch`+`WebFetch`); `res-lead` and `res-journey-architect` do not, and route any live-web need through those five.

## Existing tools this room uses (real paths, grep-verified)

Room 02-research carries no dedicated Python scanners of its own — v5's tier-0-strategy layer (`engine/tooling/agents/tier-0-strategy/`, the ancestor of this room) never had one either; a grep of `company/os/toolkit/` for `research|competitor|journey|persona|web` at build time returned no hits. This room instead leans on the shared layer:

| Tool | Path | Used by | What it does |
|---|---|---|---|
| `sofi_tools` shared library | `company/os/sofi_tools/` | all seven, via the `sofi` CLI | `brain` (read/write `_context/*`), `tickets` (Gate-1 ticket validation, Room Isolation Law check), `routing` (resolve `model·effort·caveman` for any `res-*` id), `gates` (`validate_evidence`, `gates.yaml` loader), `guard` (`assert_net_allowed` — the mechanical check behind "only Web-tool holders touch the net") |
| `sofi` CLI | `company/os/bin/sofi` | all seven | `sync`, `checkpoint`, `gate-check`, `gate-tag`, `dispatch`, `escalate`, `brain-query` — the mechanical spine of every step in `playbooks/discovery-gate-procedure.md` |
| `feature_scan.py` | `company/os/toolkit/core/feature_scan.py` | `res-lead` (rare — only when a Gate-1 re-open needs a fast static sweep of what already exists in the codebase before re-researching) | 0-token static location pass, shared across rooms |
| `sofi_scan.py` | `company/os/toolkit/core/sofi_scan.py` | `res-lead` (via `/sofi-audit`, rare for this room — Discovery has little codebase to sweep on a fresh project) | grep-first sweep engine, modes `search\|security\|design\|flow\|wiring\|all` |
| `gemini_bridge.py` + `gemini_review.py` | `company/os/toolkit/core/` | `res-lead` (oracle desk, Teaching VII, at genuine decision points — e.g. an UNKNOWN verdict that needs a second opinion before blocking the freeze) | sanitize → push → capture → digest-ingest, same oracle desk every room shares |

Web access itself is not a "tool" in the scanner sense — `WebSearch`/`WebFetch` are granted directly in each qualifying agent's `.claude/agents/<id>.md` frontmatter (`res-ux-researcher`, `res-web-scout`, `res-competitor-analyst`, `res-data-researcher`, `res-fact-checker`); `res-web-scout` is the *dedicated* holder for company-wide requests, the other four use their grants for their own artifact's direct sourcing needs (Article 09 §6).

## What a new Research tool would look like

A genuinely new script belongs at `company/rooms/02-research/tools/<name>.py`, only when no existing script in `company/os/sofi_tools` or `company/os/toolkit/` already covers the job — check `company/nexus/registry.yaml` and `company/os/GOVERNANCE.md`'s promotion ladder before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. res-fact-checker>
Gate(s): 1 (or "cross" for res-web-scout-owned tools)
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Research-owned script (none exist yet — build only on real recurring need):
- A citation-coverage linter for `res-fact-checker` that mechanically flags any sentence in `Personas.md`/`Journey_Map.md`/`Competitor_Teardown.md` ending in a period with no adjacent `[source: ...]` or `[unverified]` tag — 0-token pre-pass before the model reads the draft at all.
- A friction-ranking calculator for `res-journey-architect` that takes a raw pain-score and frequency-count table and mechanically sorts it, so the ranking itself is never a judgment call disguised as arithmetic.
- A stale-citation checker for `res-competitor-analyst` on Gate-8 loop-backs, flagging any `Competitor_Teardown.md` citation older than a configurable threshold so a re-opened Discovery pass knows exactly which competitor sources need a fresh `res-web-scout` fetch rather than reuse.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.02-research` and get an entry in this table — never silently added.
