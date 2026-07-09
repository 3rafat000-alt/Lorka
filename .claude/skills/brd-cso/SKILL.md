---
name: brd-cso
description: "CSO — enterprise-wide security veto, operates deep-audit track."
---
# Boardroom - Chief Security Officer (CSO)

Deep audit trigger — scan project source for money/auth/PII surfaces and classify as Fast-Track or Deep-Audit.

## Tool
`.claude/tools/brd/cso/deep-audit-trigger.sh`

## When to use
- Project inception: classify task risk — Fast-Track (low risk) vs Deep-Audit (money/auth/PII)
- Before any deployment: verify no unclassified AuthN/AuthZ/PII surfaces
- Security review: identify which paths need the full 9-gate lifecycle
- Change impact analysis: a PR touches payment, wallet, KYC, or credentials

## How to use
```bash
.claude/tools/brd/cso/deep-audit-trigger.sh <PRJ-ID> [--path <src-dir>]
```

## Input
- `PRJ-ID` — project identifier
- `--path` — optional source directory override (default: `projects/<PRJ>/`)
- Scans for patterns: payment, wallet, card, KYC, auth, credentials, PII, encryption

## Output
- List of flagged surface patterns with file locations
- Risk classification: Fast-Track (no flags) or Deep-Audit (flags found → full 9 gates)
- Exit code 0 if safe for Fast-Track, non-zero if Deep-Audit required

## Related
- `.claude/tools/brd/ceo/sofi-exec.sh` — exec flow after risk classification
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — adversarial check (mandatory for Deep-Audit)
- `engine/protocols/00-operating-system.md §Task-sizing`
