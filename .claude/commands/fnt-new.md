---
description: Build frontend for new feature. /fnt-new <feature>
agent: fnt-lead
---

# 🆕 FRONTEND — NEW FEATURE: $ARGUMENTS

## Delegation (parallel)

### 1. Vue or React Engineer — @fnt-vue-engineer | @fnt-react-engineer
🎭 **Role:** Framework engineer — components
📂 **Context:** UI spec frozen + API contract frozen · Gate 4
🎯 **Command:** Implement typed components per framework. Zero `any`. Every component: all states. Wired to API contract
📐 **Format:** Code in `resources/js/` · typed stores (Pinia/React Query)

### 2. CSS Artisan — @fnt-css-artisan
🎭 **Role:** CSS Artisan — Tailwind + responsive
📂 **Context:** Design tokens + UI spec
🎯 **Command:** Implement Tailwind CSS. Responsive 320–1200+. Enforce taste metrics in rendered output
📐 **Format:** Tailwind classes + custom CSS

### 3. Interaction Engineer — @fnt-interaction-engineer
🎭 **Role:** Interaction Engineer — micro-interactions
📂 **Context:** Motion spec frozen
🎯 **Command:** Implement micro-interactions per motion spec. Reduced-motion alternative that preserves meaning
📐 **Format:** CSS transitions + JS interactions

### 4. A11y Engineer — @fnt-a11y-engineer
🎭 **Role:** A11y Engineer — WCAG enforcement
📂 **Context:** A11y matrix + built components
🎯 **Command:** Enforce WCAG 2.2 AA in every component. Keyboard nav, ARIA, contrast, focus. axe-core scan
📐 **Format:** Accessible components + audit report

### 5. Performance Engineer — @fnt-performance-engineer
🎭 **Role:** Performance Engineer — budgets
📂 **Context:** Built components
🎯 **Command:** Set bundle budgets. Implement code-split, lazy load. Measure CWV. Block on violation
📐 **Format:** Performance budget config + report

## Code Review
`@fnt-code-reviewer` — adversarial diff

## Handoff
→ Grace Achieng reviews + merges → QA Room `/qa-new "frontend: $ARGUMENTS"`