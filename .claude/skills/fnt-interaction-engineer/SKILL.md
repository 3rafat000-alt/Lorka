---
name: fnt-interaction-engineer
description: "Micro-interactions + reduced-motion alternative preserves meaning."
---
# Frontend - Interaction Engineer

Generate a structured YAML interaction spec from a natural language description. Parses trigger/effect keywords (hover, focus, blur, keyboard, animation, fade, slide) into a formal spec.

## Tool
`.claude/tools/fnt/interaction-engineer/interaction-spec.sh`

## When to use
- New interactive component: document behavior before implementation
- Gate 2 design handoff: convert designer's interaction notes into machine-readable spec
- Accessibility documentation: capture keyboard, ARIA, and focus-trap requirements

## How to use
```bash
.claude/tools/fnt/interaction-engineer/interaction-spec.sh <PRJ-ID> <component-name> <description>
```

## Input
- `PRJ-ID` — project directory
- `component-name` — kebab-case component name (e.g. `dropdown-menu`)
- `description` — natural language behavior (e.g. `opens on click, closes on blur, animates with fade`)

## Output
- `docs/interactions/{name}-interaction.yaml` — YAML spec with:
  - States (idle, active, disabled)
  - Triggers (click, hover, focus, blur, keyboard)
  - Effects (toggle, animation, fade, slide)
  - Accessibility (keyboard bindings, aria attributes, focus trap)
  - Transitions (duration, easing)

## Related
- `engine/agents/fnt/interaction-engineer.md`
- `.claude/tools/fnt/interaction-engineer/interaction-spec.sh`
