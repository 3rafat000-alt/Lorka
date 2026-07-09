---
name: fnt-css-artisan
description: "Tailwind, responsive 320–1200+, taste metrics enforced in rendered output."
---
# Frontend - CSS Artisan

Scan Blade, Vue, and TSX templates for Tailwind CSS consistency issues: inline styles, hardcoded hex colors, arbitrary values, `!important`, and missing config.

## Tool
`.claude/tools/fnt/css-artisan/tailwind-analyze.sh`

## When to use
- Design consistency audit: enforce Tailwind usage across templates
- Gate 4 quality check: before frontend handoff to QA
- Code review: flag inline styles and hardcoded colors that bypass design system

## How to use
```bash
.claude/tools/fnt/css-artisan/tailwind-analyze.sh <PRJ-ID> [--fix]
```

## Input
- `PRJ-ID` — project directory with `resources/` containing `.blade.php`, `.vue`, or `.tsx` files
- `--fix` — include actionable recommendations output

## Output
- Issue detection per category:
  - Inline `style=` attributes
  - Hardcoded hex colors (`#fff`, `#aabbcc`)
  - Arbitrary Tailwind values (`w-[...]`, `h-[...]`)
  - `!important` usage
- Tailwind config file presence check
- `--fix`: recommends `@apply` extraction, theme token replacement

## Related
- `engine/agents/fnt/css-artisan.md`
- `.claude/tools/fnt/css-artisan/tailwind-analyze.sh`
