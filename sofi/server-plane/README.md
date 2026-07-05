# SOFI Orchestration — n8n · Gateway · WhatsApp (OpenWA)

24/7 automation for SOFI. You send a WhatsApp message → n8n classifies it → either
answers you inline on the spot (the cheap path) or hands the work to the SOFI
Gateway, which runs the right Claude agent on this machine (full git/brain/CLI
access) and pushes the result back to your WhatsApp. No terminal, no manual steps.

This is a **tool**, not a `PRJ-*` project. It lives on the host, not in a project brain.

WhatsApp goes through **OpenWA** — the same self-hosted gateway already running on
this box for SAKK's OTP delivery (`~/openwa/`). Orchestration gets its own session
(**`claude-bot`**, id `5b59d3b0-fbcf-4cd6-a8df-2202fc919544`) on that gateway;
SAKK's `sakk-otp` production OTP session runs alongside it in the same container and
is untouched. The workflow JSONs hardcode the session **UUID** (not a name);
`~/.sofi-run/openwa-session-id` holds the same value.

---

## ⚠️ Known limitation — read before real use (open item #1)

The `claude-bot` WhatsApp session is currently linked to the **same phone number**
as the owner (`SOFI_OWNER_CHAT`). WhatsApp routes a message you send to yourself as
`fromMe` / `message.sent` — **never** as `message.received`, which is the only event
wf10's OpenWA Trigger subscribes to. So **a genuine WhatsApp message the owner types
cannot reach the pipeline today** — every successful run to date used API-injected
test payloads.

Production needs one of:

- a **dedicated bot number distinct from the owner's** (then the owner just messages
  the bot normally, and it arrives as `message.received`) — recommended; or
- a **self-chat redesign**: trigger on `message.sent` / `fromMe`, match on the `to`
  field, and add loop-guarding so the bot's own replies don't re-trigger it.

Until then, treat the WhatsApp entry point as verified only via injected payloads.

---

## Architecture

```
 WhatsApp (owner's phone)
        │
        ▼
 OpenWA gateway  (docker, network_mode:host → binds *:2785 — already running for SAKK OTP)
   session "claude-bot"  (id 5b59d3b0-…)  ← runs alongside SAKK's "sakk-otp" session
        │  n8n OpenWA Trigger registers its own HMAC-signed webhook on activate
        ▼
 n8n  (127.0.0.1:5678, systemd)  ── http://n8n.local  (via Caddy :80)
   │
   ├─ WF "10 · WhatsApp Inbound"  — two-stage, cost-aware:
   │     OpenWA Trigger
   │       → Filter & Authorize        (owner-only, fail-closed)
   │       → Build Classify Request
   │       → Classify (haiku, sync)    POST 127.0.0.1:8099/dispatch (blocking)
   │       → Parse Classification      strict JSON {trivial,direct_answer,role,model_tier,reason}
   │       → IF Trivial?
   │           ├─ true  → OpenWA: Direct Reply (cheap path — answer inline, no agent run)
   │           └─ false → Build Work Dispatch
   │                        → SOFI Gateway /dispatch (async, callback_url set)
   │                        → OpenWA: Ack        (instant ack; real answer follows via wf11)
   │                              │
   │                              ▼
   │                        SOFI Gateway Daemon (127.0.0.1:8099, systemd)
   │                              │ builds RCCF → runs: claude -p --model … (host, full access)
   │                              │ on finish → POST callback with {response, meta:{chatId}}
   │                              ▼
   └─ WF "11 · SOFI Callback"  → OpenWA sendText → owner's WhatsApp
```

**What binds where.** Only n8n (`127.0.0.1:5678`) and the gateway (`127.0.0.1:8099`)
are truly loopback. OpenWA runs `network_mode: host`, so it binds **`*:2785` on all
interfaces** — the compose `127.0.0.1:…:2785` port mapping is *ignored* under host
networking. OpenWA's LAN exposure is mitigated by (a) API-key auth on its REST API
and (b) **HMAC-signed webhooks** (now enforced — see the Gateway/Webhook notes and
SETUP.md); firewall / host isolation is the backstop. WhatsApp itself reaches OpenWA
outbound over the WhatsApp Web protocol, not an inbound port.

### Direct n8n control (MCP)

Claude can drive n8n directly (list/create/update workflows, read executions) via an
`n8n-mcp` HTTP MCP server registered in `/home/es3dlll/Desktop/Lorka/.mcp.json` at
`http://n8n.local/mcp-server/http` (Bearer `${N8N_MCP_TOKEN}`). The API/MCP tokens
live in `~/.sofi-run/n8n-api.env`. **The n8n API key expires 2026-08-04** — after
that, MCP + REST control of n8n stops until the key is regenerated (see SETUP.md).

---

## Services (systemd --user, linger on → survive logout/boot)

| Service | Bind | What |
|---|---|---|
| `sofi-gateway.service` | 127.0.0.1:8099 | RCCF → `claude -p` bridge, async job queue + callbacks (`MemoryMax=12G`) |
| `n8n.service` | 127.0.0.1:5678 | workflow engine, UI at http://n8n.local (ordered After/Wants `openwa-otp.service`) |
| `openwa-otp.service` (pre-existing) | *:2785 (host net) | OpenWA gateway — hosts BOTH `sakk-otp` (SAKK OTP) and `claude-bot` (this orchestrator) sessions |

```bash
systemctl --user status sofi-gateway n8n openwa-otp
journalctl --user -u sofi-gateway -f      # live gateway log
```

Config/secrets live in `~/.sofi-run/` (chmod 600, never in git):
`gateway.env` · `n8n.env` · `openwa.env` · `n8n-api.env` · `openwa-session-id` ·
`gateway-token` · logs + `gateway-jobs.jsonl` + `gateway-callback-deadletter.jsonl`.

---

## The Gateway API (127.0.0.1:8099)

Auth: `X-SOFI-Token` header (value = `~/.sofi-run/gateway-token`, constant-time
compare). Loopback only.

| Route | Body / notes |
|---|---|
| `GET /healthz` | no auth; `{status, queue}` |
| `POST /dispatch` | `{command, role?, project?, model?, mode?, callback_url?, meta?, source?, timeout?}` |
| `GET /job/<id>` | job status + result |
| `GET /jobs` | recent jobs |

- `mode: "sync"` — blocks up to ~180 s and returns the result inline (quick queries;
  this is what wf10's Stage-1 classify uses). Over `SOFI_SYNC_SLOTS` concurrent sync
  runs → `503 {"error":"busy"}`.
- `mode: "async"` (default) — returns `{job_id}` instantly, runs in a worker, and (if
  `callback_url` given) POSTs `{job_id,status,response,error,meta}` when done. This is
  the WhatsApp work path — the phone gets an instant ack, the answer follows via wf11.

**Guards / operational surface:**

- **Role allowlist** — must resolve to a `.claude/agents/*.md` slug; the role is
  name-validated (`[a-z0-9][a-z0-9-]{0,63}`, path-confined) so a bad/traversal role → 404.
- **Model allowlist** — `haiku | sonnet | opus | fable | claude-fable-5`; anything
  else → 400.
- **Body cap** 256 KiB → 400; **global rate limit** 20 dispatch/min → 429
  (`RATE_LIMIT_PER_MIN`).
- **Callback SSRF/token-leak guard** — `callback_url` host must be in
  `SOFI_CALLBACK_ALLOW` (default `127.0.0.1:5678,localhost:5678`); outside it → 400,
  so the `X-SOFI-Token` is never POSTed to an unknown host.
- **Owner gate (defense-in-depth, dormant)** — `SOFI_OWNER_CHAT`. When set, any
  dispatch whose `source` starts with `whatsapp` must carry `meta.chatId ==
  SOFI_OWNER_CHAT` or it's 403'd. **Currently UNSET on purpose** — n8n's fail-closed
  owner filter is the primary gate. See SETUP.md for how to arm it safely.
- **Concurrency** — `SOFI_SYNC_SLOTS` (default 3) caps in-thread sync `claude` runs;
  the async queue has its own bound (over it → 503 `queue full`).
- **Audit + durability** — every job is appended to `gateway-jobs.jsonl` (rotates at
  ~10 MB → `.jsonl.1`, persisted `result` capped at 4000 chars); jobs carry a
  `callback_status`; callbacks still undeliverable after 3 retries are captured in
  `gateway-callback-deadletter.jsonl` instead of being silently lost. The daemon log
  (`sofi-gateway.log`) uses a rotating handler (10 MB × 5).

Manual test:
```bash
TOKEN=$(cat ~/.sofi-run/gateway-token)
curl -s -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: $TOKEN" -H 'Content-Type: application/json' \
  -d '{"command":"Report PRJ-SAKK gate + blockers.","mode":"sync","model":"haiku"}' | jq .
```

---

## Routing — two-stage, cost-aware (commit `cb353cb`)

There is no first-word command grammar. Every inbound ticket is first run through a
cheap classifier, and only real work is escalated to an agent run.

**Stage 1 — Classify (haiku, sync).** wf10 builds a small classify request and calls
the gateway *synchronously* with `model: haiku`. The classifier returns strict JSON:

```json
{ "trivial": true|false, "direct_answer": "…", "role": "<sofi-slug>",
  "model_tier": "mechanical|workhorse|gatekeeper|deep", "reason": "…" }
```

**Stage 2 — route on `trivial`.**

- `trivial: true` (~80% of tickets) → **OpenWA: Direct Reply (cheap path)**: the
  classifier's `direct_answer` is sent straight back on WhatsApp. No agent run, no
  gateway job — cheapest possible path.
- `trivial: false` → **Build Work Dispatch** → `POST /dispatch` (async, `callback_url`
  set) → **OpenWA: Ack** (instant). The real answer arrives later via wf11's callback.
  For real work the classifier picks a `role` from the 30-slug SOFI agent enum and a
  `model_tier` mapped to a model: `mechanical → haiku`, `workhorse → sonnet`,
  `gatekeeper → fable`, `deep → opus`.

**Authorization** is upstream of all of this: **Filter & Authorize** is fail-closed —
only the number in `SOFI_OWNER_CHAT` (n8n env, `963XXXXXXXXX@c.us` format) passes.
(See the Known-limitation box: same-number self-messages don't reach the trigger at
all yet.)

---

## First-time WhatsApp pairing (one manual step)

The `claude-bot` session exists on the existing OpenWA gateway but needs a phone
linked once:

```bash
KEY=$(grep OPENWA_API_KEY ~/.sofi-run/openwa.env | cut -d= -f2)
SID=$(cat ~/.sofi-run/openwa-session-id)          # 5b59d3b0-… (the claude-bot UUID)
curl -s -X POST "http://127.0.0.1:2785/api/sessions/$SID/start" -H "X-API-Key: $KEY"
# poll until status is qr_ready, then fetch + open the QR:
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:2785/api/sessions/$SID/qr" \
  | python3 -c "import sys,json,base64;q=json.load(sys.stdin)['qrCode'];open('/tmp/sofi-qr.png','wb').write(base64.b64decode(q.split(',',1)[1]))"
xdg-open /tmp/sofi-qr.png
```
Scan with the WhatsApp account you want to drive SOFI from: **Settings ▸ Linked
Devices ▸ Link a Device**. (See the Known-limitation box first — for real use this
should be a **dedicated bot number**, not the owner's own number.)

Then in n8n (http://n8n.local): open **10 · WhatsApp Inbound** and set up the
**OpenWA API** credential once (Server URL `http://127.0.0.1:2785`, API key from
`~/.sofi-run/openwa.env`) — n8n reuses the same credential on the ack/direct-reply
nodes and on **11 · SOFI Callback**. **Activate** both workflows (activating 10
auto-registers its HMAC-signed webhook with OpenWA — no manual webhook step).

Full setup + troubleshooting: [SETUP.md](./SETUP.md).

---

## Workflows

Version-controlled JSON in [`n8n/workflows/`](./n8n/workflows/), imported into n8n's DB:

- `10-whatsapp-inbound.json` — the two-stage router: OpenWA Trigger → Filter &
  Authorize (owner-only, fail-closed) → Build Classify Request → Classify (haiku,
  sync) → Parse Classification → IF Trivial? → [Direct Reply | Build Work Dispatch →
  gateway `/dispatch` → Ack]
- `11-sofi-callback.json` — gateway callback → shape reply → OpenWA sendText
- `12-health-monitor.json` — hourly gateway health check

Both WhatsApp workflows use the community node `@rmyndharis/n8n-nodes-openwa`
(installed declaratively — see `N8N_COMMUNITY_PACKAGES` in `n8n.env`, not npm-installed
by hand). The **session UUID** `5b59d3b0-fbcf-4cd6-a8df-2202fc919544` is hardcoded in
the workflow JSON (`~/.sofi-run/openwa-session-id` holds the same value). The OpenWA
Trigger's `webhookSecret` uses `{{ $env.OPENWA_WEBHOOK_SECRET }}` (from
`~/.sofi-run/openwa.env`) and enforces HMAC on every inbound webhook — see SETUP.md.

Re-import after editing:
```bash
node ~/.sofi-run/n8n-app/node_modules/n8n/bin/n8n \
  import:workflow --separate --input=sofi/server-plane/n8n/workflows/
# re-importing creates NEW rows if a workflow with that name already exists —
# dedupe manually (keep the newest createdAt per name) if you re-run this.
```
