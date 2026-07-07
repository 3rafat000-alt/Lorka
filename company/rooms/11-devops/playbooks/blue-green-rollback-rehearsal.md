# Playbook — Blue/Green Rollback Rehearsal (the room's sharpest recurring job)

> Owner: `ops-release-manager` (Camille), with `ops-cicd-engineer` (Tomás) on the trigger definition and `ops-migration-runner` (Tendai) on data-layer sequencing. This is the procedure Article 03 V4 and Teaching VI exist to enforce: **a rollback that has never been rehearsed is not a rollback, it is a written hope.** Every production cutover this room ships runs this playbook first — no exceptions for a release that "should be simple."

## Why this is the sharpest recurring job in the room

Every other deliverable in `11-devops` is verified once and moves on. A rollback is different: it has to still work on the day it's actually needed, which is precisely the day everything else is going wrong. That means it can't be verified by reading the script — it has to be *run*, deliberately, against conditions that resemble the failure it's meant to survive. This is the one piece of work this room repeats, unchanged in structure, on every single release.

## 1. Define the trigger — explicitly, in writing

Before any rehearsal, Camille and Tomás agree on the exact failing condition that fires the rollback:

- What health check, specifically? (e.g., `/health` returning non-200 for N consecutive checks, error rate over X% for Y minutes, p99 latency over Z ms.)
- What is the automated trigger's window — how long does it wait before firing?
- Who is the named owner if the automated trigger doesn't fire and a manual pull is needed? (Default: Camille, unless `ops-lead` names someone else for this specific release.)

This gets written into the ticket **before** the rehearsal starts — a rehearsal against an undefined trigger tests nothing.

## 2. Rehearse the application-layer rollback

```bash
# 1. Deploy the candidate (Green) color to the environment
# 2. Deliberately introduce the failing condition defined in Step 1
#    (a synthetic bad health-check response, an intentionally broken endpoint)
# 3. Confirm the automated trigger fires within its stated window
# 4. Confirm traffic returns cleanly to Blue (the known-good color)
# 5. Confirm Blue serves correctly post-rollback — not just that traffic moved,
#    that the application actually works there
```

Evidence pasted into the ticket: the exact commands run, their exit codes, and — critically — a direct check that the post-rollback system is actually healthy, not an inference from the rollback command completing.

## 3. Rehearse the data-layer rollback, if the release includes a migration

This step runs in coordination with `ops-migration-runner`'s own rehearsal (`playbooks/gate-6-7-release-procedure.md` §1.4) — the two are sequenced, not independent:

```bash
# 1. Confirm Tendai's forward+rollback rehearsal already passed
# 2. Confirm explicitly, in writing: if BOTH layers roll back, which runs first?
#    (Typically: freeze traffic → application-layer rollback → data-layer rollback,
#    but a release that migrated data the new app version depends on may reverse this —
#    name the actual order for THIS release, never assume last time's order still applies.)
```

A release ships only once this sequencing is written down and both specialists have signed off on it.

## 4. Confirm restored state by direct inspection

The single rule that separates a real rehearsal from theater: **never trust an exit code alone.**

- Application layer: hit the actual endpoint post-rollback, confirm the actual response, not just "the deploy command returned 0."
- Data layer: query the actual restored data, compare it against a pre-migration snapshot, confirm it matches — not just "the rollback script exited 0."

This is Article 03 V4 in practice: behavioral proxies only (exit 0, artifact exists, k runs pass, the data is verifiably back) — never verbalized confidence ("I'm confident this rolled back correctly").

## 5. File the evidence and clear the release

```bash
# rehearsal log written to the ticket: trigger definition, rehearsal commands + output,
# direct-inspection confirmation, sequencing agreement (if data-layer involved)
sofi checkpoint <PRJ> "release: rollback rehearsed and proven for gate-7 cutover"
```

Only once this is filed does `ops-lead` authorize the actual Gate-7 cutover (`playbooks/gate-6-7-release-procedure.md` §2.4).

## Rules

- A rollback rehearsal that was skipped "because this release is simple" is not a smaller version of this playbook — it is a missing step, full stop.
- A rehearsal run once, long ago, on a different release shape does not carry forward — every release gets its own rehearsal, because every release changes what "restored state" actually means.
- If the rehearsal fails, the release does not ship — the fix is to the rollback (or the release), never to the rehearsal's rigor.
- Rehearsal results, pass or fail, are always written in normal prose — never caveman-compressed. A summarized rollback failure is exactly the kind of thing compression would hide.
