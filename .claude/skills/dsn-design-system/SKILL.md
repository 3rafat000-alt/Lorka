---
name: dsn-design-system
description: "Design tokens (color/space/type), component library — visual source of truth."
---
# Design - Design System Architect

Extract design tokens (colors, spacing, typography, radii, shadows) from CSS custom properties.

## Tool
`.claude/tools/dsn/design-system/token-export.py`

## When to use
- Gate 2 Design: create the design token dictionary from CSS source
- Brand refresh: re-export tokens after colour/type/spacing changes
- Before handoff to development: deliver a machine-readable token JSON for theming
- Design audit: check that implemented CSS uses the correct tokens

## How to use
```bash
python3 .claude/tools/dsn/design-system/token-export.py <css-path> [--output <file>]
```

## Input
- CSS file containing `--token-name: value;` custom properties
- `--output` — optional output JSON file (default: stdout)
- Token naming convention: tokens with color/bg/text/border/primary/secondary/etc. → colors

## Output
- JSON object with categories: colors, spacing, typography, radii, shadows, other
- Each category contains its matched tokens as key-value pairs
- Exit code 0

## Related
- `.claude/tools/dsn/brand-designer/taste-meter.sh` — upstream: brand personality informs token choices
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: token export frozen with design
- `.claude/tools/fnt/...` — frontend consumes these tokens in component CSS
