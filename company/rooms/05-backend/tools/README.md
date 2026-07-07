# Room 05-backend — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule, restated because it's the one this room checks first: **every script under this room declares its owner (agent id), its purpose, the gate(s) it serves, and its exit contract (0/≠0 meaning) in a header comment** — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only if the owning role holds Web tools — **no `bck-*` agent holds `WebSearch`/`WebFetch`** (Article 09, `tooling-matrix.md`: devs stay on the frozen contract). `bck-integration-engineer`'s live-vendor-documentation lookups are the one legitimate exception in spirit, but mechanically she still routes any actual web fetch through `res-lead`'s room (`res-web-scout`) via `bck-lead`, same as every other dev room.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Path | Used by | What it does |
|---|---|---|---|
| `sofi_verify.py` | `company/os/agents/ceo/sofi_verify.py` | every `bck-*` specialist (self-check before handoff), `bck-lead` (re-confirm before routing to review) | Mechanical verification runner — `php -l`, `artisan view:cache`, lint, asset-resolve — GATES the pipeline with its exit code. No model tokens burned on "does it compile." Auto-detects the present toolchain, runs only what applies. |
| `sofi_scan.py` (modes `wiring`, `security`, `search`) | `company/os/agents/ceo/sofi_scan.py` | `bck-lead` (step 5 of `playbooks/gate-4-build-procedure.md`), `bck-code-reviewer` (mandatory pre-judgment pass) | `wiring` — route↔controller↔view seam, env/config reads, dead includes. `security` — OWASP static pre-flags: XSS, SQLi, mass-assignment, secrets, IDOR. `search` — ranked code locator for "where is X already implemented." The mechanical half of every review before a model reads a diff. |
| `uiux_pipeline.py` | `company/os/agents/uiux/uiux_pipeline.py` | `bck-blade-engineer`, `bck-lead` (owned by `dsn-lead`/`03-design` per `company/nexus/registry.yaml`; this room is a heavy downstream consumer since every Blade view it ships runs through the same static gate) | `gate` mode: full mechanical gate on server-rendered output — blade compile, `view:cache`, lint. Run before any Blade diff is called ready for review. |
| `migration_check.py` | `company/os/agents/tier-1-architecture/data-schema-engineer/migration_check.py` | `bck-domain-engineer`, `bck-lead` (read-only cross-check) | Enforces "migration without rollback = rejected" — scans migration files, fails if any lacks a non-empty `down()`. Owned by `04-architecture`/`08-data`; this room reads its output to confirm the physical migrations `dat-db-engineer` executes still honor the reversible design before services are written against them. |
| `sofi_tools` shared library | `company/os/sofi_tools/` | all eight, via the `sofi` CLI | `brain` (read/write `_context/*`), `tickets` (Gate-4 ticket validation, Room Isolation Law check), `routing` (resolve `model·effort·caveman` for any `bck-*` id), `gates` (`validate_evidence`, `gates.yaml` loader), `guard` (`assert_within_project`, `assert_net_allowed`). |
| `sofi` CLI | `company/os/bin/sofi` | all eight | `sync`, `checkpoint`, `claim`/`release`, `worktree`, `gate-merge`, `gate-check`, `gate-tag`, `dispatch`, `escalate`, `brain-query` — the mechanical spine of every step in both playbooks. |
| `feature_scan.py` + `spec_review_preflight.py` | `company/os/agents/ceo/` | `bck-lead` (before routing a request to `arc-review-architect`'s `/sofi-spec-review`) | 0-token static location + 4-pillar pre-flag pass, shared across rooms — the Phase-1 scan behind any spec-review this room's work triggers. |
| `gemini_bridge.py` + `gemini_review.py` | `company/os/agents/ceo/` | `bck-lead` (oracle desk, Teaching VII, at genuine decision points — e.g. a contested money-math edge case or a webhook redelivery assumption that survived one mediation round and needs a family-diverse second opinion) | Sanitize → push → capture → digest-ingest, same oracle desk every room shares. |

Web access itself is not a "tool" in the scanner sense — no `bck-*` agent's `.claude/agents/<id>.md` frontmatter grants `WebSearch`/`WebFetch`. `bck-integration-engineer`'s vendor-documentation confirmation needs route through `res-lead`'s room (`res-web-scout`) via `bck-lead`, same path any other dev room uses for a bounded live-web need.

## What a new Backend tool would look like

A genuinely new script belongs at `company/rooms/05-backend/tools/<name>.py`, only when no existing script in `company/os/sofi_tools`, `company/os/agents/uiux/`, `company/os/agents/ceo/`, or `company/os/agents/tier-1-architecture/` already covers the job — check `company/nexus/registry.yaml` and `company/os/GOVERNANCE.md`'s promotion ladder before writing anything (Article 00 §5, "arm up"). Header contract, mandatory:

```python
#!/usr/bin/env python3
"""
<name> — <one-line purpose>
Owner: <agent id, e.g. bck-queue-engineer>
Gate(s): 4
Exit contract: 0 = <meaning>, non-zero = <meaning>
"""
```

Candidates that would justify a new Backend-owned script (none exist yet — build only on real recurring need):

- An idempotency-key linter for `bck-queue-engineer` that mechanically flags any job class whose `handle()` mutates persisted state with no accompanying unique-constraint migration or dedup-key lookup — the arithmetic half of steel rule 4, leaving only the judgment call (is the constraint the *right* one) to the model.
- A contract-drift checker for `bck-api-engineer` that mechanically diffs a controller's actual response payload shape (via a quick test-run capture) against the fields `OpenAPI.yaml` declares for that endpoint, flagging any field present in one and absent in the other before `bck-code-reviewer`'s pass spends model tokens re-deriving the same diff by eye.
- A money-math invariant scanner for `bck-domain-engineer` that mechanically flags any file touching a `buy`/`sell`/`spread`/`margin`-named field where a `float`/`double` type is used instead of a fixed-precision decimal type — the mechanical half of steel rule 5, before a model has to read every money-adjacent line to catch a type slip.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.05-backend` and get an entry in this table — never silently added.
