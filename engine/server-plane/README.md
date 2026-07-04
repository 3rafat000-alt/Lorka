# SOFI Server Plane — kit

Turn a spare machine into **your own private dev server + public web edge**, with
two clean planes:

- **Private (NetBird mesh)** — reach the server's SSH / SFTP / DB over an
  encrypted WireGuard mesh. No management port open to the world.
- **Public (self-hosted Caddy edge)** — publish web projects at
  `https://<slug>.yourdomain` with auto Let's Encrypt TLS, Cloudflare as
  **DNS-only** so traffic never passes through Cloudflare.

Doctrine, architecture diagram and the security trade-off:
[`../protocols/server-plane.md`](../protocols/server-plane.md). **Read it first** —
DNS-only exposes the server's real IP by design.

## Files
| file | runs on | does |
|---|---|---|
| `.env.example` → `.env` | server | config: `DOMAIN`, `NETBIRD_SUBDOMAIN`, … |
| `bootstrap-server.sh` | **server** | Docker + NetBird (self-host) + Caddy front door + firewall |
| `Caddyfile` | server | front-door template (NetBird gRPC vhost + project imports) |
| `publish-project.sh` | **server** | add `https://<slug>.domain → 127.0.0.1:<port>` |
| `join-dev.sh` | **dev box** | install agent + join the mesh |

## Quickstart
```bash
# ── on the SERVER ──────────────────────────────────────────────
scp -r engine/server-plane  user@server:~/          # copy the kit over (or git pull)
cd ~/server-plane
cp .env.example .env && nano .env                 # set DOMAIN, NETBIRD_SUBDOMAIN
sudo bash bootstrap-server.sh                      # installs everything, prints checklist
#   → when the NetBird installer asks: reverse proxy = [4] External Caddy

# ── MANUAL, once ───────────────────────────────────────────────
# 1. Cloudflare, GREY cloud (DNS only):
#       A  netbird.zanjour.com → SERVER_PUBLIC_IP
#       A  *.zanjour.com       → SERVER_PUBLIC_IP
# 2. Router port-forward → server LAN IP:  TCP 80, TCP 443, UDP 3478
# 3. Open https://netbird.zanjour.com → create admin → mint a Setup Key
# 4. Enrol the server peer:
#       netbird up --management-url https://netbird.zanjour.com --setup-key <KEY>

# ── on the DEV BOX (this machine) ──────────────────────────────
bash join-dev.sh <SETUP_KEY> netbird.zanjour.com
netbird status                                     # note the server peer's 100.x.x.x

# ── work privately over the mesh ───────────────────────────────
ssh user@100.x.x.S
mysql -h 100.x.x.S -u app -p

# ── publish a web project (on the SERVER) ──────────────────────
bash publish-project.sh sukk 8080                  # → https://sukk.zanjour.com
```

## Public exposure (the whole surface)
| port | proto | purpose |
|---|---|---|
| 80 | TCP | Let's Encrypt + redirect → 443 |
| 443 | TCP | all HTTPS: dashboards, NetBird control, every project |
| 3478 | UDP | NetBird STUN (raw — Caddy can't front UDP) |

DB, Redis, app ports and (after cutover) SSH are reached **only over the mesh**.

## SSH cutover — last, and carefully (one-way door)
After you've confirmed `ssh user@100.x.x.S` (the server's mesh IP) works:
```bash
sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp
sudo ufw delete allow 22/tcp
```
Do **not** run this before the mesh is verified — you can lock yourself out. Keep
console/physical access until you've tested mesh SSH.

## Dynamic public IP?
Home connections often have a changing IP. Either run a Cloudflare DDNS updater
(e.g. `ddclient` or `cloudflared`'s DNS) to keep the A-records current, or use a
static IP / business line. The mesh itself survives IP changes (NetBird re-NATs);
only the public A-records need updating.

## This is not staging/prod
A published edge is infrastructure to host on — real releases still go through
SOFI Gates 6–7 (Blue/Green, tested rollback). Owner: **DevOps & Cloud Lead**.
