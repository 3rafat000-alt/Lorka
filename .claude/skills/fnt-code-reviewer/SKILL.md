---
name: fnt-code-reviewer
description: "Adversarial frontend diff review (clean context, V2)."
---
# Frontend - Code Reviewer

Adversarial frontend diff checker. Reviews diff for stale console.log, missing error handling, hardcoded strings (i18n), `any` types, missing empty states, and inline styles.

## Tool
`.claude/tools/fnt/code-reviewer/frontend-review.sh`

## When to use
- Pre-merge frontend review: automated pattern scan before PR
- Gate 5 frontend quality gate: catch common frontend issues
- Self-review: check own diff for debug artifacts and state handling gaps

## How to use
```bash
.claude/tools/fnt/code-reviewer/frontend-review.sh <PRJ-ID> [base-branch]
```

## Input
- `PRJ-ID` — project directory (must be a git repo)
- `base-branch` — comparison branch (default: `main`)

## Output
- Flagged patterns:
  - `[STALE DEBUG]` — `console.log/warn/error` left in diff
  - `[ERROR HANDLING]` — async without `.catch()`
  - `[I18N]` — Hardcoded visible strings longer than 20 chars
  - `[TYPES]` — `: any` usage that should be specific type
  - `[EMPTY STATE]` — `v-for/.map` without `v-if`/empty check
  - `[STYLE]` — Inline `style=` instead of Tailwind
- Zero-exit code on clean diff

## Related
- `engine/agents/fnt/code-reviewer.md`
- `.claude/tools/fnt/code-reviewer/frontend-review.sh`
