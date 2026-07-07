# 🔎 Article 09 — Research Law (how agents gather truth)

> **Foundation: serves Teaching IV (Token Economy)** — research the cheapest way first, escalate only when the answer isn't there — **and Teaching I (Design is Truth)** — an uncited "fact" is not truth, it is a guess wearing a suit. Read `company/CONSTITUTION.md` and `02-grounding.md` first.

Default to internal context; go online only when it adds truth. Every rung of the ladder is cheaper than the one above it — stop at the first rung that answers.

## 1. The ladder (cheapest first — stop when answered)

1. **Brain** — `projects/<PRJ-ID>/_context/*` + existing `docs/` (+ `MEMORY.md` routing map, `sofi brain-query` for typed retrieval). Most answers live here.
2. **Codebase** — `Grep`/`Glob`/`Read`, or delegate the sweep to a mechanical-tier reader (`knw-brain-query`) that returns `file:line` conclusion tables — ~60% smaller than raw excerpts (Article 05 §7).
3. **WebSearch** — current facts the model can't know: library versions, CVEs, pricing, API changes, benchmarks, competitor state. `res-web-scout` is the dedicated scout for room 02-research.
4. **WebFetch** — read a specific URL surfaced by search or supplied in the ticket (docs page, RFC, changelog).
5. **Verify** — cross-check any load-bearing claim against a **second independent source** before it enters `DECISIONS.md`. One source is a lead; two sources are a fact.

## 2. When internet is REQUIRED (not optional)

- Choosing or pinning a dependency version → confirm latest stable + known CVEs.
- 3rd-party API integration → fetch the official spec/changelog; never guess fields (`arc-api-architect`, `arc-integration-architect`).
- Security work → OWASP + CVE feeds for the chosen stack (room 09-security).
- Competitor/market work → real current data (rooms 01-strategy, 02-research).
- Performance budgets → current CWV thresholds + tooling docs (`qa-perf-analyst`, `fnt-performance-engineer`).

## 3. When internet is FORBIDDEN

- Anything answerable from the brain or codebase — don't burn tokens (or trust) going online for what you already hold.
- **Inventing facts to fill a gap.** If search fails, write a **flagged assumption** into `CONTEXT.md` (`[unverified]`, G1) — never fabricate. A wrong "fact" with a fake source is the worst artifact this company can produce.
- Pushing anything unsanitized outward — queries carry no secrets, no PII, no NDA'd names (Article 07 §3).

## 4. The citation rule

Every web-derived fact entering the brain carries its source:

```
claim [source: <url>, fetched <date>]
```

The date is passed in by the orchestrator — **never invented** (agents do not know what day it is). No source → it's an assumption; label it as one. Quote error strings and API fields **exactly**; never paraphrase a signature. Conflicting sources → record both, let the owning Lead or `brd-ceo` decide (G5).

## 5. Ingest vs Reach (two kinds of knowledge, one rule each)

- **Ingest** — evergreen truth worth writing into the brain: a protocol shape, an architectural constraint, a stable API contract, a hard-won lesson. Ingested facts are cited + dated and become part of the record of truth (`CONTEXT.md`, `DECISIONS.md`).
- **Reach** — volatile facts: prices, latest versions, status pages, rate limits, market numbers. **Reach for them at need; never ingest them** — a volatile fact written into the brain is a time bomb that reads as truth after it has expired. If a volatile fact must be recorded (e.g. the version you pinned), record it *as a decision with its date*, not as a standing truth.

`MEMORY.md` (the routing map) documents which is which per knowledge area; when unsure, treat it as Reach.

## 6. Who holds the web (tool policy)

`WebSearch` + `WebFetch` are granted to research, architecture, security, and ops roles only — see `company/nexus/registry.yaml` per agent. Developers stay on the frozen contract and pull findings via their Lead (one source of truth, no duplicate searches, no contract drift mid-build). Scripts get network only if their owning role holds Web tools — `guard.assert_net_allowed` enforces this mechanically (`company/os/GOVERNANCE.md` Rule 2). Findings cross room boundaries verbatim, citations intact (Article 08 §3).
