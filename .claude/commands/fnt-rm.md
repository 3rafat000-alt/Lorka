---
description: Remove feature from frontend. /fnt-rm <feature>
agent: fnt-lead
---

# 🗑️ FRONTEND — REMOVE: $ARGUMENTS

## Delegation

### 1. Framework Engineer — @fnt-vue-engineer | @fnt-react-engineer
🎭 **Role:** Framework engineer
📂 **Context:** Feature $ARGUMENTS components to remove
🎯 **Command:** Remove components, stores, routes. Update navigation. Ensure no import orphans
📐 **Format:** Removed code · updated router

### 2. CSS Artisan — @fnt-css-artisan
🎭 **Role:** CSS Artisan
📂 **Context:** Feature CSS to remove
🎯 **Command:** Remove feature-specific styles. Clean up dead CSS
📐 **Format:** Cleaned stylesheets

### 3. A11y Engineer — @fnt-a11y-engineer
🎭 **Role:** A11y Engineer
📂 **Context:** Post-removal frontend
🎯 **Command:** Re-scan a11y. Confirm no regressions
📐 **Format:** Updated a11y audit

## Code Review
`@fnt-code-reviewer` — adversarial

## Handoff
→ Grace Achieng merges → `/qa-sweep "frontend post-removal: $ARGUMENTS"`