# ADR-006 Implementation Guidance — Gemini Detailed Code Review
**Status:** FULL APPROVAL FOR EXECUTION  
**Priority Reordering:** By Gemini (criticality-first, not timeline-first)

---

## Execution Priority Order (Gemini Reordered)

Gemini assessed criticality and reordered phases. Original timeline (1→2→3→4→5→6) → Execution order (2→3→1→4→5→6):

1. **CRITICAL** — Phase 2: Resource Isolation (Port + DB + Caddy locks) — Days 3–5
2. **HIGH** — Phase 3: Gatekeeper Hardening (Sonnet 5 pre-flight classifier) — Days 6–8
3. **HIGH** — Phase 1: Handoff Integrity (Triple-Contract Check validation) — Days 1–2
4. **SECURITY** — Phase 4: Exfiltration Guard (regex sanitizer) — Day 9
5. **OBSERVE** — Phase 5: Observe Loop (Sentry → DECISIONS.md) — Days 10–11
6. **ORCHESTRATION** — Phase 6: Orchestration v2 (dynamic resource binding) — Days 12–13

**Rationale:** Fix shared-resource contamination risk first (Phase 2), then prevent expensive Fable 5 loops (Phase 3), then enforce handoff integrity (Phase 1). Exfiltration + observe + orchestration v2 run in parallel after core stability is established.

---

## Phase 2: Resource Isolation — CRITICAL (Days 3–5)

**Owner:** sofi-devops-cloud-lead  
**Risk:** Parallel squads on shared host → port collision, cross-project DB contamination

### Implementation Code (Gemini Provided)

**File:** `company/os/toolkit/devops/caddy_isolation.py`

```python
import os
import json
import fcntl
import sys
import hashlib

def acquire_project_lock(prj_id, squad_id):
    """
    Acquire exclusive lock on port + DB resources for a project squad.
    If collision detected, fail with clear error message.
    """
    lock_dir = os.path.expanduser("~/Desktop/Lorka/projects/.locks")
    os.makedirs(lock_dir, exist_ok=True)
    lock_file_path = os.path.join(lock_dir, f"{prj_id}.lock")
    
    # Deterministic port range per project
    # PRJ-SAKK -> 8000-8099, PRJ-SYRH -> 8100-8199
    hash_digest = hashlib.md5(prj_id.encode()).hexdigest()
    port_offset = (int(hash_digest, 16) % 50) * 2
    base_port = 8000 + port_offset
    
    try:
        f = open(lock_file_path, "w")
        # Exclusive non-blocking lock
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        manifest = {
            "squad_id": squad_id,
            "base_port": base_port,
            "mysql_db": f"sofi_{prj_id.lower()}_test",
            "caddy_subdomain": f"{prj_id.lower()}.zanjour.local"
        }
        f.write(json.dumps(manifest))
        f.flush()
        return f, manifest
    except IOError:
        print(f"[CRITICAL COLLISION] Resource lock for {prj_id} held by another squad. Halting execution.")
        sys.exit(1)

def generate_dynamic_caddyfile(manifest):
    """Generate per-squad Caddy config, reload systemd."""
    caddy_template = f"""
    {manifest['caddy_subdomain']} {{
        reverse_proxy 127.0.0.1:{manifest['base_port']}
        header_up X-Forwarded-Host {{host}}
    }}
    """
    
    with open(f"/etc/caddy/conf.d/{manifest['squad_id']}.caddy", "w") as cf:
        cf.write(caddy_template)
    os.system("systemctl reload caddy")

def release_project_lock(lock_file_obj, squad_id, manifest):
    """Release lock, tear down Caddy config."""
    fcntl.flock(lock_file_obj, fcntl.LOCK_UN)
    lock_file_obj.close()
    os.remove(f"/etc/caddy/conf.d/{squad_id}.caddy")
    os.system("systemctl reload caddy")
    print(f"[RESOURCE CLEANUP] Squad {squad_id} released. Caddy subdomains torn down.")
```

### Integration into `sofi dispatch --squad`

**Update:** `company/os/bin/sofi dispatch`

```bash
# In the dispatch function, before launching squad agents:

lock_file, manifest = caddy_isolation.acquire_project_lock(prj_id, squad_id)
caddy_isolation.generate_dynamic_caddyfile(manifest)

# Export to agents so they use correct port
export SOFI_SQUAD_PORT=${manifest['base_port']}
export SOFI_SQUAD_DB="sofi_${prj_id,,}_test"

# ... run squad agents ...

# After squad completion or failure:
caddy_isolation.release_project_lock(lock_file, squad_id, manifest)
```

### Test: Parallel PRJ-SAKK + PRJ-SYRH

```bash
# Terminal 1
sofi dispatch --squad PRJ-SAKK backend-lead frontend-lead

# Terminal 2 (simultaneous)
sofi dispatch --squad PRJ-SYRH mobile-lead

# Verify: Both squads run independently, zero port collision, zero DB cross-contamination
# Both complete successfully, Caddy subdomains torn down
```

**Success Criteria:**
- [ ] caddy_isolation.py implemented + tested
- [ ] sofi dispatch acquires/releases locks
- [ ] Port range deterministic per project (no randomness)
- [ ] Parallel test passes (zero collision)

---

## Phase 3: Gatekeeper Hardening — HIGH (Days 6–8)

**Owner:** CEO (orchestration) + sofi-backend-tech-lead  
**Risk:** Spec-review Fable 5 loops at 3.1 avg attempts → expensive tokens

### Implementation Code (Gemini Provided)

**File:** `company/os/toolkit/core/spec_review_preflight.py`

```python
def preflight_classify_failure(error_log, code_diff):
    """
    Before Fable 5 arbitration, route through cheap Sonnet 5 classifier.
    Classify root cause into TIER-0 (design) or TIER-2 (execution).
    """
    classifier_prompt = f"""
    Analyze this spec-review failure log and code diff. Classify the root cause into exactly one:
    
    - TIER-0: Fundamental logic breakdown / missing contract paths (Design failure → escalate to CEO)
    - TIER-2: Syntax error / missing import / test config (Execution failure → allow retry)
    
    Reply with ONLY: ESCALATE or RETRY_SUITE
    
    Error Log:
    {error_log}
    
    Diff:
    {code_diff}
    """
    
    verdict = call_light_model(classifier_prompt)  # Sonnet 5
    return verdict

def spec_review_with_circuit_breaker(prj_id, feature_code, attempt=1):
    """
    Enhanced spec-review with pre-flight classification + circuit breaker tuning.
    Target: 1.2 avg attempts (baseline: 3.1)
    """
    if attempt > 2:
        # After 2 failed attempts, escalate to CEO instead of retry
        escalate_to_ceo(f"Spec-review hard-failed after 2 attempts for {prj_id}. Manual arbitration needed.")
        return "ESCALATED"
    
    # Try spec-review
    result = spec_review(feature_code)
    
    if result.failed:
        # Pre-flight classify before retry
        classification = preflight_classify_failure(result.error_log, result.code_diff)
        
        if classification == "ESCALATE":
            # Design failure → escalate to CEO
            escalate_to_ceo(f"Design-layer failure in {prj_id}. Classification: TIER-0")
            return "ESCALATED"
        else:
            # Execution failure → allow retry (up to 2 times)
            log_attempt(prj_id, attempt, "TIER-2", result.error_log)
            return spec_review_with_circuit_breaker(prj_id, feature_code, attempt + 1)
    
    return result
```

### Integration into `.claude/skills/sofi-spec-review/SKILL.md`

Update hard-gate documentation:
```markdown
## Circuit Breaker Tuning (ADR-006 Phase 3)

- Attempt 1: Full spec-review (Fable 5)
- If failed, Attempt 2: Pre-flight Sonnet 5 classification
  - If TIER-0 (design) → escalate to CEO immediately
  - If TIER-2 (execution) → allow retry
- After 2 failed attempts on same finding → escalate to CEO (no further retries)

Target: 1.2 avg attempts per failing spec-review (baseline: 3.1)
```

### Test: Intentional Violations

```bash
# Inject spec-review violations
echo "Invalid 422 to 302 conversion" >> sakk-payments.rb

# Run spec-review
sofi spec-review PRJ-SAKK

# Verify:
# - Attempt 1: Full Fable 5 review
# - Attempt 2: Sonnet 5 pre-flight classifier
# - Correct routing (design violation → CEO escalation)
# - Measure: avg attempts should drop to ~1.2
```

**Success Criteria:**
- [ ] Sonnet 5 pre-flight classifier implemented
- [ ] Circuit breaker tuning active (2 attempts → escalate)
- [ ] Verdict caching reduces Fable 5 calls by 40%+
- [ ] Test passes (violations route correctly)

---

## Phase 1: Handoff Integrity — HIGH (Days 1–2)

**Owner:** sofi-principal-system-architect  
**Risk:** Semantic drift Telephone effect across multi-agent handoff chains

### Implementation Code (Gemini Provided)

**File:** `company/os/bin/sofi` (checkpoint command update)

```python
import re
import sys

def validate_handoff_contract_check(handoff_file_path):
    """
    Enforce Triple-Contract Check schema on all handoffs.
    Reject commit if validation blocks missing or unchecked.
    """
    with open(handoff_file_path, "r") as f:
        content = f.read()
    
    # Strict regex patterns for Triple-Contract Check
    has_origin = re.search(
        r'-\s*\[x\]\s*\*?\*?Upstream Origin:\*?\*?\s*Traced to UX Prototype',
        content,
        re.IGNORECASE
    )
    has_parity = re.search(
        r'-\s*\[x\]\s*\*?\*?Contract Parity:\*?\*?\s*API resource inputs match',
        content,
        re.IGNORECASE
    )
    has_immutability = re.search(
        r'-\s*\[x\]\s*\*?\*?Data Immutable:\*?\*?\s*No destructive migrations',
        content,
        re.IGNORECASE
    )
    
    if not (has_origin and has_parity and has_immutability):
        print("[METADATA VIOLATION] Handoff rejected!")
        print("Your HANDOFFS.md block must contain fully checked Triple-Contract validation tokens:")
        print("  - [x] **Upstream Origin:** Traced to UX Prototype Screen ID")
        print("  - [x] **Contract Parity:** API resource inputs match Flutter Cubit state signature")
        print("  - [x] **Data Immutable:** No destructive migrations without explicit ADR")
        sys.exit(1)
    
    return True
```

### Update `sofi checkpoint` Command

```bash
# In company/os/bin/sofi checkpoint:

# Before git commit, validate handoff contract check
python3 -c "from caddy_isolation import validate_handoff_contract_check; validate_handoff_contract_check('company/brain/org/HANDOFFS.md')"

git add .
git commit -m "..."
```

### Backfill: 10 Recent Handoffs

```bash
# Retroactively validate 10 recent PRJ-SAKK handoffs
git log --oneline | grep "feat:\|fix:" | head -10 | while read commit msg; do
  echo "Validating handoff for commit $commit..."
  # Check if commit included HANDOFFS.md update
  # Append contract check if missing
done
```

### Test: Reject Invalid Handoff

```bash
# Create mock handoff without contract check
echo "## Next Ticket
- Task: Fix auth modal
- Assigned: sofi-frontend-tech-lead" >> HANDOFFS.md

# Try checkpoint
sofi checkpoint PRJ-SAKK "feat: auth modal fix"

# Should reject with metadata violation error
```

**Success Criteria:**
- [ ] Protocol document (04-handoff-interconnect.md) updated
- [ ] sofi checkpoint validates + rejects invalid handoffs
- [ ] 10 backfilled handoffs pass validation
- [ ] Mock test passes (rejection on missing schema)

---

## Phase 4: Exfiltration Guard — SECURITY (Day 9)

**File:** `company/os/toolkit/core/sanitize_gemini_payload.py`

```python
import re

def sanitize_gemini_payload(raw_text):
    """
    Strip sensitive patterns before pushing report to external Gemini.
    Zero tolerance for secrets, API keys, DB hashes, auth tokens.
    """
    patterns = {
        r"sk_live_[0-9a-zA-Z]{24}": "[REDACTED_STRIPE_LIVE_KEY]",
        r"APP_KEY=[^\s]+": "APP_KEY=[REDACTED_LARAVEL_KEY]",
        r"PASSWORD=[^\s]+": "PASSWORD=[REDACTED_DATABASE_SECRET]",
        r"(?i)bearer\s+[0-9a-zA-Z\-\._~\+\/]+=*": "Bearer [REDACTED_AUTH_TOKEN]",
        r"GEMINI_CHAT_ID=[^\s]+": "GEMINI_CHAT_ID=[REDACTED]",
        r"cloudflare_token=[^\s]+": "cloudflare_token=[REDACTED]"
    }
    
    sanitized = raw_text
    for pattern, replacement in patterns.items():
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized
```

### Wiring into `gemini_bridge.py`

```python
# Before pushing to external Gemini:
sanitized_payload = sanitize_gemini_payload(report_text)
push_to_gemini(sanitized_payload)
```

---

## Phase 5: Observe Loop — Days 10–11

**File:** `company/os/toolkit/gate/observe_sentry_loop.py`

```python
def append_runtime_constraint_to_brain(prj_id, exception_summary):
    """
    Inject production-observed constraints back into project brain.
    Sentry exception → DECISIONS.md entry (Gate 8 feedback loop).
    """
    decision_file_path = os.path.expanduser(f"~/Desktop/Lorka/projects/PRJ-{prj_id}/_context/DECISIONS.md")
    
    log_entry = f"""

### [RUNTIME_OBSERVATION] - {datetime.now().isoformat()}
- **Source:** Automated Sentry Gate-8 Sync
- **Constraint:** {exception_summary}
- **Impact:** Future code generations for this layer must explicitly account for this runtime anomaly to prevent recurrence.
"""
    
    with open(decision_file_path, "a") as df:
        df.write(log_entry)
    
    print(f"[OBSERVE LOOP] Successfully hydrated PRJ-{prj_id} brain with latest production edge-case.")
```

---

## Phase 6: Orchestration v2 — Days 12–13

**File:** `company/os/toolkit/core/squad_orchestrator_v2.py`

Extends Phase 2 resource locking with dynamic manifest + auto-cleanup.

---

## Execution Checklist

### Week 1 (Days 1–7)

- [ ] **Day 1–2:** Phase 1 (Handoff Triple-Contract) implemented + backfilled
- [ ] **Day 3–5:** Phase 2 (Resource isolation) locks + Caddy teardown live
- [ ] **Day 6–7:** Phase 3 (Gatekeeper) pre-flight classifier wired

### Week 2 (Days 8–13)

- [ ] **Day 8:** Phase 3 testing + circuit breaker validation
- [ ] **Day 9:** Phase 4 (Exfiltration sanitizer) live + audit trail active
- [ ] **Day 10–11:** Phase 5 (Observe loop) Sentry → DECISIONS.md syncing
- [ ] **Day 12–13:** Phase 6 (Orchestration v2) parallel squad testing

### Re-Audit

- [ ] **2026-07-23 (3 weeks post-launch):** Gemini full re-audit
- [ ] Compare success metrics vs. baselines
- [ ] Publish ADR-007 "ADR-006 Remediation Outcomes"

---

## Success Metrics (Target Validation)

| Metric | Target | Baseline | Validation |
|--------|--------|----------|-----------|
| Handoff semantic drift | 0 / 50 | 2–3 / 50 | Audit HANDOFFS.md + code review |
| Cross-project test failures | 0% | 15% | 3-way parallel squad test |
| Spec-review avg attempts | 1.2 | 3.1 | Log analysis |
| Exfiltration incidents | 0 detected | 1 | Audit trail review |
| Gate 8 latency | <10 min | N/A | Integration test |
| Parallel overhead | <10% | N/A | Token cost comparison |

---

**Status:** Ready for immediate execution. All code provided. Gemini approves. 🎯
