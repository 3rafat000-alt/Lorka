---
name: fnt-vue-engineer
description: "Typed Vue 3 components + Pinia state wired to contract."
---
# Frontend - Vue Engineer

Scaffold a Vue 3 component with Composition API and `<script setup>`. Optionally generate a matching Pinia store.

## Tool
`.claude/tools/fnt/vue-engineer/vue-component.sh`

## When to use
- New Vue 3 component: scaffold from component name with typed props
- Gate 4 frontend implementation: rapid component creation with Pinia integration
- Adding store state: `--store` flag generates a full Pinia store alongside the component

## How to use
```bash
.claude/tools/fnt/vue-engineer/vue-component.sh <PRJ-ID> <ComponentName> [--store] [props...]
```

## Input
- `PRJ-ID` — project directory
- `ComponentName` — PascalCase component name (e.g. `UserCard`)
- `--store` — also generate a Pinia store
- `props` — comma-separated `name:type` pairs (e.g. `title:string,count:number`)

## Output
- `resources/js/components/{Name}.vue` — Composition API component with `defineProps`, `defineEmits`, typed props
- `resources/js/stores/{Name}.ts` — Pinia store (if `--store`) with loading/error state and fetch stub
- Import hint

## Related
- `engine/agents/fnt/vue-engineer.md`
- `.claude/tools/fnt/vue-engineer/vue-component.sh`
