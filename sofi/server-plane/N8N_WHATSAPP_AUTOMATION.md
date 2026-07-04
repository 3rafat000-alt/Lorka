# n8n + WhatsApp + SOFI Agents — 24/7 Automation

**Your setup:** n8n (local) + SOFI Gateway (127.0.0.1:8099) + Claude agents

**Goal:** Send text on WhatsApp → n8n picks it up → routes to SOFI agents → result back to WhatsApp  
**24/7 & hands-off:** systemd auto-restarts daemon + n8n + health monitoring

---

## Architecture

```
┌─ WhatsApp API webhook ─┐
│ (Twilio/official)      │
└──────────┬──────────────┘
           │ incoming message
           ▼
┌──────────────────────┐
│ n8n Task Listener    │  (workflow: 06-task-distributor)
│ POST /sofi-task      │
└──────────┬───────────┘
           │ parse + route
           ▼
┌──────────────────────────────────┐
│ n8n Request Router               │
│ ├─ audit → sofi-qa-sre-lead      │
│ ├─ fix → sofi-fix                │
│ ├─ report → sofi-tier-4-advisor  │
│ └─ feature → sofi-feature        │
└──────────┬──────────────────────┘
           │ HTTP dispatch
           ▼
┌──────────────────────────────────┐
│ SOFI Gateway (127.0.0.1:8099)    │
│ /dispatch                        │
│ ├─ Auth: X-SOFI-Token            │
│ ├─ RCCF block builder            │
│ └─ claude -p spawner             │
└──────────┬──────────────────────┘
           │ execute RCCF
           ▼
┌──────────────────────────────────┐
│ Claude Code CLI                  │
│ (full access: git, brain, tools) │
└──────────┬──────────────────────┘
           │ artifact + response
           ▼
┌──────────────────────────────────┐
│ n8n Response Formatter           │
│ (format for human readability)   │
└──────────┬──────────────────────┘
           │ formatted reply
           ▼
┌──────────────────────────────────┐
│ WhatsApp API                     │
│ Send message back to user        │
└──────────────────────────────────┘
```

---

## Step 1: WhatsApp Setup (Twilio or Official API)

### Option A: Twilio Sandbox (quickest for testing)
1. Sign up: https://www.twilio.com/console
2. Go to **Messaging** → **Try it out** → **Sandbox**
3. Enable WhatsApp Sandbox, scan QR code on your phone
4. **Webhook URL:** `https://<your-domain>/n8n/webhook/whatsapp` (via `sofi tunnel up`)
5. POST method
6. Save webhook settings

### Option B: Official WhatsApp Business API
1. Apply: Meta for Developers → WhatsApp Business Platform
2. Get access token + phone number ID
3. Set webhook (same as above)
4. Verify webhook in n8n

---

## Step 2: n8n Webhook Workflow (06-task-distributor)

Create workflow with:

**Trigger:** HTTP webhook  
**URL path:** `/whatsapp` (or `/sofi-task`)

**Node 1: Validate Webhook**
```javascript
// Code node
const sig = $input.headers['x-twilio-signature'];
const token = $env.TWILIO_AUTH_TOKEN;
const url = $env.WEBHOOK_URL;
const crypto = require('crypto');

// Validate signature (if using Twilio)
const expected = crypto
  .createHmac('sha1', token)
  .update(url + new URLSearchParams($input.body).toString())
  .digest('base64');

if (sig !== expected && token !== 'dev') {
  throw new Error('Invalid webhook signature');
}

return $input.body;
```

**Node 2: Parse Message**
```javascript
// Twilio format:
const { From, Body } = $json;
const phone = From.replace('whatsapp:', '');
const message = Body.trim();

// Split: first word = command
const [cmd, ...args] = message.split(' ');

return {
  phone,
  message,
  command: cmd.toLowerCase(),
  args: args.join(' '),
  timestamp: new Date().toISOString()
};
```

**Node 3: Route to Dispatcher**

```javascript
// Map command → agent role
const routes = {
  'audit':    { role: 'sofi-qa-sre-lead',     cmd: 'sofi audit PRJ-SAKK' },
  'fix':      { role: 'sofi-fix',             cmd: 'sofi fix <target>' },
  'report':   { role: 'sofi-tier-4-advisor',  cmd: 'sofi report <kind>' },
  'feature':  { role: 'sofi-feature',         cmd: 'sofi feature "<name>"' },
  'sync':     { role: 'sofi-ceo',             cmd: 'sofi sync PRJ-SAKK' },
  'gate':     { role: 'sofi-ceo',             cmd: 'sofi gate-check' },
  'help':     { role: null,                   msg: '...' }
};

const route = routes[$json.command] || null;

if (!route) {
  return {
    error: true,
    reply: `❌ Unknown command: ${$json.command}\n\nAvailable: audit, fix, report, feature, sync, gate, help`
  };
}

if (route.msg) {
  return { error: false, reply: route.msg };
}

return {
  error: false,
  role: route.role,
  command: route.cmd.replace('<target>', $json.args || 'all')
                     .replace('<kind>', $json.args || 'daily'),
  full_command: $json.message
};
```

**Node 4: IF Error?**

If `error === true`, reply to WhatsApp with error message, stop.

**Node 5: HTTP Dispatch to Gateway**

```
POST http://127.0.0.1:8099/dispatch
Headers:
  X-SOFI-Token: {{ $credentials.sofiGatewayToken }}
  Content-Type: application/json

Body:
{
  "role": "{{ $json.role }}",
  "project": "PRJ-SAKK",
  "command": "{{ $json.command }}",
  "context": "Triggered from WhatsApp: {{ $json.full_command }}",
  "priority": "high",
  "source": "whatsapp",
  "trigger": "{{ $json.phone }}"
}
```

**Node 6: Parse Gateway Response**

```javascript
if (!$json.success) {
  return {
    error: true,
    reply: `⚠️ Dispatch failed: ${$json.error || 'unknown error'}`
  };
}

const resp = $json.response || '';
const artifact = $json.artifact || '';

// Truncate if too long for WhatsApp (4096 chars max)
let reply = `✅ ${$json.role} executed\n\n`;
reply += resp.substring(0, 2000);
if (resp.length > 2000) reply += `\n\n... [truncated, see ${artifact}]`;

return { error: false, reply };
```

**Node 7: Send WhatsApp Reply**

```
POST to Twilio API (or official WhatsApp)

Body (Twilio format):
{
  "To": "whatsapp:{{ $json.phone }}",
  "From": "whatsapp:{{ $env.TWILIO_WHATSAPP_NUMBER }}",
  "Body": "{{ $json.reply }}"
}

Headers:
  Authorization: Basic {{ $credentials.twilio.auth }}
```

(Or use n8n's built-in Twilio node)

---

## Step 3: Deploy Infrastructure

### 3.1 Verify gateway is running
```bash
systemctl --user status sofi-gateway.service
curl http://127.0.0.1:8099/healthz
```

### 3.2 Start n8n
```bash
# If Docker:
cd sofi/server-plane/n8n && docker compose up -d

# If installed locally:
n8n start
```

### 3.3 Public webhook (for WhatsApp to reach n8n)
```bash
sofi tunnel up PRJ-N8N
# Returns: https://<slug>.tunnelurl.com (temp public URL)

# Point WhatsApp webhook to:
# https://<slug>.tunnelurl.com/n8n/webhook/whatsapp
```

Or expose via Caddy:
```
whatsapp-webhook.local {
    reverse_proxy 127.0.0.1:5678
    # n8n webhook endpoints are auto-proxied
}
```

### 3.4 Test end-to-end
```bash
# Send WhatsApp message to your test number
# or test webhook locally:
curl -X POST http://localhost:5678/n8n/webhook/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+966123456789&Body=audit"

# Check n8n execution logs for result
```

---

## Step 4: Safe Operation (24/7)

### 4.1 systemd auto-restart

Already configured:
```ini
# sofi-gateway.service
Restart=always
RestartSec=10

# n8n.service (if using systemd)
Restart=always
RestartSec=30
```

### 4.2 Health monitoring

Add workflow: **10-uptime-monitor** (cron: every 5m)
```
Cron 5m
  ↓
HTTP GET http://127.0.0.1:8099/healthz
HTTP GET http://localhost:5678/api/health (n8n)
HTTP GET http://127.0.0.1:5432 (PostgreSQL, if Docker)
  ↓
IF any fail:
  ├─ Slack critical alert
  └─ Attempt systemctl restart
```

### 4.3 Audit logging

Every dispatch logged to:
- `~/.sofi-run/logs/sofi-gateway.log` (gateway)
- `~/.sofi-run/logs/n8n-audit.log` (n8n)

Search for issues:
```bash
# Last 50 failed dispatches
grep "error\|failed" ~/.sofi-run/logs/sofi-gateway.log | tail -50

# Gateway restart events
journalctl --user -u sofi-gateway.service | grep Restart
```

### 4.4 Token rotation (monthly)
```bash
# Generate new token
openssl rand -hex 32 > /tmp/new-token

# Update env files
cp /tmp/new-token ~/.sofi-run/gateway-token

# Reload service
systemctl --user restart sofi-gateway.service

# Update n8n credential:
# Credentials → SOFI Gateway Token → edit → save
```

---

## Step 5: Commands Reference

**From WhatsApp, send:**

| Command | What it does | Example |
|---------|------------|---------|
| `audit` | Scan PRJ-SAKK for issues | `audit` |
| `fix <layer>` | Apply fixes (ui, blade, db, api, all) | `fix ui` |
| `report <kind>` | Generate report (daily, weekly, security) | `report daily` |
| `feature "<name>"` | Full feature loop (scan → review → fix → verify) | `feature "payment gateway"` |
| `sync` | Sync from git + update brain | `sync` |
| `gate` | Check current gate status + blockers | `gate` |
| `help` | Show available commands | `help` |

---

## Troubleshooting

### "Invalid webhook signature"
→ Check Twilio webhook URL matches exactly  
→ Verify X-Twilio-Signature header is present

### "Dispatch failed: agent not found"
→ Check role name in routing map (step 3, node 3)  
→ Verify agent exists: `ls .claude/agents/sofi-*.md`

### WhatsApp webhook not triggering
→ Verify tunnel is running: `sofi tunnel status`  
→ Check webhook URL in Twilio dashboard  
→ Test with curl locally first

### Gateway 401 (unauthorized)
→ Check X-SOFI-Token matches `~/.sofi-run/gateway.env`  
→ Verify n8n credential is saved and assigned to node

### Response truncated in WhatsApp
→ n8n limits replies to 4096 chars (WhatsApp limit)  
→ Workflow parses full response to `~/.sofi-run/logs/` and mentions path in reply

---

## Example: Complete "audit" Flow

```
User sends: "audit"
     ↓
n8n webhook receives + validates
     ↓
Command: audit → role: sofi-qa-sre-lead
     ↓
Gateway /dispatch receives:
{
  "role": "sofi-qa-sre-lead",
  "command": "sofi audit PRJ-SAKK",
  "priority": "high",
  "source": "whatsapp"
}
     ↓
Gateway runs:
claude -p "🎭 Role: sofi-qa-sre-lead
📂 Context: Project PRJ-SAKK, HEAD abc123, Priority high, Source whatsapp
🎯 Command: sofi audit PRJ-SAKK
📐 Format: artifact"
     ↓
Claude agent scans 30+ files, finds:
  - 3 CRITICAL bugs
  - 5 MEDIUM issues
  - 12 suggestions
     ↓
Returns artifact (file) + summary text
     ↓
n8n formats:
"✅ sofi-qa-sre-lead executed

Found 3 CRITICAL issues:
1. SQL injection in /admin/gold (line 156)
2. Race condition in fee calculation
3. Missing CSRF token on POST /api/...

... [full audit in ~/.sofi-run/artifacts/audit-2026-07-04.md]"
     ↓
Sends to WhatsApp user
     ↓
Done. Full audit logged. User gets summary + artifact path.
```

---

## Next: Integrate with Slack (optional)

Add parallel Slack notifications:
```
n8n: after WhatsApp reply
  ├─ Post to Slack #sofi-automation with same message
  └─ Add thread replies with metrics (time, token cost, gate status)
```

---

**Reference:**
- Gateway: `sofi/tooling/bin/sofi-gateway-daemon.py`
- Logs: `~/.sofi-run/logs/`
- Tunnel: `sofi tunnel up <PRJ>`
- Monitoring: `systemctl --user status sofi-gateway.service`

**Go live:** Activate workflow 06, enable webhook, test on your phone. Good luck! 🚀
