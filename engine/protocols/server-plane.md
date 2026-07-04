# Protocol — Server Plane (private mesh + self-hosted public edge)

> **Foundation:** This protocol serves Teaching **III (Radical Isolation)** — each machine is a separate plane, never cross-contaminated — and Teaching **V (Continuous Metamorphosis)** — the server plane enables permanent staging, which means continuous feedback. Read `engine/DOCTRINE.md` before this file.

SOFI's default world is **one dev box**: `sofi domain` (Caddy `:80`, routes by Host →
`<slug>.local`) and `sofi tunnel` (a throwaway `cloudflared` quick-tunnel →
random `trycloudflare.com`). The **server plane** adds a *second, permanent
machine* — a home/edge server you own — and two clean planes on top of it:

- **Private plane — NetBird mesh.** A WireGuard mesh links the dev box and the
  server peer-to-peer. SSH / SFTP / DB / file work happens over the mesh
  (`100.x.x.x`), so the server needs **no inbound management port open to the
  world**. This is the control plane and it is closed.
- **Public plane — self-hosted edge.** A single **Caddy** on the server is the
  front door for every public hostname under your real domain. It terminates
  TLS with Let's Encrypt and reverse-proxies each `<slug>.zanjour.com` to the
  project behind it. This is the publish plane and it is the *only* thing the
  internet touches.

This is the durable upgrade of `sofi tunnel`: a quick-tunnel is for a one-off
webhook/demo and dies; the server plane is a real, named, TLS edge you keep.

## The deliberate trade-off — DNS-only over Cloudflare-proxied
Two ways to put a domain in front of a home server:

| | Cloudflare **proxied** (orange cloud) / `cloudflared` tunnel | **DNS-only** (grey cloud) + Caddy/Let's Encrypt — **what we chose** |
|---|---|---|
| Real server IP | hidden | **exposed** in public DNS |
| DDoS shield | yes (CF edge) | none (you absorb it) |
| Router port-forward | none | **80/tcp, 443/tcp, 3478/udp** required |
| Who can read plaintext | **Cloudflare** (terminates TLS) | **only you** (Caddy terminates; CF sees DNS only) |

We chose **DNS-only for privacy** — traffic between visitor and your Caddy never
passes through Cloudflare. The cost is real-IP exposure and self-owned DDoS risk.
This is a recorded decision, not an accident — log it in `DECISIONS.md` for any
project that publishes through it.

## Architecture
```
Internet
  │  Cloudflare = DNS only (grey cloud): A netbird.zanjour.com, *.zanjour.com → SERVER_PUBLIC_IP
  ▼  TCP 80 · TCP 443 · UDP 3478   (router port-forward → server LAN IP)
┌─ Home server ───────────────────────────────────────────────┐
│  Caddy (host :80/:443, Let's Encrypt direct)                 │
│    ├ netbird.zanjour.com → NetBird (gRPC h2c 8081 + dash 8080)│
│    └ <slug>.zanjour.com  → project (127.0.0.1:80xx)          │
│  NetBird combined container  127.0.0.1:8080/8081 · UDP 3478  │
│  Project apps (php serve / containers) on 127.0.0.1:80xx     │
│  netbird agent — server is also a mesh peer → 100.x.x.S      │
└──────────────────────────────────────────────────────────────┘
        ▲ private WireGuard mesh (no public port)
┌─ Dev box (this machine) ──────────────────────────────────────┐
│  netbird agent → 100.x.x.D    ssh/sftp/db over mesh, privately │
└───────────────────────────────────────────────────────────────┘
```

### Why these specifics (NetBird v0.65+, combined container)
- **No external IdP.** Modern NetBird ships embedded **Dex** local user
  management. The admin account is created on the first visit to
  `https://netbird.zanjour.com`; from there you mint a **Setup Key** to enrol
  each device. (Older guides bundle Zitadel — not needed here.)
- **One hostname, not three.** The combined container multiplexes dashboard,
  management/gRPC, signal and relay-over-WebSocket on **443**. The legacy
  `signal.* :10000` split is obsolete — a single `netbird.zanjour.com` vhost
  serves all of it.
- **Caddy must speak gRPC.** The control channel is gRPC; the vhost matches
  `Content-Type: application/grpc*` and proxies to **`h2c://127.0.0.1:8081`**
  (plaintext HTTP/2). A plain `reverse_proxy localhost:8081` silently breaks
  agent connection.
- **UDP 3478 (STUN) stays raw.** It is the one thing Caddy cannot front (Caddy
  is HTTP-only). Port-forward it directly. The relay no longer needs the big
  `49152–65535` TURN range — it rides 443/WS now.

## Public ports (the whole exposure surface)
| port | proto | for | via |
|---|---|---|---|
| 80 | TCP | Let's Encrypt HTTP-01 + →443 redirect | Caddy |
| 443 | TCP | all HTTPS: dashboards, mgmt-gRPC, signal, relay-ws, projects | Caddy |
| 3478 | UDP | NetBird embedded STUN | **direct, raw** |
| 22 | TCP | SSH | **mesh-only after cutover** (see below) |

Everything else stays closed. The DB, Redis, app ports, and SSH are reached
**over the mesh**, never published.

## Pure-local mode (internal mesh, no internet, no Cloudflare)
For a control panel that stays **entirely on one machine** —
`https://netbird.local:8443` behind an **internal-CA** cert, never public, never
through Cloudflare — use [`engine/server-plane/local/`](../server-plane/local/)
(`bootstrap-local.sh`). Same NetBird combined server + embedded IdP, but the
server runs `network_mode: host` (its mandatory boot-time geo-DB call needs the
host's egress when the docker bridge is firewalled) and a **separate** Caddy on
`:8443` (`tls internal`, `admin off`, own storage) fronts it — isolated from the
public `:80` Caddy so the live `zanjour.com` edge is untouched. Full notes +
gotchas: [`local/README.md`](../server-plane/local/README.md).

## Lifecycle (owner = DevOps & Cloud Lead, Gate 6/7)
The kit lives in [`engine/server-plane/`](../server-plane/) — copy it to the server,
run it there.
1. **Server, once:** `bootstrap-server.sh` — Docker + NetBird (External-Caddy
   mode) + front-door Caddy + firewall + the server's own mesh agent.
2. **Manual, once:** create the Cloudflare grey-cloud A-records, port-forward
   80/443/3478 on the router, finish admin signup at `netbird.zanjour.com`,
   mint a Setup Key.
3. **Dev box, once:** `join-dev.sh <SETUP_KEY>` — installs the agent and joins
   the mesh against *your* management URL.
4. **Per project:** `publish-project.sh <slug> <port>` — adds the
   `<slug>.zanjour.com` vhost and reloads Caddy. Mirrors `sofi domain` but for
   the public edge.

## Boundaries (read before relying on it)
- **A published edge is still not staging/prod.** Real releases go through Gates
  6–7 (Blue/Green, tested rollback). The server plane is *infrastructure to host
  them on*, not a substitute for the gate.
- **SSH cutover is a one-way door — do it carefully.** Restrict `22/tcp` to the
  mesh CIDR (`100.x.x.0/…`) **only after** you've confirmed the mesh works and
  you can SSH over `100.x.x.S`. Locking it before the mesh is up is a lockout.
  Keep a console/physical fallback until verified. The script never auto-locks
  SSH for this reason.
- **Secrets stay out of git.** Setup keys, `config.yaml`, Caddy's ACME data, the
  NetBird data dir — none of it is committed. The kit ships templates only.
- **Owner is the DevOps & Cloud Lead.** The CI/CD engineer may publish a project
  vhost for a webhook test; no other role stands up or repoints the edge without
  recording it in `CONTEXT.md`.

Full local-domain mechanics it builds on: [local-domains.md](local-domains.md).
Throwaway public sharing it replaces for permanent use:
[public-tunnels.md](public-tunnels.md).
