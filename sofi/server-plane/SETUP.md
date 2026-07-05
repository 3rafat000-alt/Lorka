# SOFI Orchestration — Setup & Operations

Everything below is already installed and running on this box. This doc is the
runbook: how it's wired, how to pair WhatsApp, how to fix it when it breaks.

## What's already done (2026-07-05)

- `sofi-gateway.service` — running, 127.0.0.1:8099, gateway v2 (async + callbacks)
- `n8n.service` — running, 127.0.0.1:5678, served at http://n8n.local (Caddy)
- OpenWA gateway (pre-existing `openwa-otp.service`, 127.0.0.1:2785) — new session
  `sofi-orchestrator` created for this tool, separate from SAKK's `sakk-otp` session
- `@rmyndharis/n8n-nodes-openwa` community node installed (declarative, via env)
- Caddy vhost `n8n.local` + `/etc/hosts` entry
- 3 workflows imported into n8n (WhatsApp inbound, callback, health monitor)
- linger enabled → all services survive logout and reboot
- secrets in `~/.sofi-run/*.env` (chmod 600), gateway token rotated

## Secrets & config (~/.sofi-run/)

| File | Holds |
|---|---|
| `gateway.env` | `SOFI_GATEWAY_TOKEN` (service reads this) |
| `gateway-token` | same token, plain (for curl / callback header) |
| `n8n.env` | n8n config + orchestration wiring (gateway token, owner chat, community-package pin) |
| `openwa.env` | `OPENWA_API_KEY`, `OPENWA_BASE_URL`, `OPENWA_WEBHOOK_SECRET` |
| `openwa-session-id` | the `sofi-orchestrator` session UUID (also hardcoded in the workflow JSON) |
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

## Why OpenWA, not WAHA

This box already runs OpenWA (`~/openwa/`) as the WhatsApp gateway for SAKK's OTP
delivery — hardened, `network_mode: host` (fixes a ProtonVPN/ufw egress trap that
killed bridged containers on reboot), survives reboot via `openwa-otp.service` +
`restart: always`. Reusing it for orchestration (a second session, `sofi-orchestrator`)
avoids running two competing WhatsApp gateways and inherits fixes already earned.
Integration is via the official n8n community node `@rmyndharis/n8n-nodes-openwa`
(OpenWA + OpenWA Trigger), not raw HTTP nodes — it registers its own webhook on
activation and handles HMAC verification internally.

**Install the community node the declarative way, never by hand.** `npm install`ing
a package directly into `~/.sofi-run/n8n-app` (n8n's own dependency tree) will `npm`
dedupe/prune n8n's *own* dependencies with it (happened once — 2077 packages removed,
n8n's own `bin/n8n` disappeared). The correct mechanism is n8n's own installer:
```
N8N_COMMUNITY_PACKAGES_ENABLED=true
N8N_COMMUNITY_PACKAGES_MANAGED_BY_ENV=true
N8N_COMMUNITY_PACKAGES=[{"name":"@rmyndharis/n8n-nodes-openwa"}]
```
in `n8n.env` — n8n installs/verifies/registers it into its own DB
(`installed_packages`/`installed_nodes` tables) on boot, in its own `~/.n8n/nodes`
sandbox, and reconciles (install/update/remove) to match this list on every start.
A log line `no pinned version and no vetted entry — installed version will not be
reconciled across restarts` is expected (this package isn't in n8n's vetted registry)
and harmless — it still installs and stays installed.

## Pair WhatsApp (one-time, manual — needs your phone)

The `sofi-orchestrator` session exists on the gateway but isn't linked yet:

```bash
KEY=$(grep OPENWA_API_KEY ~/.sofi-run/openwa.env | cut -d= -f2)
SID=$(cat ~/.sofi-run/openwa-session-id)
curl -s -X POST "http://127.0.0.1:2785/api/sessions/$SID/start" -H "X-API-Key: $KEY"
sleep 5
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:2785/api/sessions/$SID/qr" \
  | python3 -c "import sys,json,base64;q=json.load(sys.stdin)['qrCode'];open('/tmp/sofi-qr.png','wb').write(base64.b64decode(q.split(',',1)[1]))"
xdg-open /tmp/sofi-qr.png
```
Scan with the WhatsApp account you want to drive SOFI from: **Settings ▸ Linked
Devices ▸ Link a Device**. Poll `curl -s -H "X-API-Key: $KEY"
http://127.0.0.1:2785/api/sessions/$SID` until `status` is `ready`/`working`.

In n8n (http://n8n.local): open **10 · WhatsApp Inbound**, on the **OpenWA Trigger**
node click the credential dropdown → **Create New** → **OpenWA API**:
- Server URL: `http://127.0.0.1:2785`
- API Key: value of `OPENWA_API_KEY` in `~/.sofi-run/openwa.env`

Save; the same credential is reused on the **OpenWA: Ack** node (workflow 10) and
**OpenWA: Send Result** node (workflow 11). **Activate** both workflows — activating
10 auto-registers its webhook with OpenWA (no manual webhook step). Message yourself
`status`.

## Daily ops

```bash
# health
curl -s http://127.0.0.1:8099/healthz | jq .
curl -sf http://127.0.0.1:2785/api/health/ready && echo openwa-ok
systemctl --user status sofi-gateway n8n openwa-otp

# logs
journalctl --user -u sofi-gateway -f
tail -f ~/.sofi-run/logs/sofi-gateway.log
tail -f ~/.sofi-run/gateway-jobs.jsonl        # what ran, cost, duration

# restart
systemctl --user restart sofi-gateway
systemctl --user restart n8n
systemctl --user restart openwa-otp             # affects BOTH sessions — SAKK OTP too
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

**`n8n.local` shows 502/404 right after a restart** — n8n cold-starts in ~20-25s;
transient 404s during that window are normal. `systemctl --user status n8n`.

**n8n login "secure cookie" warning** — expected on plain http. `N8N_SECURE_COOKIE=false`
is already set in `n8n.env` (safe: loopback + LAN only). Reload the page.

**Gateway 401** — token mismatch. The header/body token must equal
`~/.sofi-run/gateway-token`. n8n's copy is in `n8n.env` as `SOFI_GATEWAY_TOKEN`.

**Gateway 429** — hit the 20 dispatch/min limit (loop protection). Wait a minute or
raise `RATE_LIMIT_PER_MIN` in the daemon.

**OpenWA webhook create fails `Blocked internal address`** — its SSRF guard rejects
raw loopback/private IPs as webhook targets. This is why the n8n Trigger node (not a
manually-curled webhook) is used: n8n registers `http://n8n.local/webhook/...` (a
hostname, not a literal IP) when the workflow activates.

**WhatsApp reply never arrives** — check the async job:
`curl -s -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" http://127.0.0.1:8099/jobs | jq .`
Then check WF "11 · SOFI Callback" executions in n8n, and that the `sofi-orchestrator`
session is `ready`/`working` (`GET /api/sessions/<id>` with the OpenWA API key).

**`sakk-otp` session shows `status: failed`** — pre-existing, unrelated to this
orchestration setup (SAKK's OTP sender, not touched here). Re-link with
`~/openwa/link-sakk-otp.sh` if SAKK's phone-verification OTP needs it working.

## Files

```
sofi/tooling/bin/sofi-gateway-daemon.py     the gateway (systemd runs this)
sofi/server-plane/README.md                 overview + API + command grammar
sofi/server-plane/SETUP.md                  this runbook
sofi/server-plane/n8n/workflows/*.json      version-controlled workflows
~/.config/systemd/user/{sofi-gateway,n8n}.service
~/openwa/                                   pre-existing OpenWA gateway (shared)
~/.sofi-run/                                secrets, logs, n8n-app, job trail
```
