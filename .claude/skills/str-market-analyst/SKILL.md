---
name: str-market-analyst
description: "TAM/SAM/SOM, competitive positioning."
---
# Strategy - Market Analyst

Calculate TAM (Total Addressable Market), SAM (Serviceable Addressable Market), SOM (Serviceable Obtainable Market).

## Tool
`.claude/tools/str/market-analyst/tam-calc.sh`

## When to use
- Gate 0 inception: sizing the opportunity before committing to a project
- Investor pitch or stakeholder update: quantify market potential
- Competitive analysis: compare TAM share across competitors
- Pricing strategy: SOM informs revenue projections and pricing tiers

## How to use
```bash
.claude/tools/str/market-analyst/tam-calc.sh --total-addressable <N> --serviceable <N> --obtainable <N>
```

## Input
- `--total-addressable` — TAM in users or $
- `--serviceable` — SAM (segment you can serve)
- `--obtainable` — SOM (realistic capture target)
- All numbers in the same unit

## Output
- TAM/SAM/SOM formatted table with percentages
- SAM as % of TAM, SOM as % of SAM calculated
- Exit code 0

## Related
- `.claude/tools/str/monetization-strategist/pyramid.sh` — downstream: pricing tiers from market data
- `.claude/tools/res/competitor-analyst/teardown.sh` — upstream: competitive positioning
- `.claude/tools/str/lead/blueprint-init.sh` — market data feeds the Blueprint
