---
description: "Fix bug across lifecycle. /fix <bug-description> <severity>"
argument-hint: "[description]"
---
> **Lead persona:** `brd-ceo` — the main session *wears* this persona (`.claude/agents/brd-ceo.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🔧 FIX BUG — $ARGUMENTS

Bugfix lifecycle. Scope determines gates required.

## Step 1 — Triage
`@qa-lead` classify: Fast-Track (safe, cheap) or Deep-Audit (money/identity/auth)

## Step 2 — Root Cause
- If design bug: `/dsn-fix "$ARGUMENTS"`
- If architecture bug: `/arc-fix "$ARGUMENTS"`
- If backend bug: `/bck-fix "$ARGUMENTS"`
- If frontend bug: `/fnt-fix "$ARGUMENTS"`
- If mobile bug: `/mob-fix "$ARGUMENTS"`
- If data bug: `/dat-fix "$ARGUMENTS"`
- If security: `/sec-fix "$ARGUMENTS"`

## Step 3 — Fix + Verify
Implement fix → `/qa-sweep "$ARGUMENTS"` → `/gate-check 5`

## Step 4 — Deploy
Fast-Track: direct prod deploy
Deep-Audit: `/ops-deploy "$ARGUMENTS"` → staging → `/gate-check 6` → prod

Escalate unresolved: `/gate-check` blocks → `@gtw-conflict-resolver`
