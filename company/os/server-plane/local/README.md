# Pure-Local NetBird — internal mesh panel (no internet, no Cloudflare)

Run NetBird's control panel **entirely on one machine**, reachable only at
`https://netbird.local:8443` over an **internal CA** cert — never on the public
internet, never through Cloudflare. For private device-to-device mesh on your LAN.

> Mesh needs ≥2 devices to be useful — the panel runs on one box; you enrol a
> second device (laptop/phone on the LAN) against it.

## One command
```bash
cd company/os/server-plane/local
bash bootstrap-local.sh          # generates config, starts containers + Caddy, verifies
```
Then the two **root** steps it prints (an agent can't sudo; you run these):
```bash
echo '127.0.0.1 netbird.local' | sudo tee -a /etc/hosts
sudo cp ~/netbird-local/caddy-data/pki/authorities/local/root.crt \
        /usr/local/share/ca-certificates/caddy-netbird.local.crt
sudo update-ca-certificates
```
Open `https://netbird.local:8443` → create admin → mint a Setup Key → join devices.

## Architecture (what bootstrap builds)
```
 Browser / agent ──TLS(internal CA)──► Caddy :8443 (isolated, admin off, own storage)
                                          ├ @grpc  h2c → 127.0.0.1:18081
                                          ├ /api,/oauth2,/relay,/ws-proxy → :18081
                                          └ /*  → dashboard 127.0.0.1:8080
 netbirdio/netbird-server  (network_mode: host)  :18081 HTTP+gRPC · :33073 gRPC · :13478/udp STUN
 netbirdio/dashboard       (bridge)              127.0.0.1:8080
```
- **No Cloudflare, no Let's Encrypt** — Caddy's `tls internal` mints the cert; you
  trust its root once. Isolated from the public `:80` Caddy (separate process +
  storage + `admin off`), so the live `zanjour.com` setup is untouched.
- **Embedded IdP (Dex)** — admin + users live in the server; no external IdP.

## Files
| file | role |
|---|---|
| `bootstrap-local.sh` | end-to-end installer (idempotent) |
| `docker-compose.local.yml` | host-net server + bridge dashboard |
| `Caddyfile.local` | `:8443` front door, `tls internal`, gRPC/h2c |

## Two gotchas this kit already solves (learned the hard way)
1. **The server makes a MANDATORY internet call at boot** to resolve the GeoLite2
   geo-DB filename and **FATAL-exits if it fails** — there is no full geo-disable
   flag (`disableGeoliteUpdate` alone does not skip it). If the docker **bridge has
   no outbound internet** (restricted `iptables FORWARD`/firewall — common on
   hardened hosts), a bridged server crash-loops forever. Fix used here:
   `network_mode: host` so that one call uses the host's working egress. Truly
   air-gapped? You must pre-seed the geo DBs into the volume AND front
   `pkgs.netbird.io` with a local stub — out of scope; host-net is the pragmatic path.
2. **Caddy auto-opens `:80`** for the HTTP→HTTPS redirect (needs root). Disabled via
   `auto_https disable_redirects`; serving only on the high `:8443` keeps it rootless.

## Persistence (boot survival)
The bootstrap leaves Caddy running in the shell. For reboot survival, run the
compose stack (`restart: unless-stopped` already set) under a boot trigger, and
install Caddy as a user systemd unit, e.g.:
```ini
# ~/.config/systemd/user/caddy-netbird.service  (then: systemctl --user enable --now caddy-netbird; loginctl enable-linger)
[Service]
ExecStart=/usr/bin/caddy run --config %h/netbird-local/Caddyfile.local --adapter caddyfile
Restart=on-failure
[Install]
WantedBy=default.target
```

This is a dev/internal panel, **not** staging/prod (still SOFI Gates 6–7).
