# Room 03-design — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only if the owning role holds Web tools — in this room that's `dsn-ui-designer` and `dsn-design-system` (both hold `WebSearch`+`WebFetch`, for design-system/pattern research); `dsn-lead`, `dsn-ux-architect`, `dsn-content-strategist`, `dsn-brand-designer`, `dsn-motion-designer`, and `dsn-a11y-specialist` do not, and route any live-web need through those two or through `res-lead`'s room.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Path | Used by | What it does |
|---|---|---|---|
| `uiux_pipeline.py` | `company/os/toolkit/uiux/uiux_pipeline.py` | `dsn-lead` (owner, per `company/nexus/registry.yaml`) | The UI/UX static pipeline — `scan` (taste/token duplication + design/motion/density/a11y/RTL static pack), `rtl` (currency-echo LRM hygiene), `gate` (full mechanical gate: blade compile · view:cache · lint), `brief` (emits paste-ready `/sofi-delegate` RCCF stubs). Feeds `/sofi-audit ui` and this room's own pre-freeze static pass at Gate 2 (step 1 of `playbooks/anti-generic-taste-application.md`). Pure stdlib, never writes source. |
| `sofi_scan.py` (mode `design`) | `company/os/toolkit/core/sofi_scan.py` | `dsn-lead`, `dsn-brand-designer` (via `/sofi-audit` or directly at Gate 2) | Grep-first static sweep: hardcoded hex/px, `!important`, missing `alt`/`aria`, div-as-button, no-reduced-motion, RTL issues, generic-AI-UI smells (centered hero, three equal cards, one accent color) — the mechanical half of the anti-generic-UI checklist. |
| `sofi_scan.py` (mode `flow`) | `company/os/toolkit/core/sofi_scan.py` | `dsn-ux-architect` (rare — mostly useful on a brownfield project with an existing routes/views tree to reconcile against a fresh flow diagram) | Routes → views map, orphan/dead-end view detection — a mechanical cross-check against `dsn-ux-architect`'s own dead-end/recovery-path discipline. |
| `sofi_tools` shared library | `company/os/sofi_tools/` | all eight, via the `sofi` CLI | `brain` (read/write `_context/*`), `tickets` (Gate-2 ticket validation, Room Isolation Law check), `routing` (resolve `model·effort·caveman` for any `dsn-*` id), `gates` (`validate_evidence`, `gates.yaml` loader), `guard` (`assert_net_allowed` — the mechanical check behind "only Web-tool holders touch the net"). |
| `sofi` CLI | `company/os/bin/sofi` | all eight | `sync`, `checkpoint`, `gate-check`, `gate-tag`, `dispatch`, `escalate`, `brain-query` — the mechanical spine of every step in both playbooks. |
| `feature_scan.py` | `company/os/toolkit/core/feature_scan.py` | `dsn-lead` (rare — a Gate-2 re-open needing a fast static sweep of what already exists before re-designing) | 0-token static location pass, shared across rooms. |
| `gemini_bridge.py` + `gemini_review.py` | `company/os/toolkit/core/` | `dsn-lead` (oracle desk, Teaching VII, at genuine decision points — e.g. a contested taste-vs-a11y call that survived the room-level mediation and needs a second opinion before `dsn-lead` rules on it) | Sanitize → push → capture → digest-ingest, same oracle desk every room shares. |

Web access itself is not a "tool" in the scanner sense — `WebSearch`/`WebFetch` are granted directly in the qualifying agents' `.claude/agents/<id>.md` frontmatter (`dsn-ui-designer`, `dsn-design-system`); every other member of the room routes a live-web need through one of those two, or asks `res-lead`'s room for a bounded `res-web-scout` fetch via `dsn-lead` (Article 09 §6).

## What a new Design tool would look like

A genuinely new script belongs at `company/rooms/03-design/tools/<name>.py`, only when no existing script in `company/os/sofi_tools`, `company/os/toolkit/uiux/`, or `company/os/toolkit/core/` already covers the job — check `company/nexus/registry.yaml` and `company/os/GOVERNANCE.md`'s promotion ladder before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. dsn-a11y-specialist>
Gate(s): 2 (or "cross" for a Gate-4/5 fidelity re-check tool)
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Design-owned script (none exist yet — build only on real recurring need):
- A token-duplication linter for `dsn-design-system` that mechanically flags any hex/spacing/radius literal in `Prototype_Spec.md` with no matching entry in `Design_Tokens.md` — a 0-token pre-pass ahead of her manual cross-check.
- A screen-to-stage traceability checker for `dsn-lead`'s integration pass that mechanically diffs the screen list in `Prototype_Spec.md` against the stage list in the frozen `Journey_Map.md`, flagging any screen with no matching stage id and any stage with no matching screen — the arithmetic half of "no orphan screens," leaving only the judgment call to the model.
- A reduced-motion-fallback completeness checker for `dsn-motion-designer` that mechanically confirms every animation entry in the motion spec has a non-empty fallback field, before `dsn-a11y-specialist` spends model tokens verifying the fallback is actually a real static replacement.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.03-design` and get an entry in this table — never silently added.
