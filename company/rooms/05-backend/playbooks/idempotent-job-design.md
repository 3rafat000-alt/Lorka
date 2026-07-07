# Playbook — Idempotent Job Design (specialty procedure)

> Owner: `bck-queue-engineer` (Marek Nowak). The room's sharpest recurring job outside the core gate procedure: turning any slow or risky operation — a payment capture, a notification fan-out, an inbound webhook — into a job, event, or channel that survives being run twice, arriving late, or never arriving at all. Every real message broker redelivers; a handler that isn't idempotent isn't finished, whatever else it does correctly.

## When to run this

Any time an endpoint (`bck-api-engineer`), a domain service (`bck-domain-engineer`), or a confirmed webhook (`bck-integration-engineer`) needs to hand work off the request path — moved to a queue, fired as an event, or pushed over a WebSocket channel. Also re-run on any Gate-5 finding tracing a duplicate-processing or lost-event bug back to this room.

## Steps

### 1. Ask the question before writing a single line
"What happens if this runs twice? What happens if it arrives late? What happens if it never arrives?" Answer all three explicitly, in writing, before the `handle()` method exists. A job with no answer to any one of these is not ready to be written.

### 2. Design the dedup/idempotency key
- Derive it from something inherent to the operation, never a wall-clock timestamp or a random value generated inside the job itself (Article 05 — tools are deterministic, no randomness inside the tool; the same discipline applies here: the key must be reproducible from the input, not invented at execution time).
- For a webhook-triggered job, use the vendor's own event/delivery ID if one is documented (confirm with `bck-integration-engineer`) — never derive a synthetic key that might collide or miss a legitimate redelivery.
- Store the key with a uniqueness constraint at the database level where the job's side effect touches persisted state — app-only dedup logic is not a real guard against a race (steel rule 4, same discipline `arc-data-architect` enforces at the schema layer).

### 3. Design the retry/backoff/dead-letter policy
| Failure class | Policy |
|---|---|
| Transient (network blip, brief rate limit) | Bounded retry with exponential backoff — never unbounded |
| Vendor-documented rate limit | Backoff honoring the vendor's documented reset window, confirmed with `bck-integration-engineer` |
| Permanent (validation failure, malformed payload) | No retry — straight to dead-letter, a human inspects |
| Unknown/unclassified failure after N attempts | Dead-letter, never a silent drop |

Every job declares its own ceiling explicitly — "retry forever" is not a policy, it's a future incident.

### 4. Make every listener safe to run twice
A domain event can be delivered more than once by any real broker under partition or redelivery. Every listener either:
- checks its own idempotency key before applying a side effect, or
- is naturally idempotent (e.g. a `SET status = 'confirmed'` that's already `'confirmed'` is a no-op, not a double-charge).

Never assume "the event only fires once in practice" — design for the redelivery, because it will happen.

### 5. Scope WebSocket channels to exactly what the contract promises
- Authorize the channel per the contract's stated audience — never broadcast broader than what's documented, even if it's technically convenient.
- Document the client-facing reconnect/backoff expectation so `06-frontend`/`bck-blade-engineer` implement a consistent recovery experience, not a silent stall on disconnect.

### 6. Write the "runs twice" test as the PRIMARY test case
```bash
# example shape — adapt to the project's test framework
php artisan test --filter=JobRunsTwiceWithoutDuplicateEffect
```
This test is not a nice-to-have appended after the happy-path test — it is the test that actually proves the job is done. A job with a happy-path test and no "runs twice" test has not demonstrated idempotency, only that it works once.

### 7. Hand off the idempotency contract explicitly
When a webhook becomes a job, `bck-integration-engineer` hands `bck-queue-engineer` the vendor's redelivery behavior (does it retry on non-2xx? how many times? what's the delivery ID field?) — and `bck-queue-engineer` hands back the dedup key derivation so the integration engineer's handler and the job agree on what "the same event" means.

## Worked example (shape only)

```
Operation: payment-confirmed webhook → domain event → notification job
Runs twice?  Vendor redelivers on non-2xx up to 5x with the same X-Event-Id header.
             Dedup key = X-Event-Id, unique constraint on processed_webhook_events.event_id.
Arrives late? Job is safe to process an already-confirmed payment as a no-op (status check before mutation).
Never arrives? Reconciliation job (separate ticket, dat-etl-engineer) polls the vendor's API hourly for confirmed-but-unprocessed payments — named explicitly, not assumed away.
Retry policy: 3 attempts, exponential backoff (10s/60s/300s), dead-letter after — a human reviews the dead-letter queue.
Test: NotificationJobRunsTwiceWithoutDuplicateSend — asserts exactly one notification sent when the job is dispatched twice with the same payload.
```

## Rules

- Never write a job's `handle()` before answering the three redelivery questions in step 1 — that answer IS the design, not an afterthought documented after the fact.
- Never rely on app-only dedup logic where a database-level unique constraint is possible — the constraint is the real guard, the app logic is a fast-path optimization on top of it.
- Never ship "retry forever" — every policy declares its own ceiling and its dead-letter destination.
- The "runs twice" test is mandatory, not optional, for every job, listener, and webhook handler this room ships — `bck-code-reviewer` checks for its presence explicitly as part of the room's Gate-4 bar.
- Pairs with the core `gate-4-build-procedure.md` (step 4 dispatches this playbook's owner) and `bck-integration-engineer`'s webhook-signature discipline (the two roles co-own the idempotency contract at the webhook seam).
