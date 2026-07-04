# Testing Autonomous Gemini Loop (Teaching VII)

> **Authority:** Gemini validation (2026-07-02). **Phase:** Canary testing before team broadcast.

---

## Phase 1: Solo Agent Test (This Session)

### Step 1: Hydrate Agent Memory
```bash
python3 engine/tooling/agents/ceo/agent_preflight.py
# Expected: ✅ Agent hydrated: 4 files, 44332 chars
```

### Step 2: Test Output Guard (Intentional Violation)
```bash
# Create test output with violation pattern
cat << 'EOF' | python3 engine/tooling/agents/ceo/agent_output_guard.py PRJ-SAKK
# Agent work complete. Next steps unclear.
# What should I do now? Which option is better?
EOF

# Expected output:
# ❌ HALT: Autonomous loop violation...
# Command: sofi gemini review --prj PRJ-SAKK...
# Exit code: 1
```

### Step 3: Test Guard Pass (Clean Output)
```bash
# Clean status output (allowed)
cat << 'EOF' | python3 engine/tooling/agents/ceo/agent_output_guard.py PRJ-SAKK
[status] Pushed findings to desk. Executing guidance. Committed migration fix.
EOF

# Expected: Output passes through cleanly, exit code 0
```

### Step 4: Test Pre-flight + Wrapper (Integrated)
```bash
# Simulate agent + guard pipeline
agent_output=$(python3 engine/tooling/agents/ceo/agent_preflight.py)
echo "$agent_output" | python3 engine/tooling/agents/ceo/agent_output_guard.py PRJ-SAKK

# Expected: passes (no user ask in preflight output)
```

---

## Phase 2: Canary Deployment (Next 3 Agents)

### Broadcast to Canary Team (3 agents)
1. Share AGENT_BRIEFING.md link
2. Add to SessionStart hook:
   ```bash
   python3 engine/tooling/agents/ceo/agent_preflight.py > /dev/null
   ```
3. Wrap agent dispatch:
   ```bash
   engine/tooling/agents/ceo/agent_wrapper.sh PRJ-SAKK <agent_command>
   ```

### Monitor (First 5 Gemini Pushes)
- [ ] prune() reducing context bloat (check `sent_chars` in gemini_review.py output)
- [ ] No breaches of output guard (commits don't have user asks)
- [ ] agent_preflight.py runs without error
- [ ] Commits cite Gemini source

### Metrics (CEO Dashboard)
```bash
# Adoption rate
git log --oneline --grep="Gemini review" | wc -l

# Context reduction (prune effectiveness)
# Before: gemini_review.py line 297 sent_chars
# After: line 298 (post-prune) chars
# Ratio = after/before (should be ~0.08 for 92% reduction)

# Loop compliance
git log --oneline | grep -c "Guided by Gemini"
```

---

## Phase 3: Full Broadcast (After Canary Clean)

When canary shows:
- ✅ 0 violations caught (guard working)
- ✅ prune() effective (>80% reduction)
- ✅ All commits cite Gemini
- ✅ agent_preflight hydration silent + successful

Then:

1. **Broadcast to all agents** (AGENT_BRIEFING.md is now required)
2. **Wire wrapper into dispatch** (all agent CLI calls go through guard)
3. **Enable metrics dashboard** (CEO monitors adoption %)
4. **Set SLOs:**
   - Route latency: <5 min (decision point → Gemini push)
   - Execution latency: <30 min (reply → first commit)
   - Violation detection: <1 per 100 commits (near-zero)

---

## Rollback (If Issues Arise)

**If output guard triggers false positives:**
1. Halt: don't disable guard
2. Refine regex in agent_output_guard.py (VIOLATION_PATTERNS)
3. Add exception patterns for code blocks, quoted text, etc.
4. Re-test on canary

**If circuit breaker triggers too early:**
1. Audit loop counter logic (should only count failed retries)
2. Increase max to 5 if justified (keep escalation path)
3. Document in ADR + DECISIONS.md

**If prune() drops signal:**
1. Review prune() logic (may be too aggressive)
2. Add to keep_patterns if needed
3. Prefer keeping more context over aggressive pruning

---

## Success Criteria (Gate Check)

- [x] DOCTRINE Teaching VII written + binding
- [x] Protocol 02 with 4-layer stack documented
- [ ] Output guard tested (intentional violations halt)
- [ ] Pre-flight hydration tested (agents load briefing)
- [ ] Canary team runs without violations
- [ ] Context pruning effective (>80% reduction)
- [ ] Slack escalation channel wired
- [ ] Team briefing scheduled (broadcast date)
- [ ] CEO dashboard live (adoption %, SLO tracking)
- [ ] First full week without violations

Gate 7 (Prod release) only after all checkboxes ✅.

---

*Validate, canary, broadcast. No exceptions.*
