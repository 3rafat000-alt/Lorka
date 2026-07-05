# SOFI Orchestration — Setup & Operations

Everything below is already installed and running on this box. This doc is the
runbook: how it's wired, how to pair WhatsApp, how to fix it when it breaks.

## ✅ How you drive it — SELF-CHAT mode (active)

`claude-bot` is linked to the owner's **own** number, so you drive SOFI from your
**"message yourself"** WhatsApp chat. wf10's OpenWA Trigger subscribes to
**`message.sent`** (self-notes are `fromMe`). **Every command must start with
`sofi ` or `صوفي `** — e.g. `sofi status`, `sofi audit exchange rates`,
`صوفي دقّق أسعار الصرف`. The prefix is the loop guard (bot replies never carry it, so
they're dropped and can't re-trigger). `Filter & Authorize` accepts only `fromMe`
self-notes (`to === from`, form-agnostic across `@c.us`/`@lid`) that start with the
prefix; a normal self-note like "مرحباً" without the prefix is ignored (expected).
Verified live E2E (signed `sofi ping`, both `@c.us` and `@lid`, reached the reply
send with no loop). To switch to multi-user later: give `claude-bot` a dedicated
number and revert the trigger to `message.received` + a sender allowlist. Details in
[README.md](./README.md).

## What's already done (2026-07-05)

- `sofi-gateway.service` — running, 127.0.0.1:8099, gateway v2 (async + callbacks),
  hardened this session (`MemoryMax=12G`, SSRF/owner/concurrency guards, deadletter)
- `n8n.service` — running, 127.0.0.1:5678, served at http://n8n.local (Caddy),
  ordered After/Wants `openwa-otp.service`, loads both `n8n.env` and `openwa.env`
- OpenWA gateway (pre-existing `openwa-otp.service`, `network_mode: host` → binds
  `*:2785`) — hosts the new `claude-bot` session (id
  `5b59d3b0-fbcf-4cd6-a8df-2202fc919544`) for this tool alongside SAKK's `sakk-otp`
  session, which is live and `ready`
- `@rmyndharis/n8n-nodes-openwa` community node installed (declarative, via env)
- Webhook HMAC enforcement wired and verified (unsigned POST → 401, valid signature → 200)
- `n8n-mcp` HTTP MCP server registered (`.mcp.json`) → Claude can drive n8n directly
- Caddy vhost `n8n.local` + `/etc/hosts` entry
- 3 workflows imported into n8n (two-stage WhatsApp inbound, callback, health monitor)
- linger enabled → all services survive logout and reboot
- secrets in `~/.sofi-run/*.env` (chmod 600), gateway token rotated

## Secrets & config (~/.sofi-run/)

| File | Holds |
|---|---|
| `gateway.env` | `SOFI_GATEWAY_TOKEN` + optional daemon knobs (`SOFI_CALLBACK_ALLOW`, `SOFI_OWNER_CHAT`, `SOFI_SYNC_SLOTS`) |
| `gateway-token` | same token, plain (for curl / callback header) |
| `n8n.env` | n8n config + orchestration wiring (gateway token, owner chat, community-package pin) |
| `openwa.env` | `OPENWA_API_KEY`, `OPENWA_BASE_URL`, `OPENWA_WEBHOOK_SECRET` |
| `n8n-api.env` | `N8N_API_KEY` + `N8N_MCP_TOKEN` (for the n8n MCP/REST control plane; chmod 600) |
| `openwa-session-id` | the `claude-bot` session UUID `5b59d3b0-…` (also hardcoded in the workflow JSON) |
| `logs/sofi-gateway.log` | gateway log (rotating, 10 MB × 5) |
| `gateway-jobs.jsonl` | every job, append-only audit trail (rotates at ~10 MB → `.jsonl.1`) |
| `gateway-callback-deadletter.jsonl` | callbacks still undeliverable after 3 retries |
| `n8n-app/` | the stable n8n install the service runs from |

**Never write a secret value into these docs or into git** — reference secrets by
file/name only, as above.

**Set your WhatsApp number** before real use — edit `n8n.env`:
```
SOFI_OWNER_CHAT=963XXXXXXXXX@c.us
```
then `systemctl --user restart n8n`. Empty = anyone who messages the bridge can drive
SOFI (dev only). The **Filter & Authorize** node in wf10 is fail-closed against this
value.

### ⏰ n8n API key expires 2026-08-04

The API key n8n issued for the MCP/REST control plane (`N8N_API_KEY` in
`~/.sofi-run/n8n-api.env`) **expires 2026-08-04**. After that, both the `n8n-mcp` MCP
server and any REST control of n8n stop working until you regenerate the key in the
n8n UI (**Settings → n8n API**) and update `~/.sofi-run/n8n-api.env`. `N8N_MCP_TOKEN`
(the Bearer for the MCP HTTP endpoint) is separate and does not expire on that date.

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
killed bridged containers on reboot; note this also means OpenWA binds `*:2785`, not
loopback — the compose `127.0.0.1:…:2785` mapping is ignored under host networking),
survives reboot via `openwa-otp.service` + `restart: always`. Reusing it for
orchestration (a second session, `claude-bot`) avoids running two competing WhatsApp
gateways and inherits fixes already earned. Integration is via the official n8n
community node `@rmyndharis/n8n-nodes-openwa` (OpenWA + OpenWA Trigger), not raw HTTP
nodes — it registers its own webhook on activation and handles HMAC verification
internally.

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

## Webhook HMAC enforcement (now on) — secret is a FIXED value, NOT `$env`

Inbound webhooks from OpenWA are HMAC-verified. The OpenWA Trigger's **Webhook
Secret** must be set to the **literal 48-char value** of `OPENWA_WEBHOOK_SECRET`
(from `~/.sofi-run/openwa.env`) — as a **plain fixed string**, NOT the expression
`{{ $env.OPENWA_WEBHOOK_SECRET }}`.

**Why (n8n 2.28 gotcha, verified the hard way):** in the Trigger's **webhook-
verification** code path, `getNodeParameter('webhookSecret')` does **not evaluate**
the expression — it returns the raw literal string `{{ $env.OPENWA_WEBHOOK_SECRET }}`
and uses *that* as the HMAC key. Real OpenWA signs with the true secret, so
verification mismatches and **every real message is rejected with 401**. (Proof:
signing a test payload with the literal string as the key returns 200; signing with
the real secret returns 401.) A fixed value is used identically at registration and
verification, so HMAC matches.

The secret lives in n8n's DB (fine — single-user loopback). The repo copy
`n8n/workflows/10-whatsapp-inbound.json` stores it **redacted**
(`__REDACTED_set_to_OPENWA_WEBHOOK_SECRET__`); on any re-import, open the OpenWA
Trigger node and paste the real value from `openwa.env` into the Webhook Secret field
(Fixed, not Expression). Keeping the `EnvironmentFile=%h/.sofi-run/openwa.env` line on
the n8n unit is still correct for other uses, but the webhook secret no longer relies
on it.

Enforcement verified: unsigned / bad-signature POST → **HTTP 401**; valid
`X-OpenWA-Signature: sha256=<hmac>` with the real secret → **200** → flows to the
reply send.

> **Editor note:** the red `[ERROR: access to env vars denied]` you may still see on
> `$env` fields in the n8n editor is a task-runner preview artifact — but as above,
> for the webhook secret do not rely on `$env` at all; use the fixed value.

> **n8n version churn:** after changing a workflow via the API/CLI, do **not** click
> *Publish* or revert versions in the n8n editor — it reverts the applied changes
> (this silently undid the filter fix and dropped the trigger's pinned test data).

## Direct n8n control (MCP)

Claude can control n8n directly through an `n8n-mcp` HTTP MCP server registered in
`/home/es3dlll/Desktop/Lorka/.mcp.json`:
```
url:  http://n8n.local/mcp-server/http
auth: Authorization: Bearer ${N8N_MCP_TOKEN}
```
`N8N_MCP_TOKEN` and `N8N_API_KEY` both live in `~/.sofi-run/n8n-api.env` (chmod 600).
Remember the **API key expires 2026-08-04** (see above) — regenerate and update the
env file before then or MCP/REST control breaks.

## Pair WhatsApp (one-time, manual — needs a phone)

`claude-bot` is already linked and `ready` (self-chat mode — the owner's own number).
Re-run this only if the session drops. To move to a dedicated bot number later, link
a different phone here and revert wf10's trigger to `message.received`.

```bash
KEY=$(grep OPENWA_API_KEY ~/.sofi-run/openwa.env | cut -d= -f2)
SID=$(cat ~/.sofi-run/openwa-session-id)          # 5b59d3b0-… (the claude-bot UUID)
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

Save; the same credential is reused on the ack / direct-reply nodes (workflow 10) and
the **Send Result** node (workflow 11). **Activate** both workflows — activating 10
auto-registers its HMAC-signed webhook with OpenWA (no manual webhook step).

## Daily ops

```bash
# health
curl -s http://127.0.0.1:8099/healthz | jq .
curl -sf http://127.0.0.1:2785/api/health/ready && echo openwa-ok
systemctl --user status sofi-gateway n8n openwa-otp

# logs
journalctl --user -u sofi-gateway -f
tail -f ~/.sofi-run/logs/sofi-gateway.log
tail -f ~/.sofi-run/gateway-jobs.jsonl                    # what ran, cost, duration, callback_status
tail -f ~/.sofi-run/gateway-callback-deadletter.jsonl     # callbacks that never delivered

# restart
systemctl --user restart sofi-gateway
systemctl --user restart n8n
systemctl --user restart openwa-otp             # affects BOTH sessions — SAKK OTP too
```

## Gateway daemon knobs (optional, in gateway.env)

All optional — the daemon reads them from its environment / `~/.sofi-run/gateway.env`:

- `SOFI_CALLBACK_ALLOW` — comma-separated `host:port` allowlist for `callback_url`
  (default `127.0.0.1:5678,localhost:5678`). A dispatch with a `callback_url` outside
  it → 400 (SSRF / token-leak guard — the `X-SOFI-Token` is never POSTed to an
  unknown host).
- `SOFI_OWNER_CHAT` — daemon-side defense-in-depth owner gate. When set, any dispatch
  whose `source` starts with `whatsapp` must carry `meta.chatId == SOFI_OWNER_CHAT` or
  it's 403'd. **Currently UNSET (gate dormant) on purpose** — n8n's fail-closed owner
  filter is the primary gate. To **arm it later**: set `SOFI_OWNER_CHAT` in
  `gateway.env` **and** make sure **both** wf10 dispatch stages carry `meta.chatId`.
  Today the Stage-1 classify call uses `source: whatsapp-classify` and does **not**
  send `meta.chatId`, so arming the gate without that workflow change would 403 the
  classifier. Change the workflow first, then arm.
- `SOFI_SYNC_SLOTS` — max concurrent in-thread sync `claude` runs (default 3). Over
  that → 503 `{"error":"busy"}`.

Other fixed guards (not env-tunable at runtime): model allowlist
`haiku|sonnet|opus|fable|claude-fable-5` (else 400), role name-validation
`[a-z0-9][a-z0-9-]{0,63}` path-confined (bad/traversal role → 404), 256 KiB body cap
(→ 400), 20 dispatch/min global rate limit (→ 429, `RATE_LIMIT_PER_MIN`).

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
(If you keep `SOFI_CALLBACK_ALLOW` / `SOFI_SYNC_SLOTS` in `gateway.env`, re-add them
after this overwrites the file.)

## Troubleshooting

**`n8n.local` shows 502/404 right after a restart** — n8n cold-starts in ~20-25s;
transient 404s during that window are normal. `systemctl --user status n8n`.

**n8n login "secure cookie" warning** — expected on plain http. `N8N_SECURE_COOKIE=false`
is already set in `n8n.env` (safe: loopback + LAN only). Reload the page.

**Red `[ERROR: access to env vars denied]` on the OpenWA Trigger's Webhook Secret** —
cosmetic editor-preview artifact only; `$env` doesn't resolve in n8n 2.28's NDV
preview sandbox but does at runtime in the main process. See the HMAC section above.
Don't "fix" it by hardcoding the secret.

**HMAC rejects everything / accepts unsigned** — check that `n8n.service` still has
the second `EnvironmentFile=%h/.sofi-run/openwa.env` line and that
`OPENWA_WEBHOOK_SECRET` is set there; without it the trigger silently skips
verification. Confirm: unsigned POST → 401, valid `X-OpenWA-Signature` → 200.

**Gateway 401** — token mismatch. The header/body token must equal
`~/.sofi-run/gateway-token`. n8n's copy is in `n8n.env` as `SOFI_GATEWAY_TOKEN`.

**Gateway 400 `callback host not allowed`** — the `callback_url` host isn't in
`SOFI_CALLBACK_ALLOW`. Add the `host:port` there and restart the daemon.

**Gateway 403 `owner mismatch`** — the daemon owner gate is armed (`SOFI_OWNER_CHAT`
set) but the dispatch's `meta.chatId` doesn't match (or is missing — e.g. the
classify stage). See the daemon-knobs section; normally this gate is dormant.

**Gateway 429** — hit the 20 dispatch/min limit (loop protection). Wait a minute or
raise `RATE_LIMIT_PER_MIN` in the daemon.

**Gateway 503 `busy` / `queue full`** — too many concurrent sync runs
(`SOFI_SYNC_SLOTS`) or a saturated async queue. Retry shortly or raise the slots.

**n8n MCP / REST control stops working** — first suspect the **API key expiry
(2026-08-04)**. Regenerate in n8n **Settings → n8n API**, update `N8N_API_KEY` in
`~/.sofi-run/n8n-api.env`.

**OpenWA webhook create fails `Blocked internal address`** — its SSRF guard rejects
raw loopback/private IPs as webhook targets. This is why the n8n Trigger node (not a
manually-curled webhook) is used: n8n registers `http://n8n.local/webhook/...` (a
hostname, not a literal IP) when the workflow activates.

**WhatsApp reply never arrives** — first confirm your command started with `sofi `
or `صوفي ` (self-notes without the prefix are dropped by design). Then check the
async job:
`curl -s -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" http://127.0.0.1:8099/jobs | jq .`
Then check WF "11 · SOFI Callback" executions in n8n, look at
`gateway-callback-deadletter.jsonl` for undeliverable callbacks, and confirm the
`claude-bot` session is `ready`/`working` (`GET /api/sessions/<id>` with the OpenWA
API key).

**`sakk-otp` session** — this is SAKK's production OTP sender sharing the same OpenWA
container; it is currently **live and `ready`**, untouched by this orchestration
setup. If it ever drops, re-link with `~/openwa/link-sakk-otp.sh`.

## Files

```
sofi/tooling/bin/sofi-gateway-daemon.py     the gateway (systemd runs this)
sofi/server-plane/README.md                 overview + API + architecture + routing
sofi/server-plane/SETUP.md                  this runbook
sofi/server-plane/n8n/workflows/*.json      version-controlled workflows
.mcp.json                                   n8n-mcp HTTP server (direct Claude → n8n control)
~/.config/systemd/user/{sofi-gateway,n8n}.service
~/openwa/                                   pre-existing OpenWA gateway (shared: claude-bot + sakk-otp)
~/.sofi-run/                                secrets, logs, n8n-app, job trail, deadletter
```
