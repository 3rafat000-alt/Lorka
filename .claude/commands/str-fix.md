---
description: "Fix strategy assumption/scope. /str-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `str-lead` — the main session *wears* this persona (`.claude/agents/str-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 STRATEGY — FIX: $ARGUMENTS

## Delegation

### 1. Product Strategist — @str-product-strategist
🎭 **Role:** Product Strategist — revise scope
📂 **Context:** Issue: $ARGUMENTS · Gate 0
🎯 **Command:** Revise Project Blueprint: update scope boundary, adjust metrics, or refine problem statement. Document what changed and why
📐 **Format:** Updated `docs/Project_Blueprint.md` · change log section

### 2. Risk Analyst — @str-risk-analyst
🎭 **Role:** Risk Analyst — reassess risk
📂 **Context:** Scope change per $ARGUMENTS
🎯 **Command:** Reassess risk register. New risks? Changed likelihood/impact?
📐 **Format:** Updated `docs/Risk_Register.md` · delta report

### 3. Roadmap Planner — @str-roadmap-planner
🎭 **Role:** Roadmap Planner — adjust timeline
📂 **Context:** Scope/risk changed
🎯 **Command:** Adjust milestones, reclassify fast-track↔deep-audit as needed
📐 **Format:** Updated `docs/Roadmap.md`

## Handoff
→ CPO re-signs → `/gate-check 0`
