---
name: res-competitor-analyst
description: "Competitor teardown by user value matrix, not feature count."
---
# Research - Competitor Analyst

Scaffold a competitor teardown document with feature-by-feature scoring and qualitative notes.

## Tool
`.claude/tools/res/competitor-analyst/teardown.sh`

## When to use
- Gate 1 Discovery: analyse competitive landscape before defining product scope
- Before a new feature: check how competitors solve the same problem
- Positioning review: understand differentiators vs each competitor
- Investor or stakeholder update: competitive landscape section

## How to use
```bash
.claude/tools/res/competitor-analyst/teardown.sh <PRJ-ID> --competitor "<name>" [--features "<f1,f2,f3>"] [--notes "<notes>"]
```

## Input
- `PRJ-ID` — project identifier
- `--competitor` — competitor name
- `--features` — comma-separated feature list to score
- `--notes` — qualitative notes on the competitor
- Without --features/--notes: creates blank template

## Output
- Teardown document at `projects/<PRJ>/docs/competitor-teardown-<name>.md`
- Sections: product overview, feature matrix, strengths, weaknesses, positioning
- Exit code 0

## Related
- `.claude/tools/res/web-scout/fetch-cite.sh` — upstream: fetch competitor websites and docs
- `.claude/tools/res/lead/research-synth.sh` — downstream: competitor insights feed journey synthesis
- `.claude/tools/str/market-analyst/tam-calc.sh` — market sizing informed by competitive landscape
