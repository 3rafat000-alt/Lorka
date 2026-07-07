#!/usr/bin/env bash
# bootstrap-local.sh — stand up a PURE-LOCAL NetBird control panel.
#
#   • Internal mesh only — NO public internet, NO Cloudflare tunnel.
#   • https://netbird.local:8443 via an isolated local Caddy with an INTERNAL CA
#     (Caddy's own root, no Let's Encrypt).
#   • Combined NetBird server (management + signal + relay + embedded Dex IdP + STUN)
#     in Docker, bound to loopback/high ports.
#
# Idempotent. Non-root EXCEPT two host-trust steps it prints at the end (adding the
# hosts entry and trusting the internal CA) — those need sudo and are listed for you.
#
# Doctrine: ../../protocols/server-plane.md (Pure-local mode).
set -euo pipefail

DOMAIN="${DOMAIN:-netbird.local}"
EXT_PORT="${EXT_PORT:-8443}"      # public-facing (local) HTTPS port Caddy serves
SRV_PORT="${SRV_PORT:-18081}"     # combined server HTTP/gRPC bind (host)
STUN_PORT="${STUN_PORT:-13478}"   # embedded STUN (host, UDP)
WORK="${WORK:-$HOME/netbird-local}"
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MGMT_URL="https://${DOMAIN}:${EXT_PORT}"

say(){ printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
die(){ printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
have(){ command -v "$1" >/dev/null 2>&1; }

for b in docker caddy jq curl; do have "$b" || die "missing '$b' — install it first"; done
docker compose version >/dev/null 2>&1 || die "docker compose plugin missing"
mkdir -p "$WORK"; cd "$WORK"

# ── 1. Generate NetBird config via the official installer (patched non-interactive)
if [ -f config.yaml ]; then
  say "config.yaml exists — reuse (delete $WORK to regenerate)"
else
  say "Generating NetBird config (combined server, embedded IdP, External-Caddy)"
  curl -fsSL https://github.com/netbirdio/netbird/releases/latest/download/getting-started.sh -o nb.sh
  # neutralise the /dev/tty prompts: type 4 (External Caddy), localhost bind, no docker net, generate-only
  sed -i \
    -e 's|  REVERSE_PROXY_TYPE=$(read_reverse_proxy_type)|  REVERSE_PROXY_TYPE=4|' \
    -e 's|    BIND_LOCALHOST_ONLY=$(read_port_binding_preference)|    BIND_LOCALHOST_ONLY=true|' \
    -e 's|    4) EXTERNAL_PROXY_NETWORK=$(read_proxy_docker_network "Caddy") ;;|    4) EXTERNAL_PROXY_NETWORK="" ;;|' \
    -e 's|^  start_services_and_show_instructions|  echo "[patched] generate-only"|' \
    nb.sh
  NETBIRD_DOMAIN="$DOMAIN" NETBIRD_HTTP_PROTOCOL=https bash nb.sh
  [ -f config.yaml ] || die "installer did not produce config.yaml"
fi

# ── 2. Retarget the generated config to our local port + bind, kill the boot-time
#       geo update-check fatality, and move the server off :80.
say "Retargeting config to ${DOMAIN}:${EXT_PORT} (server bind :${SRV_PORT}, STUN :${STUN_PORT})"
sed -i \
  -e "s|${DOMAIN}:443|${DOMAIN}:${EXT_PORT}|g" \
  -e "s|${DOMAIN}/oauth2|${DOMAIN}:${EXT_PORT}/oauth2|g" \
  -e "s|${DOMAIN}/nb-auth|${DOMAIN}:${EXT_PORT}/nb-auth|g" \
  -e "s|${DOMAIN}/nb-silent-auth|${DOMAIN}:${EXT_PORT}/nb-silent-auth|g" \
  -e 's|172.30.0.10/32|172.16.0.0/12|g' \
  -e 's|listenAddress: ":80"|listenAddress: ":'"${SRV_PORT}"'"|' \
  -e 's|^    - 3478|    - '"${STUN_PORT}"'|' \
  config.yaml
grep -q disableGeoliteUpdate config.yaml || \
  sed -i '/dataDir: "\/var\/lib\/netbird"/a\  disableGeoliteUpdate: true' config.yaml
sed -i \
  -e "s|=https://${DOMAIN}$|=https://${DOMAIN}:${EXT_PORT}|g" \
  -e "s|${DOMAIN}/oauth2|${DOMAIN}:${EXT_PORT}/oauth2|g" \
  dashboard.env

# ── 3. Containers — host networking so the server's one mandatory geo boot-call
#       uses the host's egress (the docker bridge often has none here).
say "Starting containers (server: host-net, dashboard: bridge 127.0.0.1:8080)"
cp "$KIT/docker-compose.local.yml" ./docker-compose.local.yml
COMPOSE_PROJECT_NAME=nblocal docker compose -f docker-compose.local.yml up -d
say "Waiting for the server to finish first-run geo download + boot…"
for i in $(seq 1 36); do
  curl -s -o /dev/null --max-time 4 "http://127.0.0.1:${SRV_PORT}/" 2>/dev/null && { echo "  server up"; break; }
  sleep 5
done

# ── 4. Isolated local Caddy on :EXT_PORT with the internal CA.
say "Starting isolated Caddy on :${EXT_PORT} (tls internal)"
sed "s/18081/${SRV_PORT}/g; s/:8443/:${EXT_PORT}/g" "$KIT/Caddyfile.local" > Caddyfile.local
rm -rf caddy-data
pkill -f "$WORK/Caddyfile.local" 2>/dev/null || true
( caddy run --config Caddyfile.local --adapter caddyfile >caddy.log 2>&1 & )
sleep 3

# ── 5. Verify + print the remaining (root) steps.
code=$(curl -s -o /dev/null -w "%{http_code}" --resolve "${DOMAIN}:${EXT_PORT}:127.0.0.1" -k --max-time 8 "${MGMT_URL}/" || echo 000)
say "Dashboard via Caddy → HTTP ${code}  (200 = good)"

CA="$WORK/caddy-data/pki/authorities/local/root.crt"
cat <<EOF

\033[1;32m✓ Pure-local NetBird is up.\033[0m  Two one-time ROOT steps to use it from a browser/agent:

  1) Resolve the name on this machine:
       echo '127.0.0.1 ${DOMAIN}' | sudo tee -a /etc/hosts

  2) Trust Caddy's internal CA (so the cert is valid, no warnings):
       sudo cp ${CA} /usr/local/share/ca-certificates/caddy-${DOMAIN}.crt
       sudo update-ca-certificates
     (browsers using their own store: import that .crt manually)

  Then:
    • Open  ${MGMT_URL}  → create the admin account (embedded IdP) → mint a Setup Key.
    • Install the agent + join the mesh:
        curl -fsSL https://pkgs.netbird.io/install.sh | sh
        sudo netbird up --management-url ${MGMT_URL} --setup-key <KEY>
    • 'netbird status' shows peers (100.x.x.x). Add a 2nd device the same way.

  Persistence: this Caddy runs in the foreground/background of the shell. For boot
  survival install it + the compose stack as systemd services (see README.md).
EOF
