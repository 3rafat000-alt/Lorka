---
name: fnt-react-engineer
description: "Typed React components + service layer per contract, zero any."
---
# Frontend - React Engineer

Scaffold a typed React component with props interface in TSX. Generates a functional component with `PropsWithChildren` pattern.

## Tool
`.claude/tools/fnt/react-engineer/react-component.sh`

## When to use
- New React component: scaffold from component name with typed interface
- Gate 4 frontend implementation: rapid TSX component creation
- Prototyping UI: generate component with correct import path

## How to use
```bash
.claude/tools/fnt/react-engineer/react-component.sh <PRJ-ID> <ComponentName> [props...]
```

## Input
- `PRJ-ID` — project directory
- `ComponentName` — PascalCase component name (e.g. `UserCard`)
- `props` — comma-separated `name:type` pairs (e.g. `title:string,onClick:()=>void`)

## Output
- `resources/ts/components/{Name}.tsx` — typed functional component with:
  - `{Name}Props` interface from prop definitions
  - `PropsWithChildren` pattern for children passthrough
- Import hint: `import {Name} from '@/components/{Name}'`

## Related
- `engine/agents/fnt/react-engineer.md`
- `.claude/tools/fnt/react-engineer/react-component.sh`
