---
name: bck-blade-engineer
description: "Blade layouts and components, every page covers all states."
---
# Backend - Blade Engineer

Generate a Laravel Blade component (class + view) with typed properties. Creates the PHP View Component class and the `.blade.php` template in one command.

## Tool
`.claude/tools/bck/blade-engineer/blade-gen.sh`

## When to use
- New Blade component: generate class and view from component name
- Gate 4 Blade templates: rapid component creation for UI layer
- Prototyping forms and cards: typed props reduce boilerplate

## How to use
```bash
.claude/tools/bck/blade-engineer/blade-gen.sh <PRJ-ID> <component-name> [props]
```

## Input
- `PRJ-ID` — project directory
- `component-name` — kebab-case name (e.g. `user-profile`, `order-card`)
- `props` — comma-separated `name(type)` pairs (e.g. `name(string),count(int)`)

## Output
- `app/View/Components/{Pascal}.php` — component class with typed public properties
- `resources/views/components/{kebab}.blade.php` — view with `$attributes->merge()` and `$slot`
- Usage hint: `<x-component-name />`

## Related
- `engine/agents/bck/blade-engineer.md`
- `.claude/tools/bck/blade-engineer/blade-gen.sh`
