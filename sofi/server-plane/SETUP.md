# SOFI Orchestration — Setup & Operations

Everything below is already installed and running on this box. This doc is the
runbook: how it's wired, how to pair WhatsApp, how to fix it when it breaks.

## What's already done (2026-07-05)

- `sofi-gateway.service` — running, 127.0.0.1:8099, gateway v2 (async + callbacks)
- `n8n.service` — running, 127.0.0.1:5678, served at http://n8n.local (Caddy)
- `waha.service` — staged (starts when the docker image finishes pulling)
- Caddy vhost `n8n.local` + `/etc/hosts` entry
- 3 workflows imported into n8n
- linger enabled → all services survive logout and reboot
- secrets in `~/.sofi-run/*.env` (chmod 600), gateway token rotated

## Secrets & config (~/.sofi-run/)

| File | Holds |
|---|---|
| `gateway.env` | `SOFI_GATEWAY_TOKEN` (service reads this) |
| `gateway-token` | same token, plain (for curl / callback header) |
| `n8n.env` | n8n config + orchestration wiring (gateway token, WAHA url/key, owner chat) |
| `waha.env` | `WAHA_API_KEY`, `WAHA_URL` |
| `logs/sofi-gateway.log` | gateway log |
| `gateway-jobs.jsonl` | every job, append-only audit trail |
| `n8n-app/` | the stable n8n install the service runs from |

**Set your WhatsApp number** before real use — edit `n8n.env`:
```
SOFI_OWNER_CHAT=963XXXXXXXXX@c.us
```
then `systemctl --user restart n8n`. Empty = anyone who messages the bridge can
drive SOFI (dev only).

## Why n8n runs from ~/.sofi-run/n8n-app (not a global install)

The global npm install of n8n 2.28.6 pulls an incompatible `@langchain/core`
(missing `./utils/uuid` export) that makes every command fail with
`Command "start" not found`. The npx-resolved dependency tree is correctly locked,
so that working tree was copied to `~/.sofi-run/n8n-app` and the service runs its
`bin/n8n` directly. Don't `npm i -g n8n` expecting the service to pick it up.

To upgrade n8n later: pull a clean tree with npx into a temp dir, verify it boots,
`cp -a` its `node_modules` over `~/.sofi-run/n8n-app/node_modules`, restart.

## Pair WhatsApp (one-time, manual — needs your phone)

```bash
systemctl --user start waha
sleep 20
# WAHA dashboard (Swagger). API key is in ~/.sofi-run/waha.env
xdg-open http://127.0.0.1:3000
```
In the dashboard: start a session called **default**, open its QR, then on your
phone: WhatsApp → Settings → Linked devices → Link a device → scan.

WAHA is configured to POST inbound messages to
`http://host.docker.internal:5678/webhook/waha` (n8n). Nothing else to wire.

Finally, in n8n (http://n8n.local) open **10 · WhatsApp Inbound** and
**11 · SOFI Callback** and toggle each **Active**. Message yourself `status`.

## Daily ops

```bash
# health
curl -s http://127.0.0.1:8099/healthz | jq .
systemctl --user status sofi-gateway n8n waha

# logs
journalctl --user -u sofi-gateway -f
tail -f ~/.sofi-run/logs/sofi-gateway.log
tail -f ~/.sofi-run/gateway-jobs.jsonl        # what ran, cost, duration

# restart
systemctl --user restart sofi-gateway
systemctl --user restart n8n
systemctl --user restart waha
```

## Rotate the gateway token

```bash
NEW=$(openssl rand -hex 32)
printf 'SOFI_GATEWAY_TOKEN=%s\n' "$NEW" > ~/.sofi-run/gateway.env
printf '%s\n' "$NEW" > ~/.sofi-run/gateway-token
chmod 600 ~/.sofi-run/gateway.env ~/.sofi-run/gateway-token
# update the copy inside n8n.env too, then:
sed -i "s|^SOFI_GATEWAY_TOKEN=.*|SOFI_GATEWAY_TOKEN=$NEW|" ~/.sofi-run/n8n.env
systemctl --user restart sofi-gateway n8n
```

## Troubleshooting

**`n8n.local` shows 502** — n8n service is down or still booting (~20 s cold start).
`systemctl --user status n8n`; `journalctl --user -u n8n -n 30`.

**n8n login "secure cookie" warning** — expected on plain http. `N8N_SECURE_COOKIE=false`
is already set in `n8n.env` (safe: loopback + LAN only). Reload the page.

**Gateway 401** — token mismatch. The header/body token must equal
`~/.sofi-run/gateway-token`. n8n's copy is in `n8n.env` as `SOFI_GATEWAY_TOKEN`.

**Gateway 429** — hit the 20 dispatch/min limit (loop protection). Wait a minute or
raise `RATE_LIMIT_PER_MIN` in the daemon.

**WhatsApp reply never arrives** — check the async job:
`curl -s -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" http://127.0.0.1:8099/jobs | jq .`
Then check WF "11 · SOFI Callback" executions in n8n, and that WAHA session is
`WORKING` (WAHA dashboard).

**WAHA won't start** — image still pulling (`docker images | grep waha`) or docker
down. `journalctl --user -u waha -n 30`.

## Files

```
sofi/tooling/bin/sofi-gateway-daemon.py     the gateway (systemd runs this)
sofi/server-plane/README.md                 overview + API + command grammar
sofi/server-plane/SETUP.md                  this runbook
sofi/server-plane/n8n/workflows/*.json      version-controlled workflows
~/.config/systemd/user/{sofi-gateway,n8n,waha}.service
~/.sofi-run/                                secrets, logs, n8n-app, job trail
```
