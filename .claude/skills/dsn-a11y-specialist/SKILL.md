---
name: dsn-a11y-specialist
description: "WCAG 2.2 AA matrix — overrides any taste metric, no exceptions."
---
# Design - Accessibility Specialist

Run WCAG 2.2 AA checklist against project source — alt text, contrast, labels, roles, focus, motion.

## Tool
`.claude/tools/dsn/a11y-specialist/wcag-audit.sh`

## When to use
- Gate 2 Design: verify every screen spec meets WCAG 2.2 AA before freeze
- Before any frontend implementation: accessibility is a hard gate bar
- After implementation: scan generated HTML/Vue files for common a11y violations
- Pre-release audit: final WCAG compliance score
- Motion design: verify prefers-reduced-motion is respected

## How to use
```bash
.claude/tools/dsn/a11y-specialist/wcag-audit.sh <PRJ-ID> [--output <report.md>]
```

## Input
- `PRJ-ID` — project identifier
- `--output` — optional report file path
- Scans `projects/<PRJ>/` for: alt text, ARIA labels, role attributes, focus styles, contrast ratios, motion queries

## Output
- WCAG 2.2 AA checklist with ✓/⚠ per criterion
- Score: X/N criteria met
- Detailed report listing violations with file:line references
- Exit code 0 if all criteria pass, non-zero with details

## Related
- `.claude/tools/dsn/ui-designer/screen-spec.sh` — upstream: screen elements need a11y annotations
- `.claude/tools/dsn/motion-designer/motion-spec.sh` — motion must respect WCAG motion criteria
- `.claude/tools/dsn/lead/design-freeze.sh` — a11y is a hard gate for design freeze
- `engine/DOCTRINE.md §Supplement` — WCAG 2.2 AA always wins over any design dial
