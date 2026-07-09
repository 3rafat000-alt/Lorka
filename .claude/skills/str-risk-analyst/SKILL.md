---
name: str-risk-analyst
description: "Business risk register, stop criteria, deep-audit triggers."
---
# Strategy - Risk Analyst

Create and update the business risk register — track risks with impact, likelihood, and mitigation plans.

## Tool
`.claude/tools/str/risk-analyst/risk-register.sh`

## When to use
- Gate 0 inception: scaffold the risk register alongside the Project Blueprint
- Each gate transition: review and update risks, add new ones discovered during the gate
- Before an irreversible decision: document the risk and rollback plan as an ADR adjunct
- Monthly review: re-evaluate likelihood and impact of all logged risks

## How to use
```bash
.claude/tools/str/risk-analyst/risk-register.sh <PRJ-ID> [--add "<risk>"] [--impact <H|M|L>] [--likelihood <H|M|L>] [--mitigation "<plan>"]
```

## Input
- `PRJ-ID` — project identifier
- `--add` — risk description
- `--impact` — H/M/L
- `--likelihood` — H/M/L
- `--mitigation` — plan to mitigate
- Without flags: creates empty risk register template
- Writes to `projects/<PRJ>/_context/RISK_REGISTER.md`

## Output
- Risk register with per-risk entries: ID, description, impact, likelihood, mitigation, status, date
- Updated entries appended when --add is used
- Exit code 0

## Related
- `.claude/tools/brd/cso/deep-audit-trigger.sh` — security risk triggers
- `.claude/tools/brd/arbiter/conflict-log.sh` — ADR for risk-related decisions
- `engine/DOCTRINE.md §Teaching VI` — Reversibility Principle
