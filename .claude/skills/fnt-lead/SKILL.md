---
name: fnt-lead
description: "Frontend Room Lead — chooses Vue/React, merges worktree."
---
# Frontend - Room Lead (Grace Achieng)

Coordinate parallel frontend worktrees. Create, list, merge, and remove isolated git worktree branches for concurrent frontend tasks.

## Tool
`.claude/tools/fnt/lead/frontend-squad.sh`

## When to use
- Parallel frontend tasks: spin up a worktree per component or per developer
- Gate 4 parallel implementation: multiple frontend engineers on separate branches
- Worktree lifecycle: create for new feature, merge when done, remove on cleanup

## How to use
```bash
.claude/tools/fnt/lead/frontend-squad.sh <PRJ-ID> <action> [name]
```

## Input
- `PRJ-ID` — project directory (must be a git repo)
- `<action>` — `create`, `list`, `merge`, or `remove`
- `[name]` — worktree name (required for create/merge/remove)

## Output
- `create`: new branch `squad/frontend/<name>` at `_worktrees/frontend-<name>/`
- `list`: all active worktrees
- `merge`: `--no-ff` merge of squad branch into main
- `remove`: clean up worktree dir and branch

## Related
- `engine/agents/fnt/lead.md`
- `.claude/tools/fnt/lead/frontend-squad.sh`
