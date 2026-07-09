---
name: dsn-content-strategist
description: "UX copy as keyed JSON, one voice, every error explains what and how."
---
# Design - Content Strategist

Audit project copy for tone consistency — detect tone violations against a target voice.

## Tool
`.claude/tools/dsn/content-strategist/voice-check.sh`

## When to use
- Gate 2 Design: verify all UI copy uses the defined brand voice
- After copy changes: ensure new content matches the tone guide
- Pre-release audit: scan for inconsistent tone that slips through during development
- Brand voice evolution: re-audit after a tone refresh

## How to use
```bash
.claude/tools/dsn/content-strategist/voice-check.sh <PRJ-ID> [--voice "<formal|casual|playful|professional>"]
```

## Input
- `PRJ-ID` — project identifier
- `--voice` — target voice (default: "professional"; options: formal, casual, professional, playful)
- Scans `.md`, `.vue`, `.php`, `.ts` files in `projects/<PRJ>/`

## Output
- Tone match/mismatch summary per file
- Matched tone signal examples (showing the voice is present)
- Tone violations flagged with file:line and the offending text
- Exit code 0 if all files match target tone

## Related
- `.claude/tools/dsn/brand-designer/taste-meter.sh` — upstream: brand personality sets the tone
- `.claude/tools/dsn/lead/design-freeze.sh` — downstream: tone is part of the design freeze
- `.claude/tools/res/fact-checker/ground-check.sh` — cross-function: verify copy claims
