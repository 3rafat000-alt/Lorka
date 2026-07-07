#!/usr/bin/env bash
# SOFI v6 Observability Dashboard — start/stop the live server.
# Usage: dashboard/start.sh [start|stop|restart|status|tunnel|tunnel-stop]  (default: start)
#   tunnel      → expose the running dashboard publicly via Cloudflare (cloudflared, no account)
#   tunnel-stop → tear the public tunnel down
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
  tunnel)
    # Expose the dashboard publicly via a Cloudflare quick tunnel (cloudflared — no account,
    # no interstitial). Reachable at https://<rand>.trycloudflare.com until torn down.
    command -v cloudflared >/dev/null 2>&1 || { echo "✗ cloudflared not installed"; exit 1; }
    running || "$0" start
    TLOG="$HERE/.tunnel.log"; TPID="$HERE/.tunnel.pid"
    if [ -f "$TPID" ] && kill -0 "$(cat "$TPID")" 2>/dev/null; then
      echo "tunnel already up → $(grep -ohE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TLOG" | tail -1)"; exit 0
    fi
    echo "⚠️  SECURITY: this publishes the dashboard to the open internet with NO auth."
    echo "   It exposes local SOFI project state — seed / non-sensitive data only; run 'tunnel-stop' when done."
    nohup cloudflared tunnel --url "http://localhost:$PORT" >"$TLOG" 2>&1 &
    echo $! > "$TPID"
    url=""; for _ in $(seq 1 20); do
      url=$(grep -ohE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TLOG" | head -1)
      [ -n "$url" ] && break; sleep 1
    done
    if [ -n "$url" ]; then echo "✓ dashboard public via Cloudflare → $url"
    else echo "✗ tunnel URL not detected yet — see $TLOG"; tail -5 "$TLOG"; exit 1; fi ;;
  tunnel-stop)
    TPID="$HERE/.tunnel.pid"
    if [ -f "$TPID" ] && kill -0 "$(cat "$TPID")" 2>/dev/null; then
      kill "$(cat "$TPID")" && rm -f "$TPID" && echo "tunnel down"
    else echo "no tunnel running"; fi ;;
  *) echo "usage: $0 [start|stop|restart|status|tunnel|tunnel-stop]"; exit 2 ;;
esac
