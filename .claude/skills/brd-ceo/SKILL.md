---
name: brd-ceo
description: "CEO / Chief Coordinator — owns lifecycle, routing, arbitration; never writes code."
---
# Boardroom - CEO (Magnus Holt)

Executive command center: sync project state, stamp route, run adversarial gate checks.

## Tool
`.claude/tools/brd/ceo/sofi-exec.sh`

## When to use
- Start of every session: orient by reading STATE.md, syncing git, seeing current gate
- Before delegating any work: stamp the current route and head_sha
- Gate-checking before a signoff or handoff between rooms
- Emergency: project is stalled, scope has crept, or a gate needs an executive decision

## How to use
```bash
.claude/tools/brd/ceo/sofi-exec.sh <PRJ-ID> [--check-gate <N>]
```

## Input
- `PRJ-ID` — project identifier (e.g. PRJ-SAKK)
- `--check-gate N` — optional adversarial gate check (2|3|4|5)
- Reads `projects/<PRJ>/_context/STATE.md` for branch, gate, head_sha

## Output
- Project status summary (gate, branch, head_sha, last commit)
- Optional gate-check report with PASS/FAIL per artifact
- Route stamp logged in ROUTE_LOG.md

## Related
- Room spec: `engine/agents/ceo-sofi.md`
- `.claude/tools/brd/chief-of-staff/rccf-gen.sh` — delegate after orienting
- `.claude/tools/gtw/gatekeeper/gate-check.sh` — deep adversarial check
