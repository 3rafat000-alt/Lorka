---
name: str-monetization-strategist
description: "Business model, value metric, pricing hypothesis."
---
# Strategy - Monetization Strategist

Generate pricing pyramid from value metric and tier names — Free, Starter, Pro, Enterprise.

## Tool
`.claude/tools/str/monetization-strategist/pyramid.sh`

## When to use
- Gate 0 monetization planning: define the pricing model before building
- Product-market fit achieved: introduce paid tiers
- Feature gating decisions: determine which tier gets which features
- Competitor pricing response: re-evaluate tier structure and pricing points

## How to use
```bash
.claude/tools/str/monetization-strategist/pyramid.sh --product "<name>" --metric "<unit>" [--tiers "<t1,t2,t3,t4>"] [--prices "<p1,p2,p3,p4>"]
```

## Input
- `--product` — product name
- `--metric` — value metric (e.g. "seats", "API calls/mo", "storage GB")
- `--tiers` — comma-separated tier names (default: "Free,Starter,Pro,Enterprise")
- `--prices` — comma-separated prices (default: "$0,$29,$99,$299")

## Output
- Formatted pricing pyramid with value metric highlighted
- Tier-by-tier breakdown with name and price
- Exit code 0

## Related
- `.claude/tools/str/market-analyst/tam-calc.sh` — upstream: market size informs pricing
- `.claude/tools/str/lead/blueprint-init.sh` — monetization model is part of the Blueprint
- `engine/DOCTRINE.md §Teaching IV` — Token Economy applies to pricing too
