---
name: res-fact-checker
description: "Adversarial fact-checker — grounding enforcement G1–G5."
---
# Research - Fact Checker

Adversarially verify a factual claim against project sources — brain files, codebase, or external citations.

## Tool
`.claude/tools/res/fact-checker/ground-check.sh`

## When to use
- After any research artifact is created: verify every claim is grounded
- Before a Gate 2 handoff: the Journey Map and personas must be fact-checked
- V5 grounding clause enforcement: any agent asserting "tests pass" or "done" must be verified
- Any time a claim without a citation appears in CONTEXT.md or HANDOFFS.md
- CEO requests grounding audit: scan all recent artifacts for unverified claims

## How to use
```bash
.claude/tools/res/fact-checker/ground-check.sh <PRJ-ID> --claim "<claim>" [--expected-source "<path>"] [--depth <n>]
```

## Input
- `PRJ-ID` — project identifier
- `--claim` — the factual claim to verify
- `--expected-source` — optional expected source file path
- `--depth` — search depth (default: 3)
- Searches `projects/<PRJ>/` for evidence supporting or refuting the claim

## Output
- Verification status: FOUND / NOT FOUND / CONFLICT
- If found: file:line citations for supporting evidence
- If conflicting: surfaces both sources without silently choosing
- `[verified: source]` or `[unverified]` marker
- Exit code 0 if verified, non-zero if unverified or conflicting

## Related
- `.claude/tools/res/web-scout/fetch-cite.sh` — upstream: fetch external sources for fact-checking
- `engine/protocols/grounding.md` — v5 binding: ground or abstain
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — downstream: adversarial gate check uses fact-checked artifacts
