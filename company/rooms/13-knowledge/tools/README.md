# Room 13-knowledge — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`) or the org brain (`company/brain/org/`, for `knw-lead`'s and `knw-historian`'s org-level writes); none of this room's six agents hold Web tools — retrieval and doc-writing stay grep-first and codebase-first by design, never network-first.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner | What it does |
|---|---|---|
| `company/os/toolkit/core/reflection_engine.py` | `knw-reflector` | The room's standing backbone for scheduled dreaming — `scan --prj PRJ-XXXX [--since N]` mechanically locates NEW learning candidates (escalations, circuit-breaker trips, rejections, ≥3× recurring ticket-type patterns to the same target) at zero model tokens, deduped by `sig:` against what's already in `LESSONS.md`; `write --prj PRJ-XXXX --sig ... --situation ... --failed ... --rule ...` appends one distilled lesson, idempotently. Ported forward from v5's `ceo/`-housed reflection engine (built under `role: ceo-sofi`) and re-owned by this room in v6 — reflection is no longer a CEO-only act, it belongs to the Librarian's room, sequenced at gate close by `knw-lead`. |
| `company/os/sofi_tools/brain.py` | `knw-historian` (primary, `append_decision`/`append_context`), `knw-lead` (`read_state`, org governance) | The mechanical console behind `sofi brain`: `read_state`/`update_state` (STATE.md key:value), `append_context` (append-only CONTEXT bullets), `append_decision` (auto-incrementing `ADR-NNN`, the exact function `knw-historian`'s whole job runs on top of), `read_raw` (raw brain-file access for `knw-brain-query`'s rung-2 reads). |
| `company/os/sofi_tools/tickets.py` (`query`, `lesson_signatures`, `append_lesson`) | `knw-brain-query` (`query` — backs `sofi brain-query`'s structured filters), `knw-reflector` (`lesson_signatures`/`append_lesson` — the dedup and write mechanics under `reflection_engine.py`) | The shared ticket-and-lesson data layer: `query(prj, **filters)` is the case-insensitive substring filter engine behind `sofi brain-query <PRJ> status=blocked type=feature`; `lesson_signatures(prj)` returns every `sig:` already in `LESSONS.md` so reflection never re-surfaces a distilled candidate; `append_lesson` writes idempotently on `sig`. |
| `company/os/sofi_tools/guard.py` (`check_script_header`) | `knw-memory-curator` (any script this room writes), `knw-lead` (registry discipline) | Rule 8 enforcement — refuses an unowned or malformed-header script before it's promoted into `tools/`. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `knw-lead` | Confirms a gate actually closed (exit bar met) before this room's gate-close playbook runs — the mechanical trigger-confirmation step, never substituted for by "it's probably time." |
| `company/os/sofi_tools/paths.py` (`brain_file`, `project_dir`, `context_dir`) | every `knw-*` agent, indirectly | Resolves the correct brain-file path (project vs org) for every read/write this room performs — the reason project-scoped and org-scoped ledgers never get mixed by accident. |
| `company/os/caveman/integration.md` (`caveman-compress` contract) | `knw-memory-curator` | The vendored `caveman-compress` behavior contract this room's curator follows verbatim, including the `.original.md`-backup guarantee (~46% input reduction on compressible content, never on code/commits/security/rationale). Not a script this room owns — a vendored reference contract, applied by hand per `company/brain/BRAIN.md` §8's compressible/never-compressed split. |

No script above is owned exclusively by this room's *process* except the header/registry discipline itself — `reflection_engine.py` and the `sofi_tools` modules are the company's standing console, invoked here under each specialist's own agent id and logged to `.claude/memory/audit.jsonl`.

## What a new Knowledge tool would look like

A genuinely new script belongs at `company/rooms/13-knowledge/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/` or `company/os/toolkit/core/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. knw-memory-curator>
purpose: <one-line purpose>
gate:    cross
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network
(this room holds no Web tools on any agent).
"""
```

Candidates that would justify a new Knowledge-owned script (none exist yet — build only on real recurring need):

- A `memory_lint.py` for `knw-memory-curator` that mechanically walks every brain file, flags any past the ~300-line threshold with no compression pending, and cross-checks `type:`/`mem:`/`status:`/`sig:` frontmatter presence in one pass — the pre-flag `knw-memory-curator`'s hygiene sweep currently does by hand.
- A `memory_map_check.py` for `knw-lead` that resolves every pointer in `MEMORY.md` against the real filesystem and flags a dead link before it's discovered mid-boot by some other agent — the mechanical half of the room's own "every pointer resolves" bar.
- A `citation_verify.py` for `knw-brain-query` that batch-checks a proposed answer's `file:line` citations actually exist and match the claimed content, closing the last gap between "the answer looks cited" and "the citation is real."

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.13-knowledge` and get an entry in this table — never silently added.
