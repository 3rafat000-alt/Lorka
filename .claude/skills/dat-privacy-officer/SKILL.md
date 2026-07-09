---
name: dat-privacy-officer
description: "PII classification, retention windows, encryption-at-rest map."
---
# Data - Privacy Officer

Scan Eloquent models for potential PII fields and check encryption status. Identifies unencrypted PII (email, phone, SSN, etc.) and reports which fields need `$casts` encryption.

## Tool
`.claude/tools/dat/privacy-officer/pii-map.sh`

## When to use
- Gate 3+5 privacy audit: mandatory check before deployment
- Data protection compliance: GDPR/CCPA PII inventory
- Pre-release: verify all PII fields have encryption casts
- CI pipeline: `--json` flag for automated compliance gates

## How to use
```bash
.claude/tools/dat/privacy-officer/pii-map.sh <PRJ-ID> [--json]
```

## Input
- `PRJ-ID` — project directory with `app/Models/`
- `--json` — JSON output format for CI pipeline

## Output
- Per-model PII scan: list of fields matching PII patterns (email, phone, address, ssn, passport, dob, name, credit_card, iban, bic)
- Encryption status per field: `[ENCRYPTED]` if `$casts` has `encrypted` cast, `[UNENCRYPTED PII]` otherwise
- Summary: total PII fields found, unencrypted count
- JSON mode: `{"project": "...", "pii_fields": N, "unencrypted": N}`
- Exit 1 if unencrypted PII found

## Related
- `engine/agents/dat/privacy-officer.md`
- `.claude/tools/dat/privacy-officer/pii-map.sh`
