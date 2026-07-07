#!/usr/bin/env bash
# SOFI AI — scaffold a new project workspace + company brain (v6).
# Usage: bash company/os/bin/new-project.sh <PRJ-ID> "<title>" <PRIORITY> [YYYY-MM-DD]
set -euo pipefail

ID="${1:?usage: new-project.sh PRJ-XXXX \"title\" PRIORITY [date]}"
TITLE="${2:?missing title}"
PRIORITY="${3:?missing priority: CRITICAL|HIGH|MEDIUM|LOW}"
DATE="${4:-unset}"   # pass real date from caller; never invented

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"          # repo root (company/os/bin → up 3)
TPL="$ROOT/company/brain/templates"
DIR="$ROOT/projects/$ID"

if [ -d "$DIR" ]; then echo "✋ $DIR already exists — refusing to overwrite."; exit 1; fi

mkdir -p "$DIR/_context" "$DIR/docs" "$DIR/src/backend" "$DIR/src/frontend" "$DIR/src/mobile" "$DIR/_scratch"
mkdir -p "$ROOT/shared-packages"
ln -sfn "../../shared-packages" "$DIR/shared"

cat > "$DIR/_scratch/README.md" <<'SCRATCH'
# _scratch/ — ephemeral temp scripts (GOVERNANCE Rule 3)
One-off scripts for a single task live here, named `tmp_<role>_<purpose>.py`.
They are PURGED at gate exit (`sofi scratch <PRJ-ID> clean`) and are NEVER a
deliverable. Nothing in docs/ or src/ may import from here. Proved-useful scripts
get promoted to company/os/ (see company/os/GOVERNANCE.md).
SCRATCH

cat > "$DIR/_context/STATE.md" <<EOF
# STATE — $ID
title: $TITLE
doctrine: company/CONSTITUTION.md  # ← every project inherits the 7 teachings
gate: 0 (Inception)
active: str-product-strategist
status: in_progress
priority: $PRIORITY
blockers: none
branch: prj/$ID
head_sha: (set at first checkpoint — sofi checkpoint $ID "...")
last_route: gatekeeper · high · lite
created: $DATE
updated_by: new-project.sh
EOF

# FOUNDATIONS — the 7 Teachings pinned to this project. Seeded from the canonical
# brain template (company/brain/templates/FOUNDATIONS.md) with PRJ substituted, so
# doctrine text lives in ONE place; a minimal header is written if the template is gone.
if [ -f "$TPL/FOUNDATIONS.md" ]; then
  sed "s/PRJ-XXXX/$ID/g" "$TPL/FOUNDATIONS.md" > "$DIR/_context/FOUNDATIONS.md"
else
  cat > "$DIR/_context/FOUNDATIONS.md" <<EOF
---
type: brain
mem: semantic
prj: $ID
---
# FOUNDATIONS — $ID · the 7 Teachings, pinned to this project
> Template missing at scaffold time — read the full law in company/CONSTITUTION.md
> (Teachings I-VII: Design is Truth · Hierarchical Flow · Radical Isolation ·
> Token Economy · Continuous Metamorphosis · Reversibility · Autonomous Oracle Loop)
> then regenerate this file from company/brain/templates/FOUNDATIONS.md.
EOF
fi

cat > "$DIR/_context/LOCKS.md" <<EOF
# LOCKS — $ID  (path claims; check before editing a shared path — 06-git-discipline.md §5)
> \`sofi claim $ID <path>\` to claim · \`sofi release $ID <path>\` to drop.
> Already-claimed path → use a worktree or serialize via the lead.
EOF

cat > "$DIR/_context/CONTEXT.md" <<EOF
# CONTEXT — $ID  (durable facts; append-only)
- title: $TITLE
- priority: $PRIORITY
- stack: (set at gate 3 by arc-system-architect)
> Append one bullet per durable fact. Cite web facts: claim [source: url, fetched date].
EOF

cat > "$DIR/_context/DECISIONS.md" <<EOF
# DECISIONS (ADR log) — $ID
> One entry per irreversible choice. Date comes from the CEO, never invented.
EOF

cat > "$DIR/_context/HANDOFFS.md" <<EOF
# HANDOFFS (ticket queue) — $ID

## TKT-001 · gate 0
from: brd-ceo
to:   str-product-strategist
task: produce ${ID}_Problem_Statement.md + Blueprint + the 5 deep questions.
consumes: user request
expected: docs/${ID}_Blueprint.md
route: gatekeeper · high · lite
status: open
EOF

cat > "$DIR/README.md" <<EOF
# $ID — $TITLE
Priority: $PRIORITY.
**Foundation:** Read \`company/CONSTITUTION.md\` (the 7 immutable teachings) + \`_context/FOUNDATIONS.md\` (this project's pinning).
Brain: \`_context/\`. Contract: \`company/constitution/00-operating-system.md\` + \`06-git-discipline.md\`.
Git: work lives on branch \`prj/$ID\`; \`sofi sync $ID\` to enter it, \`sofi checkpoint $ID "..."\` to save.
EOF

# Create the project's integration branch at the current baseline (no switch — agents
# enter it via `sofi sync`). Skip cleanly if not a git repo / no commit yet.
if git -C "$ROOT" rev-parse --verify -q HEAD >/dev/null 2>&1; then
  if git -C "$ROOT" rev-parse --verify -q "prj/$ID" >/dev/null 2>&1; then
    echo "   branch: prj/$ID already exists"
  else
    git -C "$ROOT" branch "prj/$ID" >/dev/null 2>&1 && echo "   branch: prj/$ID created (enter with: sofi sync $ID)"
  fi
else
  echo "   branch: (skipped — no git baseline; run an initial commit first)"
fi

# Local domain: give the project a clean URL like <slug>.local (best-effort).
# Needs a one-time `sofi domain init`; skips cleanly if not set up yet.
SLUG="${SLUG:-$ID}"
SOFI_BIN="$ROOT/company/os/bin/sofi"
if [ -x "$SOFI_BIN" ]; then
  "$SOFI_BIN" domain register "$ID" "$SLUG" || \
    echo "   domain: (skipped — run 'sofi domain init' once, then 'sofi domain register $ID')"
fi

echo "✅ Scaffolded $DIR"
echo "   foundation: _context/FOUNDATIONS.md (7 teachings pinned to this project)"
echo "   brain: _context/{STATE,CONTEXT,DECISIONS,HANDOFFS,LOCKS,FOUNDATIONS}.md"
echo "   domain: $SLUG.local  (sofi domain up $ID  →  open http://$SLUG.local)"
echo "   doctrine: company/CONSTITUTION.md (read this before first task)"
echo "   next:  sofi sync $ID  →  spawn str-product-strategist on TKT-001"
