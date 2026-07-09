---
name: bck-domain-engineer
description: "Services, business logic, money math (buy≥sell, precision, invariants)."
---
# Backend - Domain Engineer

Generate service class with interface and stub methods. Enforces contract-first design by creating a matching Interface + Implementation + AppServiceProvider bind hint.

## Tool
`.claude/tools/bck/domain-engineer/service-gen.sh`

## When to use
- New domain service: generate interface + implementation from service name
- Gate 4 domain layer: contract-first service design
- Refactoring toward interfaces: introduce ServiceInterface pattern

## How to use
```bash
.claude/tools/bck/domain-engineer/service-gen.sh <PRJ-ID> <ServiceName> [methods]
```

## Input
- `PRJ-ID` — project directory
- `ServiceName` — PascalCase service name (e.g. `Payment`)
- `methods` — comma-separated method names (e.g. `process,validate,refund`)

## Output
- `app/Services/Contracts/{Name}Interface.php` — interface with declared method signatures
- `app/Services/{Name}Service.php` — implementation with method stubs
- Console hint for AppServiceProvider bind line

## Related
- `engine/agents/bck/domain-engineer.md`
- `.claude/tools/bck/domain-engineer/service-gen.sh`
