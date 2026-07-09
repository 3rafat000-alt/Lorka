---
description: "Deploy to staging then production with rollback plan. Use: /deploy <version-tag>"
argument-hint: "[description]"
---
> **Lead persona:** `ops-lead` — the main session *wears* this persona (`.claude/agents/ops-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# Deploy: $ARGUMENTS

1. `@ops-cicd-engineer` — verify CI pipeline green
2. `@ops-cloud-engineer` — confirm IaC parity
3. `@ops-release-manager` — Blue/Green deploy with tested rollback
4. `@ops-migration-runner` — run migrations with proven rollback
5. `@ops-domain-warden` — DNS/SSL/domain config

After deploy:
6. `@obs-monitoring-engineer` — verify signals on dashboards
7. `@obs-alerting-engineer` — confirm alert rules fire

Report deploy status to CEO.
