---
name: qa-design-auditor
description: "Built vs frozen spec audit — field by field."
---
# Quality - Design Auditor

Compare built output vs frozen spec field-by-field.

## Tool
`.claude/tools/qa/design-auditor/design-audit.sh`

## When to use
- Gate 5 — verify implementation matches frozen spec
- After UI/frontend changes to detect spec drift
- Before client deliverable handoff
- Contract acceptance verification

## How to use
```bash
.claude/tools/qa/design-auditor/design-audit.sh --spec spec.yaml --built built.yaml [--output diff.md]
```

## Input
Spec file and built/output file. Both YAML. Compares key-value pairs, field presence, nesting structure.

## Output
Per-field mismatch report: missing keys, extra keys, value differences. Optional markdown diff file.

## Related
- `engine/agents/qa/qa-design-auditor.md`
- `.claude/tools/qa/design-auditor/design-audit.sh`
