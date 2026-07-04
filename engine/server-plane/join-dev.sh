#!/usr/bin/env bash
# join-dev.sh — join THIS machine (the dev box) to your self-hosted NetBird mesh.
#
# Run on the developer machine (this one). After it succeeds you reach the server
# privately over its mesh IP (100.x.x.x): ssh, sftp, DB clients, file sync — all
# without any public port on the server.
#
#   bash join-dev.sh <SETUP_KEY>
#   bash join-dev.sh <SETUP_KEY> netbird.zanjour.com   # explicit mgmt host
#
# SETUP_KEY is minted in the dashboard at https://<netbird-host> (admin → Setup Keys).
set -euo pipefail

KEY="${1:?usage: join-dev.sh <SETUP_KEY> [mgmt-host]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# mgmt host: arg 2, else DOMAIN/NETBIRD_SUBDOMAIN from .env, else fail
if [ -n "${2:-}" ]; then
  NB_HOST="$2"
elif [ -f "$HERE/.env" ]; then
  # shellcheck disable=SC1091
  . "$HERE/.env"
  NB_HOST="${NETBIRD_SUBDOMAIN:-netbird}.${DOMAIN:?set DOMAIN in .env or pass mgmt-host}"
else
  echo "FATAL: no mgmt host — pass it as arg 2 or create .env with DOMAIN="; exit 1
fi
MGMT="https://$NB_HOST"

have() { command -v "$1" >/dev/null 2>&1; }

echo "▸ Joining mesh at $MGMT"

if ! have netbird; then
  echo "▸ Installing NetBird agent"
  curl -fsSL https://pkgs.netbird.io/install.sh | sh
fi

# bring this peer up against YOUR management server (not app.netbird.io)
sudo netbird up --management-url "$MGMT" --setup-key "$KEY"

echo
echo "▸ Mesh status:"
netbird status || true
cat <<EOF

✓ Joined. Find the server's mesh IP with:  netbird status   (look for the server peer, 100.x.x.x)
  Then work privately, e.g.:
     ssh    user@100.x.x.S
     sftp   user@100.x.x.S
     mysql -h 100.x.x.S -u app -p        # DB never leaves the mesh
  Leave the mesh:  sudo netbird down
EOF
