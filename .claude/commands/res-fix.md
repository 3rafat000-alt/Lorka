---
description: "Fix research insight/persona. /res-fix <issue>"
argument-hint: "[description]"
---
> **Lead persona:** `res-lead` — the main session *wears* this persona (`.claude/agents/res-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 RESEARCH — FIX: $ARGUMENTS

## Delegation

### 1. UX Researcher or Journey Architect
🎭 **Role:** Research specialist
📂 **Context:** Issue: $ARGUMENTS · Gate 1
🎯 **Command:** Revise personas or journey map. Document change + evidence
📐 **Format:** Updated document + delta log

### 2. Fact Checker — @res-fact-checker
🎭 **Role:** Fact Checker — re-verify
📂 **Context:** Revised research outputs
🎯 **Command:** Re-verify all changed claims
📐 **Format:** Updated `docs/Fact_Check_Report.md`

## Handoff
→ CPO re-signs → `/gate-check 1`
