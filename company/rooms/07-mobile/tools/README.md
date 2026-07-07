# Room 07-mobile — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only if the owning role holds Web tools — **no `mob-*` agent holds `WebSearch`/`WebFetch`** (Article 09, `tooling-matrix.md`: devs stay on the frozen contract). A vendor-documentation lookup for a platform-channel API this room genuinely needs routes through `res-lead`'s room (`res-web-scout`) via `mob-lead`, same as every other dev room.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Path | Used by | What it does |
|---|---|---|---|
| `sofi_verify.py` | `company/os/toolkit/core/sofi_verify.py` | every `mob-*` specialist (self-check before handoff, `--only lint`), `mob-lead` (re-confirm before his own review pass) | Mechanical verification runner — auto-detects the present toolchain and runs the applicable lint/build-health checks, GATES the pipeline with its exit code. No model tokens burned confirming "does it lint" before a human or model reads a diff. |
| `sofi_scan.py` (modes `wiring`, `security`, `search`) | `company/os/toolkit/core/sofi_scan.py` | `mob-lead` (step 5 of `playbooks/gate-4-build-procedure.md`), `mob-platform-engineer` (`search "catch (e)"` — the mechanical half of `playbooks/typed-network-exception-design.md` step 8) | `wiring` — route/screen/state seam location. `security` — OWASP-adjacent static pre-flags relevant to a mobile client (hardcoded secrets, insecure storage patterns). `search` — ranked code locator, this room's primary use being the unmapped-catch-block sweep. |
| `feature_scan.py` + `spec_review_preflight.py` | `company/os/toolkit/core/` | `mob-lead` (before routing a request to `arc-review-architect`'s `/sofi-spec-review`) | 0-token static location + 4-pillar pre-flag pass, shared across rooms — the Phase-1 scan behind any spec-review this room's work triggers, including the "Mobile/Client" pillar named in the binding spec-review protocol. |
| `sofi_tools` shared library | `company/os/sofi_tools/` | all six, via the `sofi` CLI | `brain` (read/write `_context/*`), `tickets` (Gate-4 ticket validation, Room Isolation Law check), `routing` (resolve `model·effort·caveman` for any `mob-*` id), `gates` (`validate_evidence`, `gates.yaml` loader), `guard` (`assert_within_project`, `assert_net_allowed`). |
| `sofi` CLI | `company/os/bin/sofi` | all six | `sync`, `checkpoint`, `claim`/`release`, `worktree`, `gate-merge`, `gate-check`, `dispatch`, `escalate`, `brain-query` — the mechanical spine of every step in both playbooks. `gate-tag` runs once `bck-lead` confirms the owner-room aggregate exit, not by this room alone. |
| `gemini_bridge.py` + `gemini_review.py` | `company/os/toolkit/core/` | `mob-lead` (oracle desk, Teaching VII, at genuine decision points — e.g. a contested state-management library boundary or a platform-channel design that survived one mediation round and needs a family-diverse second opinion) | Sanitize → push → capture → digest-ingest, same oracle desk every room shares. |

Platform-native toolchain checks (`flutter analyze`, `flutter test`, `dart format --set-exit-if-changed`) are invoked directly per `playbooks/gate-4-build-procedure.md` step 5 — they are the Flutter SDK's own mechanical gate, not a SOFI-owned script, and every `mob-*` specialist runs them before handing a diff up.

Web access itself is not a "tool" in the scanner sense — no `mob-*` agent's `.claude/agents/<id>.md` frontmatter grants `WebSearch`/`WebFetch`. A bounded live-web need (confirming a store-policy change, a platform-channel API's current documented behavior) routes through `res-lead`'s room (`res-web-scout`) via `mob-lead`, same path any other dev room uses.

## What a new Mobile tool would look like

A genuinely new script belongs at `company/rooms/07-mobile/tools/<name>.py`, only when no existing script in `company/os/sofi_tools`, `company/os/toolkit/core/`, or the Flutter SDK's own tooling already covers the job — check `company/nexus/registry.yaml` and `company/os/GOVERNANCE.md`'s promotion ladder before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. mob-platform-engineer>
Gate(s): 4
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Mobile-owned script (none exist yet — build only on real recurring need):

- A typed-exception-coverage linter for `mob-platform-engineer` that mechanically flags any network client call (`dio.get`/`dio.post`/raw `http` call) with no enclosing `try`/`catch` mapping into the `ApiException` hierarchy — the arithmetic half of the room's steel rule, leaving only the judgment call (which subtype is the *right* one) to the model. `sofi_scan.py search "catch (e)"` is the interim substitute; a dedicated AST-aware linter would catch the cases a text search misses (a call with no catch at all).
- A layer-boundary checker for `mob-flutter-engineer` that mechanically flags any `import` inside `lib/features/*/domain/` referencing a `data/` or `presentation/` path, or any framework package (`dio`, `sqflite`, `flutter/material.dart`) imported inside a domain file — the mechanical half of "dependencies point inward," before a model has to trace the import graph by eye.
- A Bloc-state-completeness checker for `mob-state-engineer` that mechanically diffs a feature's `Prototype_Spec.md`-declared screen states against the `sealed class`/subtype list in the corresponding State file, flagging a named state with no matching subtype before a model re-derives the same gap by reading both files side by side.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.07-mobile` and get an entry in this table — never silently added.
