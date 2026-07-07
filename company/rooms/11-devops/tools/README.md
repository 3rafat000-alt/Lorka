# Room 11-devops — Tools

> Governance: `company/os/GOVERNANCE.md` (10 rules) binds every script this room touches. Header rule (Rule 8): every shared/promotable script starts with a header block containing at least `role:` (owner agent id), `purpose:`, `gate:`, `inputs:`, `outputs:`, `exit:` (what each exit code means) — `guard.check_script_header` fails closed on an unowned script. Scripts write only inside their own project tree (`projects/<PRJ-ID>/`); network access only for the specialist whose spawnable frontmatter grants `WebSearch`/`WebFetch` (`ops-cloud-engineer` — infra research, dependency/pricing lookups) — every other `ops-*` agent routes research needs through `ops-cloud-engineer` or through `ops-lead`.

## Existing tools this room uses (real paths, grep-verified)

| Tool | Owner | What it does |
|---|---|---|
| `company/os/sofi_tools/domain.py` (`sofi domain register/up/down/list/rm/status/init`) | `ops-domain-warden` | The full local-domain console: registers a project's `<slug>.local` (allocates a port, writes a Caddy vhost, updates `/etc/hosts` via the repo helper), brings it up/down, lists all registered domains, tears one down. `cmd_register`/`cmd_up`/`cmd_down`/`cmd_status` are the exact operations behind every `sofi domain` invocation in the Gate-0-through-Gate-7 lifecycle. This is Noemi's primary console — she runs nothing else to do her core job. |
| `company/os/sofi_tools/tunnel.py` (`sofi tunnel up/down/list/status`) | `ops-domain-warden` (owner, Article 07 §5); `ops-cicd-engineer` may open one for a webhook test | The bounded public-tunnel mechanism: resolves a provider (cloudflared preferred, localtunnel fallback), forces the client's Host through the shared Caddy `:80`, awaits the assigned URL, stamps `public_url` into `STATE.md`, and tears it down cleanly on `cmd_down`. Every tunnel this room opens runs through this module — no ad hoc `ngrok`/manual reverse-proxy setup, ever. |
| `company/os/agents/devops/caddy_isolation.py` | `ops-cloud-engineer` (primary), `ops-domain-warden` (indirect, via the port allocation it protects) | Phase-2 resource isolation: `acquire_project_lock`/`release_project_lock` give each project squad an exclusive, non-blocking lock on its port range and DB socket (`_context/.locks/`), `generate_dynamic_caddyfile` builds the per-project Caddy subdomain config, `release_stale_lock` reclaims an orphaned lock after a 4-hour timeout, `validate_no_collision` confirms two squads never silently share a resource. This is the mechanical backbone behind Baasan's "no environment collision across projects" bar. |
| `company/os/agents/tier-1-architecture/data-schema-engineer/migration_check.py` | `ops-migration-runner` (deploy-time re-check), `dat-db-engineer` (original Gate-3/Gate-4 owner) | Enforces "migration without rollback = rejected" mechanically: scans a migration file or directory (Laravel/PHP or raw SQL) and fails (`exit 1`) if any migration lacks a non-empty `down()`/rollback path. `ops-migration-runner` re-runs this at deploy time as the static half of his rehearsal — necessary, never sufficient on its own; the dynamic rehearsal (forward → rollback → direct-inspection confirm, `playbooks/blue-green-rollback-rehearsal.md`) is his own addition on top of it. |
| `company/os/sofi_tools/gates.py` (`sofi gate-check`) | `ops-lead` | Mechanical Gate-6/Gate-7 validation against `company/nexus/gates.yaml` (`id: 6` and `id: 7`) — artifact existence (staging URL, UAT log, rollback rehearsal log, release notes), evidence-block presence, no room-boundary violations. Runs before any adversarial verify (`gtw-gatekeeper`), never substitutes for one. |
| `company/os/sofi_tools/gitops.py` (`sofi git-check`) | `ops-lead` (before every checkpoint the room signs), `ops-cicd-engineer` (pipeline's own pre-deploy step) | Mechanical secret-in-history audit + git-discipline checks (branch correctness, uncommitted drift) — the first thing the pipeline confirms before a single deploy stage runs, and the check `ops-lead` re-runs before signing the Gate-6/Gate-7 accountability report. |
| `company/os/agents/ceo/sofi_scan.py` (`security` mode) | `ops-cicd-engineer` (pipeline's scan stage, alongside deeper `09-security` review) | The zero-token static security sweep the pipeline's own `scan` stage opens with, ahead of anything `09-security` runs deeper on a contested finding — pre-flags hardcoded secrets, weak randomness, missing-auth patterns before a human/model reviews the diff. |

No script above is owned exclusively by this room's *process* except the two the room itself operates end to end (`domain.py`, `tunnel.py`, and the isolation script) — `migration_check.py`, `gates.py`, and `gitops.py` are the company's standing console, invoked here under the specialist's own agent id and logged to `.claude/memory/audit.jsonl`.

## What a new DevOps tool would look like

A genuinely new script belongs at `company/rooms/11-devops/tools/<name>.py`, only when no existing script in `company/os/sofi_tools/`, `company/os/agents/devops/`, or `company/os/agents/tier-1-architecture/data-schema-engineer/` already covers the job — check `company/nexus/registry.yaml`'s `tools:` section and `company/os/GOVERNANCE.md`'s registry rule before writing anything (Article 00 §5, "arm up"). Header contract, mandatory (Rule 8):

```python
#!/usr/bin/env python3
"""
role:    <owner agent id, e.g. ops-release-manager>
purpose: <one-line purpose>
gate:    6|7|cross
inputs:  <what the script reads, and how — path/stdin/flags>
outputs: <what it produces — stdout report, a file, JSON>
exit:    0 ok · <N> <specific failure meaning>

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network unless the
owning role holds Web tools.
"""
```

Candidates that would justify a new DevOps-owned script (none exist yet — build only on real recurring need):

- A `rollback-rehearsal-log.py` for `ops-release-manager` that structures the Blue/Green rehearsal's evidence into a single machine-checkable artifact (trigger definition, rehearsal commands, direct-inspection confirmation, sequencing agreement) so `sofi gate-check --gate 7` can validate its presence and shape mechanically instead of trusting a free-text ticket note.
- A `parity-diff.py` for `ops-cloud-engineer` that mechanically diffs staging's applied infra-as-code state against production's, flagging any drift the moment it appears rather than waiting for a specialist to notice by eye.
- An `idle-resource-scan.py` for `ops-cost-optimizer` that reads a cloud provider's utilization export and flags anything under a stated threshold for N consecutive days — closing the same gap her manual review does today, at zero model tokens.

Any of these, once real, register in `company/nexus/registry.yaml` under `tools.11-devops` and get an entry in this table — never silently added.
