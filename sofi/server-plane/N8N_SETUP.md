# n8n + SOFI Gateway Integration

**Status:** Ready for v2.0 integration  
**Gateway:** `127.0.0.1:8099` (systemd: `sofi-gateway.service`)  
**Token:** `~/.sofi-run/gateway.env` → `SOFI_GATEWAY_TOKEN`

## Quick Start

### 1. n8n already installed?
```bash
n8n start  # or docker compose up (if you have Docker setup)
# Runs on http://localhost:5678
```

### 2. Create n8n webhook credential for gateway
In n8n UI:
- **Credentials** → **+ Create new** → **HTTP Header Auth**
- **Header name:** `X-SOFI-Token`
- **Header value:** `40706bf2248f9dd7c495399049617560300aa3b02634dddd39114eab3c578988` (from `~/.sofi-run/gateway.env`)
- **Name:** "SOFI Gateway Token"
- **Save**

### 3. Test dispatch
```bash
SOFI_TOKEN="40706bf2248f9dd7c495399049617560300aa3b02634dddd39114eab3c578988"
curl -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: $SOFI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "sofi-ceo",
    "project": "PRJ-SAKK",
    "command": "Report current gate status.",
    "priority": "low",
    "source": "n8n-test"
  }' | jq .
```

Expected response:
```json
{
  "success": true,
  "response": "...",
  "artifact": "...",
  "role": "sofi-ceo",
  "ts": "2026-07-04T20:19:00+03:00"
}
```

## n8n Workflow Template

### Template: Dispatch RCCF to Gateway

**Trigger:** HTTP webhook  
**Steps:**
1. **HTTP Request** node → `POST http://127.0.0.1:8099/dispatch`
2. Headers:
   - `X-SOFI-Token: {{ $credentials['sofiGatewayToken'].headerValue }}`
   - `Content-Type: application/json`
3. Body (JSON):
```json
{
  "role": "{{ $json.body.role }}",
  "project": "{{ $json.body.project || 'PRJ-SAKK' }}",
  "command": "{{ $json.body.command }}",
  "context": "{{ $json.body.context || '' }}",
  "priority": "{{ $json.body.priority || 'medium' }}",
  "source": "n8n-webhook",
  "trigger": "{{ $json.body.trigger || 'manual' }}"
}
```

### Standard Workflows (ready to import/build)

#### 01. Heartbeat (cron: every 6h)
```
Cron: 0 */6 * * *
  ↓
HTTP POST /dispatch { role:"sofi-ceo", command:"sofi gate-check PRJ-SAKK" }
  ↓
Parse result → Slack notification
```

#### 02. Git Watcher (webhook: GitHub push)
```
GitHub Push webhook (validate HMAC)
  ↓
White-list branch (main, prj/*)
  ↓
IF sha changed:
  ├─ HTTP dispatch: sofi sync
  └─ Slack: "ð SYNC {branch} → {sha}"
```

#### 03. Health Monitor (cron: every hour)
```
Cron: 0 * * * *
  ↓
HTTP GET checks (API, frontend, WebSocket)
  ↓
IF >1 failure: rollback alert + Slack ð¨
ELSE: Slack â
```

#### 04. Weekly Report (cron: Friday 17:00)
```
Cron: 0 17 * * 5
  ↓
HTTP dispatch: Kimi context writer
  ↓
HTTP dispatch: weekly report generator
  ↓
Save to docs/WEEKLY_REPORT_*.md + Slack
```

#### 05. Brain Backup (cron: hourly)
```
Cron: 0 * * * *
  ↓
HTTP dispatch: git add _context/ && commit "brain: auto-sync"
  ↓
Log result to audit trail
```

#### 06. Task Distributor (webhook: `/sofi-task`)
```
POST /sofi-task { role, command, project, ... }
  ↓
Validate token (X-SOFI-Task-Token)
  ↓
HTTP dispatch → parse result
  ↓
Update HANDOFFS.md via gateway
  ↓
Slack: "ð Task dispatched: {role}"
```

## Security Checklist

- ✅ Gateway token in `~/.sofi-run/gateway.env` (600 permissions)
- ✅ Gateway binds `127.0.0.1` only (no internet exposure)
- ✅ n8n credentials store token securely
- ✅ All dispatches logged to `.sofi-run/logs/sofi-gateway.log`
- ✅ Each request timestamped + role + source

## Debugging

### Gateway not responding?
```bash
systemctl --user status sofi-gateway.service
journalctl --user -u sofi-gateway.service -f
```

### n8n can't reach gateway?
```bash
# From n8n container/host:
curl -v http://127.0.0.1:8099/healthz

# Check firewall:
sudo ufw allow 8099/tcp  # if using UFW
```

### Test token auth:
```bash
# Without token (should 401):
curl -X POST http://127.0.0.1:8099/dispatch -d '{}'

# With token (should work):
curl -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" \
  -d '{"role":"sofi-ceo",...}'
```

## Workflow JSON Export/Import

Export from n8n UI:
1. Workflow → ⋮ → **Download**
2. Save to `sofi/server-plane/n8n/workflows/NN-workflow-name.json`

Import:
1. n8n UI → **Create new workflow**
2. ⋮ → **Import from file**
3. Select JSON

Version control:
```bash
cd sofi/server-plane/n8n/
git add workflows/*.json
git commit -m "feat(n8n): add heartbeat workflow"
```

## Next: WhatsApp Integration

(Coming next) Set up WhatsApp webhook → n8n → task dispatcher → agents → WhatsApp reply.

```
WhatsApp API webhook
  ↓
n8n: parse incoming message
  ↓
Route to gateway dispatcher
  ↓
Claude agent executes
  ↓
n8n: format reply
  ↓
Send to WhatsApp API
```

---

**Reference:** `sofi/tooling/bin/sofi-gateway-daemon.py` (6.1K)  
**Logs:** `~/.sofi-run/logs/sofi-gateway.log`  
**Monitoring:** `systemctl --user enable sofi-gateway.service` (auto-restart on failure)
