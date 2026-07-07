#!/usr/bin/env bash
# SOFI AI — scaffold a new project workspace + company brain.
# Usage: bash engine/bin/new-project.sh <PRJ-ID> "<title>" <PRIORITY> [YYYY-MM-DD]
set -euo pipefail

ID="${1:?usage: new-project.sh PRJ-XXXX \"title\" PRIORITY [date]}"
TITLE="${2:?missing title}"
PRIORITY="${3:?missing priority: CRITICAL|HIGH|MEDIUM|LOW}"
DATE="${4:-unset}"   # pass real date from caller; never invented

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
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
get promoted to engine/tooling/ (see engine/tooling/GOVERNANCE.md).
SCRATCH

cat > "$DIR/_context/STATE.md" <<EOF
# STATE — $ID
title: $TITLE
doctrine: engine/DOCTRINE.md  # ← every project inherits the 6 teachings
gate: 0 (Inception)
active: chief-product-strategist
status: in_progress
priority: $PRIORITY
blockers: none
branch: prj/$ID
head_sha: (set at first checkpoint — sofi checkpoint $ID "...")
last_route: opus-4-8 · high · lite
created: $DATE
updated_by: new-project.sh
EOF

cat > "$DIR/_context/FOUNDATIONS.md" <<EOF
# 🪨 FOUNDATIONS — $ID — $TITLE

> **Every project inherits the 6 teachings of the Doctrine (\`engine/DOCTRINE.md\$6\`).**
> This file pins each teaching to this project's specific context.
> Read \`engine/DOCTRINE.md\$1\` (the full Creed) before this file.

## Teaching I — Design is Truth
Every feature in $ID traces to a validated screen in the Journey Map (Gate 1).
No prototype → no build. No Journey Map stage → feature goes to Backlog, not the codebase.

## Teaching II — Hierarchical Flow
$ID flows through gates in order: 0 Inception → 1 Discovery → 2 Design → 3 Architecture → 4 Build → 5 Quality → 6 Staging → 7 Prod → 8 Observe.
Gate N+1 opens only when Gate N deliverables are signed off in \`HANDOFFS.md\`.

## Teaching III — Radical Isolation
All decisions, code, data, and context for $ID live inside \`projects/$ID/\`.
Cross-project reference is forbidden. Common code → \`shared-packages/\`.

## Teaching IV — Token Economy
Every task in $ID gets the cheapest \`model·effort·caveman\` that clears the bar.
Waste is a defect. Routes are logged in \`STATE.md\` and audited weekly.

## Teaching V — Continuous Metamorphosis
$ID ships with telemetry (Gate 8). SLO breaches open a new ticket at Gate 1.
The product is never finished — it evolves from real user behavior.

## Teaching VI — Reversibility Principle
Every irreversible decision in $ID gets an ADR entry in \`DECISIONS.md\`.
No migration without rollback. No merge under 90% coverage. No ship over TTI 2s.
Cheap-to-undo → fast. Expensive-to-undo → max thinking, ADR, rollback plan.

---

> *The foundation holds. Build on it.* 🪨
EOF

cat > "$DIR/_context/LOCKS.md" <<EOF
# LOCKS — $ID  (path claims; check before editing a shared path — git-discipline §5)
> \`sofi claim $ID <path>\` to claim · \`sofi release $ID <path>\` to drop.
> Already-claimed path → use a worktree or serialize via the lead.
EOF

cat > "$DIR/_context/CONTEXT.md" <<EOF
# CONTEXT — $ID  (durable facts; append-only)
- title: $TITLE
- priority: $PRIORITY
- stack: (set at gate 3 by principal-system-architect)
> Append one bullet per durable fact. Cite web facts: claim [source: url, fetched date].
EOF

cat > "$DIR/_context/DECISIONS.md" <<EOF
# DECISIONS (ADR log) — $ID
> One entry per irreversible choice. Date comes from the CEO, never invented.
EOF

cat > "$DIR/_context/HANDOFFS.md" <<EOF
# HANDOFFS (ticket queue) — $ID

## TKT-001 · gate 0
from: ceo-sofi
to:   chief-product-strategist
task: produce Project_Blueprint.md + 5 deep questions.
consumes: user request
expected: docs/${ID}_Project_Blueprint.md
route: opus-4-8 · high · lite
status: open
EOF

# REGISTRY — the 1-line-per-artifact index the brain layer scans instead of re-reading
# the brain (read/execute split · engine/protocols/04-coordination-registry.md). Header MUST
# match registry.py's so `registry.py add` appends cleanly.
cat > "$DIR/_context/REGISTRY.md" <<EOF
# REGISTRY — $ID   (artifact index · brain-layer read only · append via registry.py)
# fmt: TKT | gate | agent | status | artifact-path | sha | Δbytes | headline
EOF

cat > "$DIR/README.md" <<EOF
# $ID — $TITLE
Priority: $PRIORITY.
**Foundation:** Read \`engine/DOCTRINE.md\` (the 6 immutable teachings) + \`_context/FOUNDATIONS.md\` (this project's pinning).
Brain: \`_context/\`. Protocols: \`engine/protocols/00-operating-system.md\` + \`git-discipline.md\`.
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
SOFI_BIN="$ROOT/engine/tooling/bin/sofi"
if [ -x "$SOFI_BIN" ]; then
  "$SOFI_BIN" domain register "$ID" "$SLUG" || \
    echo "   domain: (skipped — run 'sofi domain init' once, then 'sofi domain register $ID')"
fi

echo "✅ Scaffolded $DIR"
echo "   foundation: _context/FOUNDATIONS.md (6 teachings pinned to this project)"
echo "   brain: _context/{STATE,CONTEXT,DECISIONS,HANDOFFS,REGISTRY,LOCKS}.md"
echo "   domain: $SLUG.local  (sofi domain up $ID  →  open http://$SLUG.local)"
echo "   doctrine: engine/DOCTRINE.md (read this before first task)"
echo "   next:  sofi sync $ID  →  spawn sofi-chief-product-strategist on TKT-001"
