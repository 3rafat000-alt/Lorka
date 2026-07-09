---
description: Fix data layer issue. /dat-fix <issue>
agent: dat-lead
---

# 🔧 DATA — FIX: $ARGUMENTS

## Delegation
Select specialist:
- DB bug → `@dat-db-engineer`
- Cache bug → `@dat-cache-engineer`
- Analytics bug → `@dat-analytics-engineer`
- ML bug → `@dat-ml-engineer`
- ETL bug → `@dat-etl-engineer`
- Privacy gap → `@dat-privacy-officer`

🎭 **Role:** Appropriate data specialist
📂 **Context:** Issue: $ARGUMENTS · Gate 3–4
🎯 **Command:** Fix issue. Add regression test. Verify privacy classification unchanged if data changes
📐 **Format:** Fix commit + test

## Handoff
→ Günther Weber merges → `/qa-sweep "data fix: $ARGUMENTS"`