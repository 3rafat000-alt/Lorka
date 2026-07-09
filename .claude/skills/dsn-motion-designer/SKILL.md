---
name: dsn-motion-designer
description: "Motion specs, micro-interactions, reduced-motion alternative."
---
# Design - Motion Designer

Generate micro-interaction motion spec documents — trigger, duration, easing, behaviour.

## Tool
`.claude/tools/dsn/motion-designer/motion-spec.sh`

## When to use
- Gate 2 Design: define motion behaviour for each interactive element
- After screen specs are done: add motion specs to key interactions
- Before handoff to frontend: document animation parameters (duration, easing)
- Accessibility audit: verify motion respects prefers-reduced-motion

## How to use
```bash
.claude/tools/dsn/motion-designer/motion-spec.sh <PRJ-ID> --element "<name>" --trigger "<hover|click|scroll|load>" [--duration "<ms>"] [--easing "<ease-in-out|spring>"] [--output "<file>"]
```

## Input
- `PRJ-ID` — project identifier
- `--element` — element name
- `--trigger` — trigger type: hover, click, scroll, load
- `--duration` — animation duration (default: "200ms")
- `--easing` — easing function (default: "ease-in-out")
- `--output` — optional output path (default: `projects/<PRJ>/docs/motion/`)

## Output
- Motion spec at output path with: trigger, duration, easing, behaviour description, accessibility note
- Exit code 0

## Related
- `.claude/tools/dsn/ui-designer/screen-spec.sh` — upstream: screen elements that need motion
- `.claude/tools/dsn/a11y-specialist/wcag-audit.sh` — motion a11y compliance
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: motion specs are part of the design freeze
