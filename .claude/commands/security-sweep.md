---
description: "Run a security review across all security agents. Use: /security-sweep <scope>"
agent: sec-lead
---

# Security Sweep: $ARGUMENTS

Run the full security suite:
1. `@sec-threat-modeler` — STRIDE threat model
2. `@sec-appsec-engineer` — SAST + manual code review
3. `@sec-pentester` — live system attack
4. `@sec-authn-engineer` — auth/crypto review
5. `@sec-secrets-warden` — secret scan
6. `@sec-compliance-auditor` — regulatory compliance check

Collect all reports. Escalate any HIGH/CRITICAL finding to `@brd-cso`. Exercise veto if needed.