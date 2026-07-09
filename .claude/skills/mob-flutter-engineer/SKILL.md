---
name: mob-flutter-engineer
description: "Clean architecture feature-first (GetIt DI, DTO matching contract)."
---
# Mobile - Flutter Engineer

Scaffold a Flutter feature with clean architecture layers: `data/`, `domain/entities`, `domain/repositories`, `domain/usecases`, `presentation/`. Generates entity, repository interface, and use case stubs.

## Tool
`.claude/tools/mob/flutter-engineer/feature-scaffold.sh`

## When to use
- New Flutter feature: scaffold clean architecture directory structure
- Gate 4 mobile implementation: rapid feature creation with established layers
- Consistent project structure: every feature follows data/domain/presentation separation

## How to use
```bash
.claude/tools/mob/flutter-engineer/feature-scaffold.sh <PRJ-ID> <feature-name>
```

## Input
- `PRJ-ID` — project directory with `lib/`
- `feature-name` — kebab-case name (e.g. `user-profile`, `order-tracking`)

## Output
- Directory structure: `lib/features/{name}/{data,domain,presentation}` with subdirectories
- `domain/entities/{Name}.dart` — entity class with id field
- `domain/repositories/{Name}Repository.dart` — abstract repository with `getById`
- `domain/usecases/Get{Name}.dart` — use case class calling repository
- GoRouter import hint

## Related
- `engine/agents/mob/flutter-engineer.md`
- `.claude/tools/mob/flutter-engineer/feature-scaffold.sh`
