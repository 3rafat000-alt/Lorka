---
description: "Full 9-gate lifecycle for new feature. /new <description>"
argument-hint: "[description]"
---
> **Lead persona:** `brd-ceo` — the main session *wears* this persona (`.claude/agents/brd-ceo.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 NEW FEATURE LIFECYCLE — $ARGUMENTS

Execute full 9-gate lifecycle. Each gate: freeze → verify → advance.

## Gate 0 — Inception
`/str-new "$ARGUMENTS"` → Blueprint frozen → `/gate-check 0`

## Gate 1 — Discovery
`/res-new "$ARGUMENTS"` → Journey Map frozen → `/gate-check 1`

## Gate 2 — Design
`/dsn-new "$ARGUMENTS"` → UI spec frozen → `/gate-check 2`

## Gate 3 — Architecture
`/arc-new "$ARGUMENTS"` + `/sec-new "$ARGUMENTS"` → `/gate-check 3`

## Gate 4 — Build (parallel)
`/bck-new "$ARGUMENTS"` + `/fnt-new "$ARGUMENTS"` + `/mob-new "$ARGUMENTS"` + `/dat-new "$ARGUMENTS"`

## Gate 5 — Quality
`/qa-new "$ARGUMENTS"` + `/sec-scan "$ARGUMENTS"` → `/gate-check 5`

## Gate 6 — Staging
`/ops-deploy "$ARGUMENTS"` → staging live → `/gate-check 6`

## Gate 7 — Production
`/ops-release "$ARGUMENTS"` → prod live → `/gate-check 7`

## Gate 8 — Observe
`/obs-watch "$ARGUMENTS"` → monitoring live → SLO defined

Escalate blockers: `@gtw-conflict-resolver` → `@brd-arbiter`
