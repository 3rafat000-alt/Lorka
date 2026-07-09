---
name: bck-lead
description: "Backend Room Lead — coordinates parallel build, merges worktrees."
---
# Backend - Room Lead (Elif Kaya)

Coordinate parallel backend worktrees. Create, list, merge, and remove isolated git worktree branches for concurrent backend tasks.

## Tool
`.claude/tools/bck/lead/backend-squad.sh`

## When to use
- Parallelizing backend work: spin up a worktree per developer or per feature
- Gate 4 parallel implementation: multiple backend engineers on separate branches
- Worktree lifecycle: create for new task, merge when done, remove on cleanup

## How to use
```bash
.claude/tools/bck/lead/backend-squad.sh <PRJ-ID> <action> [name]
```

## Input
- `PRJ-ID` — project directory (must be a git repo)
- `<action>` — `create`, `list`, `merge`, or `remove`
- `[name]` — worktree name (required for create/merge/remove)

## Output
- `create`: new branch `squad/backend/<name>` at `_worktrees/<name>/`
- `list`: all active worktrees excluding bare repos
- `merge`: `--no-ff` merge of squad branch into main
- `remove`: clean up worktree dir and branch

## Related
- `engine/agents/bck/lead.md`
- `.claude/tools/bck/lead/backend-squad.sh`
