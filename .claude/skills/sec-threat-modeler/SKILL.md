---
name: sec-threat-modeler
description: "STRIDE threat model + penetration test scope — before any code."
---
# Security - Threat Modeler

Run STRIDE threat model checklist against a project component.

## Tool
`.claude/tools/sec/threat-modeler/stride-audit.sh`

## When to use
- New feature or component before implementation
- Architecture review (Gate 3)
- Post-breach root cause analysis
- Third-party integration risk assessment

## How to use
```bash
.claude/tools/sec/threat-modeler/stride-audit.sh --prj PRJ-XXXX [--component name]
```

## Input
PRJ-ID and optional component name. Runs 6 STRIDE categories (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege).

## Output
Per-category threat + mitigation printed to stdout. Each shows COVERED (green) or PENDING (red).

## Related
- `engine/agents/sec/sec-threat-modeler.md`
- `.claude/tools/sec/threat-modeler/stride-audit.sh`
