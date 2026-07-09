---
name: bck-api-engineer
description: "Endpoints per frozen contract — 422-JSON rule, no redirects."
---
# Backend - API Engineer

Scaffold a complete Laravel API endpoint: FormRequest, Controller, Service, API Resource, and test stub. Generates from endpoint name and HTTP method.

## Tool
`.claude/tools/bck/api-engineer/endpoint-scaffold.sh`

## When to use
- New REST endpoint: generate all layers at once from endpoint name
- Gate 4 backend implementation: rapid scaffold for each OpenAPI path
- Prototyping: get a working endpoint skeleton in seconds

## How to use
```bash
.claude/tools/bck/api-engineer/endpoint-scaffold.sh <PRJ-ID> <endpoint-name> [method]
```

## Input
- `PRJ-ID` — project directory
- `endpoint-name` — kebab-case name (e.g. `create-user`, `list-orders`)
- `method` — HTTP method (GET|POST|PUT|DELETE, default: POST)

## Output
- `app/Http/Requests/{Name}Request.php` — FormRequest with authorize + rules stubs
- `app/Http/Controllers/API/{Name}Controller.php` — single-action controller injecting service
- `app/Services/{Name}Service.php` — service with `execute()` stub
- `app/Http/Resources/{Plural}Resource.php` — API Resource extending JsonResource
- `tests/Feature/` directory if missing

## Related
- `engine/agents/bck/api-engineer.md`
- `.claude/tools/bck/api-engineer/endpoint-scaffold.sh`
