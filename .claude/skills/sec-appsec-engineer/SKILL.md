---
name: sec-appsec-engineer
description: "Secure code review — injection, broken auth, IDOR/BOLA, SSRF."
---
# Security - AppSec Engineer

Scan PHP/Python/JS code for injection, SSRF, IDOR patterns.

## Tool
`.claude/tools/sec/appsec-engineer/code-scan.sh`

## When to use
- Before every Gate 4 merge
- After dependency changes touching request handling
- As part of CI pipeline security gate
- Discovering legacy code injection surface

## How to use
```bash
.claude/tools/sec/appsec-engineer/code-scan.sh --prj PRJ-XXXX [--path dir] [--format plain|json]
```

## Input
PRJ-ID or explicit path. Scans files with `.php`, `.py`, `.js` extensions for dangerous patterns (SQL injection, command injection, SSRF, eval).

## Output
Per-pattern pass/fail with matching file locations. JSON format available for CI integration.

## Related
- `engine/agents/sec/sec-appsec-engineer.md`
- `.claude/tools/sec/appsec-engineer/code-scan.sh`
