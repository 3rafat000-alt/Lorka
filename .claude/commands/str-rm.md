---
description: Remove feature from strategy/scope. /str-rm <feature>
agent: str-lead
---

# 🗑️ STRATEGY — REMOVE: $ARGUMENTS

## Delegation

### 1. Product Strategist — @str-product-strategist
🎭 **Role:** Product Strategist — scope removal
📂 **Context:** Feature to remove: $ARGUMENTS · Gate 0
🎯 **Command:** Remove from Project Blueprint scope. Document: (a) why removed, (b) impact on JTBD coverage, (c) alternative if any
📐 **Format:** Updated `docs/Project_Blueprint.md` · removal section

### 2. Business Analyst — @str-business-analyst
🎭 **Role:** Business Analyst — requirements cleanup
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Archive related requirements. Mark superseded/cancelled. Trace to removal ADR
📐 **Format:** Updated `docs/Requirements.md` · archived requirements list

### 3. Roadmap Planner — @str-roadmap-planner
🎭 **Role:** Roadmap Planner — timeline recalibration
📂 **Context:** Feature removed
🎯 **Command:** Recalibrate milestones. Free up resources. Update backlog
📐 **Format:** Updated `docs/Roadmap.md`

### 4. Monetization Strategist — @str-monetization-strategist
🎭 **Role:** Monetization Strategist — pricing impact
📂 **Context:** Feature $ARGUMENTS removed from offering
🎯 **Command:** Assess revenue impact. Adjust pricing model if needed
📐 **Format:** Updated `docs/Monetization_Strategy.md`

## Handoff
→ CPO signs removal → `@knw-historian` ADR → `/gate-check 0`