---
name: sec-lead
description: "Security Room Lead — deputy CSO, exercises veto, Room gateway."
---
# Security - Room Lead

Full security sweep across all surfaces. Orchestrates sub-scanners: secrets, STRIDE, code scan, auth review, pentest.

## Tool
`.claude/tools/sec/lead/sec-sweep.sh`

## When to use
- Gate 3+5 security review required
- Pre-deployment security gate
- Periodic security posture check
- After major feature addition or dependency update

## How to use
```bash
.claude/tools/sec/lead/sec-sweep.sh --prj PRJ-XXXX [--quick|--deep]
```

## Input
PRJ-ID. `--quick` runs secret scan + STRIDE + code scan. `--deep` adds auth review + pentest.

## Output
Consolidated pass/fail report across all sub-scanners. Exit 0 = all clear.

## Related
- `engine/agents/sec/sec-lead.md`
- `.claude/tools/sec/lead/sec-sweep.sh`
