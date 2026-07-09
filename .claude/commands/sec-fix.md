---
description: Fix security vulnerability. /sec-fix <vulnerability>
agent: sec-lead
---

# 🔧 SECURITY — FIX: $ARGUMENTS

## Delegation

### 1. AppSec Engineer — @sec-appsec-engineer
🎭 **Role:** AppSec Engineer
📂 **Context:** Vulnerability: $ARGUMENTS
🎯 **Command:** Produce fix plan: root cause, affected surfaces, fix steps, verification method
📐 **Format:** `docs/Security_Fix_Plan.md`

### 2. Appropriate dev room lead — @bck-lead / @fnt-lead / @mob-lead
🎭 **Role:** Implementation lead
📂 **Context:** Fix plan approved by sec
🎯 **Command:** Implement fix per plan. Regression tests
📐 **Format:** Fix commit

### 3. AppSec Engineer — @sec-appsec-engineer (re-verify)
🎭 **Role:** AppSec Engineer — verify
📂 **Context:** Fix implemented
🎯 **Command:** Re-verify vulnerability closed. No new issues introduced
📐 **Format:** `docs/Security_Fix_Verification.md`

## Escalation
If fix fails verification → `@brd-cso` decision

## Handoff
→ `/qa-sweep "security fix: $ARGUMENTS"` → `/gate-check 5`