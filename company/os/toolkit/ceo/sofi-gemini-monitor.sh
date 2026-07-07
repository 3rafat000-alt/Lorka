#!/bin/bash
# sofi-gemini-monitor.sh
# Continuous monitor: Gemini chat → GitHub sync loop
# Run as: systemd service or cron job

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE="$SCRIPT_DIR/gemini_bridge.py"
SYNC="$SCRIPT_DIR/gemini-github-sync.py"
LOG="/tmp/sofi-gemini-monitor.log"

# Capture latest Gemini response
echo "[$(date)] Fetching latest Gemini response..." >> "$LOG"

RESPONSE=$("$BRIDGE" capture --timeout 10 2>/dev/null || echo "{}")

if [ -z "$RESPONSE" ] || [ "$RESPONSE" = "{}" ]; then
  echo "[$(date)] No new response from Gemini" >> "$LOG"
  exit 0
fi

# Sync to GitHub
echo "[$(date)] Syncing findings to GitHub..." >> "$LOG"
echo "$RESPONSE" | python3 "$SYNC" 2>&1 | tee -a "$LOG"

# Notify team (Slack webhook if configured)
if [ -n "$SLACK_WEBHOOK_SOFI_GEMINI" ]; then
  STATUS=$(echo "$RESPONSE" | jq -r '.gate_6_to_7_readiness.ready // false')
  curl -X POST "$SLACK_WEBHOOK_SOFI_GEMINI" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Gemini audit sync complete. Gate 6→7: $STATUS\"}" \
    2>/dev/null || true
fi

echo "[$(date)] Sync complete" >> "$LOG"
