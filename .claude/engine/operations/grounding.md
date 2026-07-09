# Grounding Protocol — Source-Bound Truth

**Ground or abstain.** Every claim MUST carry a verifiable source tag. No tag = suppressed.

## Source Tag System

| Tag | Meaning | Example |
|-----|---------|---------|
| `[verified: file:line]` | Code evidence at specific location | `[verified: app/Models/Wallet.php:42]` |
| `[verified: brain]` | Retrieved from brain database | `[verified: brain: user_wallet_balance]` |
| `[verified: commit:SHA]` | Git commit evidence | `[verified: commit:abc123def]` |
| `[verified: url]` | Web source (roles with Web tools) | `[verified: https://example.com/docs]` |
| `[verified: test]` | Test output evidence | `[verified: test: WalletTest::test_balance]` |
| `[inferred]` | Logical deduction from verified sources | `[inferred: from balance + fee formula]` |
| `[unverified]` | **STOP** — do not assert, escalate | — |

## Enforcement Rules

1. **No tag = suppressed.** Any statement without a source tag is treated as absent.
2. **"Tests pass" without pasted output** = suppressed. Paste the actual output.
3. **Conflicting sources** — surface both with tags, explain the discrepancy. Never silently pick one.
4. **Multi-hop claims** — each hop must be tagged individually. Chain of verification.
5. **Insufficient info = escalate** — is a REWARDED output, never a failure.
6. **Self-report is NOT evidence** — "I verified this works" without proof = unverified.

## Verification Chain

After any action, verify the outcome and tag the verification:

```
Action: git commit -m "feat(wallet): add balance check"
Verify: git log --oneline -3 [verified: commit:abc123def]
Verify: phpunit tests/Feature/WalletTest.php [verified: test: PASS]
```

## Grounding Pyramid

```
       ┌──────────┐
       │  Inferred │  ← deduction from verified sources
       ├──────────┤
       │ Verified  │  ← code, brain, test, url evidence
       ├──────────┤
       │ Grounded  │  ← tagged claim
       └──────────┘
```

## Examples

- ✅ `Wallet balance is 1,250 SYP [verified: app/Services/WalletService.php:88]`
- ✅ `User has 3 active orders [verified: brain: user_123_active_orders]`
- ✅ `Migration 2024_01_01_create_wallets_table ran [verified: php artisan migrate:status output]`
- ❌ `Wallet balance is 1,250 SYP` (no tag — suppressed)
- ❌ `All tests pass` (no output — suppressed)
- ✅ `Tests pass [verified: test: phpunit — 45 passed, 0 failed]`

## Gate Check

Gatekeeper verifies grounding compliance before passing any gate:
- Every claim in the deliverable carries a source tag
- Evidence is pasted, not just asserted
- Conflicts are surfaced, not hidden
