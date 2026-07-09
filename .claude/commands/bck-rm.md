---
description: Remove feature from backend. /bck-rm <feature>
agent: bck-lead
---

# 🗑️ BACKEND — REMOVE: $ARGUMENTS

## Delegation

### 1. API Engineer — @bck-api-engineer
🎭 **Role:** API Engineer
📂 **Context:** Feature $ARGUMENTS endpoints to deprecate
🎯 **Command:** Implement deprecation plan per API contract. Soft → hard timeline. 410 Gone on hard removal
📐 **Format:** Code in `routes/api.php` · deprecation middleware

### 2. Domain Engineer — @bck-domain-engineer
🎭 **Role:** Domain Engineer
📂 **Context:** Feature business logic removed
🎯 **Command:** Remove services, models. Archive via git. Ensure no orphaned references
📐 **Format:** Removed code · changelog

### 3. Blade Engineer — @bck-blade-engineer
🎭 **Role:** Blade Engineer
📂 **Context:** Feature views removed
🎯 **Command:** Remove Blade templates. Update navigation/sitemap
📐 **Format:** Removed views · updated layouts

## Code Review
`@bck-code-reviewer` — adversarial. Verify no dead code remains

## Handoff
→ Elif Kaya merges → `/qa-sweep "post-removal: $ARGUMENTS"`