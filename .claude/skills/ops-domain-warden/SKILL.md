---
name: ops-domain-warden
description: "Local domains + public tunnels (seed-only, bounded)."
---
# Operations - Domain Warden

Check local domain + tunnel health.

## Tool
`.claude/tools/ops/domain-warden/domain-health.sh`

## When to use
- Local dev domain resolution check
- Tunnel (cloudflared/localtunnel) health check
- Certificate expiry monitoring
- Post-scaffold domain setup verification

## How to use
```bash
.claude/tools/ops/domain-warden/domain-health.sh [--prj PRJ-XXXX] [--domain <slug>.local] [--check dns|tunnel|cert|all]
```

## Input
PRJ-ID (derives <slug>.local) or explicit domain. `--check` narrows to DNS resolution, tunnel status, or HTTPS cert.

## Output
Per-check pass/fail. DNS (resolves to expected IP), tunnel (endpoint reachable), cert (expiry, chain).

## Related
- `engine/agents/ops/ops-domain-warden.md`
- `.claude/tools/ops/domain-warden/domain-health.sh`
