---
description: Strategy blueprint for new feature. /str-new <feature-description>
agent: str-lead
---

# 🆕 STRATEGY — NEW FEATURE: $ARGUMENTS

## Delegation to Room Specialists

### 1. Product Strategist — @str-product-strategist
🎭 **Role:** Product Strategist — owns Problem Statement + scope
📂 **Context:** Feature request: $ARGUMENTS · Gate 0
🎯 **Command:** Produce Project Blueprint: (a) one-sentence problem, (b) target user, (c) top-3 JTBD, (d) success metrics, (e) frozen scope in/out
📐 **Format:** `docs/Project_Blueprint.md` · measurable metrics · 5 deep questions

### 2. Business Analyst — @str-business-analyst
🎭 **Role:** Business Analyst — requirements + acceptance criteria
📂 **Context:** Blueprint frozen · Gate 0
🎯 **Command:** Decompose into structured requirements. Each: Given/When/Then criteria, success metric, priority
📐 **Format:** `docs/Requirements.md` · every requirement traces to JTBD

### 3. Market Analyst — @str-market-analyst
🎭 **Role:** Market Analyst — TAM/SAM/SOM + positioning
📂 **Context:** Feature scope frozen
🎯 **Command:** Market sizing + competitive positioning. Web research for live data
📐 **Format:** `docs/Market_Analysis.md` · TAM/SAM/SOM table · cited sources

### 4. Risk Analyst — @str-risk-analyst
🎭 **Role:** Risk Analyst — risk register + stop criteria
📂 **Context:** Feature + market analysis
🎯 **Command:** Produce risk register (likelihood × impact × mitigation). Define stop criteria. Classify deep-audit triggers
📐 **Format:** `docs/Risk_Register.md` · every risk has reversibility class

### 5. Monetization Strategist — @str-monetization-strategist
🎭 **Role:** Monetization Strategist — business model + pricing
📂 **Context:** Feature defined, market sized
🎯 **Command:** Design business model, value metric, pricing hypothesis. Research comparable patterns
📐 **Format:** `docs/Monetization_Strategy.md` · pricing with rationale

### 6. Roadmap Planner — @str-roadmap-planner
🎭 **Role:** Roadmap Planner — milestones + backlog
📂 **Context:** All strategy inputs complete
🎯 **Command:** Produce phased roadmap. Classify each item fast-track or deep-audit. Align milestones to gates
📐 **Format:** `docs/Roadmap.md` · milestones with gate alignment

## Handoff
→ CPO signs → Gateway dispatches to Research Room `/res-new "$ARGUMENTS"`