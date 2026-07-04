# SOFI Orchestration — n8n · Gateway · WhatsApp

24/7 automation for SOFI. You send a WhatsApp message → n8n routes it → the SOFI
Gateway runs the right Claude agent on this machine (full git/brain/CLI access) →
the result is pushed back to your WhatsApp. No terminal, no manual steps.

This is a **tool**, not a `PRJ-*` project. It lives on the host, not in a project brain.

---

## Architecture

```
 WhatsApp (your phone)
        │
        ▼
 WAHA container  (127.0.0.1:3000, docker)     ← WhatsApp HTTP API + QR pairing
        │  POST /webhook/waha
        ▼
 n8n  (127.0.0.1:5678, systemd)  ── http://n8n.local  (via Caddy :80)
   ├─ WF "10 · WhatsApp Inbound"  filter+authorize → map text to RCCF → dispatch
   │        │ POST 127.0.0.1:8099/dispatch  (async, callback_url set)
   │        ▼
   │   SOFI Gateway Daemon  (127.0.0.1:8099, systemd)
   │        │ builds RCCF → runs: claude -p --model … (host, full access)
   │        │ on finish → POST callback with {response, meta:{chatId}}
   │        ▼
   └─ WF "11 · SOFI Callback"  → WAHA /api/sendText → your WhatsApp
```

Everything binds **loopback only**. The sole public-ish surface is WhatsApp itself
(Meta's servers reach WAHA through the WhatsApp Web protocol, not an inbound port).

---

## Services (systemd --user, linger on → survive logout/boot)

| Service | Bind | What |
|---|---|---|
| `sofi-gateway.service` | 127.0.0.1:8099 | RCCF → `claude -p` bridge, async job queue + callbacks |
| `n8n.service` | 127.0.0.1:5678 | workflow engine, UI at http://n8n.local |
| `waha.service` | 127.0.0.1:3000 | WhatsApp HTTP API (docker) |

```bash
systemctl --user status sofi-gateway n8n waha
journalctl --user -u sofi-gateway -f      # live gateway log
```

Config/secrets live in `~/.sofi-run/` (chmod 600, never in git):
`gateway.env` · `n8n.env` · `waha.env` · `gateway-token` · logs + `gateway-jobs.jsonl`.

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

Only the number in `SOFI_OWNER_CHAT` (n8n env) may drive SOFI. Empty = allow all
(dev only — set it before real use).

---

## First-time WhatsApp pairing (one manual step)

WAHA needs your phone paired once via QR:

```bash
systemctl --user start waha           # if not running
# open the QR / pairing screen:
xdg-open http://127.0.0.1:3000        # WAHA dashboard (API key = ~/.sofi-run/waha.env)
# start a session named "default", scan the QR in WhatsApp → Linked devices
```

Then in n8n (http://n8n.local) **activate** the two workflows
`10 · WhatsApp Inbound` and `11 · SOFI Callback`. Send yourself `status` — you
should get an ack then the result. Done.

Full setup + troubleshooting: [SETUP.md](./SETUP.md).

---

## Workflows

Version-controlled JSON in [`n8n/workflows/`](./n8n/workflows/), imported into n8n's DB:

- `10-whatsapp-inbound.json` — WAHA webhook → filter/authorize → map to RCCF → gateway dispatch → ack
- `11-sofi-callback.json` — gateway callback → shape reply → WAHA sendText
- `12-health-monitor.json` — hourly gateway health check

Re-import after editing:
```bash
node ~/.sofi-run/n8n-app/node_modules/n8n/bin/n8n \
  import:workflow --separate --input=sofi/server-plane/n8n/workflows/
```
