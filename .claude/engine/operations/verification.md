# Verification Protocol — Outcome Over Self-Report

**No gate advances on self-report.** Every claim requires mechanical evidence verified in a fresh context.

## Evidence Types

| Claim | Evidence Required | Verification Command |
|-------|------------------|---------------------|
| "Tests pass" | Test runner output + exit code | `php artisan test` / `phpunit` / `pest` / `jest` |
| "Migration ran" | `migrations` table + pretend output | `php artisan migrate --pretend` then `php artisan migrate:status` |
| "Coverage ≥ 90%" | Coverage report (Clover/HTML) | `phpunit --coverage-clover=coverage.xml` |
| "TTI < 2s" | Lighthouse JSON | `lighthouse --output=json --quiet` |
| "API responds" | curl HTTP status + body | `curl -s -o /dev/null -w "%{http_code}" <url>` |
| "Deployed" | Health endpoint returns 200 | `curl https://example.com/api/health` |
| "No secrets" | Secrets scan output | `gitleaks detect` / `trufflehog` |
| "No lint errors" | Linter output | `php -l` / `eslint` / `pint` / `blade-formatter` |
| "Build passes" | Build tool output | `npm run build` / `composer install --no-dev` |
| "Schema matches spec" | Schema dump diff | `mysqldump --no-data` diff against expected |

## Gate Check Process

```
┌─────────────────────────────────────────────────────┐
│  gtw-gatekeeper (clean context, never implementer): │
│  1. Read original ticket criteria (fresh context)   │
│  2. Read implementer's RCCF evidence block          │
│  3. Adversarial: try to DISPROVE each claim         │
│  4. Run independent verification where possible     │
│  5. PASS or BLOCK with "why"                        │
└─────────────────────────────────────────────────────┘
```

## Adversarial Mindset

The gatekeeper does not trust the implementer. Questions to ask:
- Does the evidence actually prove the claim?
- Could the evidence be faked or cherry-picked?
- Are there edge cases the implementer missed?
- Does the test cover the failure path, not just the happy path?
- Is the coverage measurement meaningful (branch coverage, not line)?

## Pass/Fail Criteria

| Gate Check Result | Meaning | Action |
|-------------------|---------|--------|
| **PASS** | All criteria met with verifiable evidence | Advance to next gate |
| **PASS WITH NOTES** | All criteria met, minor observations | Advance, but implementer should address notes |
| **BLOCK — insufficient evidence** | Claims unverifiable | Implementer must add evidence and resubmit |
| **BLOCK — criteria not met** | One or more criteria fail | Implementer reworks, resubmits |
| **BLOCK — fresh context contradiction** | Independent verification contradicts claims | Investigation required, possible escalation |

## Automation

Where possible, verification is automated:
- CI pipeline runs verification commands on every push
- Gate check scripts in `.claude/tools/gtw-gatekeeper/`
- Results logged to `.claude/engine/monitoring/`

## Enforcement

- No manual override of automated verification (except CSO/CEO joint sign-off)
- False evidence = immediate escalation to CSO
- Repeated verification failures → effort class upgrade + budget-warden review
