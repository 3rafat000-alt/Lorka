---
name: arc-infra-architect
description: "Network segmentation, scaling strategy, disaster recovery posture."
---
# Architecture - Infrastructure Architect

Scan network, scaling, backup, and health-check posture of a project. Identify infrastructure gaps before Gate 3 signoff.

## Tool
`.claude/tools/arc/infra-architect/infra-scan.sh`

## When to use
- Gate 3: infrastructure readiness audit
- Pre-deployment: verify Docker, scaling config, and backup scripts exist
- Periodic review: check for missing health endpoints or DR plans

## How to use
```bash
.claude/tools/arc/infra-architect/infra-scan.sh <PRJ-ID|--self>
```

## Input
- `PRJ-ID` — project directory, or `--self` to scan the SOFI framework
- Scans for Docker config, deploy configs (Procfile, fly.yaml, render.yaml), backup scripts, health endpoints, and resource env vars

## Output
- Network section: Dockerfile/docker-compose presence
- Scaling section: deploy platform configs found
- Backup/DR section: backup scripts in database/
- Health Checks section: routes with health check patterns
- Resource Config section: DB/REDIS/QUEUE vars from `.env.example`

## Related
- `engine/agents/arc/infra-architect.md`
- `.claude/tools/arc/infra-architect/infra-scan.sh`
