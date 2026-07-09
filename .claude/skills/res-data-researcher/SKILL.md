---
name: res-data-researcher
description: "Quantitative evidence, surveys, telemetry mining with source and date."
---
# Research - Data Researcher

Run quantitative statistics on CSV survey data — mean, standard deviation, counts, distributions.

## Tool
`.claude/tools/res/data-researcher/survey-stats.py`

## When to use
- Gate 1 Discovery: analyse survey results or quantitative user research
- After a user study: compute basic stats on Likert scales, usage metrics, or demographics
- Before writing personas: validate assumptions with numeric data
- Fact-checking a quantitative claim: compute the actual distribution from raw data

## How to use
```bash
python3 .claude/tools/res/data-researcher/survey-stats.py <csv-path> [--output <file>]
```

## Input
- CSV file with header row
- Columns can be numeric (auto-detected) or categorical
- `--output` — optional output file (default: stdout)

## Output
- Per-column statistics:
  - Numeric columns: mean, standard deviation, min, max, quartiles
  - Categorical columns: counts, percentages
- Exit code 0

## Related
- `.claude/tools/res/fact-checker/ground-check.sh` — verify statistical claims against sources
- `.claude/tools/res/ux-researcher/persona-gen.sh` — downstream: stats inform persona profiles
- `.claude/tools/res/lead/research-synth.sh` — downstream: stats feed journey map synthesis
