# SOFI Orchestration — n8n · Gateway · WhatsApp (OpenWA)

24/7 automation for SOFI. You send a WhatsApp message → n8n routes it → the SOFI
Gateway runs the right Claude agent on this machine (full git/brain/CLI access) →
the result is pushed back to your WhatsApp. No terminal, no manual steps.

This is a **tool**, not a `PRJ-*` project. It lives on the host, not in a project brain.

WhatsApp goes through **OpenWA** — the same self-hosted gateway already running on
this box for SAKK's OTP delivery (`~/openwa/`). Orchestration gets its own session
(`sofi-orchestrator`) on that gateway; SAKK's `sakk-otp` session is untouched.

---

## Architecture

```
 WhatsApp (your phone)
        │
        ▼
 OpenWA gateway  (127.0.0.1:2785, docker, network_mode:host — already running for SAKK OTP)
   session "sofi-orchestrator"  ← separate from SAKK's "sakk-otp" session
        │  n8n OpenWA Trigger node registers its own webhook on activate
        ▼
 n8n  (127.0.0.1:5678, systemd)  ── http://n8n.local  (via Caddy :80)
   ├─ WF "10 · WhatsApp Inbound"  OpenWA Trigger → filter+authorize → map to RCCF → dispatch
   │        │ POST 127.0.0.1:8099/dispatch  (async, callback_url set)
   │        ▼
   │   SOFI Gateway Daemon  (127.0.0.1:8099, systemd)
   │        │ builds RCCF → runs: claude -p --model … (host, full access)
   │        │ on finish → POST callback with {response, meta:{chatId}}
   │        ▼
   └─ WF "11 · SOFI Callback"  → OpenWA node (sendText) → your WhatsApp
```

Everything binds **loopback only**. WhatsApp reaches OpenWA over the WhatsApp Web
protocol (outbound from OpenWA), not an inbound port — no public surface.

---

## Services (systemd --user, linger on → survive logout/boot)

| Service | Bind | What |
|---|---|---|
| `sofi-gateway.service` | 127.0.0.1:8099 | RCCF → `claude -p` bridge, async job queue + callbacks |
| `n8n.service` | 127.0.0.1:5678 | workflow engine, UI at http://n8n.local |
| `openwa-otp.service` (pre-existing) | 127.0.0.1:2785 | OpenWA gateway — shared by SAKK OTP and this orchestrator, different sessions |

```bash
systemctl --user status sofi-gateway n8n openwa-otp
journalctl --user -u sofi-gateway -f      # live gateway log
```

Config/secrets live in `~/.sofi-run/` (chmod 600, never in git):
`gateway.env` · `n8n.env` · `openwa.env` · `openwa-session-id` · `gateway-token` ·
logs + `gateway-jobs.jsonl`.

---

## The Gateway API (127.0.0.1:8099)

Auth: `X-SOFI-Token` header (value = `~/.sofi-run/gateway-token`). Loopback only.

| Route | Body / notes |
|---|---|
| `GET /healthz` | no auth; `{status, queue}` |
| `POST /dispatch` | `{command, role?, project?, model?, mode?, callback_url?, meta?}` |
| `GET /job/<id>` | job status + result |
| `GET /jobs` | recent jobs |

- `mode: "sync"` — blocks up to 180 s, returns the result inline (quick queries).
- `mode: "async"` (default) — returns `{job_id}` instantly, runs in a worker, and
  (if `callback_url` given) POSTs `{job_id,status,response,error,meta}` when done.
  This is the WhatsApp path — the phone gets an instant ack, the answer follows.

Guards: role allowlist (`.claude/agents/*.md`), model allowlist
(`haiku|sonnet|opus|fable`), 256 KiB body cap, 20 dispatch/min rate limit,
constant-time token compare, every job appended to `gateway-jobs.jsonl`.

Manual test:
```bash
TOKEN=$(cat ~/.sofi-run/gateway-token)
curl -s -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: $TOKEN" -H 'Content-Type: application/json' \
  -d '{"command":"Report PRJ-SAKK gate + blockers.","mode":"sync","model":"haiku"}' | jq .
```

---

## WhatsApp command grammar

First word picks the route; the rest is the argument. Anything unmatched goes to
the CEO as a natural-language instruction.

| Send on WhatsApp | Runs |
|---|---|
| `status` | short PRJ-SAKK status (gate, last work, open tickets) |
| `gate` | current gate + blockers |
| `audit [layer]` | QA/SRE audit pass, ranked findings |
| `fix <thing>` | route fix to cheapest specialist, checkpoint each |
| `report [kind]` | status/security/etc report |
| `feature <desc>` | full feature loop |
| `sync` | `sofi sync` + summary |
| *(free text)* | CEO routes it |

Only the number in `SOFI_OWNER_CHAT` (n8n env, `963XXXXXXXXX@c.us` format) may
drive SOFI. Empty = allow all (dev only — set it before real use).

---

## First-time WhatsApp pairing (one manual step)

The `sofi-orchestrator` session was created on the existing OpenWA gateway but
needs your phone linked once:

```bash
KEY=$(grep OPENWA_API_KEY ~/.sofi-run/openwa.env | cut -d= -f2)
SID=$(cat ~/.sofi-run/openwa-session-id)
curl -s -X POST "http://127.0.0.1:2785/api/sessions/$SID/start" -H "X-API-Key: $KEY"
# poll until status is qr_ready, then fetch + open the QR:
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:2785/api/sessions/$SID/qr" \
  | python3 -c "import sys,json,base64;q=json.load(sys.stdin)['qrCode'];open('/tmp/sofi-qr.png','wb').write(base64.b64decode(q.split(',',1)[1]))"
xdg-open /tmp/sofi-qr.png
```
Scan with the WhatsApp account you want to drive SOFI from: **Settings ▸ Linked
Devices ▸ Link a Device**.

Then in n8n (http://n8n.local): open **10 · WhatsApp Inbound** and set up the
**OpenWA API** credential once (Server URL `http://127.0.0.1:2785`, API key from
`~/.sofi-run/openwa.env`) — n8n reuses the same credential on **11 · SOFI
Callback**. **Activate** both workflows (activating 10 auto-registers its webhook
with OpenWA — no manual webhook step). Send yourself `status` — you should get an
ack then the result.

Full setup + troubleshooting: [SETUP.md](./SETUP.md).

---

## Workflows

Version-controlled JSON in [`n8n/workflows/`](./n8n/workflows/), imported into n8n's DB:

- `10-whatsapp-inbound.json` — OpenWA Trigger → filter/authorize (owner allowlist) → map to RCCF → gateway dispatch → OpenWA ack
- `11-sofi-callback.json` — gateway callback → shape reply → OpenWA sendText
- `12-health-monitor.json` — hourly gateway health check

Both WhatsApp workflows use the community node `@rmyndharis/n8n-nodes-openwa`
(installed declaratively — see `N8N_COMMUNITY_PACKAGES` in `n8n.env`, not npm-installed
by hand). Session id `sofi-orchestrator` is hardcoded in the workflow JSON
(`~/.sofi-run/openwa-session-id` has the same value).

Re-import after editing:
```bash
node ~/.sofi-run/n8n-app/node_modules/n8n/bin/n8n \
  import:workflow --separate --input=sofi/server-plane/n8n/workflows/
# re-importing creates NEW rows if a workflow with that name already exists —
# dedupe manually (keep the newest createdAt per name) if you re-run this.
```
