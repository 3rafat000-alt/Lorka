---
description: "Full QA suite for new feature. /qa-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `qa-lead` — the main session *wears* this persona (`.claude/agents/qa-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 QUALITY — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. Test Architect — @qa-test-architect
🎭 **Role:** Test Architect — strategy
📂 **Context:** Feature built · Gate 5
🎯 **Command:** Classify feature risk tier (A/B/C). Define test pyramid. Design pass/kill policy
📐 **Format:** `docs/Test_Strategy.md` · tier classification

### 2. Automation Engineer — @qa-automation-engineer
🎭 **Role:** Automation Engineer — tests
📂 **Context:** Test strategy frozen
🎯 **Command:** Write unit/integration/E2E tests. Coverage ≥90% or build fails. Deterministic tests only
📐 **Format:** Test code · coverage report

### 3. Manual Explorer — @qa-manual-explorer
🎭 **Role:** Manual Explorer — edge cases
📂 **Context:** Feature stable
🎯 **Command:** Run edge-case exploration: empty, massive, offline, RTL, screen reader. File bugs with repro
📐 **Format:** `docs/Manual_QA_Report.md` · bugs + repro steps

### 4. Performance Analyst — @qa-perf-analyst
🎭 **Role:** Performance Analyst — load + CWV
📂 **Context:** Feature built + tested
🎯 **Command:** Run k6 load test + Lighthouse. LCP<2.5s, INP<200ms, CLS<0.1, TTI<2s. Block on violation
📐 **Format:** `docs/Performance_Report.md` · budgets enforced

### 5. Regression Warden — @qa-regression-warden
🎭 **Role:** Regression Warden — suite health
📂 **Context:** Full test suite
🎯 **Command:** Monitor pass rate, run time, flaky rate. Quarantine flaky tests
📐 **Format:** `docs/Suite_Health.md`

### 6. Design Auditor — @qa-design-auditor
🎭 **Role:** Design Auditor — spec match
📂 **Context:** UI spec frozen vs built
🎯 **Command:** Audit every field: layout, colors, typography, spacing, states, errors. Every discrepancy = bug
📐 **Format:** `docs/Design_Audit.md` · field-by-field comparison

## Verdict
→ Barb Jensen issues PASS or BLOCK per Test Architect's pass/kill policy
→ If BLOCK → escalate to `@brd-cqo` with evidence

## Handoff
→ PASS → DevOps Room `/ops-deploy "$ARGUMENTS"`
