---
description: Design new feature screens. /dsn-new <feature>
agent: dsn-lead
---

# 🆕 DESIGN — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. UX Architect — @dsn-ux-architect
🎭 **Role:** UX Architect — flows + IA
📂 **Context:** Journey Map frozen · Gate 2
🎯 **Command:** Design interaction flows, IA, navigation. No dead ends
📐 **Format:** `docs/UX_Architecture.md` · Mermaid flow diagrams

### 2. UI Designer — @dsn-ui-designer
🎭 **Role:** UI Designer — screen specs
📂 **Context:** UX flows frozen
🎯 **Command:** Produce high-fidelity text UI spec: 1 screen per journey stage, all states (empty/loading/error/success/edge)
📐 **Format:** `docs/UI_Spec.md` · every screen detailed

### 3. Design System Architect — @dsn-design-system
🎭 **Role:** Design System Architect — tokens
📂 **Context:** UI spec direction
🎯 **Command:** Define/extend design tokens. Colors (contrast ratios), spacing scale, typography, shadows
📐 **Format:** `docs/Design_Tokens.md` · token dictionary

### 4. Content Strategist — @dsn-content-strategist
🎭 **Role:** Content Strategist — UX copy
📂 **Context:** UI screens defined
🎯 **Command:** Produce all copy as keyed JSON. Single voice. Every error explains what + how
📐 **Format:** `docs/Copy.json` · `docs/Voice_Tone.md`

### 5. Brand Designer — @dsn-brand-designer
🎭 **Role:** Brand Designer — taste metrics
📂 **Context:** All design inputs
🎯 **Command:** Define taste metrics, anti-generic-UI guardrails. Review all screens
📐 **Format:** `docs/Brand_Guidelines.md`

### 6. Motion Designer — @dsn-motion-designer
🎭 **Role:** Motion Designer — animations
📂 **Context:** Screens + interactions
🎯 **Command:** Spec micro-interactions: duration, easing, stagger. Reduced-motion alternative
📐 **Format:** `docs/Motion_Spec.md`

### 7. Accessibility Specialist — @dsn-a11y-specialist
🎭 **Role:** A11y Specialist — WCAG 2.2 AA
📂 **Context:** All design artifacts
🎯 **Command:** Produce WCAG 2.2 AA compliance matrix. Flag violations. Veto on any issue
📐 **Format:** `docs/A11y_Matrix.md` · pass/fail per criterion

## Handoff
→ Dan Kim signs freeze → Gateway dispatches to Architecture `/arc-new "$ARGUMENTS"`