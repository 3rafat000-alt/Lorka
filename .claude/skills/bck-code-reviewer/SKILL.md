---
name: bck-code-reviewer
description: "Adversarial diff review (clean context, V2) before any merge."
---
# Backend - Code Reviewer

Review diff against base branch for SQL safety, N+1 queries, TODOs, hardcoded secrets, and unsafe mass assignment. Structural pattern scan for common Laravel issues.

## Tool
`.claude/tools/bck/code-reviewer/diff-review.sh`

## When to use
- Pre-merge review: check diff for security and code quality issues
- Gate 5 backend quality gate: automated pattern scanning
- Before PR submission: self-review your own diff for common mistakes

## How to use
```bash
.claude/tools/bck/code-reviewer/diff-review.sh <PRJ-ID> [base-branch]
```

## Input
- `PRJ-ID` — project directory (must be a git repo)
- `base-branch` — comparison branch (default: `main`)

## Output
- Files changed list
- Flagged patterns:
  - `[SECURITY]` — Raw SQL (DB::raw), hardcoded secrets
  - `[N+1]` — Potential lazy loading (::all(), ->load())
  - `[DEBT]` — TODO/FIXME/HACK/XXX markers
  - `[WARN]` — Mass assignment without validated()
- Zero-exit code on clean review

## Related
- `engine/agents/bck/code-reviewer.md`
- `.claude/tools/bck/code-reviewer/diff-review.sh`
