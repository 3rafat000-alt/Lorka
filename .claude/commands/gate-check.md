---
description: "Run adversarial gate check. Use: /gate-check <gate-number> <artifact>"
agent: gtw-gatekeeper
---

# Gate Check — Gate $1: $2

Adversarial review in clean context (not the implementer's session).

## Verification criteria:
- Gate 0: problem named? scope frozen? 5 deep questions?
- Gate 1: personas evidence-based? journey map traced? claims verified?
- Gate 2: all screens spec'd? a11y matrix? copy as JSON?
- Gate 3: system/API/data/infra designs frozen? threat model? reversible?
- Gate 4: code matches frozen contracts? all states handled? tests pass?
- Gate 5: coverage ≥90%? CWV passes? security scan clean? design matches spec?
- Gate 6: staging deployed? rollback proven? migrations run?
- Gate 7: prod deployed? monitored? release report written?
- Gate 8: SLI/SLO defined? dashboards live? alert rules dry-tested?

Paste mechanical evidence for each criterion. Issue single verdict: PASS or BLOCK with evidence.