# 🚨 Incident Response & Disaster Recovery

> **Foundation:** This protocol serves Teaching **V (Continuous Metamorphosis)** — a production incident triggers a feedback loop that re-enters at Gate 1 — and Teaching **VI (Reversibility Principle)** — rollback is the first response, not the last resort. Also: Security is always normal prose, never caveman (Doctrine §4 override). Read `engine/DOCTRINE.md` before this file.

Harvested + adapted from the old SOFI teams' emergency playbook. Copy-paste-ready runbook for when production breaks. Owners: **Linda** (DevOps, Gates 6–7) + **Naomi** (SRE, Gate 8). A breach here auto-files an issue → re-enters at **Gate 1**.

> Principles: **Don't panic. Stop the bleeding first. Log everything. Tell the team. Write the post-mortem.** Deploy/rollback confirmations are normal prose — never caveman, never silent.

## Scenario 1 — Infrastructure failure (502/503, latency spike, dashboard down)
```bash
# 1. health
kubectl get pods -n prod          # or: systemctl status <svc>
kubectl top nodes; kubectl top pods -n prod
# 2. logs (last 5 min)
kubectl logs -l app=<svc> -n prod --since=5m --tail=200
# 3. restart the unhealthy workload
kubectl rollout restart deploy/<svc> -n prod
# 4. still failing → Blue/Green rollback to last healthy release (tested script — see Gate 7)
./deploy/rollback.sh        # or: kubectl rollout undo deploy/<svc> -n prod
```
Recover: document cause in `projects/<PRJ>/_context/DECISIONS.md`, tune Prometheus/Grafana alerts, file a Gate-1 ticket for the root fix.

## Scenario 2 — Security breach (anomalous logs, unauthorized access, unexpected code change)
```bash
# 1. isolate — take the affected node off the network
# 2. revoke — rotate ALL secrets/keys NOW (vault), invalidate sessions/tokens
# 3. preserve evidence — snapshot logs before they roll
kubectl logs -l app=<svc> -n prod --since=2h > /tmp/incident-$(date +%s).log
# 4. patch the vector, redeploy from a known-good signed image
# 5. notify per disclosure policy
```
Owner escalates to **Ruth** (Security) immediately. Never compress or hide a security warning. Post-mortem mandatory.

## Scenario 3 — Data loss / bad migration
```bash
# 1. STOP writes (maintenance mode / scale to 0 the writer)
# 2. restore from the latest verified backup
# 3. replay the reversible migration's down() path  (no migration ships without rollback — Gate 3 rule)
php artisan migrate:rollback --step=1
```
If a migration lacked a rollback, that's a Gate-3 violation — file it.

## Scenario 4 — Deploy failure (pipeline red / unhealthy after release)
```bash
# 1. do NOT promote; keep traffic on the old (Blue) color
# 2. read the failed stage (Harness): lint → test → build → scan → deploy
# 3. green path or rollback; never hand-patch prod
```
Owner: **Tomás** (CI/CD) + Linda. Gate 7 requires a tested rollback ready before rollout.

## Scenario 5 — Total outage / DR
1. Declare the incident, assign a single commander.
2. Spin the DR environment from IaC (Terraform/Helm — reproducible by design).
3. Restore data from backup; verify integrity before reopening traffic.
4. Reopen gradually (canary), watch SLOs.

## Post-mortem template (write into `_context/DECISIONS.md`)
```
# Incident <date> — <one-line title>
Impact:        <who/what, duration>
Timeline:      <detection → mitigation → resolution, with timestamps>
Root cause:    <the real cause, not the symptom>
What worked / what didn't:
Action items:  <owner · gate · ticket-id>   ← these become Gate-1 tickets
```
Blameless. The lesson loops back into the pipeline.
