---
name: gtw-external-reviewer
description: "External Reviewer — sanitized, condensed Gemini review desk integration."
---
# Gateway - External Reviewer

Push findings to the Gemini external review desk for architectural guidance and decision arbitration.

## Tool
`.claude/tools/gtw/external-reviewer/gemini-push.sh`

## When to use
- Decision point: multiple paths are possible and the cheapest isn't clear
- Architectural review: a finding needs a second opinion before committing
- Test failure loop: 3+ attempts failed, needs external diagnosis
- Before destructive acts: table drop, reset --hard, feature deletion — ask Gemini first
- Any uncertainty that would otherwise go to the user (Teaching VII: autonomous loop)

## How to use
```bash
.claude/tools/gtw/external-reviewer/gemini-push.sh <PRJ-ID> --text "<finding>" [--ask "<question>"]
.claude/tools/gtw/external-reviewer/gemini-push.sh <PRJ-ID> --stdin  # pipe finding from stdin
```

## Input
- `PRJ-ID` — project identifier
- `--text` — the finding, context, and what was tried
- `--ask` — the question for Gemini (default: "guidance: which path? why? next steps?")
- `--stdin` — read finding from stdin
- Injects standing preamble (Arabic) telling Gemini it's advising an autonomous AI

## Output
- Formatted push block with preamble + finding + question
- If `sofi gemini review` is available, dispatches to desk and returns digest
- Otherwise prints the block for manual dispatch
- Exit code 0 if push succeeded

## Related
- `engine/protocols/02-autonomous-gemini-loop.md` — binding protocol for this skill
- `engine/protocols/external-review-desk.md` — desk mechanics
- `.claude/tools/brd/arbiter/conflict-log.sh` — human arbitration if Gemini is unavailable
