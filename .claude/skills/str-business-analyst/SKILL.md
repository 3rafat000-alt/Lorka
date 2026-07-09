---
name: str-business-analyst
description: "Requirements, success metrics, Given/When/Then acceptance criteria."
---
# Strategy - Business Analyst

Parse feature requirements into Given-When-Then acceptance criteria templates.

## Tool
`.claude/tools/str/business-analyst/acceptance-criteria.py`

## When to use
- Gate 0-1 transition: turning feature ideas into testable acceptance criteria
- Before writing any code: ensure requirements are unambiguous and testable
- Sprint planning: decompose user stories into GWT scenarios
- Reviewing a PR: verify implemented behaviour matches acceptance criteria

## How to use
```bash
python3 .claude/tools/str/business-analyst/acceptance-criteria.py --feature <type> [--entity <name>] [--query <string>] [--output <file>]
```

## Input
- `--feature` — feature type: login | crud | search | custom
- `--entity` — entity name (for crud/search templates, e.g. "invoice")
- `--query` — search query (for search template)
- `--output` — optional output file
- Reads standard input for custom feature descriptions if --feature custom

## Output
- Given-When-Then acceptance criteria in markdown format
- Positive and negative scenarios included
- Exit code 0

## Related
- `.claude/tools/str/product-strategist/problem-statement.sh` — upstream: problem definition
- `.claude/tools/qa/...` — downstream: tests written against these criteria
- `.claude/tools/str/lead/blueprint-init.sh` — the blueprint that frames the feature
