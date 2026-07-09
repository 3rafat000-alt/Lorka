---
description: "Security review for new feature. /sec-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `sec-lead` — the main session *wears* this persona (`.claude/agents/sec-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 SECURITY — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. Threat Modeler — @sec-threat-modeler
🎭 **Role:** Threat Modeler — STRIDE analysis
📂 **Context:** Architecture frozen · Gate 3+5
🎯 **Command:** Produce STRIDE threat model (Spoofing/Tampering/Repudiation/Info Disclosure/DoS/Elevation). Per component. Define pentest scope
📐 **Format:** `docs/Threat_Model.md` · gates architecture

### 2. AppSec Engineer — @sec-appsec-engineer
🎭 **Role:** AppSec Engineer — code review
📂 **Context:** Feature code built
🎯 **Command:** SAST scan + manual code review. Injection/IDOR/SSRF checks. Block on any HIGH
📐 **Format:** `docs/AppSec_Review.md` · severity-graded findings

### 3. Auth Engineer — @sec-authn-engineer
🎭 **Role:** Auth Engineer — auth/crypto
📂 **Context:** Feature auth requirements
🎯 **Command:** Review auth flows, session management, token rotation, password hashing, OAuth. Block on design flaws
📐 **Format:** `docs/Auth_Review.md`

### 4. Secrets Warden — @sec-secrets-warden
🎭 **Role:** Secrets Warden — secret scan
📂 **Context:** All feature code
🎯 **Command:** Scan for exposed secrets. Enforce .env/vault hygiene. Rotate on detection
📐 **Format:** `docs/Secret_Scan_Report.md`

### 5. Compliance Auditor — @sec-compliance-auditor
🎭 **Role:** Compliance Auditor — regulatory
📂 **Context:** Feature data flows
🎯 **Command:** Map data flows to regulation (GDPR/PCI/SOC2). Each field → owning control. Block on gaps
📐 **Format:** `docs/Compliance_Map.md`

## Escalation
Any HIGH/CRITICAL → `@brd-cso` for veto decision

## Handoff
→ Ruth Goldberg signs → `/gate-check 3` + `/gate-check 5`
