#!/usr/bin/env bash
# bootstrap-server.sh — stand up the SOFI "server plane" on a home/edge server.
#
#   private control plane : NetBird mesh (WireGuard, no public mgmt port)
#   public edge           : one Caddy front door, Let's Encrypt direct, DNS-only
#
# Run THIS ON THE SERVER (Debian/Ubuntu), not on the dev box. Idempotent: safe to
# re-run. It never deletes data and never auto-locks SSH (see SSH cutover below).
#
#   sudo bash bootstrap-server.sh            # interactive, asks before impactful steps
#   sudo FORCE=1 bash bootstrap-server.sh    # assume-yes for firewall + installer
#
# Reads ./.env (copy from .env.example first). Full doctrine:
#   company/brain/org/archive-v5/protocols/server-plane.md
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

# ---- config -----------------------------------------------------------------
[ -f .env ] || { echo "FATAL: no .env — copy .env.example to .env and edit it."; exit 1; }
# shellcheck disable=SC1091
. ./.env
: "${DOMAIN:?set DOMAIN in .env (e.g. zanjour.com)}"
: "${NETBIRD_SUBDOMAIN:=netbird}"
NB_HOST="${NETBIRD_SUBDOMAIN}.${DOMAIN}"
CADDY_SITES="/etc/caddy"
FORCE="${FORCE:-0}"

say()  { printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m⚠ %s\033[0m\n' "$*" >&2; }
ask()  { # ask "prompt" ; returns 0 on yes. FORCE=1 auto-yes.
  [ "$FORCE" = 1 ] && return 0
  read -r -p "$1 [y/N] " a; [ "$a" = y ] || [ "$a" = Y ]
}
need_root() { [ "$(id -u)" = 0 ] || { echo "run with sudo / as root"; exit 1; }; }
have() { command -v "$1" >/dev/null 2>&1; }

need_root
say "Server plane bootstrap — domain=$DOMAIN  netbird=$NB_HOST"

# ---- 1. Docker --------------------------------------------------------------
if have docker && docker compose version >/dev/null 2>&1; then
  say "Docker + compose present — skip"
else
  say "Installing Docker Engine + compose plugin"
  if ask "Install Docker via get.docker.com?"; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
  else
    warn "Skipped Docker — NetBird install will fail without it."
  fi
fi

# ---- 2. Caddy (the single front door) ---------------------------------------
if have caddy; then
  say "Caddy present — skip install"
else
  say "Installing Caddy (official apt repo)"
  if ask "Install Caddy?"; then
    apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
      | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
      > /etc/apt/sources.list.d/caddy-stable.list
    apt-get update && apt-get install -y caddy
  else
    warn "Skipped Caddy — the public edge needs it."
  fi
fi

# ---- 3. Front-door Caddyfile (NetBird vhost + per-project imports) -----------
say "Writing $CADDY_SITES/Caddyfile (NetBird gRPC-aware vhost + projects.d/*)"
mkdir -p "$CADDY_SITES/projects.d"
# substitute the real netbird host into the template, keep projects.d include
sed "s/{{NB_HOST}}/$NB_HOST/g" "$HERE/Caddyfile" > "$CADDY_SITES/Caddyfile"
chmod 644 "$CADDY_SITES/Caddyfile"
if have caddy; then
  caddy validate --config "$CADDY_SITES/Caddyfile" --adapter caddyfile \
    && systemctl reload caddy 2>/dev/null || systemctl restart caddy || true
fi
say "Caddy front door staged. (TLS issues only AFTER DNS + port-forward are live — Caddy retries.)"

# ---- 4. NetBird self-hosted (combined container, External-Caddy mode) -------
say "NetBird self-hosted — management URL https://$NB_HOST"
cat <<EOF
  When the installer runs it will ask TWO things:
    • reverse proxy  → choose  [4] External Caddy   (we already run Caddy)
    • domain         → enter   $NB_HOST
  It does NOT manage TLS or ports 80/443 — our Caddy does. The container binds
  127.0.0.1:8080 (dashboard) + 127.0.0.1:8081 (server/gRPC) + UDP 3478 (STUN).
EOF
if ask "Run NetBird getting-started installer now?"; then
  export NETBIRD_DOMAIN="$NB_HOST"
  curl -fsSL https://github.com/netbirdio/netbird/releases/latest/download/getting-started.sh | bash
else
  warn "Skipped NetBird install. Re-run installer later with NETBIRD_DOMAIN=$NB_HOST."
fi

# ---- 5. Firewall — open ONLY the public edge surface ------------------------
say "Firewall (ufw): the entire public surface is 80/tcp 443/tcp 3478/udp"
if have ufw; then
  if ask "Apply ufw rules (keeps SSH 22 OPEN — see SSH cutover note)?"; then
    ufw allow 22/tcp    comment 'ssh (restrict to mesh AFTER cutover)'
    ufw allow 80/tcp    comment 'caddy http / acme'
    ufw allow 443/tcp   comment 'caddy https (dash+mgmt+signal+relay+projects)'
    ufw allow 3478/udp  comment 'netbird embedded STUN (raw, not proxied)'
    ufw --force enable
    ufw status verbose
  fi
else
  warn "ufw not installed — open 80/tcp 443/tcp 3478/udp by hand, keep DB/app/SSH closed to the world."
fi

# ---- 6. Make the SERVER itself a mesh peer ----------------------------------
say "Enrolling the server as a mesh peer (so the dev box reaches it privately)"
if have netbird; then
  echo "netbird already installed on this server."
else
  curl -fsSL https://pkgs.netbird.io/install.sh | sh || \
    warn "netbird agent install failed — install manually: https://docs.netbird.io"
fi
cat <<EOF
  Finish the server peer AFTER admin signup (step needs a Setup Key):
    netbird up --management-url https://$NB_HOST --setup-key <KEY>
  Then 'netbird status' shows the server's mesh IP (100.x.x.x).
EOF

# ---- done: the manual checklist that only a human can do --------------------
cat <<EOF

\033[1;32m✓ Bootstrap finished.\033[0m  Remaining MANUAL steps (one-time):

  1) Cloudflare DNS — GREY cloud (DNS only, NOT proxied):
       A   $NB_HOST           → <SERVER_PUBLIC_IP>
       A   *.$DOMAIN          → <SERVER_PUBLIC_IP>     (covers every project subdomain)
  2) Router port-forward → this server's LAN IP:
       TCP 80, TCP 443, UDP 3478     (nothing else)
  3) Open  https://$NB_HOST  → create the admin account → mint a Setup Key.
  4) Server peer:   netbird up --management-url https://$NB_HOST --setup-key <KEY>
  5) Dev box:       bash join-dev.sh <KEY>            (run on the dev machine)
  6) Publish a web project:   bash publish-project.sh <slug> <local-port>

  SSH cutover (do LAST, after mesh verified — one-way door):
       ufw allow from 100.0.0.0/8 to any port 22 proto tcp
       ufw delete allow 22/tcp
     Only after you confirm 'ssh user@100.x.x.x' (the server's mesh IP) works.
EOF
