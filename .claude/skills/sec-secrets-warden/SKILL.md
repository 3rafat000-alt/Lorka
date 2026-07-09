---
name: sec-secrets-warden
description: "Automated secret scanning, .env/vault hygiene, immediate rotation on anomaly."
---
# Security - Secrets Warden

Scan repo for secrets, .env, keys, and credential leaks.

## Tool
`.claude/tools/sec/secrets-warden/secret-scan.sh`

## When to use
- Pre-commit or pre-PR secret leak check
- CI pipeline security gate
- Periodic credential rotation verification
- Incident response — leaked key discovery scope

## How to use
```bash
.claude/tools/sec/secrets-warden/secret-scan.sh --prj PRJ-XXXX [--path dir] [--exit-on-find]
```

## Input
PRJ-ID or explicit path. Scans for AWS keys, GitHub tokens, generic secrets, .env file patterns. `--exit-on-find` sets non-zero exit for CI gates.

## Output
Per-pattern list of matched secrets with file:line locations. Exit code 0 = no secrets found.

## Related
- `engine/agents/sec/sec-secrets-warden.md`
- `.claude/tools/sec/secrets-warden/secret-scan.sh`
