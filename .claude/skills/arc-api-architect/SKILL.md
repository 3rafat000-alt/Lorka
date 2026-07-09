---
name: arc-api-architect
description: "Frozen OpenAPI/GraphQL contract, webhook shapes."
---
# Architecture - API Architect

Validate OpenAPI spec paths against registered Laravel routes. Detect endpoints in routes but missing from spec, or vice versa.

## Tool
`.claude/tools/arc/api-architect/openapi-validate.sh`

## When to use
- Gate 3: validate API spec before architecture freeze
- Post-implementation: confirm spec matches actual routes
- Code review: catch undocumented or drifted endpoints

## How to use
```bash
.claude/tools/arc/api-architect/openapi-validate.sh <PRJ-ID> [--routes-only]
```

## Input
- `PRJ-ID` — project with `docs/api/openapi.yaml` and/or `routes/` directory
- `--routes-only` — only show registered Laravel routes (skip spec comparison)

## Output
- List of OpenAPI spec paths extracted from `openapi.yaml`
- List of registered Laravel routes from `php artisan route:list` or route file grep
- Manual comparison tip for finding gaps

## Related
- `engine/agents/arc/api-architect.md`
- `.claude/tools/arc/api-architect/openapi-validate.sh`
