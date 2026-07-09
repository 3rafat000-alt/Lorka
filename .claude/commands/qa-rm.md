---
description: "QA regression after removal. /qa-rm <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `qa-lead` — the main session *wears* this persona (`.claude/agents/qa-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ QUALITY — POST-REMOVAL QA: $ARGUMENTS

## Delegation

### 1. Automation Engineer — @qa-automation-engineer
🎭 **Role:** Automation Engineer
📂 **Context:** Feature $ARGUMENTS removed
🎯 **Command:** Update test suite: remove feature tests, update affected tests. Full suite pass
📐 **Format:** Updated tests · suite pass report

### 2. Design Auditor — @qa-design-auditor
🎭 **Role:** Design Auditor
📂 **Context:** Post-removal screens
🎯 **Command:** Audit remaining screens for design consistency after removal
📐 **Format:** Updated `docs/Design_Audit.md`

### 3. Regression Warden — @qa-regression-warden
🎭 **Role:** Regression Warden
📂 **Context:** Full suite after removal
🎯 **Command:** Confirm no regressions in remaining features
📐 **Format:** Regression pass report

## Verdict
→ Barb Jensen: PASS or BLOCK

## Handoff
→ `/gate-check 5`
