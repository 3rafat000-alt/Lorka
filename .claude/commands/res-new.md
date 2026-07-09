---
description: Research for new feature. /res-new <feature>
agent: res-lead
---

# 🆕 RESEARCH — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. UX Researcher — @res-ux-researcher
🎭 **Role:** UX Researcher — personas + pain/gain
📂 **Context:** Blueprint frozen · Gate 1
🎯 **Command:** Produce evidence-based personas. Each: goals, pains, gains, JTBD. Use WebSearch if sharpens profile
📐 **Format:** `docs/Personas.md` · grounded claims only

### 2. Journey Architect — @res-journey-architect
🎭 **Role:** Journey Architect — Customer Journey Map
📂 **Context:** Personas + feature $ARGUMENTS
🎯 **Command:** Produce CJM (Mermaid). Every stage = user goal. Every screen traces to a stage
📐 **Format:** `docs/Journey_Map.md` · frozen at Gate 1

### 3. Web Scout — @res-web-scout
🎭 **Role:** Web Scout — external research
📂 **Context:** Feature $ARGUMENTS domain
🎯 **Command:** Search/fetch/verify external sources. Cite everything. Return file:line table
📐 **Format:** `docs/Research_Sources.md` · verified citations

### 4. Competitor Analyst — @res-competitor-analyst
🎭 **Role:** Competitor Analyst — competitive landscape
📂 **Context:** Feature + preliminary research
🎯 **Command:** Produce Competitor Teardown by User Value Matrix. Not feature count
📐 **Format:** `docs/Competitive_Analysis.md`

### 5. Data Researcher — @res-data-researcher
🎭 **Role:** Data Researcher — quantitative evidence
📂 **Context:** Feature $ARGUMENTS
🎯 **Command:** Find surveys, telemetry, benchmarks. Every data point has source + date
📐 **Format:** `docs/Data_Evidence.md`

### 6. Fact Checker — @res-fact-checker
🎭 **Role:** Fact Checker — adversarial verification
📂 **Context:** All research outputs
🎯 **Command:** Adversarially verify every claim. Flag ungrounded assertions
📐 **Format:** `docs/Fact_Check_Report.md` · pass/fail per document

## Handoff
→ CPO signs → Gateway dispatches to Design Room `/dsn-new "$ARGUMENTS"`