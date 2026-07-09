---
description: "Quick security scan on existing code. /sec-scan <scope>"
argument-hint: "[description]"
---
> **Lead persona:** `sec-lead` — the main session *wears* this persona (`.claude/agents/sec-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔍 SECURITY — SCAN: $ARGUMENTS

## Delegation

### 1. AppSec Engineer — @sec-appsec-engineer
🎭 **Role:** AppSec Engineer — fast scan
📂 **Context:** Scope: $ARGUMENTS
🎯 **Command:** SAST scan + quick manual review. Report HIGH/CRITICAL only
📐 **Format:** `docs/Quick_Security_Scan.md`

### 2. Secrets Warden — @sec-secrets-warden
🎭 **Role:** Secrets Warden
📂 **Context:** Scope files
🎯 **Command:** Secret scan. Block on any live secret
📐 **Format:** Scan report

## Escalation
Any HIGN/CRITICAL → `@brd-cso`

## Handoff
→ Append to gate-check evidence
