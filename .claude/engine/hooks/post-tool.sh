#!/usr/bin/env bash
set -euo pipefail

# Post-tool hook — checkpoint nudge + state recording
# Tracks uncommitted files, suggests checkpoints, logs outcomes

SOFI_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
LOG_DIR="$SOFI_ROOT/.claude/engine/monitoring"

# === Checkpoint nudge ===
if git -C "$SOFI_ROOT" diff --quiet 2>/dev/null; then
  # Clean working tree — no nudge
  :
else
  count=$(git -C "$SOFI_ROOT" diff --name-only 2>/dev/null | wc -l)
  staged=$(git -C "$SOFI_ROOT" diff --cached --name-only 2>/dev/null | wc -l)
  total=$((count + staged))

  if [ "$total" -gt 3 ]; then
    echo "💡 Tip: $total modified files. Consider 'sofi checkpoint' before moving on."
  fi
fi

# === Track git state ===
if [ -n "${OPENCODE_TOOL:-}" ]; then
  echo "[$(date -Iseconds)] tool=${OPENCODE_TOOL:-unknown}" >> "$LOG_DIR/tool-trace.log" 2>/dev/null || true
fi

# === Detect new files created ===
if echo "${OPENCODE_COMMAND:-}" | grep -qE '(Write|create|new)'; then
  new_files=$(git -C "$SOFI_ROOT" ls-files --others --exclude-standard 2>/dev/null | head -5)
  if [ -n "$new_files" ]; then
    echo "📄 New files detected (not yet staged):"
    echo "$new_files" | sed 's/^/   /'
  fi
fi

exit 0
