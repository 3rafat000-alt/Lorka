---
name: gtw-gatekeeper
description: "Gatekeeper — adversarial check in clean context; implementer never self-grades."
---
# Gateway - Gatekeeper

Adversarial fresh-context gate verification — checks all upstream deliverables exist before a gate pass.

## Tool
`.claude/tools/gtw/gatekeeper/gate-check.sh`

## When to use
- Every gate transition: before advancing from Gate N → N+1, adversarial check that all Gate-N artifacts are complete
- After a signoff: independent re-verification (the signer and the gatekeeper are never the same agent)
- Pre-landing PR review: verify no gate was skipped before merging
- Any time an implementer claims "done": the gatekeeper verifies with cold evidence

## How to use
```bash
.claude/tools/gtw/gatekeeper/gate-check.sh <PRJ-ID> <gate-number>
```

## Input
- `PRJ-ID` — project identifier
- `gate-number` — the gate to check (2, 3, 4, or 5)
- Reads `projects/<PRJ>/docs/` and `projects/<PRJ>/_context/` for gate artifacts
- Supported gates: 2 (Prototype_Spec, Journey_Map), 3 (Architecture.md, DECISIONS.md), 4 (source, OpenAPI), 5 (tests, coverage)

## Output
- Per-artifact checklist with ✓/✗ markers
- ERROR count and exit code (0 = pass, non-zero = reject)
- Specific missing file paths listed for easy remediation

## Related
- `.claude/tools/brd/ceo/sofi-exec.sh --check-gate <N>` — combined exec + gate check
- `engine/lifecycle/gates.md` — gate definitions and artifact requirements
- `engine/protocols/verification.md` — v5: outcome over self-report
