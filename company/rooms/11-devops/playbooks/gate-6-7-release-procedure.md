# Playbook — Gate 6-7 Release Procedure

> Owner: `ops-lead`. The room's core procedure — the path from a confirmed Quality PASS to a live, healthy, rollback-proven production system. Binding for every `11-devops` release; no shortcut collapses staging into production, no matter how simple the release feels.

## 0. Preconditions — before this room touches anything

`ops-lead` confirms, before assigning a single ticket:

```bash
sofi sync <PRJ>                                   # never blind — orient on branch + head_sha
sofi gate-check --gate 5 --prj <PRJ>               # mechanical: qa-lead's PASS actually recorded?
```

If `gate-check --gate 5` is not green, or the PASS ticket in `HANDOFFS.md` reads BLOCK or is missing an evidence block: **stop, reject upward to `qa-lead`.** This room does not deploy against an assumed pass.

## 1. Gate 6 — Staging / UAT

**Step 1.1 — Pipeline confirmed green (`ops-cicd-engineer`, Tomás)**

```bash
sofi git-check <PRJ>                               # secrets-in-history + branch discipline first
# then the pipeline's own dry run — lint → test → build → scan → deploy(staging)
```
No inline secrets, security-scan stage active, every stage's exit code pasted into the ticket.

**Step 1.2 — Staging provisioned in parity with prod (`ops-cloud-engineer`, Baasan)**

Reads `arc-lead`'s frozen `Tech_Stack.md` + infra posture, provisions staging as code:

```bash
# infra-as-code apply against the staging workspace, per the frozen posture
# paired teardown script written alongside — never provisioned without one
```

**Step 1.3 — Local domain confirmed / staging URL live (`ops-domain-warden`, Noemi)**

```bash
sofi domain register <PRJ>          # idempotent — already done at scaffold, confirm here
sofi domain up <PRJ>                 # brings <slug>.local live for this environment
sofi domain status                   # paste as evidence: URL + port recorded in STATE.md
```

**Step 1.4 — Migration rollback rehearsed BEFORE any real migration runs (`ops-migration-runner`, Tendai)**

```bash
# 1. snapshot real staging-shaped data
# 2. run the forward migration against the snapshot
# 3. run the rollback
# 4. inspect the restored data directly — not just the rollback command's exit code
```
Only after this rehearsal passes with pasted evidence does the real migration run against staging.

**Step 1.5 — UAT (`ops-lead` coordinates, reads the log herself)**

Simulated or real UAT runs against the staging URL; every finding is logged with reproduction steps in `docs/<PRJ>_UAT_Log.md`. `ops-lead` reads the log directly — she does not accept a specialist's summary in place of it.

**Step 1.6 — pass^k re-run on critical paths (Article 03 V3)**

Critical-path checks (money/auth/PII surfaces `qa-test-architect` flagged Tier-A at Gate 5) re-run `k` times against the staging environment. A flaky result here blocks Gate 6 exactly as it would have blocked Gate 5.

**Step 1.7 — Gate 6 close**

```bash
sofi gate-check --gate 6 --prj <PRJ>
sofi gate-tag <PRJ> 6                              # <PRJ>-gate6-done, immutable restore point
```

## 2. Gate 7 — Production

**Step 2.1 — Rollback rehearsal, application layer (`ops-release-manager`, Camille)**

Camille rehearses the Blue/Green rollback against a real staging-like condition — deploys a deliberately broken health check, confirms the automated rollback trigger (Tomás's pipeline config) actually fires and actually restores the prior color. Restored state confirmed by direct inspection, never by trusting the exit code alone (Article 03 V4).

```bash
# trigger a synthetic health-check failure on the Green (candidate) color
# confirm automatic rollback to Blue fires within its stated window
# confirm Blue is serving correctly post-rollback
```

**Step 2.2 — Sequencing agreement (Camille + Tendai)**

Camille and Tendai explicitly confirm: if the release needs rolling back, does the data-layer rollback (Tendai) run before or after the application-layer rollback (Camille)? This is written down, not assumed, before cutover.

**Step 2.3 — Monitoring confirmed live (`ops-lead` ↔ `obs-lead`)**

`ops-lead` confirms with `obs-lead` that monitoring hooks are wired and reporting before authorizing cutover. No telemetry, no deployment (Teaching V).

**Step 2.4 — Blue/Green cutover (Camille executes, Linda authorizes)**

```bash
# verify Green (candidate) healthy
# verify Blue (current) still healthy, kept warm
# shift traffic to Green deliberately
# hold the confirmation window; keep Blue warm as the tested way back
# health checks pasted as evidence at each step
```

**Step 2.5 — Gate 7 close**

```bash
sofi gate-check --gate 7 --prj <PRJ>
sofi gate-tag <PRJ> 7
sofi checkpoint <PRJ> "release: gate-7 prod cutover, rollback rehearsed and proven"
```

## 3. Handoff to Observability

`ops-lead` hands the live production system to `obs-lead`, monitoring already confirmed live — this handoff is what opens Gate 8. `docs/<PRJ>_Release_Notes.md` and the accountability report go to `brd-ceo` the same cycle.

## Rules

- No step in this playbook runs out of order — staging before production, rehearsal before real execution, always.
- Every step's evidence is pasted into its ticket before the next step starts; a verbal "it worked" is not evidence (Article 03 V1).
- A `09-security` veto at any step freezes the whole procedure immediately — `ops-lead` does not negotiate past it.
- If any step fails twice under correction, the third attempt is the circuit-breaker's last try; a fourth failure halts with a structured crash dump and an escalation ticket, never a fourth silent retry.
