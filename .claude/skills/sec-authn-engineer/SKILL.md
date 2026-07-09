---
name: sec-authn-engineer
description: "Auth/session/crypto design review (lifetimes, rotation, hashing)."
---
# Security - Auth Engineer

Review auth flow: sessions, tokens, MFA, PIN enforcement.

## Tool
`.claude/tools/sec/authn-engineer/auth-review.sh`

## When to use
- New authentication implementation review
- Session management audit before launch
- Token expiry configuration check
- MFA/PIN enforcement gap analysis

## How to use
```bash
.claude/tools/sec/authn-engineer/auth-review.sh --prj PRJ-XXXX [--check sessions|tokens|mfa|all]
```

## Input
PRJ-ID. `--check` narrows to specific subsystem. Scans for Sanctum/Passport/JWT usage, session regeneration, TTL configuration, MFA patterns.

## Output
Per-category pass/fail with code locations. Highlights missing regeneration, missing expiry, missing MFA enforcement.

## Related
- `engine/agents/sec/sec-authn-engineer.md`
- `.claude/tools/sec/authn-engineer/auth-review.sh`
