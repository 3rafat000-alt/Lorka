# Room 06-frontend — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); no member of this room holds `WebSearch`/`WebFetch` in their spawnable frontmatter, so any research need (a browser-compat question, a library's real API) routes through `fnt-lead` to a room that does (`04-architecture`, `02-research`) rather than guessing.

## Existing tools this room uses (real paths, grep-verified)

None of the scripts below are owned exclusively by this room — v5 had no dedicated Tier-2 frontend toolkit under `os/toolkit/`, so `06-frontend` reads the same shared/cross-room consoles other Build and Quality rooms already use, invoked here under this room's own agent ids and logged to `.claude/memory/audit.jsonl`:

| Tool | Owner here | What it does |
|---|---|---|
| `company/os/toolkit/uiux/uiux_pipeline.py` | `fnt-css-artisan` (taste/design modes), `fnt-a11y-engineer` (design/a11y static pack) | The shared design-system console: `scan --taste` flags a literal value that duplicates an in-scope `:root` design token at zero model tokens (exactly the hardcoded-value smell `fnt-css-artisan` hunts); `scan --design` runs the tokens/motion/density/a11y/RTL static pack `fnt-a11y-engineer` reads before opening a component by hand; `gate` runs the full pipeline exit-gated for a pre-merge sanity pass; `brief` emits paste-ready `/sofi-delegate` stubs when a finding needs routing to a specific specialist. Cross-room: `bck-blade-engineer` runs the same tool on server-rendered markup — both rooms style from the same token file, so alignment matters. |
| `company/os/toolkit/gate/perf_budget.py` | `fnt-performance-engineer` (pre-emptive self-check) | Enforces the Core Web Vitals budget — fails when TTI≥2s or LCP/INP/CLS breaches threshold. Accepts metrics as flags or a JSON file (Lighthouse output shape). Owned for real by `10-quality`'s `qa-perf-analyst` at Gate 5; this room runs it pre-emptively during the a11y-performance hardening pass (`playbooks/a11y-performance-hardening.md`) so a regression is caught at merge time, not bounced back from Gate 5. Exit: `0` within budget · `1` breached · `2` bad input. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `fnt-lead` | Mechanical Gate-4 validation for this room's slice against `company/nexus/gates.yaml` `id: 4` — artifact existence, evidence-block presence, OpenAPI byte-parity, state completeness. Runs before any adversarial verify. |
| `company/os/sofi_tools/gitops.py` (`sofi worktree` / `sofi gate-merge`) | `fnt-lead` | Creates and merges this room's isolated worktree (`worktrees/<PRJ>-gate4-frontend`) behind the frozen bundle, alongside `05-backend` and `07-mobile`'s own worktrees — `--no-ff` merge only, never before `fnt-code-reviewer`'s PASS. |
| `company/os/sofi_tools/brain.py` (`sofi brain`, `sofi brain-query`) | every `fnt-*` agent | Reads/writes the project brain; `brain-query type:lesson` is the lookup a specialist runs before repeating a mistake already distilled in a past project's `LESSONS.md` (a past store-with-two-owners bug, a past reduced-motion regression). |

## What a new Frontend tool would look like

A genuinely new script belongs at `company/rooms/06-frontend/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/toolkit/uiux/`, or `company/os/toolkit/gate/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. fnt-a11y-engineer>
purpose: <one-line purpose>
gate:    4
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network (this
room holds no Web tools; a research need routes through fnt-lead).
"""
```

Candidates that would justify a new Frontend-owned script (none exist yet — build only on real recurring need):

- A `contract-parity-check.py` for `fnt-code-reviewer` that mechanically cross-references every fetch call's request/response shape in `src/frontend/**` against `docs/<PRJ>_OpenAPI.yaml`, flagging any client-side field with no contract origin (or vice versa) before the fresh-context review even starts — closing the same gap `arc-api-architect`'s hypothetical `contract-schema-parity.py` closes on the backend side, at zero model tokens.
- A `reduced-motion-lint.py` for `fnt-interaction-engineer`/`fnt-a11y-engineer` that mechanically walks the CSS/JS for every `@media (prefers-reduced-motion: reduce)` block and flags one that's just `animation: none`/`transition: none` with nothing put back — pre-flagging the exact "bare removal" smell this room's a11y engineer currently has to catch by eye.
- A `bundle-diff.py` for `fnt-performance-engineer` that mechanically diffs two bundle-analyzer JSON outputs (pre/post) and emits a structured before/after table per chunk, so `docs/<PRJ>_Frontend_Perf_Baseline.md` can be generated rather than hand-assembled from raw Lighthouse/webpack-analyzer output.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.06-frontend` and get an entry in this table — never silently added.
