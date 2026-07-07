# Playbook — Competitor Teardown

> Owner: `res-competitor-analyst` (Pieter van Zyl), sourcing support from `res-web-scout`, verification from `res-fact-checker`. The room's sharpest recurring specialty job: judging competitors by resolved user friction, not feature parity, for every market-facing project.

## When to run this

Any Gate-1 pass on a project `01-strategy` has flagged as market-facing (the project competes for the same user attention/spend as existing products). Skip it for internal tools, admin panels, or single-tenant B2B builds with no open market — check `docs/<PRJ>_Blueprint.md` for the market-facing flag before starting; if it's ambiguous, ask `res-lead`, don't assume either way.

## Steps

### 1. Ground in the persona, not the market
Read `res-ux-researcher`'s frozen `docs/<PRJ>_Personas.md` and pain/gain table first. The teardown is judged through the primary persona's top 3-5 friction points — a competitor with more features but no answer to the persona's actual top pain is not "ahead."

### 2. Identify the field
List 3-5 real, currently-operating competitors — direct competitors first, then one or two adjacent/substitute products the persona might reach for instead (the substitute is often more informative than the direct competitor). Never include a defunct or pre-launch product as a live comparison point.

### 3. Request sourced material
```bash
sofi dispatch PRJ-XXXX --agent res-web-scout --ticket TKT-NNN-scout \
  --intent "fetch <competitor>'s current product page, changelog, and recent app-store/support-forum feedback"
```
Repeat per competitor. Never work from memory of an older product version — competitors ship changes; a teardown built on stale memory is a liability, not research.

### 4. Walk the flow against the persona's friction
For each competitor, for each of the persona's top friction points: does the competitor resolve it, partially resolve it, or not address it? Score honestly — "resolves it but adds new friction elsewhere" is its own category, not a pass.

### 5. Mine the honest evidence: error states, empty states, and complaints
Screenshot or describe what the competitor shows when something goes wrong (a failed payment, an empty search result, an offline state) — this is where marketing polish stops and real product quality shows. Pull the 3-5 most substantive recent complaints from app-store reviews or support forums; a five-star average with a specific recurring complaint buried in the text is more informative than the star rating.

### 6. Write the teardown, one weak point named per competitor — no exceptions
Every competitor entry, including the market leader, states at least one honest weak point. A teardown with a competitor entry that reads as pure praise has not looked hard enough — go back to step 5.

### 7. Route to the fact-checker
```bash
sofi dispatch PRJ-XXXX --agent res-fact-checker --ticket TKT-NNN --target Competitor_Teardown.md
```
Every claim needs a source and fetch date; `res-fact-checker` verifies each cited source actually supports the specific claim made about that competitor, not something adjacent to it.

### 8. Hand to res-lead
The finished, fact-checked teardown joins the rest of the Gate-1 bundle at `docs/<PRJ>_Competitor_Teardown.md`, routed to `res-lead` for the room-level freeze decision.

## Worked shape (what the artifact looks like)

```
## Competitor: <Name>
- Resolves persona friction "<friction 1>"? Yes / Partially / No — <evidence>
- Resolves persona friction "<friction 2>"? Yes / Partially / No — <evidence>
- Honest weak point: <specific, sourced observation from error states/reviews>
- Sources: [source: url, fetched date] · [source: url, fetched date]
```

## Rules

- Never a feature-count table alone — every row must connect to a specific persona friction point or it doesn't belong in this artifact.
- Never skip the "honest weak point" for the market leader out of assumed deference — that is exactly the entry `03-design` most needs to differentiate against.
- Never fetch once and treat it as evergreen — competitor products change; if this teardown is reused on a Gate-8 loop-back, re-fetch, don't reuse the old citations.
- Pairs with `playbooks/discovery-gate-procedure.md` step 3 (this playbook is the detailed version of that step, specific to `res-competitor-analyst`'s job).
