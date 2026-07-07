# 🔎 Research & Internet — how agents gather truth

> **Foundation:** This protocol serves Teaching **IV (Token Economy)** — research the cheapest way first (brain → codebase → search → fetch), escalate only when the answer isn't there. Read `engine/DOCTRINE.md` before this file.

Teaches every agent when and how to use search, the web, and verification. Default to internal context; go online only when it adds truth.

## Escalation ladder (cheapest first — stop when answered)
1. **Brain** — `projects/<PRJ-ID>/_context/*` + existing `docs/`. Most answers live here.
2. **Codebase** — `Grep`/`Glob`/`Read`, or delegate to `cavecrew-investigator` (returns `file:line`, ~60% smaller result).
3. **WebSearch** — current facts the model can't know: library versions, CVEs, pricing, API changes, benchmarks, competitor state.
4. **WebFetch** — read a specific URL surfaced by search or given by the user (docs page, RFC, changelog).
5. **Verify** — cross-check any load-bearing claim against a 2nd source before it enters `DECISIONS.md`.

## When internet is REQUIRED (not optional)
- Choosing/ pinning a dependency version → confirm latest stable + known CVEs.
- 3rd-party API integration → fetch the official spec/changelog, never guess fields.
- Security (`security-compliance-architect`) → check OWASP + CVE feeds for the chosen stack.
- Competitor/market work (`chief-product-strategist`, `ux-researcher`) → real current data.
- Performance budgets → current CWV thresholds + tooling docs.

## When internet is FORBIDDEN
- Anything answerable from the brain/codebase (don't burn tokens going online).
- Inventing facts to fill a gap — if search fails, write a flagged assumption in `CONTEXT.md`, don't fabricate.

## Citation rule
Every web-derived fact entering the brain carries its source: `claim [source: <url>, fetched <date-from-CEO>]`. No source → it's an assumption, label it.

## Anti-hallucination
- Quote error strings / API fields exactly; never paraphrase a signature.
- Distinguish "I read this" (cited) from "I infer this" (assumption).
- Conflicting sources → record both, let the role lead or CEO decide.

## Tools by capability (see `tooling-matrix.md`)
`WebSearch` + `WebFetch` granted to research/architecture/security/ops roles. Devs request a finding via their lead instead of each going online (saves tokens, one source of truth).
