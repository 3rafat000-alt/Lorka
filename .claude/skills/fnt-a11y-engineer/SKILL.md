---
name: fnt-a11y-engineer
description: "Enforce WCAG 2.2 AA in shipped code — keyboard, ARIA, contrast."
---
# Frontend - Accessibility Engineer

Scan templates for WCAG 2.2 AA compliance issues: missing alt text, missing labels, empty buttons, missing ARIA landmarks, and positive tabindex values.

## Tool
`.claude/tools/fnt/a11y-engineer/a11y-audit.sh`

## When to use
- Gate 4/5 accessibility audit: mandatory check before frontend signoff
- Pre-deployment: verify all templates meet WCAG 2.2 AA standard
- After any template change: regression check for accessibility issues

## How to use
```bash
.claude/tools/fnt/a11y-engineer/a11y-audit.sh <PRJ-ID> [--strict]
```

## Input
- `PRJ-ID` — project directory with `resources/` containing `.blade.php` and `.vue` files
- `--strict` — exit 1 on warnings in addition to failures

## Output
- PASS/FAIL per check:
  - Images have `alt` text
  - Inputs have `<label>` or `aria-label`
  - Buttons have visible text or `aria-label`
  - WARN: landmarks without ARIA roles
  - WARN: positive tabindex values
- Aggregate score (percentage)
- WCAG 2.2 AA compliance verdict

## Related
- `engine/agents/fnt/a11y-engineer.md`
- `.claude/tools/fnt/a11y-engineer/a11y-audit.sh`
