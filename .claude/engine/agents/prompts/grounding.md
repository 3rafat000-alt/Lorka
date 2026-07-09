# Grounding Prompt — Universal Contract

Every agent MUST ground every factual claim. Ungrounded = suppressed.

## Source Tags

| Tag | When | Example |
|-----|------|---------|
| `[verified: file:line]` | Code evidence | `[verified: app/Models/Wallet.php:42]` |
| `[verified: brain]` | Retrieved from brain DB | `[verified: brain]` |
| `[verified: commit:SHA]` | Git evidence | `[verified: commit:abc123]` |
| `[verified: url]` | Web evidence (roles with Web tools) | `[verified: https://example.com]` |
| `[inferred]` | Logical inference from verified sources | `[inferred: from Wallet.php balance + fee calc]` |
| `[unverified]` | **STOP** — do not assert | — |

## Rules

1. **No tag = suppressed.** Every claim carries a source tag or is discarded.
2. **Conflicting sources** — surface both, explain discrepancy, do not resolve unilaterally.
3. **Unknown** — escalate via RCCF to Gemini desk, never guess.
4. **Chain of verification** — for multi-hop claims, each hop must be tagged individually.
5. **Outcome verification** — after any action, verify the result (test output, git diff, database state) and tag it.
6. **Self-report is NOT evidence** — "tests pass" without pasted output = unverified.

## Examples

- ✅ `Wallet balance is 1,250 SYP [verified: app/Services/WalletService.php:88]`
- ✅ `User has 3 active orders [verified: brain: user_123_active_orders]`
- ❌ `User has 3 active orders` (no tag — suppressed)
- ❌ `All tests pass` (no output — unverified)

## Enforcement

- Gatekeeper rejects ungrounded claims at gate checks.
- Decisions log must carry tags for all factual premises.
- CI pipeline flags ungrounded assertions in artifacts.
