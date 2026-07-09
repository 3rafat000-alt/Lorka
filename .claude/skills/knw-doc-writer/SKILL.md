---
name: knw-doc-writer
description: "README files and guides — answer the first question in one screen."
---
# Knowledge - Doc Writer

Generate Diataxis doc structure for a module.

## Tool
`.claude/tools/knw/doc-writer/diataxis-init.sh`

## When to use
- New module created — docs scaffold needed
- Feature reaching Gate 4 — user docs required
- Existing module missing documentation
- Tutorial or how-to gap identified

## How to use
```bash
.claude/tools/knw/doc-writer/diataxis-init.sh --module module_name [--output docs/] [--overview 'Brief description']
```

## Input
Module name. Optional output path and overview. Generates 4 Diataxis quadrants: tutorial, how-to, reference, explanation.

## Output
Four markdown files in output dir: `tutorial.md`, `how-to.md`, `reference.md`, `explanation.md`. Each pre-filled with section structure and audience metadata.

## Related
- `engine/agents/knw/knw-doc-writer.md`
- `.claude/tools/knw/doc-writer/diataxis-init.sh`
