---
description: Remove feature from design. /dsn-rm <feature>
agent: dsn-lead
---

# 🗑️ DESIGN — REMOVE: $ARGUMENTS

## Delegation

### 1. UX Architect — @dsn-ux-architect
🎭 **Role:** UX Architect
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Remove flows. Reconnect remaining flows (no dead ends)
📐 **Format:** Updated `docs/UX_Architecture.md`

### 2. UI Designer — @dsn-ui-designer
🎭 **Role:** UI Designer
📂 **Context:** Feature screens removed
🎯 **Command:** Archive screen specs. Update related screens if impacted
📐 **Format:** Updated `docs/UI_Spec.md`

### 3. Content Strategist — @dsn-content-strategist
🎭 **Role:** Content Strategist
📂 **Context:** Feature copy removed
🎯 **Command:** Archive copy keys. Remove from Copy.json
📐 **Format:** Updated `docs/Copy.json`

### 4. Accessibility Specialist — @dsn-a11y-specialist
🎭 **Role:** A11y Specialist
📂 **Context:** Post-removal designs
🎯 **Command:** Re-check WCAG 2.2 AA matrix
📐 **Format:** Updated `docs/A11y_Matrix.md`

## Handoff
→ Dan Kim signs removal → `/gate-check 2`