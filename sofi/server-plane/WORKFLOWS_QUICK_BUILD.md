# n8n Workflows — Quick Build Guide (11 more)

Already done: **01-heartbeat** (template provided)

Build the remaining 11 workflows **by copy-pasting these templates into n8n Code nodes.**

---

## Workflow 02: Git Watcher (GitHub Push)

**Trigger:** Webhook (GitHub push)

**Nodes:**

1. **GitHub Webhook** (incoming)
   - Path: `/github`
   - Headers: `x-hub-signature-256`

2. **Validate Signature** (Code)
   ```javascript
   const crypto = require('crypto');
   const sig = $input.headers['x-hub-signature-256'];
   const payload = JSON.stringify($input.body);
   const secret = $env.GITHUB_WEBHOOK_SECRET;
   
   const expected = 'sha256=' + crypto
     .createHmac('sha256', secret)
     .update(payload).digest('hex');
   
   if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) {
     throw new Error('Invalid signature');
   }
   return $input.body;
   ```

3. **Check Branch** (Switch node)
   - IF branch matches `main|prj/*`
   - AND sha != last seen (store in $global)

4. **HTTP Dispatch** (if changed)
   ```json
   {
     "role": "sofi-ceo",
     "command": "sofi sync {{ $json.repository.name }}",
     "priority": "high",
     "source": "github-push",
     "trigger": "{{ $json.ref }}"
   }
   ```

5. **Slack Notify**
   - ✅ Success: "ð SYNC {branch} → {sha[:7]}"
   - ⚠️ Error: "ð´ Sync failed: {error}"

---

## Workflow 03: Health Monitor (Cron 1h)

**Trigger:** Cron `0 * * * *` (hourly)

**Nodes:**

1. **Cron** (Asia/Riyadh)

2. **Parallel health checks** (multiple HTTP Request nodes):
   ```
   GET http://127.0.0.1:8099/healthz
   GET http://localhost:5678/api/health  (n8n)
   GET http://sakk.local/api/health      (SAKK API)
   GET http://sakk.local/admin/login     (admin login page)
   ```

3. **Aggregate Results** (Code)
   ```javascript
   const checks = $json;
   const failed = Object.entries(checks)
     .filter(([_, r]) => !r.success || r.status > 399);
   
   return {
     total: Object.keys(checks).length,
     failed: failed.length,
     failures: failed.map(([k, v]) => `${k}: ${v.status || v.error}`),
     healthy: failed.length === 0
   };
   ```

4. **IF Healthy?** (Switch)
   - YES → Slack "â OK" (green)
   - NO → Slack "ð¨ ALERT" (red) + escalate

5. **Escalate if critical** (HTTP dispatch)
   ```json
   {
     "role": "sofi-release-incident-manager",
     "command": "Incident: health check failed — {{ $json.failures.join(', ') }}",
     "priority": "critical",
     "source": "health-monitor"
   }
   ```

---

## Workflow 04: Kimi Context Writer (Cron daily 00:00)

**Trigger:** Cron `0 0 * * *` (midnight)

**Nodes:**

1. **Cron** (midnight)

2. **Read Brain Files** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Read STATE.md + CONTEXT.md + HANDOFFS.md from PRJ-SAKK, output summary",
     "project": "PRJ-SAKK",
     "priority": "low"
   }
   ```

3. **Summarize for Kimi** (Code)
   ```javascript
   const summary = $json.response || '';
   return {
     context_data: summary.substring(0, 4000),  // Truncate for Kimi
     timestamp: new Date().toISOString()
   };
   ```

4. **HTTP to Kimi API** (HTTP Request)
   ```
   POST https://api.moonshot.cn/v1/chat/completions
   
   Body:
   {
     "model": "moonshot-v1-128k",
     "messages": [
       { "role": "system", "content": "أنت كاتب سياقات محترف. اقرأ بيانات SOFI وأكتب نقطة واحدة عن أهم تطور اليوم (الإنجازات · المشاكل · القرارات)." },
       { "role": "user", "content": "{{ $json.context_data }}" }
     ],
     "temperature": 0.3,
     "max_tokens": 500
   }
   ```

5. **Append to CONTEXT.md** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Append to CONTEXT.md: '## Daily Summary ({{ date }})\\n{{ kimi_response }}' + commit 'brain: daily-kimi'",
     "priority": "low"
   }
   ```

6. **Slack confirmation**
   - "ð Kimi context updated"

---

## Workflow 05: Gate Check (Cron 12h)

**Trigger:** Cron `0 */12 * * *` (00:00, 12:00)

**Nodes:**

1. **Cron**

2. **HTTP Dispatch** (gate-check)
   ```json
   {
     "role": "sofi-ceo",
     "command": "sofi gate-check PRJ-SAKK",
     "priority": "medium"
   }
   ```

3. **Parse Result** (Code)
   ```javascript
   const resp = $json.response || '';
   const match = resp.match(/Gate (\d+)/);
   const gate = match ? parseInt(match[1]) : null;
   return {
     gate,
     blocked: resp.includes('blocker'),
     blockers_list: resp.match(/blocker: .+/g) || [],
     full_response: resp.substring(0, 1000)
   };
   ```

4. **IF Blocked?** (Switch)
   - YES → Slack "🔴 BLOCKER @ Gate {gate}" + escalate to team
   - NO → Slack "✅ Gate {gate} clear"

---

## Workflow 06: Task Distributor (Webhook `/sofi-task`)

**Trigger:** HTTP Webhook `/sofi-task`

**Nodes:**

1. **HTTP Webhook**
   - Method: POST
   - Path: `/sofi-task`

2. **Validate Token** (Code)
   ```javascript
   const token = $input.headers['x-sofi-task-token'];
   if (token !== $env.SOFI_TASK_TOKEN) {
     throw new Error('Unauthorized');
   }
   return $input.body;
   ```

3. **Route Command** (Switch)
   ```
   $json.command = ?
   
   case 'audit': → role='sofi-qa-sre-lead'
   case 'fix': → role='sofi-fix'
   case 'report': → role='sofi-tier-4-advisor'
   case 'feature': → role='sofi-feature'
   case 'review': → role='sofi-spec-review'
   default: → error 404
   ```

4. **Dispatch via Gateway** (HTTP)
   ```json
   {
     "role": "{{ $json.role }}",
     "command": "{{ $json.command_details }}",
     "project": "{{ $json.project || 'PRJ-SAKK' }}",
     "priority": "{{ $json.priority || 'medium' }}",
     "source": "n8n-task-webhook",
     "trigger": "{{ $json.trigger_id }}"
   }
   ```

5. **Update HANDOFFS.md** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Add to HANDOFFS.md: '## TASK: {{ $json.command }}\\nStatus: dispatched to {{ $json.role }}\\nTime: {{ timestamp }}' + commit",
     "priority": "low"
   }
   ```

6. **Return Result** (Webhook response)
   ```json
   {
     "success": {{ $json.success }},
     "response": "{{ $json.response }}",
     "ticket": "{{ $json.ticket_id }}"
   }
   ```

---

## Workflow 07: Brain Backup (Cron hourly)

**Trigger:** Cron `0 * * * *`

**Nodes:**

1. **Cron**

2. **Dispatch git commit** (HTTP)
   ```json
   {
     "role": "sofi-ceo",
     "command": "git add projects/*/\_context/ && git commit -m 'brain: auto-sync @ $(date)' || true",
     "priority": "low"
   }
   ```

3. **Log backup** (Code)
   ```javascript
   return {
     backup_timestamp: new Date().toISOString(),
     success: $json.success,
     message: $json.response
   };
   ```

4. **Store in audit log** (File write via gateway)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Append to ~/.sofi-run/logs/brain-backup.log: '{{ $json.backup_timestamp }} | {{ $json.message }}'",
     "priority": "low"
   }
   ```

---

## Workflow 08: Weekly Report (Cron Fri 17:00)

**Trigger:** Cron `0 17 * * 5` (Friday 5pm)

**Nodes:**

1. **Cron**

2. **Collect week data** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Summarize this week: commits, deploys, incidents, PRs merged. Output as JSON: {commits: N, deploys: N, incidents: [list], prs: N}",
     "priority": "low"
   }
   ```

3. **Kimi report generator** (HTTP Kimi API)
   ```
   Body:
   {
     "model": "moonshot-v1-128k",
     "messages": [
       { "role": "system", "content": "أنت مدير تقارير. أكتب تقرير أسبوعي احترافي: ## ðƒâ„† ملخص (الإنجازات · المشاكل) · ## ðƒâ„ Metrics · ## ðƒ¯ التوصيات (3-5 نقاط)." },
       { "role": "user", "content": "{{ $json.weekly_data }}" }
     ]
   }
   ```

4. **Save report** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Write docs/WEEKLY_REPORT_{{ week }}.md with content: {{ kimi_response }} + commit",
     "priority": "low"
   }
   ```

5. **Slack digest**
   - Post to #sofi-automation with report link

---

## Workflow 09: Uptime Monitor (Cron every 5m)

**Trigger:** Cron `*/5 * * * *`

**Nodes:**

1. **Cron**

2. **HTTP HEAD checks** (latency test)
   ```
   HEAD http://127.0.0.1:8099/healthz
   HEAD http://localhost:5678/api/health
   HEAD http://sakk.local/
   ```

3. **Measure latency** (Code)
   ```javascript
   const results = $json;
   return {
     checks: Object.entries(results).map(([svc, resp]) => ({
       service: svc,
       latency_ms: resp.responseTime,
       status: resp.statusCode,
       healthy: resp.statusCode < 400 && resp.responseTime < 2000
     }))
   };
   ```

4. **IF any latency > 2s?** (Switch)
   - YES → Slack warning (yellow)
   - NO → Slack OK (green)

5. **Log to Prometheus** (optional, HTTP POST)
   ```
   POST http://prometheus.local:9090/push/metrics
   
   sofi_uptime_check_latency_ms{service="gateway"} 42
   sofi_uptime_check_status{service="gateway"} 1
   ```

---

## Workflow 10: PR Auto-Reviewer (GitHub PR webhook + label check)

**Trigger:** Webhook (GitHub PR opened/synchronized) + label `auto-review`

**Nodes:**

1. **GitHub Webhook** (PR events)

2. **Check CI status** (GitHub API call)
   ```
   GET https://api.github.com/repos/[owner]/[repo]/commits/[sha]/check-runs
   ```

3. **IF CI failing?** (Switch)
   - YES → Comment "⏳ Waiting for CI" + stop
   - NO → Continue

4. **Git diff retriever** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "git diff origin/main...{{ $json.head.sha }} -- . ':!:(exclude)**/package-lock.json' ':!:vendor/**' ':!:pubspec.lock' ':!:**/*.g.dart' | head -3000",
     "priority": "medium"
   }
   ```

5. **Kimi code review** (HTTP Kimi API)
   ```
   {
     "model": "moonshot-v1-128k",
     "messages": [
       { "role": "system", "content": "You are a code reviewer. Find CRITICAL/HIGH bugs, security issues, logic errors. Format: SEVERITY: [description] → [file:line]" },
       { "role": "user", "content": "{{ $json.diff }}" }
     ]
   }
   ```

6. **Claude review** (HTTP dispatch)
   ```json
   {
     "role": "sofi-tier-2-advisor",
     "command": "Review this diff for code quality: {{ $json.diff }}",
     "priority": "medium"
   }
   ```

7. **Merge results** (Code)
   ```javascript
   const kimi = $json[0].response || '';
   const claude = $json[1].response || '';
   
   // Vote: both happy = approve & merge
   const canMerge = !kimi.includes('CRITICAL') && !claude.includes('CRITICAL');
   
   return {
     kimi_review: kimi.substring(0, 1000),
     claude_review: claude.substring(0, 1000),
     verdict: canMerge ? 'APPROVE_MERGE' : 'REQUEST_CHANGES'
   };
   ```

8. **GitHub action** (GitHub API call)
   ```
   IF verdict = APPROVE_MERGE:
     POST /reviews with "APPROVE"
     POST /merges with "squash"
   ELSE:
     POST /reviews with "REQUEST_CHANGES"
     POST /issues/{number}/labels with "blocked-review"
   ```

---

## Workflow 11: SOFI Sync (Cron every 3h)

**Trigger:** Cron `0 */3 * * *` (every 3 hours)

**Nodes:**

1. **Cron**

2. **Run sofi sync** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "sofi sync PRJ-SAKK",
     "priority": "low"
   }
   ```

3. **Update dashboard** (HTTP dispatch)
   ```json
   {
     "role": "sofi-ceo",
     "command": "Update STATE.md: head_sha, last_updated + commit",
     "priority": "low"
   }
   ```

4. **Slack notification**
   - "ð SOFI Sync: PRJ-SAKK @ {timestamp}"

---

## Workflow 12: Task Executor (optional, advanced)

**Trigger:** Webhook `/execute-task`

Similar to #06 but with:
- Higher timeout (600s)
- Artifact capture to `~/.sofi-run/artifacts/`
- Progress updates to Slack thread
- Auto-checkpoint after execution

---

## Building All 11 at Once

**Copy-paste strategy:**

1. Export **01-heartbeat** from n8n
2. **Search-replace:**
   - `"name": "01-Heartbeat"` → `"name": "02-Git Watcher"`
   - Update nodes per templates above
   - Update credentials (Slack, GitHub, etc.)
3. **Import** to n8n
4. **Test** each one
5. **Export** → save to `sofi/server-plane/n8n/workflows/NN-name.json`
6. **Commit** all 12 to git

**Estimated time:** 2h for all 11 (test + debug)

---

## Credentials to Set Up

Before importing workflows, create in n8n:

- **SOFI Gateway Token** (HTTP Header Auth)
- **Slack Webhook URL** (HTTP)
- **GitHub Token** (Credentials)
- **GitHub Webhook Secret** (env var)
- **Kimi API Key** (HTTP Header Auth)
- **Twilio** (optional, if WhatsApp)

---

**Next:** Import templates, test one, go live! 🚀
