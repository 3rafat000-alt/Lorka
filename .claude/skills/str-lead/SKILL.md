---
name: str-lead
description: "Strategy Room Lead — owns Gate 0 exit, Room gateway."
---
# Strategy - Lead

Scaffold the Project Blueprint from template — the Gate 0 inception artifact.

## Tool
`.claude/tools/str/lead/blueprint-init.sh`

## When to use
- New project inception (Gate 0): create the foundational Project_Blueprint.md
- A project needs its problem statement, target user, and scope formally documented
- Before any Discovery work begins: the Blueprint must define the JTBD and success metrics
- CEO mandates a new project scaffold with the standard template

## How to use
```bash
.claude/tools/str/lead/blueprint-init.sh <PRJ-ID> --title "<Project Title>" --problem "<problem>" --user "<target user>"
```

## Input
- `PRJ-ID` — project identifier
- `--title` — project title
- `--problem` — what problem does this solve
- `--user` — who is the target user (role, not name)
- Writes to `projects/<PRJ>/docs/Project_Blueprint.md`

## Output
- Project_Blueprint.md with sections: Problem, User, JTBD, Scope, Success Metrics, Risks
- Exit code 0 if created, non-zero if already exists or missing args

## Related
- Room agents: .claude/tools/str/product-strategist, business-analyst, market-analyst
- Gate flow: `sofi-v6-gate-flow` — Gate 0
- `.claude/tools/res/lead/research-synth.sh` — next gate after Blueprint
