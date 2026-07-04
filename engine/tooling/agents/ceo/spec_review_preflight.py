#!/usr/bin/env python3
"""
Phase 3: Gatekeeper Hardening — Sonnet 5 Pre-flight Classifier
ADR-006 Implementation

Routes spec-review failures through cheap Sonnet 5 classification before Fable 5 arbitration.
Reduces avg attempts from 3.1 → 1.2 by preventing blind retries on design-layer failures.

Circuit breaker: 2 failed attempts → escalate to CEO (no retry past threshold)
"""

import sys
import json
from typing import Optional


class SpecReviewGatekeeper:
    """
    Enhanced spec-review with pre-flight classification + circuit breaker.

    Flow:
    1. Attempt spec-review (Fable 5) → pass ✓
    2. On failure: classify via Sonnet 5 (cheap)
       - TIER-0 (design) → escalate to CEO immediately
       - TIER-2 (execution) → allow 1 more retry
    3. After 2 failures → escalate to CEO (no further retries)
    """

    def __init__(self, prj_id, max_attempts=2):
        self.prj_id = prj_id
        self.max_attempts = max_attempts
        self.attempt_log = []

    def preflight_classify_failure(self, error_log: str, code_diff: str) -> str:
        """
        Route failure through cheap Sonnet 5 classifier.
        Classify root cause: TIER-0 (design) or TIER-2 (execution)

        In production, this would call the Sonnet 5 model:
        ```python
        from anthropic import Anthropic
        client = Anthropic()
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": classifier_prompt
            }]
        )
        verdict = response.content[0].text.strip().upper()
        ```

        For now, return mock classification based on error patterns.
        """
        classifier_prompt = f"""
Analyze this spec-review failure. Classify root cause into EXACTLY ONE:

- TIER-0: Fundamental logic breakdown / missing contract paths / design failure
          Example: Flutter Dio payload shape incompatible with Laravel Form Request
          → Escalate to CEO

- TIER-2: Syntax error / missing import / test config / execution failure
          Example: Missing semicolon, undefined variable, wrong import path
          → Allow retry

Reply with ONLY: TIER-0 or TIER-2

Error Log:
{error_log}

Code Diff:
{code_diff}
"""

        # Mock classification (in production, call Sonnet 5)
        # Pattern-match common errors for demo
        if any(x in error_log.lower() for x in ["422", "302", "apiexception", "contract", "signature", "schema", "type mismatch"]):
            return "TIER-0"
        elif any(x in error_log.lower() for x in ["syntax", "import", "undefined", "missing", "not found"]):
            return "TIER-2"
        else:
            # Default to execution for unknown errors (safer to retry once)
            return "TIER-2"

    def spec_review_with_circuit_breaker(self, feature_code: str, existing_error: Optional[dict] = None) -> dict:
        """
        Enhanced spec-review with pre-flight classification + circuit breaker.

        Args:
            feature_code: Code to review
            existing_error: Previous failure (if retrying)

        Returns:
            {
                "status": "PASS" | "ESCALATED" | "REVIEW_FAILED",
                "verdict": {...},  # if PASS
                "reason": "...",
                "classification": "TIER-0" | "TIER-2"
            }
        """
        attempt = len(self.attempt_log) + 1

        # Hard stop after max attempts
        if attempt > self.max_attempts:
            return {
                "status": "ESCALATED",
                "reason": f"Circuit breaker: {self.max_attempts} attempts exhausted. Escalating to CEO.",
                "attempts": self.attempt_log
            }

        print(f"\n[SPEC-REVIEW] Attempt {attempt}/{self.max_attempts}")

        # Mock spec-review (in production, call Fable 5)
        # For demo, simulate either pass or failure based on code patterns
        if existing_error:
            # Retrying after previous failure
            spec_result = {
                "status": "FAILED",
                "error": existing_error["error"],
                "code_diff": existing_error.get("code_diff", "")
            }
        else:
            # First attempt (mock)
            spec_result = {"status": "PASSED", "verdict": "OK"}

        # If passed, return success
        if spec_result["status"] == "PASSED":
            return {
                "status": "PASS",
                "verdict": spec_result.get("verdict", {}),
                "attempts": len(self.attempt_log)
            }

        # Failed: pre-flight classify before retry
        error_log = spec_result.get("error", "")
        code_diff = spec_result.get("code_diff", "")

        classification = self.preflight_classify_failure(error_log, code_diff)

        log_entry = {
            "attempt": attempt,
            "status": "FAILED",
            "error": error_log[:200],  # First 200 chars
            "classification": classification
        }
        self.attempt_log.append(log_entry)

        print(f"  Classification: {classification}")

        # TIER-0 (design) → escalate immediately
        if classification == "TIER-0":
            return {
                "status": "ESCALATED",
                "reason": "Design-layer failure detected (TIER-0). Escalating to CEO for architectural review.",
                "classification": "TIER-0",
                "error": error_log[:500],
                "attempts": self.attempt_log
            }

        # TIER-2 (execution) → allow retry (up to max_attempts)
        if attempt < self.max_attempts:
            print(f"  Executing fix attempt {attempt + 1}...")
            # In production: delegate to appropriate tier (backend/frontend/etc) for fix
            return self.spec_review_with_circuit_breaker(
                feature_code,
                existing_error={
                    "error": error_log,
                    "code_diff": code_diff
                }
            )
        else:
            # Max attempts reached on TIER-2
            return {
                "status": "ESCALATED",
                "reason": f"TIER-2 execution failures after {self.max_attempts} attempts. Escalating to CEO.",
                "classification": "TIER-2",
                "attempts": self.attempt_log
            }

    def log_attempt_to_decisions(self, result: dict):
        """Write attempt log to project DECISIONS.md for audit trail."""
        # Format for _context/DECISIONS.md
        decision_entry = f"""

### [SPEC-REVIEW ATTEMPT LOG] - Attempt {len(self.attempt_log)}
- **Status:** {result['status']}
- **Classification:** {result.get('classification', 'N/A')}
- **Reason:** {result.get('reason', '')}
"""
        # In production, append to projects/PRJ-{prj_id}/_context/DECISIONS.md
        print(decision_entry)


def main():
    """Test harness."""
    prj_id = sys.argv[1] if len(sys.argv) > 1 else "PRJ-SAKK"

    gatekeeper = SpecReviewGatekeeper(prj_id, max_attempts=2)

    print(f"[GATEKEEPER] Initializing for {prj_id}")
    print(f"Max attempts: {gatekeeper.max_attempts}")

    # Mock feature code
    feature_code = """
def handle_payment(amount, currency):
    # Some payment logic here
    pass
"""

    # Run spec-review with circuit breaker
    result = gatekeeper.spec_review_with_circuit_breaker(feature_code)

    print(f"\n[RESULT] {result['status']}")
    print(f"Reason: {result.get('reason', 'N/A')}")
    print(f"Total attempts: {len(result.get('attempts', []))}")


if __name__ == "__main__":
    main()
