---
name: str-product-strategist
description: "Problem Statement, scope boundaries, 5 deep questions."
---
# Strategy - Product Strategist

Generate a structured problem statement questionnaire to surface the real problem, not the symptom.

## Tool
`.claude/tools/str/product-strategist/problem-statement.sh`

## When to use
- Gate 0 inception: before writing any code, define the problem with rigour
- Stakeholder has a vague request: decompose into the actual pain, user, and workaround
- Product discovery: interview prep or self-guided problem exploration
- Existing feature is underperforming: revisit the problem statement to see if the right problem was solved

## How to use
```bash
.claude/tools/str/product-strategist/problem-statement.sh [--output <file>]
```

## Input
- `--output` — optional output file (default: stdout)
- No project context needed — pure questionnaire generation

## Output
- Structured questionnaire with 4 sections: The Pain, The User, The Solution, The Evidence
- Ready to fill in by stakeholder interview or product team workshop
- Exit code 0

## Related
- `.claude/tools/str/lead/blueprint-init.sh` — feeds into Project Blueprint
- `.claude/tools/res/ux-researcher/persona-gen.sh` — downstream: personas from problem statement
- `.claude/tools/str/business-analyst/acceptance-criteria.py` — downstream: criteria from defined feature
