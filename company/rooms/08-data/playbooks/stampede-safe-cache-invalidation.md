# Playbook — Stampede-Safe Cache Invalidation (specialty procedure)

> Owner: `dat-cache-engineer` (Rafael Couto). The room's sharpest recurring job outside the core gate procedure: designing a Redis (or equivalent) caching layer whose invalidation survives a thundering-herd miss instead of amplifying it into an outage. A cache that works fine at low traffic and falls over the first time a hot key expires under real load has not been designed, it has been assumed.

## When to run this

Any time `dat-db-engineer` hands over a query that's a caching candidate (high read frequency, expensive to compute, tolerant of some staleness), or a Gate-5 finding traces a latency spike or an outage back to a cache-miss cascade. Also re-run any time an existing cache key's underlying data-mutation pattern changes — a key that was safe to cache under one write pattern may not be under a new one.

## Steps

### 1. Confirm the query is actually a caching candidate — don't cache by default
Ask, in order: is this read hot enough that the query cost matters? Is some staleness tolerable for this data? Is there a cheaper fix (an index `dat-db-engineer` hasn't added yet) that solves the cost problem without adding a cache's correctness burden at all? Caching is not free — it trades a query-cost problem for an invalidation-correctness problem, and that trade has to be worth making, explicitly.

### 2. Design the cache key and its versioning
- Derive the key from the entity's identity plus a version component (a row's `updated_at`, an explicit version column, or a content hash) — never a bare entity ID with an implicit "whatever's there is current" assumption.
- State exactly what invalidates the key: a specific write path, a specific event, or a specific TTL — name it, don't leave it implicit in "the cache clears itself eventually."

### 3. Pick a stampede-prevention mechanism — explicitly, not by default
| Mechanism | When it fits |
|---|---|
| **Distributed lock on miss** (one request recomputes, others wait or serve stale) | Expensive-to-compute value, moderate concurrency, staleness during the lock window is acceptable |
| **TTL + jitter** (randomize expiry within a window, not all keys expiring at once) | Many similar keys created around the same time (e.g. a daily batch), preventing a synchronized mass-expiry |
| **Stale-while-revalidate** (serve the stale value immediately, refresh in the background) | High-concurrency reads where even a brief lock-wait is unacceptable, and slight staleness is fine |
| **Versioned key, never expire the old version** (write a new version, flip a pointer, old versions age out passively) | Data that changes in discrete, known events rather than continuously — avoids the miss/stampede question by never deleting the old value out from under in-flight readers |

Pick one, state why, and write it into the design doc before implementation — "TTL and hope" is not a listed option because it isn't a mechanism, it's the absence of one.

### 4. Answer the thousand-request-miss question explicitly
Write down: if this key is cold (first request, post-deploy, or post-invalidation) and a thousand requests arrive for it in the same second, what happens? With a lock: 999 wait or get stale, 1 recomputes. With stale-while-revalidate: all 999 get the (possibly slightly stale, possibly absent-on-true-cold-start) value while one background refresh runs. If the honest answer is "they'd all hit the database at once," the design isn't done — go back to step 3.

### 5. Design the cold-start / cold-deploy case separately
A key that's never been populated (true cold start, or the entire cache flushed on deploy) is a distinct case from a normal miss under steady-state traffic — it can hit every key at once, not just one. State explicitly whether the deploy process pre-warms critical keys, or whether the stampede-prevention mechanism from step 3 is trusted to absorb a cold-start spike on its own; don't leave this implicit.

### 6. Validate against real traffic once the backend is built
Read actual read patterns from `bck-domain-engineer`'s built services (via `dat-lead`/`bck-lead`) — confirm the assumed hot keys are actually hot, and that the concurrency assumption behind the chosen stampede mechanism holds under the real request rate, not the one guessed at design time.

### 7. Write the invalidation contract as a document the calling service can rely on
Not just code — a short, explicit doc per key: what triggers invalidation, what the stampede mechanism is, what the cold-start behavior is. `bck-domain-engineer`'s services depend on this contract holding; a cache design that only lives in Rafael's head is not a deliverable.

## Worked example (shape only)

```
Key: user:{id}:v{updated_at_epoch}
Candidate: profile-read endpoint, ~200 req/s at peak, DB read costs ~40ms uncached.
Staleness tolerance: up to 30s acceptable (not a real-time balance field).
Mechanism: stale-while-revalidate — serve current cached version immediately,
           background-refresh triggers when age > 20s, single-flight guarded
           per key so only one refresh runs concurrently.
Thousand-request-miss: true cold key (never cached) — first request computes
           and populates synchronously, held behind a per-key lock; the other
           999 wait up to 200ms for the lock, then read the now-populated key.
           Never falls through to 999 simultaneous DB reads.
Cold-deploy: top 500 users by activity pre-warmed via a deploy-time job;
           the rest rely on the lock-on-miss path above, bounded by design.
Invalidation trigger: profile-update write path calls cache->forget(key)
           explicitly; version bump on updated_at makes any stale reference
           self-invalidating even if forget() is ever missed.
```

## Rules

- Never cache a query without first asking whether an index fixes the actual cost problem — a cache is a correctness trade, not a free win.
- Never accept a design with no answer to the thousand-request-miss question — that answer IS the design, same discipline as `bck-queue-engineer`'s "runs twice" question for jobs.
- Never treat cold-start/cold-deploy as the same case as a steady-state miss — it can hit every key at once and needs its own explicit answer.
- The invalidation contract is a document, not tribal knowledge — `bck-domain-engineer`'s services rely on it existing in writing.
- Pairs with the core `gate-3-4-data-layer.md` (step 9 dispatches this playbook's owner) and `dat-db-engineer`'s optimized-query handoff (the two roles co-own the cost/correctness trade at the caching seam).
