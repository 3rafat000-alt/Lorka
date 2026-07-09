---
description: Fix QA-reported bug. /qa-fix <bug>
agent: qa-lead
---

# 🔧 QUALITY — FIX: $ARGUMENTS

## Delegation

### 1. Automation Engineer — @qa-automation-engineer
🎭 **Role:** Automation Engineer — regression
📂 **Context:** Bug: $ARGUMENTS · Gate 5
🎯 **Command:** Write regression test reproducing bug. Test must fail before fix
📐 **Format:** Regression test code

### 2. Appropriate dev room lead — @bck-lead / @fnt-lead / @mob-lead
🎭 **Role:** Implementation lead
📂 **Context:** Bug + regression test
🎯 **Command:** Fix root cause. All tests green including new regression test
📐 **Format:** Fix commit

### 3. Automation Engineer — @qa-automation-engineer (re-verify)
🎭 **Role:** Automation Engineer — verify
📂 **Context:** Fix implemented
🎯 **Command:** Re-verify bug closed. Full suite pass. Flaky check
📐 **Format:** Verification report

## Verdict
→ Barb Jensen: PASS (bug fixed, no regression) or BLOCK (needs more work)

## Handoff
→ `/ops-deploy "fix: $ARGUMENTS"`
