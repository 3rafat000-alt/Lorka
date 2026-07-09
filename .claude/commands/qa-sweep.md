---
description: "Quick QA on fix. /qa-sweep <scope>"
argument-hint: "[description]"
---
> **Lead persona:** `qa-lead` — the main session *wears* this persona (`.claude/agents/qa-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔍 QA SWEEP — $ARGUMENTS

## Delegation

### 1. Automation Engineer — @qa-automation-engineer
🎭 **Role:** Automation Engineer
📂 **Context:** Scope: $ARGUMENTS · Gate 5
🎯 **Command:** Run full test suite. Report pass/fail. Coverage check
📐 **Format:** Test run report + coverage

### 2. Regression Warden — @qa-regression-warden
🎭 **Role:** Regression Warden
📂 **Context:** Full suite results
🎯 **Command:** Check for regressions. Flag any flaky tests
📐 **Format:** Regression check

### 3. Performance Analyst — @qa-perf-analyst
🎭 **Role:** Performance Analyst
📂 **Context:** If $ARGUMENTS touches CWV paths
🎯 **Command:** Quick perf check. CWV budgets
📐 **Format:** Quick perf report

## Verdict
→ Barb Jensen: PASS or BLOCK

## Handoff
→ If PASS → deploy path continues
