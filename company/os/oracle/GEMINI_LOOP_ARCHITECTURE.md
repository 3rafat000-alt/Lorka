# Autonomous Gemini Loop — System Architecture

> **For:** Project leads, team members, CEO. **Purpose:** Understand how the team works end-to-end with Gemini as the decision engine.
> 
> **Binding as of:** 2026-07-02. Authority: DOCTRINE.md Teaching VII.

---

## System Overview

**Before (old, banned):**
```
Agent: "Here's a finding."
User: "What should we do?"
Agent: "I think A or B."
User: "Try A."
Agent: "Done. What next?"
User: "Move to next task."
```
❌ Sequential back-and-forth. Slow. User is a bottleneck.

**After (new, binding):**
```
Agent: "Pushing finding to desk…" → [offline]
       Gemini: "Do X (priority), then Y (reason: Z), expect outcome W."
Agent: "Executing X…" → [done] → "Executing Y…" → [done]
Agent: "Committed. Status: converged."
User: Reads status. Observes. No questions.
```
✅ Parallel agent+Gemini work. Fast. User is observer.

---

## The 4-Layer Stack

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: AGENT BEHAVIOR (SOFI agents, every spawn)              │
│ - Read AGENT_BRIEFING.md at spawn                               │
│ - Follow work loop: work → route → execute → commit → loop      │
│ - Never ask user for decisions (always → Gemini)                │
│ - Push findings inline via sofi gemini review                   │
│ - Checkpoint after each major sub-task                          │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: GEMINI ROUTING (Python tooling)                        │
│ - engine/tooling/agents/ceo/gemini_review.py                      │
│   ├─ Sanitize (redact secrets before send)                      │
│   ├─ Condense (if >6k chars, drop code, keep signal)            │
│   ├─ Push (send report + standing preamble to desk)             │
│   ├─ Capture (receive reply, resilient on timeout)              │
│   ├─ Parse (extract action items, severity, steps)              │
│   └─ Ingest (append digest to HANDOFFS.md)                      │
│ - Outputs: JSON with action_items, or .md with digest           │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: GEMINI BRIDGE (Playwright automation)                  │
│ - engine/tooling/agents/ceo/gemini_bridge.py                      │
│ - Attaches to browser (--remote-debugging-port=9222)            │
│ - Navigates to pinned Gemini chat                               │
│ - Sends message (push)                                          │
│ - Waits for reply (capture) with timeout handling               │
│ - Never touches cookies or UI; pure CDP protocol                │
│ - Retries on network fail (up to MAX_RETRIES)                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: EXTERNAL ORACLE (Gemini AI)                            │
│ - Pinned chat (config: ~/.engine/gemini_bridge.json)              │
│ - Receives: [standing framing] + [agent finding] + [question]   │
│ - Standing framing: "advising autonomous AI, not human"         │
│   → Gemini knows to reply with steps, not prose                 │
│ - Replies with: priorities, explanations, action steps          │
│ - Ingested back → agent executes → loops until converged        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow (round-trip example)

```
1. AGENT WRITES FINDING
   ├─ Audit completes
   ├─ 3 test failures, root cause unclear
   └─ Composes inline: "Failed 3× on db:migrate. Tried X, Y, Z. Logs show E. What's happening?"

2. AGENT ROUTES TO GEMINI
   └─ sofi gemini review --prj PRJ-SAKK --json \
        --text "migration fails 3×…" \
        --ask "Why? How to fix?"

3. GEMINI_REVIEW.PY PROCESSES
   ├─ Sanitize: redact any secrets in logs
   ├─ Condense: truncate if >6k chars
   ├─ Prepend standing preamble
   └─ Push to bridge (offline)

4. GEMINI_BRIDGE.PY SENDS
   ├─ Connect to browser (9222)
   ├─ Navigate to pinned chat URL
   ├─ Inject message (full report + question)
   └─ Wait for reply (300s timeout)

5. GEMINI RECEIVES & REPLIES
   ├─ Sees preamble: "advising AI agent"
   ├─ Analyzes: logs + context
   └─ Replies with:
       [SEV-🔴] Root cause: fk_constraint_violation on users table
       [Reason] Migration tries to drop column before removing fk.
       [Fix steps]
         1. Modify migration: drop fk first (reversible w/ rollback)
         2. Then drop column
         3. Test on staging DB (use backup for safety)
       [Outcome] Migration will succeed; rollback is reversible.

6. GEMINI_REVIEW.PY CAPTURES & PARSES
   ├─ Receive reply (captured via CDP)
   ├─ Parse sections + action items
   ├─ Generate JSON:
       {
         "action_items": [
           { "sev": "🔴", "title": "Root cause…", "steps": […] },
           { "sev": "🟡", "title": "Fix…", "steps": […] },
           …
         ]
       }
   └─ Append digest to HANDOFFS.md (git-ready)

7. AGENT EXECUTES
   ├─ Read action_items JSON
   ├─ For each item:
   │  ├─ Execute step 1 (modify migration)
   │  ├─ Commit (cite decision source)
   │  ├─ Execute step 2 (test on staging)
   │  └─ Commit (cite decision source)
   └─ Done. No user ask.

8. AGENT REPORTS STATUS TO USER
   └─ "[status] Migration root cause: fk constraint. Fixed per Gemini guidance. Tests pass. Committed."

9. USER OBSERVES
   └─ Reads status. Optionally reads HANDOFFS.md digest. Moves on.
```

---

## Standing Preamble (why it matters)

**What we send Gemini:**

```
[سياق ثابت — اقرأه أولاً] 
أنت مستشار معماري تُوجّه وكيل ذكاء اصطناعي ذاتي التشغيل (SOFI AI)، 
لستَ تخاطب إنساناً. الوكيل سينفّذ توجيهك مباشرةً وبلا وسيط بشري.

لذلك: أعطِ توجيهاً مفصّلاً ودقيقاً وقابلاً للتنفيذ خطوة بخطوة، 
لكل توصية سبب + أثر متوقّع + خطوة تنفيذ ملموسة، مرتّباً بالأولوية. 
تجنّب العموميات؛ الوكيل يحتاج أوامر عمل لا نصائح عامة.

[الآن السؤال الفعلي:]
<agent finding + context>
```

**Why this works:**
- Gemini knows it's advising AI, not a human who needs explanation.
- Replies are prioritized, actionable steps, not discussions.
- No hedging ("you might try…"), only directives ("do A, then B, expect C").
- Agent can parse and execute without re-routing.

---

## Decision Routing Matrix (when to push)

```
SITUATION                              ROUTE TO GEMINI?   WHY
─────────────────────────────────────────────────────────────────
Test passes, spec says do X            ❌ No              Frozen. Just do it.
Test fails, root cause unknown         ✅ Yes             "Why?" "Fix?"
Multiple paths, unclear winner         ✅ Yes             "Which? Priority? Justify?"
Estimate exceeds budget                ✅ Yes             "Cut scope? Extend? Redesign?"
Prior gate incomplete                  ✅ Yes             "Unblock path?"
Integration spec ambiguous             ✅ Yes             "Reconcile?"
Before git reset/table drop            ✅ Yes             "Should I? Why reversible?"
Mechanical: typo, rename, format       ❌ No              Just fix it.
Schema flaw found in audit             ✅ Yes             "Severity? Fix priority?"
Test timeout on CI (retry 3× passes)   ✅ Yes             "Flaky? Real? Diagnose?"
```

---

## Project Brain Integration

Every Gemini reply is automatically ingested into the project brain:

```
projects/PRJ-SAKK/
  _context/
    ├─ HANDOFFS.md          ← appended with Gemini digest + action items
    ├─ CONTEXT.md           ← updated with any new facts/decisions
    ├─ STATE.md             ← head_sha updated after each commit
    └─ reports/
       └─ gemini-reply-<topic>-<timestamp>.md  ← full reply saved

Each commit cites decision:
  git commit -m "fix: migration fk constraint

  Root cause + fix path from Gemini review <date>.
  PR: <PR#> | GATE: <gate>"
```

---

## Escape Hatches (when NOT to route)

**Destructive act?** Push to Gemini first ("should I X?"), then act + document in ADR.

```bash
# WRONG: just do it
git reset --hard origin/main

# RIGHT: ask Gemini first
sofi gemini review --prj PRJ-SAKK --text \
  "Need to discard local commits. Reason: X. Is this safe? Rollback plan?"
# Then, after Gemini says yes, execute + document in DECISIONS.md
```

**Real scope change?** Document in HANDOFFS.md, sync upstream. Don't re-route to Gemini.

```markdown
# HANDOFFS.md
- [ ] **SCOPE CHANGE (CEO decision):** Reduce feature X from full to MVP.
  Reason: timeline crunch. Approved: CEO (2026-07-02).
  Impact: 5 FE screens cut, backend API partial, 2-week save.
```

**Terminal error (outside your scope)?** Escalate up-chain, don't guess.

```bash
sofi escalate PRJ-SAKK ticket-123 <to> \
  "Blocked: Stripe API key not found in config. Permission missing?"
```

---

## Metrics & SLO

**For the weekly CEO audit:**

| Metric | Target | How to measure |
|--------|--------|---|
| **Gemini loop adoption** | 100% of decision points | Grep commits for "Gemini review" citation. Flag missing. |
| **Route latency** | <5 min from decision to push | Timestamp finding vs timestamp gemini_review call. |
| **Execution latency** | <30 min from reply to first commit | Timestamp gemini_review reply vs git log --since. |
| **Conversation token waste** | 0 deliberation, status-only | Audit messages for "what should we do?" → flag as defect. |
| **Self-correction loops** | Max 3/task | Log failures; on 4th, must have pushed to Gemini. |
| **Report file orphans** | 0 authored but not pushed | Find `.md` in `_context/reports/` with no HANDOFFS entry. |

---

## Compliance Checklist (for team leads)

Before launching a sprint:

- [ ] Every agent has read `AGENT_BRIEFING.md`
- [ ] `sofi gemini status` returns ✅
- [ ] Test push succeeds: `echo "test" | sofi gemini review --prj <PRJ> --json`
- [ ] HANDOFFS.md template exists and is tracked
- [ ] Gemini bridge config in place: `~/.engine/gemini_bridge.json` or env var
- [ ] At least one prior decision loop has been executed (not just theory)
- [ ] Team knows escalation path for "Gemini is unreachable"

---

## Escalation Path

**If Gemini desk is down or unreachable:**

1. Check status: `sofi gemini status`
2. Check bridge connectivity: `curl https://gemini.google.com` (basic test)
3. If down for >15 min:
   - Do NOT work blind. Escalate: `sofi escalate <PRJ> <ticket> <to> "Gemini unreachable, status blocked"`
   - CEO routes to DevOps or escalates deadline.
   - Do NOT guess or proceed with own decision-making.

---

## Examples (real usage)

**Example 1: Test mystery**

```bash
# Agent discovers 3 test failures after refactor
$ npm test

# After local debugging (3 attempts) fails, route to Gemini
$ sofi gemini review --prj PRJ-SAKK --json \
    --text "3 auth tests fail after middleware refactor…
    Tried: revert middleware, clear cache, isolation…
    Logs show: SessionStore::get() returns null (was OK before).
    Question: Did middleware refactor break session initialization? How to debug?" \
    --ask "Root cause + fix steps?"

# Gemini replies in 30s: "SessionMiddleware runs AFTER app boot in your order. Moved to BEFORE. Fixed. Test 5x."

# Agent executes: move middleware, test 5x, commit, done.
```

**Example 2: Architecture decision**

```bash
# Agent proposes 3 caching strategies
$ sofi gemini review --prj PRJ-SAKK --json \
    --text "Cache strategy decision:
    Option A: Redis (cost: cloud service, latency: 1ms)
    Option B: File cache (cost: 0, latency: 5ms, disk-bound)
    Option C: In-memory (cost: 0, latency: 0.1ms, memory-bound, no persistence)
    Workload: 10k daily active, read:write = 9:1, max 100MB.
    Which fits?" \
    --ask "Recommendation: which strategy, why, trade-offs?"

# Gemini replies: "Option A + cache-aside pattern. Rationale: …. Fallback to File if cloud quota hit."

# Agent implements Option A, tests under load, commits, done.
```

**Example 3: Blocker escalation (correct)**

```bash
# Agent hits a blocker BEFORE routing to Gemini
$ sofi escalate PRJ-SAKK ticket-456 <to> \
  "Waiting on: Stripe API key provisioning (outside my scope). Can't proceed without it. Unblock?"

# CEO assigns DevOps to provision, re-opens agent's ticket.
# Agent continues.
```

---

## Authority & Changes

This architecture is binding per DOCTRINE.md Teaching VII and Protocol 02.

Changes only by:
1. Amendment to DOCTRINE.md (consensus of 6+ founding principles)
2. CEO + OODA engine recommendation (data-driven)
3. Documented in DECISIONS.md with full rationale + ADR

No single agent, no single role, no external pressure can override this.

---

*Binding. Autonomous. Scalable. Gemini is the decision engine. Agents execute. Users observe.* 🚀
