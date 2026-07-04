# ⚖️ Tooling Governance — the law for SOFI AI scripts

Every Python script an agent writes or runs obeys this. The rules are enforced in
code by `sofi_tools/guard.py`; a violation raises `GovernanceError` and the script
exits non-zero. **Scripts serve the work and never step outside it.**

> Doctrine echo: Design is Truth · few token do trick · a script that can't be
> trusted to stay in its lane is rejected, same as a migration without rollback.

## The ten rules

1. **Scope sandbox.** A *project* script writes only inside its own
   `projects/<PRJ-ID>/` tree. A *shared-library* change writes only inside
   `engine/tooling/`. Nothing ever writes outside the workspace root.
   → `guard.assert_within_project` / `assert_within_tooling` / `assert_within_repo`.

2. **Network policy.** A script may reach the internet **only if the running role
   holds Web tools** (see `protocols/tooling-matrix.md`). Devs, QA, content stay
   offline and pull web findings through their lead. → `guard.assert_net_allowed(role)`.

3. **Temp scripts are ephemeral.** Throwaway scripts for one task live in
   `projects/<PRJ-ID>/_scratch/`, named `tmp_<role>_<purpose>.py`. They are
   **purged at gate exit** (`sofi scratch <PRJ> clean`) and are **never** a
   deliverable. Nothing in `docs/` or `src/` may import from `_scratch/`.

4. **Shared scripts are earned.** To promote a script from `_scratch/` to the
   shared library or a per-role toolkit it must: (a) carry the governance header
   (Rule 8), (b) be registered in `registry.yaml`, (c) be reviewed by the role's
   lead. → `guard.check_script_header`.

5. **No destructive op without a safety net.** Any delete/overwrite of existing
   work requires an explicit `--confirm` flag **and** a backup first. Mirrors the
   "migration without rollback = rejected" rule.

6. **State changes are logged.** A script that mutates the brain appends a line to
   `_context/_runlog.md` (and `CONTEXT.md` when it changes durable facts).
   → `runlog.log(...)`.

7. **No hardcoded secrets.** Secrets come from environment/vault, never literals.
   Promotion scans for secret patterns and refuses on a hit. → `guard.scan_secrets`.

8. **Header contract.** Every shared/promotable script starts with a header block
   containing at least: `role:` (owner), `purpose:`, `gate:`, `inputs:`,
   `outputs:`, `exit:` (what each exit code means).

9. **Deterministic + idempotent.** Same inputs → same result. Re-running a tool
   must not corrupt the brain or double-append. No wall-clock/randomness inside
   tools — timestamps are passed in by the CEO (who owns the clock).

10. **Exit codes gate the pipeline.** `0` = pass, non-zero = a real failure CI can
    block on. Quality/security tools must fail the build, not warn.

## Who may run Bash/scripts
Per `tooling-matrix.md`: CEO, all leads, architects, security, devs, QA-automation,
perf, DevOps/CI/containers/SRE hold Bash. Pure-research/design roles
(strategist, UX researcher, journey, UI, content, manual tester) do **not** run
scripts — they think and write specs.

## Lifecycle of a script
```
need a one-off?        → projects/<PRJ>/_scratch/tmp_<role>_<purpose>.py   (Rule 3)
   ↓ proved useful, reusable, headered, reviewed                          (Rule 4)
promote → per-role toolkit  engine/tooling/agents/<tier>/<role>/<name>.py
   ↓ used by 2+ roles
promote → shared library    engine/tooling/sofi_tools/<module>.py
   ↓ always
register in registry.yaml + log the promotion decision in DECISIONS.md
```
