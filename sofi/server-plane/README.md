# SOFI Server-Plane Orchestration

**n8n + Gateway Daemon + Claude Agents = 24/7 Autonomous Automation**

> Your WhatsApp message → n8n picks it up → routes to SOFI agents → results come back. No manual intervention.

---

## Status

✅ **Gateway Daemon:** Running on `127.0.0.1:8099` (systemd: `sofi-gateway.service`)  
📋 **n8n:** Ready to configure (local or Docker)  
🎯 **Workflows:** 12 templates ready (heartbeat, git-watcher, health-monitor, task-distributor, etc.)  
🔒 **Security:** Token-based auth, localhost-only binding, full audit trail

---

## What This Does

| Feature | What | How | When |
|---------|------|-----|------|
| **Heartbeat** | Gate status check | Cron every 6h | Automated health check |
| **Git Watcher** | Syncs from GitHub | Webhook on push | Real-time code updates |
| **Health Monitor** | API/frontend uptime | Cron every 1h | Detects failures early |
| **Task Distributor** | Routes WhatsApp/Slack commands | Webhook `/sofi-task` | User messages trigger agents |
| **Brain Backup** | Auto-commits state | Cron hourly | Never lose context |
| **Weekly Report** | Kimi-powered summary | Cron Friday 17:00 | Leadership visibility |
| **PR Auto-Reviewer** | Diffs via Claude | Webhook on PR | Code quality gate |
| **Uptime Monitor** | Latency tracking | Cron every 5m | SRE visibility |

---

## Quick Start (5 minutes)

### 1. Gateway already running
```bash
curl http://127.0.0.1:8099/healthz
# Output: {"status":"ok","service":"sofi-gateway"}
```

### 2. Install n8n (if not already)
```bash
# Option A: NPM
npm install -g n8n
n8n start

# Option B: Docker (recommended)
cd sofi/server-plane/n8n
docker compose up -d
```

### 3. Configure n8n credential
- Open http://localhost:5678
- **Credentials** → **Create new** → **HTTP Header Auth**
- **Header name:** `X-SOFI-Token`
- **Header value:** `40706bf2248f9dd7c495399049617560300aa3b02634dddd39114eab3c578988`
- **Save**

### 4. Test dispatch
```bash
curl -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: 40706bf2248f9dd7c495399049617560300aa3b02634dddd39114eab3c578988" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "sofi-ceo",
    "command": "sofi gate-check PRJ-SAKK",
    "priority": "low"
  }' | jq .
```

Expected: `{"success":true, "response":"...", ...}`

---

## Installation

### Prerequisites
- Linux (tested: Ubuntu 22.04+, Fedora 39+)
- Python 3.10+
- Claude Code CLI (`claude` in PATH)
- n8n (npm or Docker)
- `systemd --user` support

### Setup Steps

#### 1. Gateway Daemon (already done)
```bash
# Binary ready at:
# /home/es3dlll/Desktop/Lorka/sofi/tooling/bin/sofi-gateway-daemon.py

# Service installed at:
# ~/.config/systemd/user/sofi-gateway.service

# Token stored at:
# ~/.sofi-run/gateway.env

# Verify running:
systemctl --user status sofi-gateway.service
journalctl --user -u sofi-gateway.service -f
```

#### 2. n8n Setup

**Docker (recommended):**
```bash
cd sofi/server-plane/n8n
cp .env.example .env
# Edit .env: set N8N_DB_PASSWORD, N8N_ENCRYPTION_KEY
docker compose up -d

# Access: http://localhost:5678 (or n8n.local if Caddy configured)
```

**NPM:**
```bash
npm install -g n8n
# Set environment variables:
export N8N_DB_TYPE=postgres
export N8N_DB_HOST=localhost
export N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)
n8n start
```

#### 3. Workflows

**Option A: Import JSON (quickest)**
1. n8n UI → **Create new workflow**
2. ⋮ → **Import from file**
3. Select `sofi/server-plane/01-heartbeat-workflow.json`
4. Edit environment variables (Slack webhook, etc.)
5. **Save & activate**

**Option B: Build manually**
Follow templates in [N8N_SETUP.md](./N8N_SETUP.md) (section "Standard Workflows")

#### 4. Environment Variables

Create `~/.sofi-run/n8n.env` (or set in docker-compose.yml):
```bash
# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/HERE
SLACK_CHANNEL=#sofi-automation

# GitHub (optional)
GITHUB_TOKEN=ghp_xxxxxxxxx
GITHUB_WEBHOOK_SECRET=$(openssl rand -hex 32)

# Twilio / WhatsApp (optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+1234567890
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Your Machine (localhost)               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐        ┌──────────────────────┐   │
│  │ n8n Workflows    │        │ SOFI Gateway Daemon  │   │
│  │ (5678)           │───────▶│ (127.0.0.1:8099)     │   │
│  │                  │ HTTP   │                      │   │
│  │ • Heartbeat      │ POST   │ • RCCF builder       │   │
│  │ • Git watcher    │ /disp  │ • Claude spawner     │   │
│  │ • Health monitor │        │ • Audit logging      │   │
│  │ • Task router    │        │ • Token auth         │   │
│  │ • ...12 total    │        └──────────┬───────────┘   │
│  └──────────────────┘                   │                │
│                                         │ Claude -p RCCF │
│                                         ▼                │
│                                    ┌─────────────┐       │
│                                    │ Claude Code │       │
│                                    │ CLI         │       │
│                                    │ + agents    │       │
│                                    └─────────────┘       │
│                                                          │
│  ┌──────────────────┐                                    │
│  │ PostgreSQL (if   │                                    │
│  │ Docker)          │                                    │
│  │ (5432)           │                                    │
│  └──────────────────┘                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
         │
         │ webhook/events
         ▼
   ┌──────────────┐
   │ GitHub       │  (push webhook)
   │ Slack        │  (slash commands)
   │ WhatsApp API │  (incoming messages)
   │ Cron events  │  (scheduled)
   └──────────────┘
```

---

## Files

```
sofi/server-plane/
├── README.md                       ← You are here
├── N8N_SETUP.md                   ← Quick start guide
├── N8N_WHATSAPP_AUTOMATION.md     ← Full WhatsApp integration
├── 01-heartbeat-workflow.json     ← Example workflow (gate check)
│
├── n8n/  (if using Docker)
│   ├── docker-compose.yml         ← n8n + PostgreSQL
│   ├── .env.example               ← Configuration template
│   ├── .env                       ← (gitignored) secrets
│   ├── Caddyfile                  ← Reverse proxy config
│   └── workflows/
│       ├── 01-heartbeat.json
│       ├── 02-git-watcher.json
│       ├── 03-kimi-context.json
│       ├── ...
│       └── 12-sofi-sync.json
│
└── sofi/tooling/bin/
    └── sofi-gateway-daemon.py     ← Gateway (HTTP server)
```

---

## Operations

### Monitor Services

**Gateway:**
```bash
systemctl --user status sofi-gateway.service
journalctl --user -u sofi-gateway.service -f
```

**n8n (Docker):**
```bash
docker compose -f sofi/server-plane/n8n/docker-compose.yml logs -f n8n
```

**n8n (npm):**
```bash
# Logs printed to stdout
ps aux | grep n8n
```

### View Audit Logs

```bash
# Gateway dispatch log
tail -50f ~/.sofi-run/logs/sofi-gateway.log

# n8n execution history
# (in UI: Executions tab)
```

### Restart Services

```bash
# Gateway
systemctl --user restart sofi-gateway.service

# n8n (Docker)
docker compose -f sofi/server-plane/n8n/docker-compose.yml restart n8n

# n8n (npm)
# Kill process, restart
```

### Health Check

```bash
# All green?
curl http://127.0.0.1:8099/healthz && echo "✅ Gateway OK"
curl http://localhost:5678/api/health && echo "✅ n8n OK"
```

---

## Security

### Token Management

**Gateway token:**
- Stored: `~/.sofi-run/gateway.env` (chmod 600)
- Used by: All n8n workflows (via HTTP Header Auth credential)
- Rotation: Monthly (run `openssl rand -hex 32 > ~/.sofi-run/gateway-token`)

**Webhook secrets:**
- GitHub: `GITHUB_WEBHOOK_SECRET` (env var)
- Twilio: Signature validation in n8n Code node
- Custom: HTTP Header `X-SOFI-Webhook-Signature`

### Access Control

- ✅ Gateway binds `127.0.0.1` only (no internet exposure)
- ✅ n8n runs on `localhost:5678` or behind Caddy auth
- ✅ All dispatch requests logged (role, source, timestamp)
- ✅ Claude runs under user `es3dlll` (not root)

### Audit Trail

Every dispatch logged with:
```json
{
  "timestamp": "2026-07-04T20:19:00+03:00",
  "role": "sofi-ceo",
  "source": "n8n-heartbeat",
  "command": "sofi gate-check",
  "status": "success",
  "duration_ms": 4523
}
```

Searchable in:
```bash
grep "role=sofi-ceo" ~/.sofi-run/logs/sofi-gateway.log
```

---

## Scaling

### Add New Workflow

1. Design trigger + steps in n8n UI
2. **Export workflow** → Save to `sofi/server-plane/n8n/workflows/NN-name.json`
3. **Commit to git:** `git add workflows/ && git commit`
4. **Version control:** Workflows auto-sync via git-watcher

### Add New Agent

1. Create `.claude/agents/sofi-<name>.md` (RCCF spec)
2. Add to gateway routing (update `resolve_agent()` in daemon)
3. Add to n8n task-router (workflow: 06-task-distributor)
4. Test: `curl -X POST http://127.0.0.1:8099/dispatch ...`

### Performance Tuning

**Gateway:**
- Timeout: 300s (5m) — adjust in `sofi-gateway-daemon.py`
- Concurrency: ThreadingHTTPServer (Python's built-in)
- Max requests: Unlimited (systemd will restart on OOM)

**n8n:**
- Max executions: Docker memory limit (default: 2GB)
- Queue workers: Single threaded (scale horizontally if needed)
- DB: PostgreSQL (scales better than SQLite)

---

## Troubleshooting

### "Cannot connect to gateway"
```bash
# Is daemon running?
systemctl --user is-active sofi-gateway.service

# Is it listening?
netstat -tln | grep 8099

# Port conflict?
lsof -i :8099
```

### "401 Unauthorized"
```bash
# Check token
cat ~/.sofi-run/gateway.env

# Is n8n credential saved?
# (n8n UI → Credentials → SOFI Gateway Token)

# Test manually
curl -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" \
  http://127.0.0.1:8099/healthz
```

### "claude: command not found"
```bash
# Is Claude CLI in PATH?
which claude

# If not, add to ~/.bashrc
export PATH="/path/to/claude/bin:$PATH"

# Reload daemon
systemctl --user restart sofi-gateway.service
```

### "Dispatch timeout"
```bash
# Check logs
journalctl --user -u sofi-gateway.service | grep timeout

# Increase timeout in daemon.py (line ~26):
# TIMEOUT = 600  # 10m instead of 5m

# Restart
systemctl --user restart sofi-gateway.service
```

### n8n stuck / hung process
```bash
# Kill n8n
pkill -f "node.*n8n"  # if npm
docker kill n8n       # if Docker

# Restart
systemctl --user restart n8n.service
# or: docker compose up -d
```

---

## Integration Points

### Incoming Webhooks

| Source | Path | Format |
|--------|------|--------|
| GitHub | `/n8n/webhook/github` | Push events, PR events |
| Slack | `/n8n/webhook/slack` | Slash commands |
| WhatsApp | `/n8n/webhook/whatsapp` | Incoming messages (Twilio) |
| Custom | `/sofi-task` | JSON RCCF payload |

### Outgoing APIs

| Destination | Use | Auth |
|-------------|-----|------|
| SOFI Gateway | Dispatch agents | `X-SOFI-Token` |
| Slack | Notifications | Webhook URL |
| GitHub | Comments / status | Token in env |
| WhatsApp | Replies | Twilio credentials |

---

## Examples

### Dispatch "audit" (manual)
```bash
curl -X POST http://127.0.0.1:8099/dispatch \
  -H "X-SOFI-Token: $(cat ~/.sofi-run/gateway-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "sofi-qa-sre-lead",
    "command": "sofi audit PRJ-SAKK layer=ui",
    "priority": "high",
    "source": "manual-test"
  }' | jq '.response'
```

### Trigger heartbeat workflow (n8n UI)
1. Open workflow: **01-Heartbeat Gate Check**
2. Click ▶️ **Execute Workflow**
3. Check execution log

### View last 10 dispatches
```bash
tail -10 ~/.sofi-run/logs/sofi-gateway.log | jq .
```

---

## Support

- **Gateway issues:** `journalctl --user -u sofi-gateway.service -f`
- **n8n issues:** Check n8n execution logs (UI) or Docker logs
- **Agent issues:** `claude -p "{{ RCCF block }}" --verbose`
- **Integration issues:** Check webhook validation in n8n Code nodes

---

## Next Steps

1. ✅ **Gateway running** — already done
2. 📦 **Install n8n** — follow [N8N_SETUP.md](./N8N_SETUP.md)
3. 🔌 **Configure webhooks** — GitHub, Slack, WhatsApp
4. 🚀 **Activate workflows** — one by one (test each)
5. 📊 **Monitor 24/7** — health-monitor workflow + alerts
6. 🔄 **Iterate** — add new workflows, agents, integrations

---

**Questions?** Check `N8N_SETUP.md` or `N8N_WHATSAPP_AUTOMATION.md` for detailed walkthrough.

**Go live:** Your 24/7 autonomous agent is ready. Activate workflows, test one message on WhatsApp, and watch it work! 🚀

---

**Created:** 2026-07-04  
**Status:** ✅ Gateway + templates ready  
**Owner:** devops-cloud-lead / sofi-ceo
