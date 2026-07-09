---
name: qa-perf-analyst
description: "k6/Lighthouse, Core Web Vitals, TTI < 2s budget."
---
# Quality - Performance Analyst

Run Lighthouse against performance budgets.

## Tool
`.claude/tools/qa/perf-analyst/perf-budget.sh`

## When to use
- Pre-deployment performance gate (TTI < 2s, LCP < 2.5s)
- After frontend changes affecting bundle size
- Core Web Vitals baseline capture
- Performance regression detection

## How to use
```bash
.claude/tools/qa/perf-analyst/perf-budget.sh --url URL [--tti-max 2000] [--lcp-max 2500] [--lhr-budget budget.json] [--k6-script script.js]
```

## Input
Target URL. Optional TTI/LCP thresholds, Lighthouse budget file, k6 script. Runs Lighthouse (headless) and/or k6 against the URL.

## Output
Per-metric pass/fail against budget with measured values. Exit 0 = within all budgets.

## Related
- `engine/agents/qa/qa-perf-analyst.md`
- `.claude/tools/qa/perf-analyst/perf-budget.sh`
