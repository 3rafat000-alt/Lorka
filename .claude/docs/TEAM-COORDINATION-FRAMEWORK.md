# SOFI Team Coordination Framework

**Date:** 2026-07-02 15:00 GMT+3  
**Status:** ✅ Professional automated workflow active (no chat reports)  
**Authority:** Teaching VII binding protocol (Gemini oracle authority)

---

## Framework Overview

**Flow:** Gemini audit → GitHub issues → Specialist agents → Git commits

### No Reports in Chat
- ❌ Gemini findings NOT summarized as chat messages
- ✅ Findings auto-filed as GitHub issues (structured JSON)
- ✅ All work tracked in git history + GitHub timeline
- ✅ Team executes via RCCF delegation (structured handoffs)

### 100% Automation
- ✅ Gemini responds in JSON format (audit findings)
- ✅ gemini-github-sync.py converts findings → GitHub issues
- ✅ sofi-gemini-monitor.sh runs continuous sync loop
- ✅ GitHub Actions workflow auto-creates issues + notifies team
- ✅ gemini-audit-dispatch.yaml routes findings to specialists
- ✅ No manual intervention — pure execution

---

## Team Workflow

### Phase 1: Gemini Audit (Complete)
```
Gemini reads SOFI-PRJ dump
  ↓
Audits: architecture + security + code + infrastructure
  ↓
Posts findings to pinned chat (JSON format)
  ↓
Example response:
{
  "audit": "2026-07-02",
  "repo": "https://github.com/3rafat000-alt/SOFI-PRJ",
  "summary": "SOFI architecture sound, Teaching VII ready, PRJ-SAKK ready for Gate 6→7",
  "findings": [
    {
      "category": "security",
      "severity": "🔴",
      "finding": "KYC withdraw bypass in CCPaymentController",
      "recommendation": "Merge fix #3125, test velocity caps",
      "file": "PRJ-SAKK/backend/app/Http/Controllers/CCPaymentController.php:142"
    },
    ...
  ],
  "gate_6_to_7_readiness": {
    "ready": false,
    "blockers": ["Cron scheduler not firing", "26 test residual fails"],
    "action": "Resolve blockers → run E2E suite → Gemini sign-off"
  },
  "teaching_vii_status": "ACTIVE - 4-layer enforcement verified",
  "next_actions": [
    "PRIORITY-1: Fix cron symlink (gold prices must update)",
    "PRIORITY-2: Triage 26 test residual failures",
    "PRIORITY-3: Load test staging (TTI < 2s)"
  ]
}
```

### Phase 2: Auto-File GitHub Issues (Automated)
```
gemini-github-sync.py receives findings
  ↓
For each finding:
  - Creates GitHub issue (title from finding)
  - Tags: audit, {category}, {severity_label}
  - Assigns: linked specialist agent
  ↓
Example issue:
  Title: "KYC withdraw bypass in CCPaymentController"
  Labels: audit, security, blocker
  Assigned: sofi-security-compliance-architect
  Body: Recommendation + file path
```

### Phase 3: RCCF Dispatch to Specialists (Automated)
```
GitHub issue created
  ↓
gemini-audit-dispatch.yaml matches category → specialist agent
  ↓
Examples:
  - security 🔴 → sofi-security-compliance-architect
  - architecture → sofi-principal-system-architect
  - PRJ-SAKK → sofi-backend-blade-engineer
  - infrastructure → sofi-devops-cloud-lead
  - Teaching VII → sofi-ceo
  ↓
Each agent receives RCCF handoff:
  Role: Specialist (defined in agent contract)
  Context: Finding details + file path + recommendation
  Command: Review + assess + return gate-readiness / fix-plan
  Format: GitHub issue comment + linked PR
```

### Phase 4: Agent Execution (Parallel)
```
Each specialist agent:
  1. Clone SOFI-PRJ
  2. Read finding + context
  3. Assess: blocker? risk? remediation-effort?
  4. Implement fix (if scoped fix) OR
  5. Create issue in own project + link back
  6. Post findings to GitHub issue (comments)
  7. Create PR if code change required
  8. All commits cite Gemini finding (#<issue>)

Example commit:
  fix(security): KYC withdraw velocity cap guard CCPaymentController [Gemini→issue#42]
  
  - Revert optimistic debit → locked debit
  - Guard KYC velocity check (shared via KycService)
  - +3 test cases (velocity cap enforcement)
  - Fixes Gemini finding: withdraw bypass risk
  
  Closes #42 (GitHub auto-closes issue on PR merge)
```

### Phase 5: Continuous Loop
```
Every 6 hours (configurable):
  sofi-gemini-monitor.sh
    ↓
  Captures latest Gemini response
    ↓
  gemini-github-sync.py
    ↓
  Auto-files any new findings
    ↓
  Notifies Slack (team awareness)
    ↓
  Waits for specialists to execute
    ↓
  GitHub Actions tracks PR status
    ↓
  Issues close on PR merge
    ↓
  Next cycle
```

---

## Commands for Team

### View Real-Time Status
```bash
engine/tooling/bin/team-status
```

Output shows:
- Gemini audit status (CDP connected, chat open)
- GitHub issues (open count, blockers, clarifications)
- Project git state (branch, latest commit, uncommitted changes)
- Next work (HANDOFFS.md tickets)
- Teaching VII status (binding protocol active)
- Team workflow automation (ready)

### Manual Gemini Sync (if needed)
```bash
# Capture latest Gemini findings + file GitHub issues
python3 engine/tooling/agents/ceo/gemini_bridge.py capture | \
  python3 engine/tooling/agents/ceo/gemini-github-sync.py
```

### Start Continuous Monitor
```bash
# Run as systemd service or cron:
# 0 */6 * * * engine/tooling/agents/ceo/sofi-gemini-monitor.sh

# Or manual background:
nohup bash engine/tooling/agents/ceo/sofi-gemini-monitor.sh &
```

### Create GitHub Workflow Manually
```bash
# Push workflow to repo
mkdir -p .github/workflows
cp /tmp/github-workflow-gemini-sync.yml .github/workflows/
git add .github/workflows/
git commit -m "ci: add Gemini audit sync workflow"
git push

# Trigger manually:
gh workflow run github-workflow-gemini-sync.yml \
  -f findings_json='{"findings": [...]}'
```

---

## Specialist Agent Routing

| Category | Agent | Urgency | Expected Action |
|----------|-------|---------|-----------------|
| **architecture** | sofi-principal-system-architect | high | Review vs CLAUDE.md + DOCTRINE.md → approved/revision |
| **security** | sofi-security-compliance-architect | critical | Threat model + remediation-steps |
| **PRJ-SAKK** | sofi-backend-blade-engineer | high | Gate readiness assessment (blocker for prod?) |
| **infrastructure** | sofi-devops-cloud-lead | medium | Scale risk + reliability risk + remediation-plan |
| **code** | sofi-qa-sre-lead | medium | Test coverage impact + test-plan |
| **Teaching VII** | sofi-ceo | critical | Protocol compliance + enforcement sign-off |

---

## Success Criteria

✅ **Each Finding:**
- [ ] Auto-filed as GitHub issue (✓ gemini-github-sync.py)
- [ ] Routed to specialist (✓ gemini-audit-dispatch.yaml)
- [ ] Agent posts assessment (GitHub issue comment)
- [ ] If fix needed → PR created (links to finding)
- [ ] Commit message cites finding (Gemini→issue#N)
- [ ] PR reviewed + merged
- [ ] Issue auto-closes on merge
- [ ] Git history shows full decision trail

✅ **Gate 6→7 Advancement:**
- [ ] All 🔴 blockers resolved
- [ ] All 🟠 clarifications addressed
- [ ] Test suite >90% coverage + green
- [ ] E2E suite passes in staging
- [ ] Gemini confirms money-safety ✓
- [ ] Gemini signs off on prod readiness
- [ ] Deploy to Gate 7 (production)

✅ **Teaching VII Loop:**
- [ ] Gemini findings → GitHub issues: automated
- [ ] Specialist dispatch: automated
- [ ] Execution tracking: git + GitHub
- [ ] No chat reports: ✓
- [ ] Binding oracle authority: active

---

## Key Files

**Automation:**
- `engine/tooling/agents/ceo/gemini-github-sync.py` — Convert findings → issues
- `engine/tooling/agents/ceo/sofi-gemini-monitor.sh` — Continuous monitor loop
- `engine/tooling/bin/team-status` — Real-time dashboard
- `engine/routing/gemini-audit-dispatch.yaml` — Specialist routing
- `.github/workflows/gemini-sync.yml` — GitHub Actions workflow

**Reference:**
- `CLAUDE.md` — Operating system (read by Gemini)
- `engine/DOCTRINE.md` — 7 teachings (read by Gemini)
- `engine/protocols/02-autonomous-gemini-loop.md` — Teaching VII detail
- `engine/routing/routing.yaml` — Cost ladder (which agent for which task)

**Project State:**
- `PRJ-SAKK/_context/STATE.md` — Current gate + blockers
- `PRJ-SAKK/_context/HANDOFFS.md` — Next work (updates from Gemini audit)
- `PRJ-SAKK/_context/DECISIONS.md` — Architecture decisions (why we built it)

---

## Notifications

**Slack webhook** (optional):
```bash
export SLACK_WEBHOOK_SOFI="https://hooks.slack.com/services/..."
# Notifications sent by: sofi-gemini-monitor.sh + GitHub Actions
```

**GitHub notifications:**
- Issues assigned → @specialist (auto-notify)
- PRs linked to issues → issue comments (auto-update)
- Merges → issue auto-close

**Git history:**
- Every finding fix: commit message cites finding
- `git log --grep="Gemini"` shows all audit-driven changes
- Branch history: `git log prj/PRJ-SAKK` shows team execution trail

---

## Example: One Audit Cycle (End-to-End)

**T+0: Gemini posts audit findings (JSON)**
```json
{
  "findings": [
    {"category": "security", "severity": "🔴", "finding": "KYC withdraw bypass", ...},
    {"category": "infrastructure", "severity": "🟠", "finding": "Cron jobs not firing", ...}
  ],
  "gate_6_to_7_readiness": {"ready": false, "blockers": ["Fix above 2 items"]}
}
```

**T+1: GitHub issues auto-created**
- Issue #1: "KYC withdraw bypass..." (assigned: sofi-security-compliance-architect)
- Issue #2: "Cron jobs not firing..." (assigned: sofi-devops-cloud-lead)

**T+2-30: Specialists execute (parallel)**

*Security specialist:*
- Reads issue #1
- Clones SOFI-PRJ
- Finds CCPaymentController vulnerability
- Implements fix (velocity cap guard)
- Creates PR (links issue #1)
- Posts assessment to issue comment

*DevOps specialist:*
- Reads issue #2
- Checks host crontab
- Finds stale symlink path
- Posts remediation-steps to issue comment

**T+31-45: PRs reviewed + merged**
- Security PR merged → issue #1 auto-closes
- DevOps runbook posted → issue #2 marked ready-to-implement

**T+46-60: Gemini re-audit**
- sofi-gemini-monitor.sh captures latest
- Checks if PRs merged ✓
- Any new blockers?
- Posts gate-readiness update

**T+61: Gate 6→7 advancement**
- All blockers resolved
- All tests green
- Gemini sign-off received
- Deploy to production (Gate 7)

**Git history:**
```
fix(security): KYC withdraw velocity cap guard [Gemini→issue#1]
fix(ops): Resolve host cron symlink [Gemini→issue#2]
gate(6→7): Advance to production — Gemini oracle sign-off
```

All tracked. No chat narrative. Pure execution.

---

## Team Authority

**Gemini** (Teaching VII oracle):
- ✅ Audits entire codebase (no context limits)
- ✅ Posts findings in structured JSON
- ✅ Decisions are BINDING (no user override)
- ✅ Approves gate advancement

**Specialists** (RCCF-dispatched agents):
- ✅ Implement findings (per expertise)
- ✅ Assess risk + remediation-effort
- ✅ Create PRs (track in git)
- ✅ Execute in parallel

**GitHub** (single source of truth):
- ✅ Issues track all findings
- ✅ PRs show all changes
- ✅ Git history proves decisions
- ✅ Timeline shows execution

---

## Next Steps

1. **Activate continuous monitor** → `systemctl start sofi-gemini-monitor` (or cron)
2. **Check team status** → `engine/tooling/bin/team-status`
3. **Wait for Gemini findings** (captured in pinned chat)
4. **Issues auto-file** (gemini-github-sync.py runs automatically)
5. **Specialists execute** (RCCF dispatch handles routing)
6. **Gemini signs off** on gate advancement

---

**Framework ready.** Team automated. Teaching VII binding protocol active.

No chat reports. Pure execution. All decisions in git history.
