#!/usr/bin/env bash
# SOFI v5 Observability Dashboard — start/stop the live server.
# Usage: dashboard/start.sh [start|stop|restart|status]  (default: start)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${SOFI_DASH_PORT:-8787}"
PIDFILE="$HERE/.server.pid"
LOG="$HERE/.server.log"

running(){ [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; }

case "${1:-start}" in
  start)
    if running; then echo "already running (pid $(cat "$PIDFILE")) → http://127.0.0.1:$PORT"; exit 0; fi
    nohup python3 "$HERE/server.py" --port "$PORT" >"$LOG" 2>&1 &
    echo $! > "$PIDFILE"
    sleep 2
    if running; then echo "✓ dashboard up → http://127.0.0.1:$PORT  (or http://dashboard.local once caddy is reloaded)"
    else echo "✗ failed to start — see $LOG"; tail -5 "$LOG"; exit 1; fi ;;
  stop)
    if running; then kill "$(cat "$PIDFILE")" && rm -f "$PIDFILE" && echo "stopped"; else echo "not running"; fi ;;
  restart) "$0" stop || true; exec "$0" start ;;
  status)
    if running; then echo "running (pid $(cat "$PIDFILE")) → http://127.0.0.1:$PORT"; else echo "stopped"; fi ;;
  *) echo "usage: $0 [start|stop|restart|status]"; exit 2 ;;
esac
