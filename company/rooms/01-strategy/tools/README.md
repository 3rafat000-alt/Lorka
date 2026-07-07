# Room 01-strategy — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only for the three specialists whose spawnable frontmatter grants `WebSearch`/`WebFetch` (`str-product-strategist`, `str-market-analyst`, `str-monetization-strategist`) — the other four route research needs through them via `str-lead`, never open a fetch themselves.

## Existing tools this room uses (real paths, grep-verified)

`01-strategy` has no dedicated Python toolkit ported from v5 yet — grepping `company/os/agents/` (`ceo/`, `devops/`, `tier-1-architecture/`, `tier-3-quality/`, `tier-4-infrastructure/`, `uiux/`) finds nothing scoped to Strategy specifically, the same gap the Boardroom noted for itself. The room works from shared library calls and one frozen template:

| Tool | Used by | What it does |
|---|---|---|
| `company/templates/project-blueprint.template.md` | `str-lead` (assembly), `str-product-strategist` (source content) | The frozen shape for `docs/<PRJ>_Blueprint.md` — Problem Statement, Target User, JTBD, Business Goals & Metrics, Constraints/Assumptions, Scope Boundary, Priority, the 5 Deep Questions. This room fills it; nothing invents a different Blueprint shape. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `str-lead` | Mechanical Gate-0 validation against `company/nexus/gates.yaml` `id: 0` — artifact existence, evidence-block presence, no boundary violations. Runs before any adversarial verify. |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `str-*` agent | Reads/writes the project brain; `brain-query type:risk` is the lookup `str-roadmap-planner` runs in `playbooks/two-track-sizing.md` step 1. |
| `company/os/sofi_tools/domain.py` (`sofi domain register`/`list`) | `str-lead` (confirmation only — `new-project.sh` auto-runs the register) | Confirms `<slug>.local` landed before Gate-0 sign-off; the local-domain-first discipline (Article 10). |
| `company/os/bin/new-project.sh` | `str-lead` (kicks off the whole room's work) | Scaffolds `projects/<PRJ-XXXX>/` — brain dirs, `prj/<PRJ>` branch, `<slug>.local` registration — the trigger event for `playbooks/gate-0-inception.md` step 1. |
| `company/os/agents/ceo/ceo_toolkit.py`'s `ProjectInspector` | `str-product-strategist` (occasional) | When the raw idea is a brownfield extension of an existing codebase rather than a greenfield project, a health-check of the existing tree sharpens the Problem Statement before it's written from a blank page — borrowed from the Boardroom's toolbox, not owned here. |

No script above is owned exclusively by this room — the shared `sofi_tools` modules and `new-project.sh` are the company's standing console, invoked here under the specialist's own agent id and logged to `.claude/memory/audit.jsonl`.

## What a new Strategy tool would look like

A genuinely new script belongs at `company/rooms/01-strategy/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/` or `company/os/agents/ceo/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. str-risk-analyst>
Gate(s): 0 (or 0-1 for str-lead/str-roadmap-planner)
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Strategy-owned script (none exist yet — build only on real recurring need):
- A `kill-criterion-linter.py` for `str-risk-analyst` that mechanically checks every entry in `docs/<PRJ>_Risk_Register.md` has a non-empty, non-generic kill-criterion field (rejecting "monitor closely"-shaped entries) before the register reaches `str-lead`'s gate-check — 0-token static location feeding the specialist's own review.
- A `two-track-classifier.py` for `str-roadmap-planner` that mechanically cross-references each roadmap milestone against the Risk Register's flagged money/credentials/auth/PII entries (`playbooks/two-track-sizing.md` step 1) and pre-flags the automatic `deep_audit` calls, leaving only the genuinely ambiguous ones for the four-question judgment pass.
- A `metric-coverage-check.py` for `str-business-analyst` that confirms every business goal in the Blueprint has at least one requirement in `docs/<PRJ>_Requirements.md` carrying a measurable success metric traced back to it — closing the loop the room bar names ("a goal without a number is a wish").

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.01-strategy` and get an entry in this table — never silently added.
