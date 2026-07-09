---
name: mob-lead
description: "Mobile Room Lead — reviews and merges (no dedicated reviewer)."
---
# Mobile - Room Lead (João Silva)

Coordinate parallel mobile worktrees. Create, list, merge, and remove isolated git worktree branches for concurrent Flutter tasks.

## Tool
`.claude/tools/mob/lead/mob-squad.sh`

## When to use
- Parallel mobile tasks: spin up a worktree per feature or per developer
- Gate 4 parallel implementation: multiple mobile engineers on separate branches
- Worktree lifecycle: create for new feature, merge when done, remove on cleanup

## How to use
```bash
.claude/tools/mob/lead/mob-squad.sh <PRJ-ID> <action> [name]
```

## Input
- `PRJ-ID` — project directory (must be a git repo)
- `<action>` — `create`, `list`, `merge`, or `remove`
- `[name]` — worktree name (required for create/merge/remove)

## Output
- `create`: new branch `squad/mobile/<name>` at `_worktrees/mobile-<name>/`
- `list`: all active worktrees
- `merge`: `--no-ff` merge of squad branch into main
- `remove`: clean up worktree dir and branch

## Related
- `engine/agents/mob/lead.md`
- `.claude/tools/mob/lead/mob-squad.sh`
