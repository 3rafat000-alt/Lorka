---
description: "Remove feature safely across lifecycle. /rm <feature> <impact-analysis>"
argument-hint: "[description]"
---
> **Lead persona:** `brd-ceo` — the main session *wears* this persona (`.claude/agents/brd-ceo.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🗑️ REMOVE FEATURE — $ARGUMENTS

Safe feature removal lifecycle. Reversibility Principle: every removal has rollback.

## Step 1 — Impact Analysis
`@str-risk-analyst` — business impact of removal
`@sec-compliance-auditor` — regulatory impact
`@dat-privacy-officer` — data retention obligations

## Step 2 — Design Impact
`@dsn-ux-architect` — flow changes without feature
`@dsn-content-strategist` — copy changes

## Step 3 — Architecture Impact
`@arc-system-architect` — system impact
`@arc-api-architect` — API deprecation plan
`@arc-data-architect` — data migration/archival

## Step 4 — Removal (parallel)
`@bck-lead` — backend removal + migration
`@fnt-lead` — frontend removal
`@mob-lead` — mobile removal
`@dat-lead` — data archival/deletion

## Step 5 — Verify
`/qa-sweep "post-removal $ARGUMENTS"` → `/gate-check 5`

## Step 6 — Document
`@knw-historian` — ADR: removed feature, date, reason, rollback plan
`@knw-doc-writer` — update docs

Escalate irreversible: `@gtw-gatekeeper` blocks → `@brd-ceo` decides
