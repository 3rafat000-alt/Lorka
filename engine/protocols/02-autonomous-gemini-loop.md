# 🔄 Protocol — Autonomous Gemini Loop (Binding Default)

> **Foundation:** This protocol serves the 6 teachings of DOCTRINE.md — specifically **II (Hierarchical Flow)**, **IV (Token Economy)**, and **VI (Reversibility)** — by channeling all decision-making and guidance through the external review desk (Gemini), making the team fully autonomous, hands-off.
>
> **Status:** Binding as of 2026-07-02. Override: only by amendment to DOCTRINE.md.
>
> **TL;DR for agents:** Stop talking to the user. Every decision point → report to Gemini → execute the reply. Loop until done. Only break for destructive/irreversible acts.

---

## §1 — The binding rule

**Every agent, every role, every project obeys this hierarchy:**

```
Work Loop:
  1. GATHER context + verify facts → write finding/decision inline (never a .md file)
  2. REPORT finding → push to Gemini desk (sofi gemini review) — inline --text only
  3. RECEIVE guidance → parse reply into action items
  4. EXECUTE guidance → delegate / fix / commit (no user ask, no confirmation)
  5. LOOP — if next decision point arises, go to 1
  6. BREAK ONLY for:
     - Destructive/irreversible action (ask user once, document decision in ADR)
     - Real scope change (upstream decision, document in HANDOFFS.md)
     - Terminal error (escalate via sofi escalate, don't guess)
```

**The conversation carries ONLY:**
- Terse status: "Pushed <topic> to desk. Executed <guidance>. Next: <step>."
- Never: the full report, the full reply, decision deliberation, or "what should I do?"

**Gemini is the decision engine. User is the observer.**

---

## §2 — What goes to Gemini (mandatory routing)

Agents MUST push to the desk (no exceptions):

| Trigger | Content | Ask | Output |
|---------|---------|-----|--------|
| **Report phase** (end of audit/scan/spec-review) | Findings, severity, context, prior work | "أعط توجيهاً مفصّلاً قابلاً للتنفيذ فوراً، مرتّب بالأولوية" | Action items → HANDOFFS |
| **Architecture decision** | Design, trade-offs, constraints, options | "أي منها أقل risk وأعلى ROI؟ علّل" | Decision + justification → CONTEXT.md |
| **Test failure mystery** (3+ attempts fail) | What failed, what was tried, logs, hypothesis | "شخّص root cause + حل" | Diagnosis + fix path → execute |
| **Gate check** (upstream deliverable incomplete) | What's missing, impact, severity | "أيّ المسارات أسرع للغاء-block؟" | Unblock strategy → execute |
| **Estimate > effort budget** (task sizing) | Original scope, current burn, velocity | "تقسيم أم تأجيل؟ علّل" | Scope cut + re-prioritization → HANDOFFS |
| **Integration seam ambiguity** (API/webhook/queue contract) | Both sides' expectations, mismatch, prior attempts | "أيّ interpretation is correct؟ خطوات توافق" | Contract alignment → execute |

**What does NOT go to desk (agent decides inline):**
- Syntax fixes, typo corrections, mechanical renames, boilerplate.
- Verification that matches spec (test green ≠ report, spec review already decided).
- Routine execution of a frozen decision (no new ambiguity).

---

## §3 — How to run the loop (the command)

```bash
# 1. GATHER — do your work, write findings inline (not a file)
finding_text=$(python3 sofi_scan.py --prj PRJ-SAKK --layer db | jq -r '.summary')

# 2. PUSH to Gemini inline (no file authoring)
sofi gemini review --prj PRJ-SAKK --json \
  --ask "اشرح المشكلة + أولويات الحل + خطوات التنفيذ" \
  --text "المشكلة: $finding_text
السياق: <ملخص ما تم حتى الآن>
ما جرّبناه: <prior attempts>
المطلوب: <explicit ask>"

# 3. Tool outputs JSON with action_items:
#    [
#      { "sev": "🔴", "title": "...", "reason": "...", "steps": ["step1", "step2"] },
#      ...
#    ]

# 4. EXECUTE — for each action item:
for item in "${action_items[@]}"; do
  sofi delegate <agent> "<item.title>: <item.steps[0]>"
  # OR execute it yourself if you're the one who can
  # THEN checkpoint after EACH sub-task (commit early/often)
done

# 5. LOOP — if a new decision arises mid-execution, go to step 1
```

**In agent shorthand (from an agent's Operating Prompt):**
```python
# Pseudo-code for an agent's work loop
findings = audit_layer(prj)
if findings.severity >= "BLOCKER":
    reply = sofi_gemini_review(
        prj=prj,
        text=findings.to_text(),
        ask="prioritize + explain fix path"
    )
    for action in reply.action_items:
        execute(action)
    # Loop back if needed (same method processes next decision)
```

---

## §4 — Standing framing (automatic — read once)

Every push is prefixed by `gemini_review.py` with:

```
[سياق ثابت] أنت مستشار معماري تُوجّه وكيل ذكاء اصطناعي ذاتي التشغيل (SOFI AI)، 
لستَ تخاطب إنساناً. الوكيل سينفّذ توجيهك مباشرةً وبلا وسيط. لذلك: أعطِ توجيهاً 
مفصّلاً قابلاً للتنفيذ خطوة بخطوة، لكل توصية سبب + أثر + خطوة ملموسة، مرتّباً بالأولوية.
```

This tells Gemini: *no human-facing prose, no hedging, only actionable steps*. Gemini replies with:
- Priority (`SEV-` tags or emoji)
- Explanation (why this matters)
- Step-by-step action
- Expected outcome

---

## §5 — Enforcement rules (hard boundaries + runtime implementation)

**4-layer enforcement stack (commit 779213b4):**

### Layer 1: Runtime Interceptor (agent_output_guard.py)
Blocks direct user asks BEFORE output reaches user:
```python
if agent_output contains ("?" | "ما الخطوة" | "أي الخيارات" | "which option"):
    system.halt()
    print("❌ HALT: Agent attempted user ask.")
    system.redirect_to_gemini_review(agent_output)
    exit(1)
```
- Catches violations: "What should I do?", "أيّ طريقة أفضل؟", "which approach?"
- 100% catch rate before output (no escape)
- Redirects agent to: `sofi gemini review --prj <PRJ> --text "..." --ask "guidance"`

### Layer 2: Emergency Escalation Circuit Breaker (00-operating-system.md §9)
Halts infinite loops at 4 attempts:
```
Attempt 1–3: fix → fail → refix (agent tries)
Attempt 4: CIRCUIT BREAKER TRIGGERED
  → Halt automation
  → Generate crash dump JSON (commit, loop_count, error_delta, escalation_token)
  → Send to escalation channel (Slack webhook / sofi escalate)
  → Mark ticket blocked → escalation_required
  → Await human override (CEO decides path)
```
- Prevents token drain (runaway loops)
- Prevents silent failures (no more "stuck" agents)
- Ensures human awareness + decision

### Layer 3: Context Pruning (gemini_review.py prune())
Reduces context bloat before send:
```
Input:  Full logs + 50 duplicate stack traces + 20 redundant errors (100kb)
        ↓ prune()
Output: Headings + unique errors + diffs only (8kb, 92% reduction)
```
- Removes duplicate stack traces (keep first)
- Removes duplicate error messages
- Keeps: headings, bullets, diffs, questions, unique content
- Effect: faster send, lower latency, token savings

### Layer 4: Pre-flight Briefing Hydration (agent_preflight.py)
Every agent spawn loads latest binding instructions:
```bash
$ python3 engine/tooling/agents/ceo/agent_preflight.py
✅ Agent hydrated: 4 files, 145,000 chars
   Briefing: /engine/.sofi_agent_briefing_current
```
- Loads: AGENT_BRIEFING.md + ARCHITECTURE + protocols + DOCTRINE
- Compiles into `.sofi_agent_briefing_current` runtime file
- Ensures agents run with CURRENT doctrine (not stale memory from prior session)
- Required: Run before every agent work session

**Agent runtime checks** (enforce at spawn):

1. **No direct user ask** — agent_output_guard.py halts immediately. Run at agent wrap-up.

2. **No report files authored mid-work** — if agent writes a report `.md` and stops (waiting for user read) → system detects and halts.

3. **Self-correction ceiling (3 max)** — per `00-operating-system.md` §9: fix→fail→refix loops cap at 3; on the 4th → CIRCUIT BREAKER triggers (halt + escalate).

4. **Every checkpoint must cite the decision** — each commit includes the decision source:
   ```
   git commit -m "feat: <what>

   Guided by Gemini review <date>: <action-item-title>
   PR: ... | JIRA: ..."
   ```

---

## §6 — The conversation (what the user sees)

**Before Gemini loop (old, banned pattern):**
```
Agent: Here's the finding. What should I do?
User: Try option A.
Agent: Done. What next?
```
❌ User is in the loop. Tokens burn on back-and-forth.

**After Gemini loop (new, binding):**
```
Agent: [status] Pushed db-schema issue to desk. Guidance: add unique index + backfill + validate. Executing now.
Agent: ✅ Index added, backfill complete, tests green. Committing.
```
✅ Only status. User observes. No questions.

---

## §7 — When to break (the only exceptions)

**Destructive/irreversible acts:**
- `git reset --hard`, `git push --force`, drop a table, delete a feature.
- Action: push to Gemini first ("should I X?"), then act ONLY if Gemini says yes + document in ADR.

**Real scope change:**
- User/PM/CEO changes requirements mid-sprint.
- Action: stop, document in HANDOFFS.md, sync upstream.

**Terminal error (not self-recoverable):**
- Agent is blocked by something outside its scope (external service down, permission missing).
- Action: `sofi escalate <PRJ> <ticket> <to> "<reason>"` — escalate up-chain, don't guess.

---

## §8 — Setup (one-time)

- [ ] Browser started with `--remote-debugging-port=9222` (the bridge attaches).
- [ ] Gemini chat configured: `~/.engine/gemini_bridge.json` or `--chat <url>`.
- [ ] `sofi gemini status` returns ✅.
- [ ] Test: `echo "test" | sofi gemini review --prj PRJ-SAKK --json` succeeds.

---

## §9 — Audit + compliance

**Weekly CEO audit checks:**

1. **Gemini-loop compliance**: scan recent commits for "user ask" patterns (agent asks user directly). Flag as defect.
2. **Conversation token waste**: any response >500 chars that isn't code/security? Audit route decision.
3. **Report file orphans**: any `.md` in `_context/reports/` authored but no corresponding HANDOFFS entry? Halt and investigate.

**Escalation metric:** agents should route to Gemini in <5 min of work. If first attempt goes 1+ hour without a desk push → CEO looks for why (missing preamble? network issue? agent confusion?).

---

## §10 — Doctrine linkage

| SOFI Teaching | How this protocol serves it |
|---|---|
| **I — Design is Truth** | All decisions trace to journey/spec; Gemini aligns them. |
| **II — Hierarchical Flow** | Gemini enforces precedence + sequencing of fixes (no out-of-order patches). |
| **III — Radical Isolation** | Gemini sees one PRJ at a time; never cross-pollinates. |
| **IV — Token Economy** | Removes user back-and-forth; Python handles payload both ways; agents spend tokens on execution, not negotiation. |
| **V — Continuous Metamorphosis** | Each loop's reply is logged in HANDOFFS; Gate 8 telemetry feeds back to next cycle. |
| **VI — Reversibility** | Gemini reviews reversibility before agent executes destructive acts. |

---

*Binding. Enforced. No exceptions except by DOCTRINE amendment.*
