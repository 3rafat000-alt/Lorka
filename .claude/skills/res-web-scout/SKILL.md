---
name: res-web-scout
description: "Web search/fetch/verify/cite — dedicated scout (holds Web tools)."
---
# Research - Web Scout

Fetch a URL, capture content, verify accessibility, and produce a grounded citation block.

## Tool
`.claude/tools/res/web-scout/fetch-cite.sh`

## When to use
- Gate 1 Discovery: researching competitors, benchmarks, or reference implementations
- Fact-checking: verify a claim against a published source
- Literature review: capture relevant articles, docs, or standards
- Grounding clause compliance (v5): every external claim needs a [verified: url] citation

## How to use
```bash
.claude/tools/res/web-scout/fetch-cite.sh <url> [--cite "<context>"]
```

## Input
- `url` — full URL to fetch
- `--cite` — optional context note describing why this was fetched
- Uses curl with 10s timeout and follows redirects

## Output
- Fetch status (success/failure)
- Page title extracted from HTML
- Citation block: `[verified: <url>]` or `[unverified: <url>]`
- Exit code 0 if fetch succeeded, non-zero if failed

## Related
- `.claude/tools/res/fact-checker/ground-check.sh` — downstream: verify a claim against fetched sources
- `engine/protocols/grounding.md` — v5: ground or abstain
- `.claude/tools/res/competitor-analyst/teardown.sh` — uses web-scout data for competitive analysis
