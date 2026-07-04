#!/usr/bin/env bash
# publish-project.sh — give a project a public HTTPS vhost on the server edge.
# Run ON THE SERVER. Mirrors `sofi domain` but for the real domain, not *.local.
#
#   bash publish-project.sh <slug> <local-port>     # add/replace vhost, reload Caddy
#   bash publish-project.sh sukk 8080
#   bash publish-project.sh --rm <slug>             # remove a vhost
#   bash publish-project.sh --list                  # show published vhosts
#
# Result: https://<slug>.<DOMAIN>  →  127.0.0.1:<local-port>  (Let's Encrypt auto).
# Prereq: bootstrap-server.sh has run (Caddy + /etc/caddy/projects.d exist) and a
#         GREY-cloud DNS record  A <slug>.<DOMAIN> → SERVER_PUBLIC_IP  exists.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$HERE/.env" ] && . "$HERE/.env" || true
: "${DOMAIN:?set DOMAIN in .env (e.g. zanjour.com)}"
SITES="/etc/caddy/projects.d"
[ -d "$SITES" ] || { echo "FATAL: $SITES missing — run bootstrap-server.sh first."; exit 1; }

reload() {
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
  systemctl reload caddy 2>/dev/null || systemctl restart caddy
}

case "${1:-}" in
  --list)
    ls -1 "$SITES"/*.caddy 2>/dev/null | sed 's#.*/##;s/\.caddy$//' || echo "(none)"
    exit 0 ;;
  --rm)
    slug="${2:?usage: --rm <slug>}"
    rm -f "$SITES/$slug.caddy"
    reload
    echo "✓ removed $slug.$DOMAIN"
    exit 0 ;;
esac

slug="${1:?usage: publish-project.sh <slug> <local-port>}"
port="${2:?usage: publish-project.sh <slug> <local-port>}"
host="$slug.$DOMAIN"

cat > "$SITES/$slug.caddy" <<EOF
$host {
	reverse_proxy 127.0.0.1:$port
}
EOF

reload
cat <<EOF
✓ published  https://$host  →  127.0.0.1:$port
  Ensure a GREY-cloud DNS record exists:  A  $host → <SERVER_PUBLIC_IP>
  (covered already if you set the wildcard  A *.$DOMAIN → IP).
  First TLS handshake fetches the Let's Encrypt cert; give it ~30s.
EOF
