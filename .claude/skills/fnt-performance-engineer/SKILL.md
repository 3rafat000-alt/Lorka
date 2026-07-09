---
name: fnt-performance-engineer
description: "Bundle budgets, code-split, Core Web Vitals enforcement."
---
# Frontend - Performance Engineer

Check compiled JS/CSS bundle sizes against a configurable budget. Reports individual bundle sizes, total size, and flags heavy dependencies from package.json.

## Tool
`.claude/tools/fnt/performance-engineer/bundle-analyze.sh`

## When to use
- Gate 4 performance gate: verify bundle stays under 300KB (or custom) budget
- CI pipeline: `--json` flag produces machine-readable output for automated gates
- Dependency audit: after adding npm packages, check bundle impact

## How to use
```bash
.claude/tools/fnt/performance-engineer/bundle-analyze.sh <PRJ-ID> [--budget <kb>] [--json]
```

## Input
- `PRJ-ID` — project directory with `public/build/assets/`
- `--budget` — max total bundle size in KB (default: 300)
- `--json` — output JSON for CI consumption

## Output
- Per-file report: JS bundle, CSS bundle, vendor JS with size and flag if large
- package.json scan for heavy dependencies
- Total vs budget, with pass/fail and remaining/exceeded KB
- Exit 0 if within budget, 1 if exceeded

## Related
- `engine/agents/fnt/performance-engineer.md`
- `.claude/tools/fnt/performance-engineer/bundle-analyze.sh`
