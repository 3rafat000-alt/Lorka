# Fast-Track vs Deep-Audit — Risk-Based Gate Classification

Every feature MUST be classified before entering the lifecycle. Classification determines which gates are mandatory.

## Fast-Track

Collapses Gates 1-3 into one Blueprint check. Saves ~60% overhead.

### Eligible
- UI copy changes, label edits, placeholder text
- i18n / translation updates (non-functional)
- Non-money Blade field additions/removals
- CSS / Tailwind visual tweaks (no logic impact)
- Component layout adjustments (responsive fixes)
- Typo fixes, documentation corrections
- Non-production config changes (dev-only)

### Process
```
Blueprint Check -> Gate 4 Build -> Gate 5 Quality -> Gate 6 Staging -> Gate 7 Production
```
One lightweight review covers Gates 1-3 instead of three separate deep-dives.

### Gate
- Blueprint check: str-lead reviews scope, confirms fast-track eligibility
- Quality gate: standard Gate 5, no shortcuts
- If scope creep detected mid-build -> escalate to Deep-Audit

## Deep-Audit

Full 9 gates. Every gate signed individually. No exceptions.

### Mandatory For
- Money: transactions, wallets, payments, pricing, financial calculations
- Auth: login, registration, password reset, session management, OAuth, SSO
- KYC/Identity: user verification, document upload, compliance checks
- PII: personal data collection, storage, export, deletion
- Security-critical: encryption, secrets management, RBAC, API keys
- Integrations: third-party APIs, webhooks, webhook handlers
- Data-mutating: migrations without rollback, bulk operations, DDL
- Compliance: GDPR, PCI-DSS, financial regulation surfaces

### Process
```
0 Inception -> 1 Discovery -> 2 Design -> 3 Architecture -> 4 Build -> 5 Quality -> 6 Staging -> 7 Production -> 8 Observe
```
Each gate produces a signed artifact. No skip. Reject upward if upstream incomplete.

## Classification Authority

- **str-lead** (Amara Okafor) classifies at Inception
- Gatekeeper may reclassify mid-flight if scope changes
- When in doubt: **Deep-Audit** by default
- Reclassification requires ADR entry
