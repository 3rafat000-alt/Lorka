---
name: sec-compliance-auditor
description: "Data flow mapped to regulation (GDPR/PCI) with owning controls."
---
# Security - Compliance Auditor

Map data flow to GDPR/PCI compliance requirements.

## Tool
`.claude/tools/sec/compliance-auditor/data-flow.sh`

## When to use
- Gate 3 data architecture review
- Regulatory compliance audit (GDPR, PCI-DSS)
- PII inventory mapping
- Vendor/data-processor due diligence

## How to use
```bash
.claude/tools/sec/compliance-auditor/data-flow.sh --prj PRJ-XXXX [--framework gdpr|pci|all]
```

## Input
PRJ-ID. `--framework` selects regulatory lens. Scans migrations, models, and configuration for PII fields (email, phone, SSN, card numbers, etc.) and data-controller patterns.

## Output
Tables, models, and PII fields found with file locations. Flags retention/consent gaps per framework.

## Related
- `engine/agents/sec/sec-compliance-auditor.md`
- `.claude/tools/sec/compliance-auditor/data-flow.sh`
