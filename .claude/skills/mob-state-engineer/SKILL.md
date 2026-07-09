---
name: mob-state-engineer
description: "Bloc/Cubit state, all states covered, Hydrated persistence."
---
# Mobile - State Engineer

Generate a Flutter Bloc or Cubit with sealed state classes. Supports full Bloc (with events) or simpler Cubit pattern. Generates state, event, and implementation files.

## Tool
`.claude/tools/mob/state-engineer/bloc-gen.sh`

## When to use
- New Bloc/Cubit: scaffold state management for a feature
- Gate 4 mobile state layer: generate Initial/Loading/Loaded/Error states
- Transitioning from Cubit to Bloc: use `--cubit` for simpler, omit for full events

## How to use
```bash
.claude/tools/mob/state-engineer/bloc-gen.sh <PRJ-ID> <BlocName> [--cubit]
```

## Input
- `PRJ-ID` — project directory with `lib/`
- `BlocName` — PascalCase bloc name (e.g. `Auth`)
- `--cubit` — generate Cubit instead of full Bloc (no event classes)

## Output
- `lib/bloc/{name}/{name}_bloc.dart` — Bloc with event handlers (or Cubit)
- `lib/bloc/{name}/{name}_event.dart` — sealed event classes (Bloc only)
- `lib/bloc/{name}/{name}_state.dart` — sealed state classes (Initial, Loading, Loaded, Error)
- Import hint: `{Name}Bloc()` or `{Name}Cubit()`

## Related
- `engine/agents/mob/state-engineer.md`
- `.claude/tools/mob/state-engineer/bloc-gen.sh`
